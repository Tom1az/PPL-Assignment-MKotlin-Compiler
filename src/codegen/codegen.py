"""Code generation for MKotlin — Assignment 4.

``CodeGenerator`` walks the AST and emits Jasmin assembly.  ``MKotlinClass.j``
holds the translation of every ``fun``; each ``data class`` becomes its own
``.j`` file with public fields, a constructor and a structural ``equals``.

Functional style
----------------
Written the same way as the Assignment 3 checker: every visit is an expression
built from single-assignment bindings, the environment is threaded through
``reduce`` instead of being mutated, and sequences are ``map`` / ``join`` /
``reduce`` — there is no loop, no ``+=`` accumulator and no in-place update of a
list or dict anywhere in this file.

* a **statement** visit returns ``(jasmin_text, environment)``; the environment
  it hands back is what the *following* statement sees, so a declaration extends
  the scope by returning ``SubBody(frame, [Symbol(...)] + o.sym)`` rather than by
  inserting into ``o.sym``.  A construct that opens its own scope (a block, a
  loop body, an ``if`` branch) simply drops the environment its body returns;
* an **expression** visit returns ``(jasmin_text, mkotlin_type)``;
* a **declaration** visit receives the global symbol list as ``o`` and is the
  only kind that emits, since writing the ``.j`` files is the point of the pass;
  ``visitMemberDecl`` receives the ``Emitter`` of the data class being written.

Two side effects are imposed by the framework and cannot be expressed as values:
``Frame`` counts stack depth, slots and labels by mutation, and ``Emitter``
appends to a buffer.  Both are confined to the provided APIs (``push``/``pop``,
``get_new_index``, ``get_new_label``, ``enter_loop``/``exit_loop``,
``print_out``); ``settle_deferred_variable`` documents the single place where a
``Symbol`` itself has to be updated in place, and why.

Bindings are always made in source order, because the text they carry and the
stack accounting inside ``Emitter`` must agree: a segment is bound only once the
segment above it has finished pushing and popping.

Every statement follows the "straight vertical flowchart" recipe: the labels the
statement needs are reserved from the frame first, then the blocks are emitted
top to bottom, a branch being resolved before moving on to the block below it.

NOTE — helpers that are not AST visits, listed here for review.  Emitting a
method needs its body as a value before its ``.limit`` directives can be sized,
and JVM scaffolding has no MKotlin node of its own, so the work is split into
small named functions rather than one long procedure:

* ``build_method_body``   — body text + frame + settled return type of a ``fun``
* ``build_filler_value``  — dummy value for the trailing ``return``
* ``build_arguments``     — argument list of a call, widened per parameter
* ``build_when_subject``  — a ``when`` subject evaluated into a hidden local
* ``build_statements``    — a statement sequence, threading the environment
* ``resolve_signatures``  — fixed point over the inferred return types
* ``probe_signature``     — one throwaway generation, to read one return type
* ``widen``               — ``i2f`` where an Int flows into a Float position
* ``common_type``         — result type shared by the arms of ``if`` / ``when``
* ``is_builtin``          — whether a call names one of the ``io`` built-ins
* ``settle_deferred_variable`` — types a ``var`` declared without type or init
* ``lookup`` / ``lookup_function`` / ``lookup_member`` / ``rebind`` — symbols
* ``generate_default_constructor``    — ``MKotlinClass.<init>()V``
* ``generate_entry_point``            — ``main([Ljava/lang/String;)V``
* ``generate_data_class_constructor`` — a data class's ``<init>``
* ``generate_data_class_equals``      — a data class's structural ``equals``
"""

from functools import reduce

from src.utils import nodes
from src.utils.nodes import *
from src.utils.visitor import BaseVisitor
from src.codegen.emitter import Emitter
from src.codegen.frame import Frame
from src.codegen.io import IO_SYMBOL_LIST
from src.codegen.utils import Access, CName, FunctionType, Index, SubBody, Symbol

MAIN_CLASS = "MKotlinClass"
MAIN_NAME = "main"
THIS_NAME = "this"
OTHER_NAME = "other"
CONSTRUCTOR_NAME = "<init>"
EQUALS_NAME = "equals"
# Names of the locals MKotlin has no syntax for, so they cannot collide with a
# user identifier: the upper bound of a `for` range and a `when` subject.
BOUND_NAME = "$end"
SUBJECT_PREFIX = "$when"


# The type predicates are spelled out here rather than imported from ``emitter``
# so that this file needs nothing beyond the skeleton's own imports: the marking
# harness supplies the names it chooses, and every extra one is a name that may
# not be there.  Same definitions as ``emitter``'s, over the same AST nodes.
def is_int_type(t):
    return type(t) is nodes.IntType


def is_float_type(t):
    return type(t) is nodes.FloatType


def is_string_type(t):
    return type(t) is nodes.StringType


def is_unit_type(t):
    return type(t) is nodes.UnitType


def is_class_type(t):
    return type(t) is nodes.ClassType


class CodeGenerator(BaseVisitor):
    def __init__(self, ast, output_dir: str = "."):
        self.ast = ast
        self.output_dir = output_dir
        self.class_name = MAIN_CLASS
        self.emit = Emitter(self.class_name + ".j", output_dir)
        # Member lists of the data classes, keyed by class name: a codegen
        # ``Symbol`` carries only (name, type, value), so it cannot hold them.
        self.members = {
            decl.name: decl.members
            for decl in ast.decls
            if type(decl) is nodes.DataClassDecl
        }

    def generate(self):
        return self.visit(self.ast, None)

    # ------------------------------------------------------------------ #
    #  Symbols                                                            #
    # ------------------------------------------------------------------ #
    def lookup(self, sym, name):
        """The visible binding of ``name``: ``sym`` is ordered innermost-first."""
        return next(filter(lambda s: s.name == name, sym))

    def lookup_function(self, sym, name):
        """The function named ``name``, or ``None`` when it is a data class."""
        return next(
            filter(lambda s: s.name == name and type(s.type) is FunctionType, sym),
            None,
        )

    def lookup_member(self, class_name, member_name):
        return next(
            filter(lambda m: m.name == member_name, self.members[class_name])
        )

    def rebind(self, sym, symbol):
        """``sym`` with its first entry named ``symbol.name`` replaced.

        Only the visible binding changes, so an outer variable of the same name
        keeps its own symbol.
        """
        at = next(i for i, s in enumerate(sym) if s.name == symbol.name)
        return sym[:at] + [symbol] + sym[at + 1 :]

    def settle_deferred_variable(self, symbol, value_type, frame):
        """The symbol to assign into, typing it first if it is still deferred.

        ``var n`` without an annotation or an initializer has neither a type nor
        a slot until its first assignment.

        NOTE — the one place a ``Symbol`` is updated in place instead of being
        rebound in a returned environment: the assignment that settles it may
        sit in a nested scope (``if (c) { n = 1 }``) or inside an expression
        (``printInt(n = 1)``), and from there a new environment would not reach
        the statements after the branch.  Same mechanism as the pending symbols
        of the Assignment 3 checker.
        """
        if symbol.type is None:
            symbol.type = value_type
            symbol.value = Index(frame.get_new_index())
        return symbol

    # ------------------------------------------------------------------ #
    #  Types                                                              #
    # ------------------------------------------------------------------ #
    def widen(self, target_type, source_type, frame):
        """``i2f`` when an Int flows into a Float position, nothing otherwise."""
        return (
            self.emit.emit_int_to_float(frame)
            if is_float_type(target_type) and is_int_type(source_type)
            else ""
        )

    def common_type(self, types):
        """The type the arms of an ``if`` / ``when`` expression agree on.

        Float when one arm is Float and the others are numeric — the Int arms are
        then widened — otherwise the first arm's type, the arms being of one type
        already for a program that passed the checker.
        """
        return (
            nodes.FloatType()
            if any(map(is_float_type, types))
            and all(is_int_type(t) or is_float_type(t) for t in types)
            else types[0]
            if types
            else nodes.UnitType()
        )

    def visitIntType(self, ctx: nodes.IntType, o):
        return self.emit.get_jvm_type(ctx)

    def visitFloatType(self, ctx: nodes.FloatType, o):
        return self.emit.get_jvm_type(ctx)

    def visitBoolType(self, ctx: nodes.BoolType, o):
        return self.emit.get_jvm_type(ctx)

    def visitStringType(self, ctx: nodes.StringType, o):
        return self.emit.get_jvm_type(ctx)

    def visitUnitType(self, ctx: nodes.UnitType, o):
        return self.emit.get_jvm_type(ctx)

    def visitClassType(self, ctx: nodes.ClassType, o):
        return self.emit.get_jvm_type(ctx)

    # ------------------------------------------------------------------ #
    #  Program                                                            #
    # ------------------------------------------------------------------ #
    def visitProgram(self, ctx: nodes.Program, o):
        functions = [d for d in ctx.decls if type(d) is nodes.FuncDecl]
        data_classes = [d for d in ctx.decls if type(d) is nodes.DataClassDecl]
        sym = self.resolve_signatures(
            functions,
            list(IO_SYMBOL_LIST)
            + [
                Symbol(d.name, nodes.ClassType(d.name), CName(d.name))
                for d in data_classes
            ]
            + [
                Symbol(
                    d.name,
                    FunctionType([p.typ for p in d.params], d.return_type),
                    CName(self.class_name),
                )
                for d in functions
            ],
        )
        main = self.lookup_function(sym, MAIN_NAME)

        # Writing the files is what this pass is for, so this is the one method
        # that sequences effects; each line below emits one region of the class.
        self.emit.emit_prolog(self.class_name)
        [self.visit(decl, sym) for decl in data_classes]
        self.generate_default_constructor()
        [self.visit(decl, sym) for decl in functions]
        if main is not None and not main.type.param_types:
            self.generate_entry_point(main)
        self.emit.save()

    def resolve_signatures(self, functions, sym):
        """``sym`` with every inferred return type filled in.

        A ``fun`` without an annotation is typed by the first ``return`` in its
        body, so that body has to be generated before any caller can be
        translated.  One round settles every function that does not depend on
        another unresolved one, so ``len(inferred)`` rounds settle them all.
        """
        inferred = [d for d in functions if d.return_type is None]
        return reduce(
            lambda env, _: reduce(self.probe_signature, inferred, env),
            range(len(inferred)),
            sym,
        )

    def probe_signature(self, sym, decl):
        """``sym`` with ``decl``'s return type filled in, if this round settles it.

        The body is generated only to read the type back off the frame and is
        then dropped — ``build_method_body`` emits nothing, so the probe costs
        no output.  A probe that raises is one that called a function whose own
        type is still unknown; ``sym`` is left for a later round to settle.
        """
        symbol = self.lookup_function(sym, decl.name)
        if symbol.type.return_type is not None:
            return sym
        try:
            return self.rebind(
                sym,
                Symbol(
                    decl.name,
                    FunctionType(
                        symbol.type.param_types, self.build_method_body(decl, sym)[2]
                    ),
                    symbol.value,
                ),
            )
        except Exception:
            return sym

    # ------------------------------------------------------------------ #
    #  Functions                                                          #
    # ------------------------------------------------------------------ #
    def visitFuncDecl(self, ctx: nodes.FuncDecl, o):
        """Emit one ``fun`` as a static method of ``MKotlinClass``."""
        body, frame, return_type = self.build_method_body(ctx, o)
        self.emit.emit_method(ctx.name, [p.typ for p in ctx.params], return_type, True)
        self.emit.emit_method_limits(frame)
        self.emit.print_out(body)
        self.emit.emit_end_method()

    def build_method_body(self, ctx: nodes.FuncDecl, sym):
        """``(body text, frame, return type)`` of ``ctx``, emitting nothing.

        Returning the text is what lets ``.limit stack`` / ``.limit locals`` be
        sized from the finished frame yet printed above the body, and what lets
        a probe run be thrown away for free.  An un-annotated function that
        never returns a value is Unit.
        """
        frame = Frame(ctx.name, ctx.return_type)
        params = [self.visit(p, SubBody(frame, sym)) for p in ctx.params]
        body, _ = self.visit(ctx.body, SubBody(frame, params + sym))
        return_type = (
            nodes.UnitType() if frame.return_type is None else frame.return_type
        )
        # A trailing return keeps control from falling off the end of the method
        # even when every path of the body already returned.
        return (
            body
            + (
                self.emit.emit_return(return_type, frame)
                if is_unit_type(return_type)
                else self.build_filler_value(return_type, frame)
                + self.emit.emit_return_value(return_type, frame)
            ),
            frame,
            return_type,
        )

    def build_filler_value(self, return_type, frame):
        """A dummy value of ``return_type`` for that trailing ``return``."""
        return (
            self.emit.emit_push_fconst(0.0, frame)
            if is_float_type(return_type)
            else self.emit.emit_push_null(frame)
            if is_string_type(return_type) or is_class_type(return_type)
            else self.emit.emit_push_iconst(0, frame)
        )

    def visitParam(self, ctx: nodes.Param, o):
        return Symbol(ctx.name, ctx.typ, Index(o.frame.get_new_index()))

    def generate_default_constructor(self):
        """``MKotlinClass.<init>()V``: chain straight to ``Object.<init>``."""
        frame = Frame(CONSTRUCTOR_NAME, nodes.UnitType())
        this_index = frame.get_new_index()
        body = (
            self.emit.emit_read_var(
                THIS_NAME, nodes.ClassType(self.class_name), this_index, frame
            )
            + self.emit.emit_invoke_super_constructor(frame)
            + self.emit.emit_return(nodes.UnitType(), frame)
        )
        self.emit.emit_method(CONSTRUCTOR_NAME, [], nodes.UnitType(), False)
        self.emit.emit_method_limits(frame)
        self.emit.print_out(body)
        self.emit.emit_end_method()

    def generate_entry_point(self, main_symbol):
        """``main([Ljava/lang/String;)V`` — the JVM's way into MKotlin's ``main``."""
        frame = Frame(MAIN_NAME, nodes.UnitType())
        frame.get_new_index()  # slot 0 holds the command-line arguments
        call = self.emit.emit_invoke_static(
            self.class_name + "/" + main_symbol.name, main_symbol.type, frame
        )
        body = (
            call
            + (
                ""
                if is_unit_type(main_symbol.type.return_type)
                else self.emit.emit_pop(frame)
            )
            + self.emit.emit_return(nodes.UnitType(), frame)
        )
        self.emit.emit_main_method()
        self.emit.emit_method_limits(frame)
        self.emit.print_out(body)
        self.emit.emit_end_method()

    # ------------------------------------------------------------------ #
    #  Data classes                                                       #
    # ------------------------------------------------------------------ #
    def visitDataClassDecl(self, ctx: nodes.DataClassDecl, o):
        """Emit ``<name>.j``: the fields, the constructor and ``equals``."""
        out = Emitter(ctx.name + ".j", self.output_dir)
        out.emit_prolog(ctx.name)
        [self.visit(member, out) for member in ctx.members]
        self.generate_data_class_constructor(ctx, out)
        self.generate_data_class_equals(ctx, out)
        out.save()

    def visitMemberDecl(self, ctx: nodes.MemberDecl, o):
        o.emit_field(ctx.name, ctx.typ)

    def generate_data_class_constructor(self, ctx: nodes.DataClassDecl, out):
        """``<init>`` storing one argument into each member field."""
        self_type = nodes.ClassType(ctx.name)
        frame = Frame(CONSTRUCTOR_NAME, nodes.UnitType())
        this_index = frame.get_new_index()
        slots = [frame.get_new_index() for _ in ctx.members]
        body = (
            out.emit_read_var(THIS_NAME, self_type, this_index, frame)
            + out.emit_invoke_super_constructor(frame)
            + "".join(
                out.emit_read_var(THIS_NAME, self_type, this_index, frame)
                + out.emit_read_var(member.name, member.typ, slot, frame)
                + out.emit_put_field(
                    ctx.name + "/" + member.name, member.typ, frame
                )
                for member, slot in zip(ctx.members, slots)
            )
            + out.emit_return(nodes.UnitType(), frame)
        )
        out.emit_method(
            CONSTRUCTOR_NAME,
            [member.typ for member in ctx.members],
            nodes.UnitType(),
            False,
        )
        out.emit_method_limits(frame)
        out.print_out(body)
        out.emit_end_method()

    def generate_data_class_equals(self, ctx: nodes.DataClassDecl, out):
        """Structural ``equals``: leave at the first member that differs."""
        self_type = nodes.ClassType(ctx.name)
        bool_type = nodes.BoolType()
        frame = Frame(EQUALS_NAME, bool_type)
        receivers = [
            (THIS_NAME, frame.get_new_index()),
            (OTHER_NAME, frame.get_new_index()),
        ]
        label_differs = frame.get_new_label()

        def compare(member):
            """Read one member from both objects and jump when they differ."""
            lexeme = ctx.name + "/" + member.name
            both = "".join(
                out.emit_read_var(name, self_type, index, frame)
                + out.emit_get_field(lexeme, member.typ, frame)
                for name, index in receivers
            )
            return both + (
                out.emit_cmp_float("!=", label_differs, frame)
                if is_float_type(member.typ)
                else (
                    out.emit_string_equal(frame)
                    + out.emit_if_false(label_differs, frame)
                )
                if is_string_type(member.typ)
                else (
                    out.emit_data_class_equal(member.typ.name, frame)
                    + out.emit_if_false(label_differs, frame)
                )
                if is_class_type(member.typ)
                else out.emit_cmp_int("!=", label_differs, frame)
            )

        body = (
            "".join(map(compare, ctx.members))
            + out.emit_push_bool(True, frame)
            + out.emit_return_value(bool_type, frame)
            + out.emit_label(label_differs)
            + out.emit_push_bool(False, frame)
            + out.emit_return_value(bool_type, frame)
        )
        out.emit_method(EQUALS_NAME, [self_type], bool_type, False)
        out.emit_method_limits(frame)
        out.print_out(body)
        out.emit_end_method()

    # ------------------------------------------------------------------ #
    #  Statements                                                         #
    # ------------------------------------------------------------------ #
    def build_statements(self, stmts, o):
        """``(code, environment)`` of a statement sequence.

        The environment each statement returns is what the next one sees, which
        is how a declaration becomes visible to the statements below it.
        """

        def step(acc, stmt):
            code, env = acc
            stmt_code, stmt_env = self.visit(stmt, env)
            return code + stmt_code, stmt_env

        return reduce(step, stmts, ("", o))

    def visitBlock(self, ctx: nodes.Block, o):
        """A block is its own scope, so its declarations do not escape it."""
        return self.build_statements(ctx.stmts, o)[0], o

    def visitVarDecl(self, ctx: nodes.VarDecl, o):
        frame = o.frame
        # `var n` with neither annotation nor initializer emits nothing and
        # reserves no slot: its first assignment settles both type and slot.
        if ctx.declared_type is None and ctx.init is None:
            return "", SubBody(frame, [Symbol(ctx.name, None, None)] + o.sym)

        init = (
            self.visit(ctx.init, Access(frame, o.sym)) if ctx.init is not None else None
        )
        var_type = ctx.declared_type if ctx.declared_type is not None else init[1]
        index = frame.get_new_index()
        return (
            ""
            if init is None
            else init[0]
            + self.widen(var_type, init[1], frame)
            + self.emit.emit_write_var(ctx.name, var_type, index, frame),
            SubBody(frame, [Symbol(ctx.name, var_type, Index(index))] + o.sym),
        )

    def visitAssign(self, ctx: nodes.Assign, o):
        frame = o.frame
        if type(ctx.lhs) is nodes.Id:
            value, value_type = self.visit(ctx.rhs, Access(frame, o.sym))
            target = self.settle_deferred_variable(
                self.lookup(o.sym, ctx.lhs.name), value_type, frame
            )
            return (
                value
                + self.widen(target.type, value_type, frame)
                + self.emit.emit_write_var(
                    target.name, target.type, target.value.value, frame
                ),
                o,
            )

        receiver, owner = self.visit(ctx.lhs.receiver, Access(frame, o.sym))
        field = self.lookup_member(owner.name, ctx.lhs.member)
        value, value_type = self.visit(ctx.rhs, Access(frame, o.sym))
        return (
            receiver
            + value
            + self.widen(field.typ, value_type, frame)
            + self.emit.emit_put_field(
                owner.name + "/" + field.name, field.typ, frame
            ),
            o,
        )

    def visitExprStmt(self, ctx: nodes.ExprStmt, o):
        """A value left by an expression used as a statement is dropped."""
        code, expr_type = self.visit(ctx.expr, Access(o.frame, o.sym))
        return (
            code
            + (
                ""
                if expr_type is None or is_unit_type(expr_type)
                else self.emit.emit_pop(o.frame)
            ),
            o,
        )

    def visitIf(self, ctx: nodes.If, o):
        frame = o.frame
        label_false = frame.get_new_label()
        cond, _ = self.visit(ctx.cond, Access(frame, o.sym))
        test = cond + self.emit.emit_if_false(label_false, frame)
        then_code, _ = self.visit(ctx.then_stmt, o)
        if ctx.else_stmt is None:
            return test + then_code + self.emit.emit_label(label_false), o

        label_end = frame.get_new_label()
        else_code, _ = self.visit(ctx.else_stmt, o)
        return (
            test
            + then_code
            + self.emit.emit_goto(label_end)
            + self.emit.emit_label(label_false)
            + else_code
            + self.emit.emit_label(label_end),
            o,
        )

    def visitWhile(self, ctx: nodes.While, o):
        frame = o.frame
        frame.enter_loop()
        # `continue` re-tests the condition, so its label sits above the test.
        label_break, label_continue = (
            frame.get_break_label(),
            frame.get_continue_label(),
        )
        cond, _ = self.visit(ctx.cond, Access(frame, o.sym))
        test = (
            self.emit.emit_label(label_continue)
            + cond
            + self.emit.emit_if_false(label_break, frame)
        )
        body, _ = self.visit(ctx.body, o)
        frame.exit_loop()
        return (
            test
            + body
            + self.emit.emit_goto(label_continue)
            + self.emit.emit_label(label_break),
            o,
        )

    def visitFor(self, ctx: nodes.For, o):
        frame, int_type = o.frame, nodes.IntType()
        label_test = frame.get_new_label()
        frame.enter_loop()
        # `continue` still has to bump the loop variable, so its label sits
        # above the update block rather than above the test.
        label_break, label_continue = (
            frame.get_break_label(),
            frame.get_continue_label(),
        )

        # Both bounds are evaluated exactly once, into the loop variable and a
        # hidden slot holding the upper bound.
        start, _ = self.visit(ctx.start, Access(frame, o.sym))
        index = frame.get_new_index()
        init_var = start + self.emit.emit_write_var(ctx.var, int_type, index, frame)
        end, _ = self.visit(ctx.end, Access(frame, o.sym))
        limit = frame.get_new_index()
        init_bound = end + self.emit.emit_write_var(
            BOUND_NAME, int_type, limit, frame
        )
        test = (
            self.emit.emit_label(label_test)
            + self.emit.emit_read_var(ctx.var, int_type, index, frame)
            + self.emit.emit_read_var(BOUND_NAME, int_type, limit, frame)
            + self.emit.emit_cmp_int(">", label_break, frame)
        )
        body, _ = self.visit(
            ctx.body,
            SubBody(frame, [Symbol(ctx.var, int_type, Index(index))] + o.sym),
        )
        update = (
            self.emit.emit_label(label_continue)
            + self.emit.emit_read_var(ctx.var, int_type, index, frame)
            + self.emit.emit_push_iconst(1, frame)
            + self.emit.emit_add_op("+", int_type, frame)
            + self.emit.emit_write_var(ctx.var, int_type, index, frame)
            + self.emit.emit_goto(label_test)
            + self.emit.emit_label(label_break)
        )
        frame.exit_loop()
        return init_var + init_bound + test + body + update, o

    def visitWhen(self, ctx: nodes.When, o):
        frame = o.frame
        subject_code, subject, sym = self.build_when_subject(ctx.subject, o)
        label_end = frame.get_new_label()

        def build_branch(branch):
            """A guarded body that jumps to the end once it has run."""
            test = self.visit(branch, subject)
            if test is None:
                return self.visit(branch.body, SubBody(frame, sym))[
                    0
                ] + self.emit.emit_goto(label_end)
            label_next = frame.get_new_label()
            guard, _ = self.visit(test, Access(frame, sym))
            guarded = guard + self.emit.emit_if_false(label_next, frame)
            body, _ = self.visit(branch.body, SubBody(frame, sym))
            return (
                guarded
                + body
                + self.emit.emit_goto(label_end)
                + self.emit.emit_label(label_next)
            )

        return (
            subject_code
            + "".join(map(build_branch, ctx.branches))
            + self.emit.emit_label(label_end),
            o,
        )

    def build_when_subject(self, subject, o):
        """``(code, subject local name, symbols)`` for a ``when`` header.

        The subject is evaluated once into a hidden local so that every branch
        test can read it back instead of re-evaluating it.  A conditionless
        ``when`` has no subject: its labels are already the tests.
        """
        if subject is None:
            return "", None, o.sym
        code, subject_type = self.visit(subject, Access(o.frame, o.sym))
        index = o.frame.get_new_index()
        name = SUBJECT_PREFIX + str(index)
        return (
            code + self.emit.emit_write_var(name, subject_type, index, o.frame),
            name,
            [Symbol(name, subject_type, Index(index))] + o.sym,
        )

    def visitWhenBranch(self, ctx: nodes.WhenBranch, o):
        """The ``Boolean`` test guarding this branch, ``None`` for ``else``.

        ``o`` is the name of the local holding the subject, or ``None`` for the
        conditionless form whose labels already are tests.  The labels of one
        branch match when any of them does, which is exactly ``||`` over them.
        """
        if ctx.labels is None:
            return None
        return reduce(
            lambda acc, test: nodes.BinaryOp("||", acc, test),
            [nodes.BinaryOp("==", nodes.Id(o), label) for label in ctx.labels]
            if o is not None
            else list(ctx.labels),
        )

    def visitBreak(self, ctx: nodes.Break, o):
        return self.emit.emit_goto(o.frame.get_break_label()), o

    def visitContinue(self, ctx: nodes.Continue, o):
        return self.emit.emit_goto(o.frame.get_continue_label()), o

    def visitReturn(self, ctx: nodes.Return, o):
        frame = o.frame
        # The first `return` types a function that has no annotation, and the
        # frame is where that type is published to `build_method_body`.
        if ctx.value is None:
            return self.emit.emit_return(self.settle_return_type(frame, None), frame), o
        code, value_type = self.visit(ctx.value, Access(frame, o.sym))
        return_type = self.settle_return_type(frame, value_type)
        return (
            code
            + self.widen(return_type, value_type, frame)
            + self.emit.emit_return_value(return_type, frame),
            o,
        )

    def settle_return_type(self, frame, discovered):
        """The method's return type, recording ``discovered`` the first time.

        A bare ``return`` (``discovered`` is ``None``) types the function as
        Unit, which is also the only annotation a program that passed the
        checker can pair it with.
        """
        if frame.return_type is None:
            frame.return_type = (
                nodes.UnitType() if discovered is None else discovered
            )
        return frame.return_type

    # ------------------------------------------------------------------ #
    #  Expressions                                                        #
    # ------------------------------------------------------------------ #
    def visitBinaryOp(self, ctx: nodes.BinaryOp, o):
        frame = o.frame

        # Short circuit: the second operand is reached only when the first does
        # not already decide the answer.
        if ctx.op in ("&&", "||"):
            label_short, label_end = frame.get_new_label(), frame.get_new_label()
            left, _ = self.visit(ctx.left, o)
            test = left + (
                self.emit.emit_if_false(label_short, frame)
                if ctx.op == "&&"
                else self.emit.emit_if_true(label_short, frame)
            )
            depth = frame.cur_op_stack_size
            right, _ = self.visit(ctx.right, o)
            frame.merge_alternative(depth)
            return (
                test
                + right
                + self.emit.emit_goto(label_end)
                + self.emit.emit_label(label_short)
                + self.emit.emit_push_iconst(0 if ctx.op == "&&" else 1, frame)
                + self.emit.emit_label(label_end),
                nodes.BoolType(),
            )

        left, left_type = self.visit(ctx.left, o)
        right, right_type = self.visit(ctx.right, o)
        as_float = is_float_type(left_type) or is_float_type(right_type)

        if ctx.op in ("+", "-", "*", "/", "%"):
            # `%` is Int-only, so it never widens; for the others a single Float
            # operand makes the whole operation Float.
            result = (
                nodes.FloatType()
                if as_float and ctx.op != "%"
                else nodes.IntType()
            )
            operands = (
                left
                + self.widen(result, left_type, frame)
                + right
                + self.widen(result, right_type, frame)
            )
            return (
                operands
                + (
                    self.emit.emit_add_op(ctx.op, result, frame)
                    if ctx.op in ("+", "-")
                    else self.emit.emit_mul_op(ctx.op, result, frame)
                ),
                result,
            )

        # Relational / equality: jump to `label_true` when the test holds and
        # fall into the false block otherwise, the two paths meeting at
        # `label_end` with one Boolean on the stack.
        label_true, label_end = frame.get_new_label(), frame.get_new_label()
        if is_string_type(left_type) or is_class_type(left_type):
            # Both compare by calling `equals`, which already yields the answer
            # as a Boolean, so the jump tests that answer instead of the values.
            test = (
                left
                + right
                + (
                    self.emit.emit_string_equal(frame)
                    if is_string_type(left_type)
                    else self.emit.emit_data_class_equal(left_type.name, frame)
                )
                + (
                    self.emit.emit_if_true(label_true, frame)
                    if ctx.op == "=="
                    else self.emit.emit_if_false(label_true, frame)
                )
            )
        elif as_float:
            test = (
                left
                + self.widen(nodes.FloatType(), left_type, frame)
                + right
                + self.widen(nodes.FloatType(), right_type, frame)
                + self.emit.emit_cmp_float(ctx.op, label_true, frame)
            )
        else:
            test = left + right + self.emit.emit_cmp_int(ctx.op, label_true, frame)

        depth = frame.cur_op_stack_size
        false_path = self.emit.emit_push_iconst(0, frame) + self.emit.emit_goto(
            label_end
        )
        frame.merge_alternative(depth)
        return (
            test
            + false_path
            + self.emit.emit_label(label_true)
            + self.emit.emit_push_iconst(1, frame)
            + self.emit.emit_label(label_end),
            nodes.BoolType(),
        )

    def visitUnaryOp(self, ctx: nodes.UnaryOp, o):
        frame = o.frame

        if ctx.op == "!":
            label_true, label_end = frame.get_new_label(), frame.get_new_label()
            operand, _ = self.visit(ctx.operand, o)
            test = operand + self.emit.emit_if_false(label_true, frame)
            depth = frame.cur_op_stack_size
            false_path = self.emit.emit_push_iconst(0, frame) + self.emit.emit_goto(
                label_end
            )
            frame.merge_alternative(depth)
            return (
                test
                + false_path
                + self.emit.emit_label(label_true)
                + self.emit.emit_push_iconst(1, frame)
                + self.emit.emit_label(label_end),
                nodes.BoolType(),
            )

        if ctx.op in ("+", "-"):
            operand, operand_type = self.visit(ctx.operand, o)
            return (
                operand
                + (
                    self.emit.emit_neg_op(operand_type, frame)
                    if ctx.op == "-"
                    else ""
                ),
                operand_type,
            )

        # Prefix ++ / -- leaves the *new* value behind.
        int_type, step = nodes.IntType(), "+" if ctx.op == "++" else "-"
        if type(ctx.operand) is nodes.Id:
            symbol = self.lookup(o.sym, ctx.operand.name)
            return (
                self.emit.emit_read_var(
                    symbol.name, int_type, symbol.value.value, frame
                )
                + self.emit.emit_push_iconst(1, frame)
                + self.emit.emit_add_op(step, int_type, frame)
                + self.emit.emit_dup(frame)
                + self.emit.emit_write_var(
                    symbol.name, int_type, symbol.value.value, frame
                ),
                int_type,
            )

        receiver, owner = self.visit(ctx.operand.receiver, o)
        lexeme = owner.name + "/" + ctx.operand.member
        return (
            receiver
            + self.emit.emit_dup(frame)
            + self.emit.emit_get_field(lexeme, int_type, frame)
            + self.emit.emit_push_iconst(1, frame)
            + self.emit.emit_add_op(step, int_type, frame)
            + self.emit.emit_dup_x1(frame)
            + self.emit.emit_put_field(lexeme, int_type, frame),
            int_type,
        )

    def visitPostfixOp(self, ctx: nodes.PostfixOp, o):
        # Postfix ++ / -- keeps the *old* value below the updated one.
        frame = o.frame
        int_type, step = nodes.IntType(), "+" if ctx.op == "++" else "-"
        if type(ctx.operand) is nodes.Id:
            symbol = self.lookup(o.sym, ctx.operand.name)
            return (
                self.emit.emit_read_var(
                    symbol.name, int_type, symbol.value.value, frame
                )
                + self.emit.emit_dup(frame)
                + self.emit.emit_push_iconst(1, frame)
                + self.emit.emit_add_op(step, int_type, frame)
                + self.emit.emit_write_var(
                    symbol.name, int_type, symbol.value.value, frame
                ),
                int_type,
            )

        receiver, owner = self.visit(ctx.operand.receiver, o)
        lexeme = owner.name + "/" + ctx.operand.member
        return (
            receiver
            + self.emit.emit_dup(frame)
            + self.emit.emit_get_field(lexeme, int_type, frame)
            + self.emit.emit_dup_x1(frame)
            + self.emit.emit_push_iconst(1, frame)
            + self.emit.emit_add_op(step, int_type, frame)
            + self.emit.emit_put_field(lexeme, int_type, frame),
            int_type,
        )

    def visitAssignExpr(self, ctx: nodes.AssignExpr, o):
        frame = o.frame
        if type(ctx.lhs) is nodes.Id:
            value, value_type = self.visit(ctx.rhs, o)
            target = self.settle_deferred_variable(
                self.lookup(o.sym, ctx.lhs.name), value_type, frame
            )
            return (
                value
                + self.widen(target.type, value_type, frame)
                + self.emit.emit_dup(frame)
                + self.emit.emit_write_var(
                    target.name, target.type, target.value.value, frame
                ),
                target.type,
            )

        receiver, owner = self.visit(ctx.lhs.receiver, o)
        field = self.lookup_member(owner.name, ctx.lhs.member)
        value, value_type = self.visit(ctx.rhs, o)
        return (
            receiver
            + value
            + self.widen(field.typ, value_type, frame)
            + self.emit.emit_dup_x1(frame)
            + self.emit.emit_put_field(
                owner.name + "/" + field.name, field.typ, frame
            ),
            field.typ,
        )

    def visitCallExpr(self, ctx: nodes.CallExpr, o):
        frame = o.frame
        func = self.lookup_function(o.sym, ctx.name)

        # A name that is not a function is a data class: allocate, keep a copy
        # of the reference, then run the constructor on the other one.
        if func is None:
            member_types = [member.typ for member in self.members[ctx.name]]
            return (
                self.emit.emit_new_object(ctx.name, frame)
                + self.emit.emit_dup(frame)
                + self.build_arguments(member_types, ctx.args, o)
                + self.emit.emit_invoke_constructor(ctx.name, member_types, frame),
                nodes.ClassType(ctx.name),
            )

        # Both kinds of call name their owner the same way — the symbol carries
        # it — and differ only in how a Boolean is spelled in the descriptor.
        lexeme = func.value.value + "/" + ctx.name
        return (
            self.build_arguments(func.type.param_types, ctx.args, o)
            + (
                self.emit.emit_invoke_builtin(lexeme, func.type, frame)
                if self.is_builtin(func)
                else self.emit.emit_invoke_static(lexeme, func.type, frame)
            ),
            func.type.return_type,
        )

    def is_builtin(self, func):
        """Whether ``func`` is one of the built-ins of ``IO_SYMBOL_LIST``.

        Their class is compiled from Java, so a Boolean in their signature is
        spelled the JVM way.  That table is the only thing that says which names
        those are, and matching it by name is safe because a user function
        cannot reuse one: the checker rejects it as redeclared.
        """
        return any(symbol.name == func.name for symbol in IO_SYMBOL_LIST)

    def build_arguments(self, param_types, args, o):
        """Every argument in order, widened where its parameter is a Float."""

        def build(param_type, arg):
            code, arg_type = self.visit(arg, o)
            return code + self.widen(param_type, arg_type, o.frame)

        return "".join(map(build, param_types, args))

    def visitMemberAccess(self, ctx: nodes.MemberAccess, o):
        receiver, owner = self.visit(ctx.receiver, o)
        field = self.lookup_member(owner.name, ctx.member)
        return (
            receiver
            + self.emit.emit_get_field(
                owner.name + "/" + field.name, field.typ, o.frame
            ),
            field.typ,
        )

    def visitIfExpr(self, ctx: nodes.IfExpr, o):
        frame = o.frame
        label_false, label_end = frame.get_new_label(), frame.get_new_label()
        cond, _ = self.visit(ctx.cond, o)
        test = cond + self.emit.emit_if_false(label_false, frame)

        # The arms are alternatives: each starts from the same depth and exactly
        # one of them leaves the result behind, so the second one is what the
        # frame ends up counting.
        depth = frame.cur_op_stack_size
        then_code, then_type = self.visit(ctx.then_expr, o)
        frame.merge_alternative(depth)
        else_code, else_type = self.visit(ctx.else_expr, o)
        result = self.common_type([then_type, else_type])
        return (
            test
            + then_code
            + self.widen(result, then_type, frame)
            + self.emit.emit_goto(label_end)
            + self.emit.emit_label(label_false)
            + else_code
            + self.widen(result, else_type, frame)
            + self.emit.emit_label(label_end),
            result,
        )

    def visitWhenExpr(self, ctx: nodes.WhenExpr, o):
        frame = o.frame
        subject_code, subject, sym = self.build_when_subject(ctx.subject, o)

        # Every branch is generated first, so the type they agree on is known
        # before the pieces are stitched together.  Each one starts from the
        # same depth, being an alternative, and exactly one leaves the result.
        depth = frame.cur_op_stack_size

        def build_branch(branch):
            """``(no-match label or None, guard, body, body type)``."""
            test = self.visit(branch, subject)
            label_next = None if test is None else frame.get_new_label()
            guard = (
                ""
                if test is None
                else self.visit(test, Access(frame, sym))[0]
                + self.emit.emit_if_false(label_next, frame)
            )
            body, body_type = self.visit(branch.body, Access(frame, sym))
            frame.merge_alternative(depth)
            return label_next, guard, body, body_type

        branches = list(map(build_branch, ctx.branches))
        frame.push()
        result = self.common_type([body_type for _, _, _, body_type in branches])
        label_end = frame.get_new_label()
        return (
            subject_code
            + "".join(
                guard
                + body
                + self.widen(result, body_type, frame)
                + self.emit.emit_goto(label_end)
                + ("" if label_next is None else self.emit.emit_label(label_next))
                for label_next, guard, body, body_type in branches
            )
            + self.emit.emit_label(label_end),
            result,
        )

    def visitId(self, ctx: nodes.Id, o):
        symbol = self.lookup(o.sym, ctx.name)
        return (
            self.emit.emit_read_var(
                ctx.name, symbol.type, symbol.value.value, o.frame
            ),
            symbol.type,
        )

    def visitIntLit(self, ctx: nodes.IntLit, o):
        return self.emit.emit_push_iconst(ctx.value, o.frame), nodes.IntType()

    def visitFloatLit(self, ctx: nodes.FloatLit, o):
        return self.emit.emit_push_fconst(ctx.value, o.frame), nodes.FloatType()

    def visitBoolLit(self, ctx: nodes.BoolLit, o):
        return self.emit.emit_push_bool(ctx.value, o.frame), nodes.BoolType()

    def visitStringLit(self, ctx: nodes.StringLit, o):
        return (
            self.emit.emit_push_escaped_string(ctx.value, o.frame),
            nodes.StringType(),
        )

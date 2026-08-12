"""Static semantic checker for MKotlin — Assignment 3.

Implement the ``StaticChecker`` class so that, given the AST produced by
Assignment 2, it either returns normally (the program is well-formed) or raises
exactly one of the exceptions defined in ``static_error.py`` for the first
violation it finds, in deterministic traversal order.

See ``mkotlin-semantic_constraints_and_errors.md`` for the full set of rules.

This file is a skeleton: every visit method currently raises
``NotImplementedError``.  Replace the bodies with your implementation.
"""

from functools import reduce
from src.utils import nodes
from src.utils.visitor import BaseVisitor
from src.semantics.static_error import (
    Function, Parameter, Variable, Constant, Class, Member,
    Redeclared, UndeclaredIdentifier, UndeclaredFunction, UndeclaredClass,
    TypeCannotBeInferred, TypeMismatchInStatement, TypeMismatchInExpression,
    MustInLoop,
)


# --------------------------------------------------------------------------- #
#  Built-in function signatures (predeclared in global scope)                 #
#  name -> (param_types, return_type)                                         #
# --------------------------------------------------------------------------- #
BUILTIN_FUNCS = {
    "readInt":     ([], nodes.IntType()),
    "readFloat":   ([], nodes.FloatType()),
    "readBool":    ([], nodes.BoolType()),
    "readString":  ([], nodes.StringType()),
    "printInt":    ([nodes.IntType()], nodes.UnitType()),
    "printFloat":  ([nodes.FloatType()], nodes.UnitType()),
    "printBool":   ([nodes.BoolType()], nodes.UnitType()),
    "printString": ([nodes.StringType()], nodes.UnitType()),
}

# Tám lớp lỗi tĩnh; gom lại để lượt duyệt thăm dò chỉ nuốt lỗi ngữ nghĩa,
# không nuốt luôn lỗi lập trình của chính checker.
STATIC_ERRORS = (
    Redeclared, UndeclaredIdentifier, UndeclaredFunction, UndeclaredClass,
    TypeCannotBeInferred, TypeMismatchInStatement, TypeMismatchInExpression,
    MustInLoop,
)

class Symbol:
    def __init__(self, name, typ, is_mutable=False, in_loop=False, members=None):
        self.name = name
        self.typ = typ
        self.is_mutable = is_mutable
        self.in_loop = in_loop
        self.members = members

class StaticChecker(BaseVisitor):
    def __init__(self, ast):
        self.ast = ast

    def check(self):
        """Run the checker.  Returns normally if the program is valid,
        otherwise raises a ``StaticError`` subclass."""
        return self.visit(self.ast, None)

    def _lookup(self, o, name):
        return next(filter(lambda s: s.name == name, [s for sc in o for s in sc]), False)

    # ----------------------------------------------------------------- #
    #  TODO: implement the visitor methods below.                       #
    #  The inherited BaseVisitor methods raise NotImplementedError, so  #
    #  the checker is non-functional until you fill these in.           #
    # ----------------------------------------------------------------- #
    # Program & declarations
    
    def visitProgram(self, ctx: nodes.Program, o):
        built_ins = [Symbol(name, (param_typ, ret_typ)) for name, (param_typ, ret_typ) in BUILTIN_FUNCS.items()]
        return reduce(lambda acc, decl: self.visit(decl, acc), ctx.decls, [built_ins])

    def visitDataClassDecl(self, ctx: nodes.DataClassDecl, o): 
        if ctx.name in [item.name for item in o[0]]:
            raise Redeclared(Class(), ctx.name)
        member_scope = [[]] + o
        member_env = reduce(lambda acc, member: self.visit(member, acc), ctx.members, member_scope)
        member_list = [(m.name, m.typ) for m in member_env[0]]
        return [o[0] + [Symbol(ctx.name, nodes.ClassType(ctx.name), members = member_list)]] + o[1:]

    def visitMemberDecl(self, ctx: nodes.MemberDecl, o): 
        if ctx.name in [item.name for item in o[0]]:
            raise Redeclared(Member(), ctx.name)
        
        elif ctx.typ == nodes.UnitType():
            raise TypeMismatchInStatement(ctx)
        
        elif isinstance(ctx.typ, nodes.ClassType):
            if not any(sym.name == ctx.typ.name and isinstance(sym.typ, nodes.ClassType) for sym in o[-1]):
                raise UndeclaredClass(ctx.typ.name)

        elif not isinstance(ctx.typ, (nodes.IntType, nodes.FloatType, nodes.BoolType, nodes.StringType)):
            raise TypeMismatchInStatement(ctx)

        return [o[0] + [Symbol(ctx.name, ctx.typ)]] + o[1:]    
        
    def visitFuncDecl(self, ctx: nodes.FuncDecl, o):
        if ctx.name in [item.name for item in o[0]]:
            raise Redeclared(Function(), ctx.name)

        if isinstance(ctx.return_type, nodes.ClassType):
            if not any(sym.name == ctx.return_type.name and isinstance(sym.typ, nodes.ClassType) for sym in o[-1]):
                raise UndeclaredClass(ctx.return_type.name)

        param_types = [param.typ for param in ctx.params]

        # soft=True: lượt thăm dò (nuốt lỗi) để suy kiểu trả về theo Rule 5.
        # soft=False: lượt thật, báo lỗi đúng thứ tự.
        # Frame (pending / bare / func) nằm trong env qua Symbol("$frame"), không gắn self.
        def run_with_pending(ret, soft):
            func = Symbol(ctx.name, (param_types, ret))
            ret_sym = Symbol("$return", ret)
            frame = {"func": func, "pending": [], "bare": []}
            env = [[ret_sym, Symbol("$frame", frame)], o[0] + [func]] + o[1:]
            env = reduce(lambda acc, param: self.visit(param, acc), ctx.params, env)

            def step(e, stmt):
                if soft and ret_sym.typ is not None and ret is None:
                    return e
                try:
                    return self.visit(stmt, e)
                except STATIC_ERRORS:
                    if soft:
                        return e
                    raise

            reduce(step, ctx.body.stmts, env)
            return func, ret_sym, frame["pending"], frame["bare"]

        assumed_ret_typ = ctx.return_type
        if assumed_ret_typ is None:
            _, ret_sym, _, _ = run_with_pending(None, soft=True)
            assumed_ret_typ = ret_sym.typ

        func, ret_sym, pending, bare_returns = run_with_pending(assumed_ret_typ, soft=False)

        unresolved = next((node for sym, node in pending if sym.typ is None), None)
        if unresolved is not None:
            raise TypeCannotBeInferred(unresolved)

        if ret_sym.typ is None:
            ret_sym.typ = nodes.UnitType()
        elif not isinstance(ret_sym.typ, nodes.UnitType) and bare_returns:
            raise TypeMismatchInStatement(bare_returns[0])

        func.typ = (param_types, ret_sym.typ)
        return [o[0] + [func]] + o[1:]
        
    def visitParam(self, ctx: nodes.Param, o):
        if ctx.name in [item.name for item in o[0]]:
            raise Redeclared(Parameter(), ctx.name)
        
        elif ctx.typ == nodes.UnitType():
            raise TypeMismatchInStatement(ctx)
        
        elif isinstance(ctx.typ, nodes.ClassType):
            if not any(sym.name == ctx.typ.name and isinstance(sym.typ, nodes.ClassType) for sym in o[-1]):
                raise UndeclaredClass(ctx.typ.name)
        
        elif not isinstance(ctx.typ, (nodes.IntType, nodes.FloatType, nodes.BoolType, nodes.StringType)):
            raise TypeMismatchInStatement(ctx)
        
        return [o[0] + [Symbol(ctx.name, ctx.typ)]] + o[1:]

    # Types
    def visitIntType(self, ctx: nodes.IntType, o):       
        return nodes.IntType() 

    def visitFloatType(self, ctx: nodes.FloatType, o):   
        return nodes.FloatType()

    def visitBoolType(self, ctx: nodes.BoolType, o):     
        return nodes.BoolType()

    def visitStringType(self, ctx: nodes.StringType, o): 
        return nodes.StringType()

    def visitUnitType(self, ctx: nodes.UnitType, o):     
        return nodes.UnitType()

    def visitClassType(self, ctx: nodes.ClassType, o):   
        return nodes.ClassType(ctx.name)

    # Statements
    def visitVarDecl(self, ctx: nodes.VarDecl, o):       
        if ctx.name in [item.name for item in o[0]]:
            raise Redeclared(Variable(), ctx.name)

        if ctx.mutable is False and ctx.init is None:
            raise TypeCannotBeInferred(ctx)
        
        if ctx.declared_type is not None:
            if isinstance(ctx.declared_type, nodes.UnitType):
                raise TypeMismatchInStatement(ctx)
            
            if isinstance(ctx.declared_type, nodes.ClassType):
                if not any(sym.name == ctx.declared_type.name and isinstance(sym.typ, nodes.ClassType) for sym in o[-1]):
                    raise UndeclaredClass(ctx.declared_type.name)

            if ctx.init is not None:
                init_typ = self.visit(ctx.init, o)

                # Annotation chỉ dùng để kiểm tra biểu thức khởi tạo; nó không phải
                # ngữ cảnh neo kiểu cho một `var` chưa xác định (Rule 2.2.1).
                if init_typ is None:
                    raise TypeCannotBeInferred(ctx.init)

                if not (init_typ == ctx.declared_type or (isinstance(init_typ, nodes.IntType) and isinstance(ctx.declared_type, nodes.FloatType))):
                    raise TypeMismatchInStatement(ctx)

            return [o[0] + [Symbol(ctx.name, ctx.declared_type, is_mutable = ctx.mutable)]] + o[1:]

        else:
            if ctx.init is not None:
                init_typ = self.visit(ctx.init, o)

                if init_typ is None:
                    # Initializer không phải ngữ cảnh suy kiểu cho giá trị bên trong.
                    raise TypeCannotBeInferred(ctx.init)

                if isinstance(init_typ, nodes.UnitType):
                    raise TypeMismatchInStatement(ctx)

                return [o[0] + [Symbol(ctx.name, init_typ, is_mutable = ctx.mutable)]] + o[1:]
            else:
                # Decided by first usage — ghi vào frame trong env, không dùng self._pending.
                sym = Symbol(ctx.name, None, is_mutable=ctx.mutable)
                frame_sym = self._lookup(o, "$frame")
                if frame_sym is not False:
                    frame = frame_sym.typ
                    frame["pending"] = frame["pending"] + [(sym, ctx)]
                return [o[0] + [sym]] + o[1:]

    def visitBlock(self, ctx: nodes.Block, o):           
        reduce(lambda acc, stmt: self.visit(stmt, acc), ctx.stmts, [[]] + o)
        return o

    def visitIf(self, ctx: nodes.If, o):                 
        cond_typ = self.visit(ctx.cond, o)

        if cond_typ is None:
            raise TypeCannotBeInferred(ctx.cond)

        if cond_typ != nodes.BoolType():
            raise TypeMismatchInStatement(ctx)

        # Each branch body gets its own nested scope (even if not a Block).
        self.visit(ctx.then_stmt, [[]] + o)

        if ctx.else_stmt is not None:
            self.visit(ctx.else_stmt, [[]] + o)

        return o

    def visitWhile(self, ctx: nodes.While, o):           
        cond_typ = self.visit(ctx.cond, o)

        if cond_typ is None:
            raise TypeCannotBeInferred(ctx.cond)

        if cond_typ != nodes.BoolType():
            raise TypeMismatchInStatement(ctx)

        # Đánh dấu $loop cho break/continue; scope thân lồng bên dưới (giống for).
        loop_env = [[Symbol("$loop", None, in_loop=True)]] + o
        self.visit(ctx.body, [[]] + loop_env)

        return o

    def visitFor(self, ctx: nodes.For, o):   
        start_type = self.visit(ctx.start, o)
        end_type = self.visit(ctx.end, o)

        # Biên của range không phải ngữ cảnh suy kiểu: báo lỗi ngay tại biên sai.
        if start_type is None:
            raise TypeCannotBeInferred(ctx.start)
        if end_type is None:
            raise TypeCannotBeInferred(ctx.end)

        if not isinstance(start_type, nodes.IntType) or not isinstance(end_type, nodes.IntType):
            raise TypeMismatchInStatement(ctx)
        
        loop_var_scope = [[Symbol(ctx.var, nodes.IntType(), is_mutable = False, in_loop = True)]] + o # scope của loop_var cùng tầng với header

        self.visit(ctx.body, [[]] + loop_var_scope) # lồng thêm scope ở dưới loop_var

        return o

    def visitWhen(self, ctx: nodes.When, o):   
        if ctx.subject is not None:
            subject_typ = self.visit(ctx.subject, o)

            if subject_typ is None:
                raise TypeCannotBeInferred(ctx.subject)
            
            if subject_typ not in [nodes.IntType(), nodes.FloatType(), nodes.BoolType(), nodes.StringType()]:
                raise TypeMismatchInStatement(ctx)

            context = (subject_typ, o)
        
        else:
            context = (None, o)

        else_count = reduce(lambda acc, branch: acc + (1 if branch.labels is None else 0), ctx.branches, 0)
        if else_count > 1:
            raise TypeMismatchInStatement(ctx)
        
        reduce(lambda acc, branch: self.visit(branch, acc), ctx.branches, context)

        return o

    def visitWhenBranch(self, ctx: nodes.WhenBranch, o): 
        subject_type, scope = o

        if ctx.labels is not None:
            def check_compatibility(label, subject_typ):
                label_typ = self.visit(label, scope)

                if label_typ is None:
                    raise TypeCannotBeInferred(label)

                if subject_typ is not None:
                    # Nhãn được widen Int/Float theo cả hai chiều.
                    numeric = (nodes.IntType(), nodes.FloatType())
                    is_compatible = label_typ == subject_typ or (
                        label_typ in numeric and subject_typ in numeric
                    )

                    if not is_compatible:
                        raise TypeMismatchInExpression(label)
                
                elif label_typ != nodes.BoolType():
                    raise TypeMismatchInExpression(label)

                return None
            
            reduce(lambda _, label: check_compatibility(label, subject_type), ctx.labels, None)

        self.visit(ctx.body, [[]] + scope)

        return o

    def visitBreak(self, ctx: nodes.Break, o):           
        if not any(sym.in_loop for scope in o for sym in scope):
            raise MustInLoop(ctx)
        
        return o

    def visitContinue(self, ctx: nodes.Continue, o): 
        if not any(sym.in_loop for scope in o for sym in scope):
            raise MustInLoop(ctx)
        
        return o
    
    def visitReturn(self, ctx: nodes.Return, o):
        ret_symbol = self._lookup(o, "$return")
        if ret_symbol is False:
            raise TypeCannotBeInferred(ctx)

        frame_sym = self._lookup(o, "$frame")
        frame = frame_sym.typ if frame_sym is not False else None

        # typ là Type | None
        expected = ret_symbol.typ

        if ctx.value is None:
            # expected is None: ghi vào frame["bare"], cuối FuncDecl mới đối chiếu.
            if expected is None:
                if frame is not None:
                    frame["bare"] = frame["bare"] + [ctx]
                return o
            if expected != nodes.UnitType():
                raise TypeMismatchInStatement(ctx)
            return o

        if isinstance(expected, nodes.UnitType):
            raise TypeMismatchInStatement(ctx)

        if expected is None:
            ret_typ = self.visit(ctx.value, o)
            if ret_typ is None:
                raise TypeCannotBeInferred(ctx)
            if isinstance(ret_typ, nodes.UnitType):
                raise TypeMismatchInStatement(ctx)
            ret_symbol.typ = ret_typ
            if frame is not None:
                frame["func"].typ = (frame["func"].typ[0], ret_typ)
            return o

        if isinstance(ctx.value, nodes.Id):
            val_sym = next(filter(lambda sym: sym.name == ctx.value.name, [sym for scope in o for sym in scope]), False)
            if val_sym is False or isinstance(val_sym.typ, tuple) or (isinstance(val_sym.typ, nodes.ClassType) and val_sym.members is not None):
                raise UndeclaredIdentifier(ctx.value.name)
            if val_sym.typ is None:
                val_sym.typ = expected
                return o
            ret_typ = val_sym.typ
        else:
            ret_typ = self.visit(ctx.value, o)
            if ret_typ is None:
                raise TypeCannotBeInferred(ctx)

        if not (expected == ret_typ or (expected == nodes.FloatType() and ret_typ == nodes.IntType())):
            raise TypeMismatchInStatement(ctx)

        return o
        
    def visitAssign(self, ctx: nodes.Assign, o):    
        def find_root(expr):
            return find_root(expr.receiver) if isinstance(expr, nodes.MemberAccess) else expr

        def root_is_mutable(expr):
            root = find_root(expr)
            if not isinstance(root, nodes.Id):
                return False
            sym = next(filter(lambda sym: sym.name == root.name, [sym for scope in o for sym in scope]), False)
            return sym is not False and sym.is_mutable

        if isinstance(ctx.lhs, nodes.Id):
            sym = next(filter(lambda sym: sym.name == ctx.lhs.name, [sym for scope in o for sym in scope]), False)
            if sym is False or isinstance(sym.typ, tuple) or (isinstance(sym.typ, nodes.ClassType) and sym.members is not None):
                raise UndeclaredIdentifier(ctx.lhs.name)

            lhs_typ, mutable = sym.typ, sym.is_mutable

        elif isinstance(ctx.lhs, nodes.MemberAccess):
            lhs_typ = self.visit(ctx.lhs, o)
            mutable = root_is_mutable(ctx.lhs)
            sym = None
        else:
            raise TypeMismatchInStatement(ctx)

        if not mutable:
            raise TypeMismatchInStatement(ctx)

        if lhs_typ is None:
            rhs_typ = self.visit(ctx.rhs, o)
            if rhs_typ is None:
                # The right-hand side must be checkable on its own.
                raise TypeCannotBeInferred(ctx.rhs)
            if sym is None:
                raise TypeCannotBeInferred(ctx)
            # Unit is not a valid variable type (same as var x = printInt(1)).
            if isinstance(rhs_typ, nodes.UnitType):
                raise TypeMismatchInStatement(ctx)
            sym.typ = rhs_typ
            return o

        if isinstance(ctx.rhs, nodes.Id):
            rhs_sym = next(filter(lambda sym: sym.name == ctx.rhs.name, [sym for scope in o for sym in scope]), False)
            if rhs_sym is False or isinstance(rhs_sym.typ, tuple) or (isinstance(rhs_sym.typ, nodes.ClassType) and rhs_sym.members is not None):
                raise UndeclaredIdentifier(ctx.rhs.name)
            if rhs_sym.typ is None:
                rhs_sym.typ = lhs_typ
                return o
            rhs_typ = rhs_sym.typ
        else:
            rhs_typ = self.visit(ctx.rhs, o)
            if rhs_typ is None:
                raise TypeCannotBeInferred(ctx)

        if not (lhs_typ == rhs_typ or (isinstance(lhs_typ, nodes.FloatType) and isinstance(rhs_typ, nodes.IntType))):
            raise TypeMismatchInStatement(ctx)
        
        return o

    def visitExprStmt(self, ctx: nodes.ExprStmt, o):
        self.visit(ctx.expr, o)
        return o

    # Expressions
    def visitBinaryOp(self, ctx: nodes.BinaryOp, o):     
        op = ctx.op

        def lookup_var(name):
            sym = next(filter(lambda s: s.name == name, [s for sc in o for s in sc]), False)
            if sym is False or isinstance(sym.typ, tuple) or (isinstance(sym.typ, nodes.ClassType) and sym.members is not None):
                return False
            return sym

        def maybe_anchor(side_expr, other_expr):
            if op in ["+", "-", "*", "/"] and isinstance(side_expr, nodes.Id) and isinstance(other_expr, nodes.IntLit):
                sym = lookup_var(side_expr.name)
                if sym is not False and sym.typ is None:
                    sym.typ = nodes.IntType()
            return None

        maybe_anchor(ctx.left, ctx.right)
        maybe_anchor(ctx.right, ctx.left)

        left = self.visit(ctx.left, o)
        right = self.visit(ctx.right, o)
        if left is None or right is None:
            raise TypeCannotBeInferred(ctx)

        if op == "..":
            raise TypeMismatchInExpression(ctx)

        if op in ["+", "-", "*", "/"]:
            if not isinstance(left, (nodes.IntType, nodes.FloatType)) or not isinstance(right, (nodes.IntType, nodes.FloatType)):
                raise TypeMismatchInExpression(ctx)
            if isinstance(left, nodes.IntType) and isinstance(right, nodes.IntType):
                return nodes.IntType()
            return nodes.FloatType()

        if op == "%":
            if not isinstance(left, nodes.IntType) or not isinstance(right, nodes.IntType):
                raise TypeMismatchInExpression(ctx)
            return nodes.IntType()

        if op in ["<", "<=", ">", ">="]:
            if not isinstance(left, (nodes.IntType, nodes.FloatType)) or not isinstance(right, (nodes.IntType, nodes.FloatType)):
                raise TypeMismatchInExpression(ctx)
            return nodes.BoolType()

        if op in ["==", "!="]:
            same = left == right
            num_mix = (
                (isinstance(left, nodes.IntType) and isinstance(right, nodes.FloatType))
                or (isinstance(left, nodes.FloatType) and isinstance(right, nodes.IntType))
            )
            comparable = isinstance(left, (nodes.IntType, nodes.FloatType, nodes.BoolType, nodes.StringType, nodes.ClassType))
            if not ((same and comparable) or num_mix):
                raise TypeMismatchInExpression(ctx)
            return nodes.BoolType()

        if op in ["&&", "||"]:
            if left != nodes.BoolType() or right != nodes.BoolType():
                raise TypeMismatchInExpression(ctx)
            return nodes.BoolType()

        raise TypeMismatchInExpression(ctx)

    def visitUnaryOp(self, ctx: nodes.UnaryOp, o):
        if ctx.op == "!":
            t = self.visit(ctx.operand, o)
            if t is None:
                raise TypeCannotBeInferred(ctx)
            if t != nodes.BoolType():
                raise TypeMismatchInExpression(ctx)
            return nodes.BoolType()

        if ctx.op in ["+", "-"]:
            t = self.visit(ctx.operand, o)
            if t is None:
                raise TypeCannotBeInferred(ctx)
            if not isinstance(t, (nodes.IntType, nodes.FloatType)):
                raise TypeMismatchInExpression(ctx)
            return t

        # prefix ++ / -- — Forum #7: (1) phải Int → Expression; (2) phải gán được → Statement
        def find_root(expr):
            return find_root(expr.receiver) if isinstance(expr, nodes.MemberAccess) else expr

        def root_is_mutable(expr):
            root = find_root(expr)
            if not isinstance(root, nodes.Id):
                return False
            sym = next(filter(lambda s: s.name == root.name, [s for sc in o for s in sc]), False)
            return sym is not False and sym.is_mutable

        t = self.visit(ctx.operand, o)
        if t is None:
            raise TypeCannotBeInferred(ctx)
        if not isinstance(t, nodes.IntType):
            raise TypeMismatchInExpression(ctx)
        if not isinstance(ctx.operand, (nodes.Id, nodes.MemberAccess)) or not root_is_mutable(ctx.operand):
            raise TypeMismatchInStatement(ctx)
        return nodes.IntType()

    def visitPostfixOp(self, ctx: nodes.PostfixOp, o):
        def find_root(expr):
            return find_root(expr.receiver) if isinstance(expr, nodes.MemberAccess) else expr

        def root_is_mutable(expr):
            root = find_root(expr)
            if not isinstance(root, nodes.Id):
                return False
            sym = next(filter(lambda s: s.name == root.name, [s for sc in o for s in sc]), False)
            return sym is not False and sym.is_mutable

        t = self.visit(ctx.operand, o)
        if t is None:
            raise TypeCannotBeInferred(ctx)
        if not isinstance(t, nodes.IntType):
            raise TypeMismatchInExpression(ctx)
        if not isinstance(ctx.operand, (nodes.Id, nodes.MemberAccess)) or not root_is_mutable(ctx.operand):
            raise TypeMismatchInStatement(ctx)
        return nodes.IntType()

    def visitAssignExpr(self, ctx: nodes.AssignExpr, o):
        def find_root(expr):
            return find_root(expr.receiver) if isinstance(expr, nodes.MemberAccess) else expr

        def root_is_mutable(expr):
            root = find_root(expr)
            if not isinstance(root, nodes.Id):
                return False
            sym = next(filter(lambda s: s.name == root.name, [s for sc in o for s in sc]), False)
            return sym is not False and sym.is_mutable

        if isinstance(ctx.lhs, nodes.Id):
            sym = next(filter(lambda s: s.name == ctx.lhs.name, [s for sc in o for s in sc]), False)
            if sym is False or isinstance(sym.typ, tuple) or (isinstance(sym.typ, nodes.ClassType) and sym.members is not None):
                raise UndeclaredIdentifier(ctx.lhs.name)
            lhs_typ, mutable = sym.typ, sym.is_mutable
        elif isinstance(ctx.lhs, nodes.MemberAccess):
            lhs_typ = self.visit(ctx.lhs, o)
            mutable = root_is_mutable(ctx.lhs)
            sym = None
        else:
            raise TypeMismatchInExpression(ctx)

        if not mutable:
            raise TypeMismatchInStatement(ctx)

        if lhs_typ is None:
            rhs_typ = self.visit(ctx.rhs, o)
            if rhs_typ is None or sym is None:
                raise TypeCannotBeInferred(ctx)
            if isinstance(rhs_typ, nodes.UnitType):
                raise TypeMismatchInExpression(ctx)
            sym.typ = rhs_typ
            return rhs_typ

        if isinstance(ctx.rhs, nodes.Id):
            rhs_sym = next(filter(lambda s: s.name == ctx.rhs.name, [s for sc in o for s in sc]), False)
            if rhs_sym is False or isinstance(rhs_sym.typ, tuple) or (isinstance(rhs_sym.typ, nodes.ClassType) and rhs_sym.members is not None):
                raise UndeclaredIdentifier(ctx.rhs.name)
            if rhs_sym.typ is None:
                rhs_sym.typ = lhs_typ
                return lhs_typ
            rhs_typ = rhs_sym.typ
        else:
            rhs_typ = self.visit(ctx.rhs, o)
            if rhs_typ is None:
                raise TypeCannotBeInferred(ctx)

        if not (lhs_typ == rhs_typ or (isinstance(lhs_typ, nodes.FloatType) and isinstance(rhs_typ, nodes.IntType))):
            raise TypeMismatchInExpression(ctx)
        return lhs_typ
    def visitCallExpr(self, ctx: nodes.CallExpr, o):     
        sym = next(filter(lambda sym: sym.name == ctx.name and (isinstance(sym.typ, tuple) or (isinstance(sym.typ, nodes.ClassType) and sym.members is not None)), [sym for scope in o for sym in scope]), False)
        if not sym:
            raise UndeclaredFunction(ctx.name)

        def bind_arg(expected, arg):
            if isinstance(arg, nodes.Id):
                arg_sym = next(filter(lambda sym: sym.name == arg.name, [sym for scope in o for sym in scope]), False)
                if arg_sym is False or isinstance(arg_sym.typ, tuple) or (isinstance(arg_sym.typ, nodes.ClassType) and arg_sym.members is not None):
                    raise UndeclaredIdentifier(arg.name)
                if arg_sym.typ is None:
                    arg_sym.typ = expected
                    return expected
                return arg_sym.typ
            arg_typ = self.visit(arg, o)
            if arg_typ is None:
                raise TypeCannotBeInferred(arg)
            return arg_typ

        if isinstance(sym.typ, tuple):
            params, ret = sym.typ
            if len(params) != len(ctx.args):
                raise TypeMismatchInExpression(ctx)
            argType = [bind_arg(param, arg) for param, arg in zip(params, ctx.args)]
            parArgType = zip(params, argType)
            cond = next(filter(lambda x: not (x[0] == x[1] or (isinstance(x[0], nodes.FloatType) and isinstance(x[1], nodes.IntType))), parArgType), False)
            if cond:
                raise TypeMismatchInExpression(ctx)
            return ret

        if isinstance(sym.typ, nodes.ClassType):
            if len(sym.members) != len(ctx.args):
                raise TypeMismatchInExpression(ctx)
            memType = [t for (_, t) in sym.members]
            argType = [bind_arg(t, arg) for t, arg in zip(memType, ctx.args)]
            memArgType = zip(memType, argType)
            cond = next(filter(lambda x: not (x[0] == x[1] or (isinstance(x[0], nodes.FloatType) and isinstance(x[1], nodes.IntType))), memArgType), False)
            if cond:
                raise TypeMismatchInExpression(ctx)
            return sym.typ

        raise UndeclaredFunction(ctx.name)

    def visitMemberAccess(self, ctx: nodes.MemberAccess, o): 
        receiver_typ = self.visit(ctx.receiver, o)

        if receiver_typ is None:
            raise TypeCannotBeInferred(ctx)
        
        if not isinstance(receiver_typ, nodes.ClassType):
            raise TypeMismatchInExpression(ctx)
        
        class_sym = next(filter(lambda sym: isinstance(sym.typ, nodes.ClassType) and sym.name == receiver_typ.name and sym.members is not None, [sym for scope in o for sym in scope]), False)
        if class_sym is False:
            raise TypeMismatchInExpression(ctx)

        to_use_member = next(filter(lambda m: m[0] == ctx.member, class_sym.members), False)
        if to_use_member is False:
            raise TypeMismatchInExpression(ctx)

        return to_use_member[1]

    def visitIfExpr(self, ctx: nodes.IfExpr, o):
        cond_typ = self.visit(ctx.cond, o)
        if cond_typ is None:
            raise TypeCannotBeInferred(ctx.cond)
        if cond_typ != nodes.BoolType():
            raise TypeMismatchInExpression(ctx)

        then_typ = self.visit(ctx.then_expr, o)
        else_typ = self.visit(ctx.else_expr, o)
        if then_typ is None or else_typ is None:
            raise TypeCannotBeInferred(ctx)

        # Hai nhánh phải cùng kiểu; không có widening giữa các nhánh (giống WhenExpr).
        if then_typ != else_typ:
            raise TypeMismatchInExpression(ctx)
        return then_typ

    def visitWhenExpr(self, ctx: nodes.WhenExpr, o):
        if ctx.subject is not None:
            subject_typ = self.visit(ctx.subject, o)
            if subject_typ is None:
                raise TypeCannotBeInferred(ctx.subject)
            if subject_typ not in [nodes.IntType(), nodes.FloatType(), nodes.BoolType(), nodes.StringType()]:
                raise TypeMismatchInExpression(ctx)
        else:
            subject_typ = None

        else_count = reduce(lambda acc, b: acc + (1 if b.labels is None else 0), ctx.branches, 0)
        if else_count != 1:
            raise TypeMismatchInExpression(ctx)

        def check_branch(acc, branch):
            if branch.labels is not None:
                def check_label(_, label):
                    label_typ = self.visit(label, o)
                    if label_typ is None:
                        raise TypeCannotBeInferred(label)
                    if subject_typ is not None:
                        numeric = (nodes.IntType(), nodes.FloatType())
                        if not (label_typ == subject_typ or (
                            label_typ in numeric and subject_typ in numeric
                        )):
                            raise TypeMismatchInExpression(label)
                    elif label_typ != nodes.BoolType():
                        raise TypeMismatchInExpression(label)
                    return None
                reduce(check_label, branch.labels, None)

            body_typ = self.visit(branch.body, o)
            if body_typ is None:
                raise TypeCannotBeInferred(branch.body)
            # Every branch must yield the *same* type; promotion does not merge them.
            if acc is None:
                return body_typ
            if acc == body_typ:
                return acc
            raise TypeMismatchInExpression(ctx)

        return reduce(check_branch, ctx.branches, None)

    def visitId(self, ctx: nodes.Id, o):                 
        sym = next(filter(lambda sym: sym.name == ctx.name, [sym for scope in o for sym in scope]), False)
        if not sym or isinstance(sym.typ, tuple) or (isinstance(sym.typ, nodes.ClassType) and sym.members is not None):
            raise UndeclaredIdentifier(ctx.name)
        return sym.typ
    
    def visitIntLit(self, ctx: nodes.IntLit, o):         
        return nodes.IntType()

    def visitFloatLit(self, ctx: nodes.FloatLit, o):     
        return nodes.FloatType()

    def visitBoolLit(self, ctx: nodes.BoolLit, o):       
        return nodes.BoolType()

    def visitStringLit(self, ctx: nodes.StringLit, o):   
        return nodes.StringType()
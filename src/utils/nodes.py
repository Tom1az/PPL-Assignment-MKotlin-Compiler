"""AST node definitions for the MKotlin language.

Every node is a small immutable-ish dataclass with a readable ``__repr__`` so
that AST-generation tests can compare against an expected string.  See
``mkotlin-ast_representation.md`` for ``VarDecl``, ``ExprStmt``, and
``WhenBranch`` conventions.

The class hierarchy is intentionally close to the structure of the language
specification:

    Program
      ├── decls: list[Decl]            (DataClassDecl | FuncDecl)

    Types        : IntType, FloatType, BoolType, StringType, UnitType, ClassType
    Declarations : DataClassDecl, MemberDecl, FuncDecl, Param, VarDecl
    Statements   : Block, If, While, For, When, Break, Continue, Return,
                   Assign, ExprStmt
    Expressions  : BinaryOp, UnaryOp, PostfixOp, CallExpr, MemberAccess,
                   IfExpr, WhenExpr, Id, IntLit, FloatLit, BoolLit, StringLit
"""

from dataclasses import dataclass, field
from typing import List, Optional


# --------------------------------------------------------------------------- #
#  Base classes                                                               #
# --------------------------------------------------------------------------- #
class AST:
    def accept(self, v, param=None):
        return v.visit(self, param)


class Type(AST):
    pass


class Decl(AST):
    pass


class Stmt(AST):
    pass


class Expr(AST):
    pass


class LHS(Expr):
    """Marker base for assignable expressions (Id, MemberAccess)."""


# --------------------------------------------------------------------------- #
#  Types                                                                      #
# --------------------------------------------------------------------------- #
@dataclass
class IntType(Type):
    def __repr__(self):
        return "IntType"


@dataclass
class FloatType(Type):
    def __repr__(self):
        return "FloatType"


@dataclass
class BoolType(Type):
    def __repr__(self):
        return "BoolType"


@dataclass
class StringType(Type):
    def __repr__(self):
        return "StringType"


@dataclass
class UnitType(Type):
    def __repr__(self):
        return "UnitType"


@dataclass
class ClassType(Type):
    """A user-defined data class type, referenced by name."""

    name: str

    def __repr__(self):
        return f"ClassType({self.name})"


# --------------------------------------------------------------------------- #
#  Program & top-level declarations                                           #
# --------------------------------------------------------------------------- #
@dataclass
class Program(AST):
    decls: List[Decl] = field(default_factory=list)

    def __repr__(self):
        return f"Program([{', '.join(repr(d) for d in self.decls)}])"


@dataclass
class MemberDecl(AST):
    name: str
    typ: Type

    def __repr__(self):
        return f"MemberDecl({self.name}, {self.typ})"


@dataclass
class DataClassDecl(Decl):
    name: str
    members: List[MemberDecl] = field(default_factory=list)

    def __repr__(self):
        return f"DataClassDecl({self.name}, [{', '.join(repr(m) for m in self.members)}])"


@dataclass
class Param(AST):
    name: str
    typ: Type

    def __repr__(self):
        return f"Param({self.name}, {self.typ})"


@dataclass
class FuncDecl(Decl):
    name: str
    params: List[Param]
    return_type: Optional[Type]   # None => inferred
    body: "Block"

    def __repr__(self):
        rt = repr(self.return_type) if self.return_type is not None else "None"
        return (
            f"FuncDecl({self.name}, "
            f"[{', '.join(repr(p) for p in self.params)}], "
            f"{rt}, {self.body})"
        )


# --------------------------------------------------------------------------- #
#  Statements                                                                 #
# --------------------------------------------------------------------------- #
@dataclass
class VarDecl(Stmt):
    """A `val` or `var` declaration.

    ``mutable`` is True for ``var`` and False for ``val``.
    ``declared_type`` is None when the type is inferred.
    ``init`` is None when there is no initializer.
    """

    name: str
    mutable: bool
    declared_type: Optional[Type]
    init: Optional[Expr]

    def __repr__(self):
        kind = "var" if self.mutable else "val"
        t = repr(self.declared_type) if self.declared_type is not None else "None"
        i = repr(self.init) if self.init is not None else "None"
        return f"VarDecl({kind}, {self.name}, {t}, {i})"


@dataclass
class Block(Stmt):
    stmts: List[Stmt] = field(default_factory=list)

    def __repr__(self):
        return f"Block([{', '.join(repr(s) for s in self.stmts)}])"


@dataclass
class If(Stmt):
    cond: Expr
    then_stmt: Stmt
    else_stmt: Optional[Stmt] = None

    def __repr__(self):
        e = repr(self.else_stmt) if self.else_stmt is not None else "None"
        return f"If({self.cond}, {self.then_stmt}, {e})"


@dataclass
class While(Stmt):
    cond: Expr
    body: Stmt

    def __repr__(self):
        return f"While({self.cond}, {self.body})"


@dataclass
class For(Stmt):
    var: str
    start: Expr
    end: Expr
    body: Stmt

    def __repr__(self):
        return f"For({self.var}, {self.start}, {self.end}, {self.body})"


@dataclass
class WhenBranch(AST):
    """One branch of a `when`.

    ``labels`` is None for the `else` branch, otherwise a list of label
    expressions (subject form) or guard expressions (conditionless form).
    """

    labels: Optional[List[Expr]]
    body: AST   # Stmt for a when-statement, Expr for a when-expression

    def __repr__(self):
        if self.labels is None:
            return f"WhenBranch(else, {self.body})"
        return f"WhenBranch([{', '.join(repr(e) for e in self.labels)}], {self.body})"


@dataclass
class When(Stmt):
    subject: Optional[Expr]   # None => conditionless form
    branches: List[WhenBranch] = field(default_factory=list)

    def __repr__(self):
        s = repr(self.subject) if self.subject is not None else "None"
        return f"When({s}, [{', '.join(repr(b) for b in self.branches)}])"


@dataclass
class Break(Stmt):
    def __repr__(self):
        return "Break()"


@dataclass
class Continue(Stmt):
    def __repr__(self):
        return "Continue()"


@dataclass
class Return(Stmt):
    value: Optional[Expr] = None

    def __repr__(self):
        v = repr(self.value) if self.value is not None else "None"
        return f"Return({v})"


@dataclass
class Assign(Stmt):
    lhs: LHS
    rhs: Expr

    def __repr__(self):
        return f"Assign({self.lhs}, {self.rhs})"


@dataclass
class ExprStmt(Stmt):
    expr: Expr

    def __repr__(self):
        return f"ExprStmt({self.expr})"


# --------------------------------------------------------------------------- #
#  Expressions                                                                #
# --------------------------------------------------------------------------- #
@dataclass
class BinaryOp(Expr):
    op: str
    left: Expr
    right: Expr

    def __repr__(self):
        return f"BinaryOp({self.op}, {self.left}, {self.right})"


@dataclass
class UnaryOp(Expr):
    """Prefix unary operator: ! - + ++ --"""

    op: str
    operand: Expr

    def __repr__(self):
        return f"UnaryOp({self.op}, {self.operand})"


@dataclass
class PostfixOp(Expr):
    """Postfix ++ / --"""

    op: str
    operand: Expr

    def __repr__(self):
        return f"PostfixOp({self.op}, {self.operand})"


@dataclass
class AssignExpr(Expr):
    """Assignment used in expression position (e.g. `x = y = 1`)."""

    lhs: LHS
    rhs: Expr

    def __repr__(self):
        return f"AssignExpr({self.lhs}, {self.rhs})"


@dataclass
class CallExpr(Expr):
    """A function call or a data-class constructor call.

    The two are syntactically identical; the static checker resolves which
    one ``name`` refers to.
    """

    name: str
    args: List[Expr] = field(default_factory=list)

    def __repr__(self):
        return f"CallExpr({self.name}, [{', '.join(repr(a) for a in self.args)}])"


@dataclass
class MemberAccess(LHS):
    receiver: Expr
    member: str

    def __repr__(self):
        return f"MemberAccess({self.receiver}, {self.member})"


@dataclass
class IfExpr(Expr):
    cond: Expr
    then_expr: Expr
    else_expr: Expr

    def __repr__(self):
        return f"IfExpr({self.cond}, {self.then_expr}, {self.else_expr})"


@dataclass
class WhenExpr(Expr):
    subject: Optional[Expr]
    branches: List[WhenBranch] = field(default_factory=list)

    def __repr__(self):
        s = repr(self.subject) if self.subject is not None else "None"
        return f"WhenExpr({s}, [{', '.join(repr(b) for b in self.branches)}])"


@dataclass
class Id(LHS):
    name: str

    def __repr__(self):
        return f"Id({self.name})"


@dataclass
class IntLit(Expr):
    value: int

    def __repr__(self):
        return f"IntLit({self.value})"


@dataclass
class FloatLit(Expr):
    value: float

    def __repr__(self):
        return f"FloatLit({self.value})"


@dataclass
class BoolLit(Expr):
    value: bool

    def __repr__(self):
        return f"BoolLit({str(self.value).lower()})"


@dataclass
class StringLit(Expr):
    value: str

    def __repr__(self):
        return f"StringLit({self.value})"

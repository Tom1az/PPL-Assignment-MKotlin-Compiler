"""Static semantic checker for MKotlin — Assignment 3.

Implement the ``StaticChecker`` class so that, given the AST produced by
Assignment 2, it either returns normally (the program is well-formed) or raises
exactly one of the exceptions defined in ``static_error.py`` for the first
violation it finds, in deterministic traversal order.

See ``mkotlin-semantic_constraints_and_errors.md`` for the full set of rules.

This file is a skeleton: every visit method currently raises
``NotImplementedError``.  Replace the bodies with your implementation.
"""

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

class Symbol:
    def __init__(self, name, typ):
        self.name = name
        self.typ = typ

class StaticChecker(BaseVisitor):
    def __init__(self, ast):
        self.ast = ast

    def check(self):
        """Run the checker.  Returns normally if the program is valid,
        otherwise raises a ``StaticError`` subclass."""
        return self.visit(self.ast, None)

    # ----------------------------------------------------------------- #
    #  TODO: implement the visitor methods below.                       #
    #  The inherited BaseVisitor methods raise NotImplementedError, so  #
    #  the checker is non-functional until you fill these in.           #
    # ----------------------------------------------------------------- #
    # Program & declarations
    
    def visitProgram(self, ctx: nodes.Program, o):
        o = reduce(lambda acc, decl: self.visit(decl, acc), ctx.decls, o if o is not None else [[]])

    def visitDataClassDecl(self, ctx: nodes.DataClassDecl, o): 
        if ctx.name in [item.name for item in o[0]]:
            raise Redeclared(Class, ctx.name)
        return [o[0] + [ctx.name]] + o[1:]

    def visitMemberDecl(self, ctx: nodes.MemberDecl, o): 
        if ctx.name in [item.name for item in o[0]]:
            raise Redeclared()
        
    def visitFuncDecl(self, ctx: nodes.FuncDecl, o):     raise NotImplementedError()
    def visitParam(self, ctx: nodes.Param, o):           raise NotImplementedError()

    # Types
    def visitIntType(self, ctx: nodes.IntType, o):       raise NotImplementedError()
    def visitFloatType(self, ctx: nodes.FloatType, o):   raise NotImplementedError()
    def visitBoolType(self, ctx: nodes.BoolType, o):     raise NotImplementedError()
    def visitStringType(self, ctx: nodes.StringType, o): raise NotImplementedError()
    def visitUnitType(self, ctx: nodes.UnitType, o):     raise NotImplementedError()
    def visitClassType(self, ctx: nodes.ClassType, o):   raise NotImplementedError()

    # Statements
    def visitVarDecl(self, ctx: nodes.VarDecl, o):       raise NotImplementedError()
    def visitBlock(self, ctx: nodes.Block, o):           raise NotImplementedError()
    def visitIf(self, ctx: nodes.If, o):                 raise NotImplementedError()
    def visitWhile(self, ctx: nodes.While, o):           raise NotImplementedError()
    def visitFor(self, ctx: nodes.For, o):               raise NotImplementedError()
    def visitWhen(self, ctx: nodes.When, o):             raise NotImplementedError()
    def visitWhenBranch(self, ctx: nodes.WhenBranch, o): raise NotImplementedError()
    def visitBreak(self, ctx: nodes.Break, o):           raise NotImplementedError()
    def visitContinue(self, ctx: nodes.Continue, o):     raise NotImplementedError()
    def visitReturn(self, ctx: nodes.Return, o):         raise NotImplementedError()
    def visitAssign(self, ctx: nodes.Assign, o):         raise NotImplementedError()
    def visitExprStmt(self, ctx: nodes.ExprStmt, o):     raise NotImplementedError()

    # Expressions
    def visitBinaryOp(self, ctx: nodes.BinaryOp, o):     raise NotImplementedError()
    def visitUnaryOp(self, ctx: nodes.UnaryOp, o):       raise NotImplementedError()
    def visitPostfixOp(self, ctx: nodes.PostfixOp, o):   raise NotImplementedError()
    def visitAssignExpr(self, ctx: nodes.AssignExpr, o): raise NotImplementedError()
    def visitCallExpr(self, ctx: nodes.CallExpr, o):     raise NotImplementedError()
    def visitMemberAccess(self, ctx: nodes.MemberAccess, o): raise NotImplementedError()
    def visitIfExpr(self, ctx: nodes.IfExpr, o):         raise NotImplementedError()
    def visitWhenExpr(self, ctx: nodes.WhenExpr, o):     raise NotImplementedError()
    def visitId(self, ctx: nodes.Id, o):                 raise NotImplementedError()
    def visitIntLit(self, ctx: nodes.IntLit, o):         raise NotImplementedError()
    def visitFloatLit(self, ctx: nodes.FloatLit, o):     raise NotImplementedError()
    def visitBoolLit(self, ctx: nodes.BoolLit, o):       raise NotImplementedError()
    def visitStringLit(self, ctx: nodes.StringLit, o):   raise NotImplementedError()
        

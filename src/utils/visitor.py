"""Base visitor classes for traversing the MKotlin AST.

``ASTVisitor`` dispatches on the concrete node class to a ``visit<ClassName>``
method, which subclasses (the static checker, the code generator) override.
"""

from src.utils import nodes


class ASTVisitor:
    """Generic visitor: dispatches ``visit(node, param)`` to ``visitX``."""

    def visit(self, node, param=None):
        method = "visit" + type(node).__name__
        visitor = getattr(self, method, self.generic_visit)
        return visitor(node, param)

    def generic_visit(self, node, param):
        raise NotImplementedError(
            f"No visit method for node type {type(node).__name__}"
        )


class BaseVisitor(ASTVisitor):
    """A convenience base that declares every visit method, each raising
    ``NotImplementedError``.  Students override the ones they need.
    """

    # Program & declarations
    def visitProgram(self, ctx: nodes.Program, o):       raise NotImplementedError()
    def visitDataClassDecl(self, ctx: nodes.DataClassDecl, o): raise NotImplementedError()
    def visitMemberDecl(self, ctx: nodes.MemberDecl, o): raise NotImplementedError()
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

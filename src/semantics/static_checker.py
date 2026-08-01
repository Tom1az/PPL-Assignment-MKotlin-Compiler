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

class Symbol:
    def __init__(self, name, typ, is_mutable=False, is_constant=False, is_in_loop=False):
        self.name = name
        self.typ = typ
        self.is_mutable = is_mutable
        self.is_constant = is_constant
        self.is_in_loop = is_in_loop

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
        built_ins = [Symbol(name, (param_typ, ret_typ)) for name, (param_typ, ret_typ) in BUILTIN_FUNCS.items()]
        return reduce(lambda acc, decl: self.visit(decl, acc), ctx.decls, [built_ins])

    def visitDataClassDecl(self, ctx: nodes.DataClassDecl, o): 
        if ctx.name in [item.name for item in o[0]]:
            raise Redeclared(Class(), ctx.name)
        member_scope = [[]] + o
        reduce(lambda acc, member: self.visit(member, acc), ctx.members, member_scope)
        return [o[0] + [Symbol(ctx.name, nodes.ClassType(ctx.name))]] + o[1:]

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
        func_symbol = Symbol(ctx.name, (param_types, ctx.return_type))
        ret_symbol = Symbol("return", ctx.return_type)

        new_o = [o[0] + [func_symbol]] + o[1:]
        o_after_func_decl = [[ret_symbol]] + new_o
        o_after_params = reduce(lambda acc, param: self.visit(param, acc), ctx.params, o_after_func_decl)
        reduce(lambda acc, stmt: self.visit(stmt, acc), ctx.body.stmts, o_after_params)
        
        if ret_symbol.typ is None:
            ret_symbol.typ = nodes.UnitType()
        func_symbol.typ = (param_types, ret_symbol.typ)

        return new_o
        
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
        pass

    def visitBlock(self, ctx: nodes.Block, o):           
        reduce(lambda acc, stmt: self.visit(stmt, acc), ctx.stmts, [[]] + o)
        return o

    def visitIf(self, ctx: nodes.If, o):                 
        cond_typ = self.visit(ctx.cond, 0)

        if cond_typ != nodes.BoolType():
            raise TypeMismatchInStatement(ctx)

        self.visit(ctx.then_stmt, o)

        if ctx.else_stmt is not None:
            self.visit(ctx.else_stmt, o)

        return o

    def visitWhile(self, ctx: nodes.While, o):           
        cond_typ = self.visit(ctx.cond, 0)

        if cond_typ != nodes.BoolType():
            raise TypeMismatchInStatement(ctx)

        self.visit(ctx.body, [Symbol("loop", None, is_in_loop=True)] + o)

        return o

    def visitFor(self, ctx: nodes.For, o):   
        start_type = self.visit(ctx.start, o)
        end_type = self.visit(ctx.end, o)

        if start_type != end_type:
            raise TypeMismatchInStatement(ctx)

        

        
    def visitWhen(self, ctx: nodes.When, o):             raise NotImplementedError()
    def visitWhenBranch(self, ctx: nodes.WhenBranch, o): raise NotImplementedError()
    def visitBreak(self, ctx: nodes.Break, o):           
        if not any(sym.is_in_loop for scope in o for sym in scope):
            raise MustInLoop(ctx)
        
        return o

    def visitContinue(self, ctx: nodes.Continue, o): 
        if not any(sym.is_in_loop for scope in o for sym in scope):
            raise MustInLoop(ctx)
        
        return o
    
    def visitReturn(self, ctx: nodes.Return, o):         
        ret_symbol = next(filter(lambda sym: sym.name == "return", [sym for scope in o for sym in scope]), False)

        if ctx.value is None:
            if ret_symbol.typ is not None and ret_symbol.typ != nodes.UnitType():
                raise TypeMismatchInStatement(ctx)
            return o
        
        ret_typ = self.visit(ctx.value, o)
        if ret_symbol.typ is None:
            ret_symbol.typ = ret_typ
        elif not (ret_symbol.typ == ret_typ or (ret_symbol.typ == nodes.FloatType() and ret_typ == nodes.IntType())):
            raise TypeMismatchInStatement(ctx)
        return o

        
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
    
    def visitIntLit(self, ctx: nodes.IntLit, o):         
        return nodes.IntType()

    def visitFloatLit(self, ctx: nodes.FloatLit, o):     
        return nodes.FloatType()

    def visitBoolLit(self, ctx: nodes.BoolLit, o):       
        return nodes.BoolType()

    def visitStringLit(self, ctx: nodes.StringLit, o):   
        return nodes.StringType()
        

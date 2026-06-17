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
    def visitProgram(self, ctx: nodes.Program, o):
        raise NotImplementedError(
            "Assignment 3: implement StaticChecker.visitProgram (and the rest)."
        )

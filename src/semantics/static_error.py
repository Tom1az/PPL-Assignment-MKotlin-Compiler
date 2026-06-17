"""Semantic error exception classes for the MKotlin static checker.

These are the eight error types described in
``mkotlin-semantic_constraints_and_errors.md``.  The static checker raises the
appropriate exception for the first violation it finds.  Do **not** modify this
file; the test suite imports these classes by name.
"""


# --------------------------------------------------------------------------- #
#  "Kind" markers used by Redeclared                                          #
# --------------------------------------------------------------------------- #
class Kind:
    def __str__(self):
        return self.__class__.__name__


class Function(Kind):
    pass


class Parameter(Kind):
    pass


class Variable(Kind):
    pass


class Constant(Kind):
    """A `val` binding."""


class Class(Kind):
    pass


class Member(Kind):
    pass


# --------------------------------------------------------------------------- #
#  Static errors                                                              #
# --------------------------------------------------------------------------- #
class StaticError(Exception):
    """Base class for all static-semantic errors."""


class Redeclared(StaticError):
    def __init__(self, kind: Kind, name: str):
        self.kind = kind
        self.name = name

    def __str__(self):
        return f"Redeclared {self.kind}: {self.name}"


class UndeclaredIdentifier(StaticError):
    def __init__(self, name: str):
        self.name = name

    def __str__(self):
        return f"Undeclared Identifier: {self.name}"


class UndeclaredFunction(StaticError):
    def __init__(self, name: str):
        self.name = name

    def __str__(self):
        return f"Undeclared Function: {self.name}"


class UndeclaredClass(StaticError):
    def __init__(self, name: str):
        self.name = name

    def __str__(self):
        return f"Undeclared Class: {self.name}"


class TypeCannotBeInferred(StaticError):
    def __init__(self, ctx):
        self.ctx = ctx

    def __str__(self):
        return f"Type Cannot Be Inferred: {self.ctx}"


class TypeMismatchInStatement(StaticError):
    def __init__(self, ctx):
        self.ctx = ctx

    def __str__(self):
        return f"Type Mismatch In Statement: {self.ctx}"


class TypeMismatchInExpression(StaticError):
    def __init__(self, ctx):
        self.ctx = ctx

    def __str__(self):
        return f"Type Mismatch In Expression: {self.ctx}"


class MustInLoop(StaticError):
    def __init__(self, ctx):
        self.ctx = ctx

    def __str__(self):
        return f"Must In Loop: {self.ctx}"

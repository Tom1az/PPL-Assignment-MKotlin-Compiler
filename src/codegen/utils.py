"""Utility classes for MKotlin code generation."""

from src.utils.nodes import Type


class FunctionType(Type):
    """Function type used during code generation (built-ins and user functions)."""

    def __init__(self, param_types, return_type):
        self.param_types = param_types
        self.return_type = return_type


class Value:
    """Base class for symbol values."""
    pass


class Index(Value):
    """Local variable slot index."""

    def __init__(self, value: int):
        self.value = value


class CName(Value):
    """Fully qualified class name for static calls (e.g. ``io``)."""

    def __init__(self, value: str):
        self.value = value


class Symbol:
    """Symbol-table entry: name, MKotlin type, and codegen value."""

    def __init__(self, name: str, typ: Type, value: Value):
        self.name = name
        self.type = typ
        self.value = value


class Access:
    """Evaluation context passed while generating expressions."""

    def __init__(self, frame, sym: list[Symbol], is_left: bool = False):
        self.frame = frame
        self.sym = sym
        self.is_left = is_left


class SubBody:
    """Context passed while generating statements."""

    def __init__(self, frame, sym: list[Symbol]):
        self.frame = frame
        self.sym = sym

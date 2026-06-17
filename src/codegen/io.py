"""Built-in I/O symbols for MKotlin code generation."""

from src.utils.nodes import IntType, FloatType, BoolType, StringType, UnitType
from src.codegen.utils import FunctionType, Symbol, CName

LIB_NAME = "io"

IO_SYMBOL_LIST = [
    Symbol("readInt", FunctionType([], IntType()), CName(LIB_NAME)),
    Symbol("readFloat", FunctionType([], FloatType()), CName(LIB_NAME)),
    Symbol("readBool", FunctionType([], BoolType()), CName(LIB_NAME)),
    Symbol("readString", FunctionType([], StringType()), CName(LIB_NAME)),
    Symbol("printInt", FunctionType([IntType()], UnitType()), CName(LIB_NAME)),
    Symbol("printFloat", FunctionType([FloatType()], UnitType()), CName(LIB_NAME)),
    Symbol("printBool", FunctionType([BoolType()], UnitType()), CName(LIB_NAME)),
    Symbol("printString", FunctionType([StringType()], UnitType()), CName(LIB_NAME)),
]

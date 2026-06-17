"""Jasmin emission helpers for MKotlin — Assignment 4.

``Emitter`` wraps ``JasminCode`` with MKotlin-aware helpers so students can focus
on AST traversal in ``codegen.py``.  Low-level instruction strings are produced
by ``jasmin_code.py``; this module handles type descriptors, stack bookkeeping
via ``Frame``, and common patterns (constants, locals, branches, ``io`` calls).
"""

import os
from typing import Optional, Union

from src.utils import nodes
from src.codegen.jasmin_code import JasminCode
from src.codegen.error import IllegalOperandException
from src.codegen.utils import FunctionType


def is_int_type(t):
    return type(t) is nodes.IntType


def is_float_type(t):
    return type(t) is nodes.FloatType


def is_bool_type(t):
    return type(t) is nodes.BoolType


def is_string_type(t):
    return type(t) is nodes.StringType


def is_unit_type(t):
    return type(t) is nodes.UnitType


def is_class_type(t):
    return type(t) is nodes.ClassType


class Emitter:
    """Generate Jasmin instructions for one ``.j`` output file."""

    def __init__(self, filename: str, output_dir: Optional[str] = None):
        self.filename = filename
        if output_dir is None:
            output_dir = os.path.join(
                os.path.dirname(os.path.dirname(__file__)), "runtime"
            )
        self.filepath = os.path.join(output_dir, filename)
        self.buff: list[str] = []
        self.jvm = JasminCode()

    def print_out(self, code: str):
        self.buff.append(code)

    def emit(self) -> str:
        return "".join(self.buff)

    def save(self):
        with open(self.filepath, "w", encoding="utf-8") as f:
            f.write(self.emit())

    # ------------------------------------------------------------------ #
    #  Type descriptors                                                   #
    # ------------------------------------------------------------------ #
    def get_jvm_type(self, in_type) -> str:
        if is_int_type(in_type) or is_bool_type(in_type):
            return "I"
        if is_float_type(in_type):
            return "F"
        if is_string_type(in_type):
            return "Ljava/lang/String;"
        if is_unit_type(in_type):
            return "V"
        if is_class_type(in_type):
            return "L" + in_type.name + ";"
        if type(in_type) is FunctionType:
            params = "".join(self.get_jvm_type(p) for p in in_type.param_types)
            return "(" + params + ")" + self.get_jvm_type(in_type.return_type)
        raise IllegalOperandException(f"Unknown type: {type(in_type)}")

    # ------------------------------------------------------------------ #
    #  Class / method scaffolding                                         #
    # ------------------------------------------------------------------ #
    def emit_prolog(self, class_name: str, super_name: str = "java/lang/Object"):
        self.print_out(self.jvm.emitCLASS("public " + class_name))
        self.print_out(self.jvm.emitSUPER(super_name))

    def emit_method(self, name: str, param_types, return_type, is_static: bool = True):
        ft = FunctionType(list(param_types), return_type)
        self.print_out(self.jvm.emitMETHOD(name, self.get_jvm_type(ft), is_static))

    def emit_end_method(self):
        self.print_out(self.jvm.emitENDMETHOD())

    def emit_limit_stack(self, n: int):
        self.print_out(self.jvm.emitLIMITSTACK(n))

    def emit_limit_local(self, n: int):
        self.print_out(self.jvm.emitLIMITLOCAL(n))

    # ------------------------------------------------------------------ #
    #  Constants                                                          #
    # ------------------------------------------------------------------ #
    def emit_push_iconst(self, value: int, frame) -> str:
        frame.push()
        if -1 <= value <= 5:
            return self.jvm.emitICONST(value)
        if -128 <= value <= 127:
            return self.jvm.emitBIPUSH(value)
        if -32768 <= value <= 32767:
            return self.jvm.emitSIPUSH(value)
        return self.jvm.emitLDC(str(value))

    def emit_push_fconst(self, value: float, frame) -> str:
        frame.push()
        if value == 0.0:
            return self.jvm.emitFCONST("0.0")
        if value == 1.0:
            return self.jvm.emitFCONST("1.0")
        if value == 2.0:
            return self.jvm.emitFCONST("2.0")
        return self.jvm.emitLDC(str(value))

    def emit_push_bool(self, value: bool, frame) -> str:
        return self.emit_push_iconst(1 if value else 0, frame)

    def emit_push_string(self, value: str, frame) -> str:
        frame.push()
        escaped = value.replace("\\", "\\\\").replace('"', '\\"')
        return self.jvm.emitLDC('"' + escaped + '"')

    # ------------------------------------------------------------------ #
    #  Locals                                                             #
    # ------------------------------------------------------------------ #
    def emit_read_var(self, name: str, in_type, index: int, frame) -> str:
        frame.push()
        if is_int_type(in_type) or is_bool_type(in_type):
            return self.jvm.emitILOAD(index)
        if is_float_type(in_type):
            return self.jvm.emitFLOAD(index)
        if is_string_type(in_type) or is_class_type(in_type):
            return self.jvm.emitALOAD(index)
        raise IllegalOperandException(f"Cannot read var {name}: {type(in_type)}")

    def emit_write_var(self, name: str, in_type, index: int, frame) -> str:
        frame.pop()
        if is_int_type(in_type) or is_bool_type(in_type):
            return self.jvm.emitISTORE(index)
        if is_float_type(in_type):
            return self.jvm.emitFSTORE(index)
        if is_string_type(in_type) or is_class_type(in_type):
            return self.jvm.emitASTORE(index)
        raise IllegalOperandException(f"Cannot write var {name}: {type(in_type)}")

    # ------------------------------------------------------------------ #
    #  Fields & calls                                                     #
    # ------------------------------------------------------------------ #
    def emit_get_field(self, lexeme: str, field_type, frame) -> str:
        frame.pop()
        frame.push()
        return self.jvm.emitGETFIELD(lexeme, self.get_jvm_type(field_type))

    def emit_put_field(self, lexeme: str, field_type, frame) -> str:
        frame.pop()
        frame.pop()
        return self.jvm.emitPUTFIELD(lexeme, self.get_jvm_type(field_type))

    def emit_invoke_static(self, lexeme: str, func_type: FunctionType, frame) -> str:
        for _ in func_type.param_types:
            frame.pop()
        if not is_unit_type(func_type.return_type):
            frame.push()
        return self.jvm.emitINVOKESTATIC(lexeme, self.get_jvm_type(func_type))

    def emit_invoke_io(self, name: str, func_type: FunctionType, frame) -> str:
        """Invoke a built-in in class ``io`` (e.g. ``printInt``)."""
        return self.emit_invoke_static("io/" + name, func_type, frame)

    # ------------------------------------------------------------------ #
    #  Arithmetic / logic (selected)                                      #
    # ------------------------------------------------------------------ #
    def emit_add_op(self, op: str, in_type, frame) -> str:
        frame.pop()
        if op == "+":
            return self.jvm.emitIADD() if is_int_type(in_type) else self.jvm.emitFADD()
        return self.jvm.emitISUB() if is_int_type(in_type) else self.jvm.emitFSUB()

    def emit_mul_op(self, op: str, in_type, frame) -> str:
        frame.pop()
        if op == "*":
            return self.jvm.emitIMUL() if is_int_type(in_type) else self.jvm.emitFMUL()
        if op == "/":
            return self.jvm.emitIDIV() if is_int_type(in_type) else self.jvm.emitFDIV()
        return self.jvm.emitIREM()

    def emit_and_op(self, frame) -> str:
        frame.pop()
        return self.jvm.emitIAND()

    def emit_or_op(self, frame) -> str:
        frame.pop()
        return self.jvm.emitIOR()

    def emit_neg_op(self, in_type, frame) -> str:
        return self.jvm.emitINEG() if is_int_type(in_type) else self.jvm.emitFNEG()

    def emit_int_to_float(self, frame) -> str:
        return self.jvm.emitI2F()

    # ------------------------------------------------------------------ #
    #  Branches & labels                                                  #
    # ------------------------------------------------------------------ #
    def emit_label(self, label: int) -> str:
        return self.jvm.emitLABEL(label)

    def emit_goto(self, label: int) -> str:
        return self.jvm.emitGOTO(label)

    def emit_if_false(self, label: int) -> str:
        frame.pop()
        return self.jvm.emitIFEQ(label)

    def emit_if_true(self, label: int) -> str:
        frame.pop()
        return self.jvm.emitIFNE(label)

    def emit_cmp_int(self, op: str, label: int) -> str:
        frame.pop()
        mapping = {
            "==": self.jvm.emitIFICMPEQ,
            "!=": self.jvm.emitIFICMPNE,
            "<": self.jvm.emitIFICMPLT,
            "<=": self.jvm.emitIFICMPLE,
            ">": self.jvm.emitIFICMPGT,
            ">=": self.jvm.emitIFICMPGE,
        }
        return mapping[op](label)

    # ------------------------------------------------------------------ #
    #  Returns & stack                                                      #
    # ------------------------------------------------------------------ #
    def emit_return(self, in_type, frame) -> str:
        if is_unit_type(in_type):
            return self.jvm.emitRETURN()
        if is_int_type(in_type) or is_bool_type(in_type):
            return self.jvm.emitIRETURN()
        if is_float_type(in_type):
            return self.jvm.emitFRETURN()
        if is_string_type(in_type) or is_class_type(in_type):
            return self.jvm.emitARETURN()
        raise IllegalOperandException(f"Cannot return type {type(in_type)}")

    def emit_pop(self, frame) -> str:
        frame.pop()
        return self.jvm.emitPOP()

    def emit_dup(self, frame) -> str:
        frame.push()
        return self.jvm.emitDUP()

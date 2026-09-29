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

# --------------------------------------------------------------------------- #
#  ADDED (Assignment 4) — names the JVM needs but MKotlin has no type for.    #
# --------------------------------------------------------------------------- #
OBJECT_CLASS = "java/lang/Object"
STRING_CLASS = "java/lang/String"
OBJECT_DESCRIPTOR = "L" + OBJECT_CLASS + ";"
STRING_ARRAY_DESCRIPTOR = "[L" + STRING_CLASS + ";"
CONSTRUCTOR_NAME = "<init>"
EQUALS_NAME = "equals"


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
        # The starter popped one argument at a time in a `for` loop; `pop` takes
        # a count, so the same stack effect is one call and the file stays free
        # of loops.
        frame.pop(len(func_type.param_types))
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

    # The three helpers below took no ``frame`` in the starter even though their
    # bodies called ``frame.pop()``, and ``emit_cmp_int`` popped once for an
    # instruction that consumes two operands.  Both were confirmed as starter
    # bugs on the forum (Q1 - ASM4) and fixed here: ``frame`` is now the last
    # parameter, as in every other ``emit_*``, and the stack updates match the
    # real instruction.
    def emit_if_false(self, label: int, frame) -> str:
        """``ifeq``: jump when the Boolean on top is false; consumes 1 operand."""
        frame.pop()
        return self.jvm.emitIFEQ(label)

    def emit_if_true(self, label: int, frame) -> str:
        """``ifne``: jump when the Boolean on top is true; consumes 1 operand."""
        frame.pop()
        return self.jvm.emitIFNE(label)

    def emit_cmp_int(self, op: str, label: int, frame) -> str:
        """``if_icmp<op>``: jump when the test holds; consumes 2 operands."""
        frame.pop(2)
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

    # ==================================================================== #
    #  ADDED (Assignment 4) — everything below is new; nothing above this  #
    #  line was changed except emit_if_false / emit_if_true / emit_cmp_int #
    #  (the starter bugs the forum asked us to fix).                       #
    #                                                                      #
    #  Same conventions as above: the class/method directives print into    #
    #  the buffer, the instruction helpers return text and update ``frame``.#
    # ==================================================================== #

    # --- Class / method scaffolding ------------------------------------- #
    def emit_field(self, lexeme: str, field_type, is_public: bool = True):
        """Declare one data-class member as a ``.field``.

        NOTE — the only place in this project where directive text is written
        by hand: ``JasminCode`` (and its ``MachineCode`` interface) has no field
        emitter and ``jasmin_code.py`` must stay untouched.  The descriptor
        still comes from ``get_jvm_type`` and the newline from ``JasminCode.END``,
        so swapping the notation only leaves this one line to adapt.
        """
        self.print_out(
            ".field "
            + ("public" if is_public else "private")
            + " "
            + lexeme
            + " "
            + self.get_jvm_type(field_type)
            + JasminCode.END
        )

    def emit_main_method(self):
        """Declare the JVM entry point ``main([Ljava/lang/String;)V``.

        Its parameter is a String array, a type MKotlin has no node for, so the
        descriptor cannot come from ``get_jvm_type`` alone.
        """
        self.print_out(
            self.jvm.emitMETHOD(
                "main",
                "("
                + STRING_ARRAY_DESCRIPTOR
                + ")"
                + self.get_jvm_type(nodes.UnitType()),
                True,
            )
        )

    def emit_method_limits(self, frame):
        """Both ``.limit`` directives, sized from the frame's high-water marks."""
        self.emit_limit_stack(max(frame.max_op_stack_size, 1))
        self.emit_limit_local(max(frame.max_index, 1))

    # --- Constants ------------------------------------------------------ #
    def emit_push_escaped_string(self, value: str, frame) -> str:
        """Push a string literal that is **already** escaped.

        ``StringLit.value`` keeps the escape sequences exactly as the MKotlin
        source wrote them (``\\n``, ``\\t``, ``\\"``, ...) and Jasmin reads the
        same escapes inside a quoted operand, so the text is passed through
        as is.  ``emit_push_string`` is for a raw Python string and would escape
        these a second time, turning ``\\n`` into a backslash followed by ``n``.
        """
        frame.push()
        return self.jvm.emitLDC('"' + value + '"')

    def emit_push_null(self, frame) -> str:
        frame.push()
        return self.jvm.emitPUSHNULL()

    # --- Objects & instance calls --------------------------------------- #
    def emit_new_object(self, class_name: str, frame) -> str:
        """``new C``: push an uninitialised reference."""
        frame.push()
        return self.jvm.emitNEW(class_name)

    def emit_invoke_constructor(self, class_name: str, param_types, frame) -> str:
        """``C.<init>``: consumes the uninitialised reference and the arguments."""
        frame.pop(1 + len(param_types))
        return self.jvm.emitINVOKESPECIAL(
            class_name + "/" + CONSTRUCTOR_NAME,
            self.get_jvm_type(FunctionType(list(param_types), nodes.UnitType())),
        )

    def emit_invoke_super_constructor(self, frame) -> str:
        """``java/lang/Object.<init>``: consumes the receiver."""
        frame.pop()
        return self.jvm.emitINVOKESPECIAL()

    def emit_invoke_virtual(self, lexeme: str, func_type: FunctionType, frame) -> str:
        """Invoke an instance method; consumes the receiver and the arguments."""
        frame.pop(1 + len(func_type.param_types))
        if not is_unit_type(func_type.return_type):
            frame.push()
        return self.jvm.emitINVOKEVIRTUAL(lexeme, self.get_jvm_type(func_type))

    def emit_string_equal(self, frame) -> str:
        """``String.equals`` — how MKotlin compares two ``String`` values.

        Its parameter is declared ``java/lang/Object``, a JVM type with no
        MKotlin counterpart, so that half of the descriptor is spelled out here.
        """
        frame.pop()
        return self.jvm.emitINVOKEVIRTUAL(
            STRING_CLASS + "/" + EQUALS_NAME,
            "("
            + OBJECT_DESCRIPTOR
            + ")"
            + self.get_java_jvm_type(nodes.BoolType()),
        )

    def emit_data_class_equal(self, class_name: str, frame) -> str:
        """The structural ``equals`` generated for a data class."""
        return self.emit_invoke_virtual(
            class_name + "/" + EQUALS_NAME,
            FunctionType([nodes.ClassType(class_name)], nodes.BoolType()),
            frame,
        )

    # --- Calls into classes compiled from Java --------------------------- #
    def get_java_jvm_type(self, in_type) -> str:
        """Descriptor of ``in_type`` **as a class compiled from Java declares it**.

        Java's ``boolean`` compiles to the descriptor ``Z``, whereas
        ``get_jvm_type`` maps MKotlin's Boolean to ``I``.  Generated MKotlin
        methods stay on ``I`` and are consistent with one another, but a call
        into already-compiled Java — ``io.printBool``/``readBool`` from
        ``io.java``, or ``String.equals`` — has to be spelled the JVM way or the
        JVM raises ``NoSuchMethodError``.
        """
        if is_bool_type(in_type):
            return "Z"
        if type(in_type) is FunctionType:
            params = "".join(self.get_java_jvm_type(p) for p in in_type.param_types)
            return "(" + params + ")" + self.get_java_jvm_type(in_type.return_type)
        return self.get_jvm_type(in_type)

    def emit_invoke_builtin(self, lexeme: str, func_type: FunctionType, frame) -> str:
        """``emit_invoke_static`` for a method compiled from Java.

        Takes the same fully qualified ``lexeme`` (``io/printBool``) and has the
        same stack effect, but spells the descriptor the way Java compiles it,
        so use this rather than ``emit_invoke_io`` whenever a Boolean is
        involved.  The owner class is left to the caller, which reads it off the
        symbol, so no class name is hard-coded here.
        """
        frame.pop(len(func_type.param_types))
        if not is_unit_type(func_type.return_type):
            frame.push()
        return self.jvm.emitINVOKESTATIC(lexeme, self.get_java_jvm_type(func_type))

    # --- Returns -------------------------------------------------------- #
    def emit_return_value(self, in_type, frame) -> str:
        """``emit_return`` for a method that returns a value.

        ``emit_return`` leaves ``frame`` untouched, so on its own it does not
        account for the value ``ireturn`` / ``freturn`` / ``areturn`` consumes;
        this variant does, which keeps the caller a single expression.
        """
        frame.pop()
        return self.emit_return(in_type, frame)

    # --- Branches & stack ----------------------------------------------- #
    def emit_cmp_float(self, op: str, label: int, frame) -> str:
        """``fcmpl`` then a jump on its result; consumes 2 float operands.

        The float counterpart of ``emit_cmp_int``: ``fcmpl`` turns the two
        operands into -1 / 0 / 1, then the ``if<op>`` compares that against 0.
        """
        frame.pop(2)
        mapping = {
            "==": self.jvm.emitIFEQ,
            "!=": self.jvm.emitIFNE,
            "<": self.jvm.emitIFLT,
            "<=": self.jvm.emitIFLE,
            ">": self.jvm.emitIFGT,
            ">=": self.jvm.emitIFGE,
        }
        return self.jvm.emitFCMPL() + mapping[op](label)

    def emit_dup_x1(self, frame) -> str:
        """Duplicate the top value and insert the copy below the one under it."""
        frame.push()
        return self.jvm.emitDUPX1()

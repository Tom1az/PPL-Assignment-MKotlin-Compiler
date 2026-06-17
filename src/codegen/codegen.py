"""Code generation for MKotlin — Assignment 4.

Implement ``CodeGenerator`` to traverse the checked AST and emit Jasmin
assembly, producing a ``.j`` file that the bundled Jasmin assembler turns into a
``.class`` runnable on the JVM.  Use ``Emitter`` (``emitter.py``) for the
high-level instruction helpers, ``jasmin_code.py`` for raw Jasmin strings,
``utils.py`` / ``io.py`` for symbol-table support, and ``Frame`` (``frame.py``)
for label / local / stack bookkeeping.

This file is a skeleton and raises ``NotImplementedError``.
"""

from src.utils import nodes
from src.utils.visitor import BaseVisitor


class CodeGenerator(BaseVisitor):
    def __init__(self, ast, output_dir: str = "."):
        self.ast = ast
        self.output_dir = output_dir
        self.class_name = "MKotlinClass"

    def generate(self):
        raise NotImplementedError(
            "Assignment 4: implement CodeGenerator.generate to emit Jasmin code."
        )

    def visitProgram(self, ctx: nodes.Program, o):
        raise NotImplementedError(
            "Assignment 4: implement the CodeGenerator visitor methods."
        )

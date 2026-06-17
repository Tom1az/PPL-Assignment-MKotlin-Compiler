"""Testing utilities for the MKotlin compiler.

Each wrapper takes source text (or, for the checker / codegen, source text that
is first lexed, parsed and turned into an AST) and returns a string result that
the test cases compare against an expected value.

These wrappers depend on the ANTLR-generated lexer/parser, which are produced
by ``python3 run.py build``.  Imports are deferred so that this module can be
imported even before the grammar is built.
"""

import glob
import os
import subprocess

from antlr4 import InputStream, CommonTokenStream, Token

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RUNTIME_DIR = os.path.join(ROOT, "src", "runtime")
MAIN_CLASS = "MKotlinClass"

from src.grammar.lexererr import LexerError
from src.utils.error_listener import NewErrorListener, SyntaxException


def _make_lexer(source: str):
    from src.grammar.MKotlinLexer import MKotlinLexer

    return MKotlinLexer(InputStream(source))


def _make_parser(source: str):
    from src.grammar.MKotlinParser import MKotlinParser

    lexer = _make_lexer(source)
    tokens = CommonTokenStream(lexer)
    parser = MKotlinParser(tokens)
    parser.removeErrorListeners()
    parser.addErrorListener(NewErrorListener.INSTANCE)
    return parser


# --------------------------------------------------------------------------- #
#  Lexer                                                                      #
# --------------------------------------------------------------------------- #
class Tokenizer:
    """Return a comma-separated string of token lexemes, ending with ``EOF``.

    A lexical error stops tokenization and appends the error lexeme:
    ``ERROR_TOKEN`` / ``UNCLOSE_STRING`` / ``ILLEGAL_ESCAPE`` content.
    """

    @staticmethod
    def tokens(source: str) -> str:
        lexer = _make_lexer(source)
        result = []
        try:
            tok = lexer.nextToken()

            while tok.type != Token.EOF:
                result.append(tok.text)
                tok = lexer.nextToken()
            result.append("EOF")
        except LexerError as e:
            result.append(e.message)
        return ",".join(result)


# --------------------------------------------------------------------------- #
#  Parser                                                                     #
# --------------------------------------------------------------------------- #
class Parser:
    """Return ``"success"`` if the source parses, else the syntax-error text."""

    @staticmethod
    def parse(source: str) -> str:
        parser = _make_parser(source)
        try:
            parser.program()
            return "success"
        except SyntaxException as e:
            return str(e.message)


# --------------------------------------------------------------------------- #
#  AST generation                                                             #
# --------------------------------------------------------------------------- #
class ASTGenerator:
    """Return ``repr()`` of the generated AST."""

    @staticmethod
    def gen(source: str):
        from src.astgen.ast_generation import ASTGeneration

        parser = _make_parser(source)
        tree = parser.program()
        ast = ASTGeneration().visit(tree)
        return ast


# --------------------------------------------------------------------------- #
#  Static checker                                                             #
# --------------------------------------------------------------------------- #
class Checker:
    """Run the static checker; return ``str()`` of the raised error, or
    ``"Static checking passed"`` when no error is raised."""

    @staticmethod
    def check(source: str) -> str:
        from src.astgen.ast_generation import ASTGeneration
        from src.semantics.static_checker import StaticChecker
        from src.semantics.static_error import StaticError

        parser = _make_parser(source)
        tree = parser.program()
        ast = ASTGeneration().visit(tree)
        try:
            StaticChecker(ast).check()
            return "Static checking passed"
        except StaticError as e:
            return str(e)


# --------------------------------------------------------------------------- #
#  Code generation                                                            #
# --------------------------------------------------------------------------- #
class CodeGenerator:
    """Generate Jasmin from an AST, assemble with jasmin.jar, and run on the JVM."""

    def __init__(self):
        self.runtime_dir = RUNTIME_DIR

    def _cleanup_generated_files(self):
        """Remove previously generated .j and .class files (keep io.class)."""
        for j_file in glob.glob(os.path.join(self.runtime_dir, "*.j")):
            try:
                os.remove(j_file)
            except OSError:
                pass
        for class_file in glob.glob(os.path.join(self.runtime_dir, "*.class")):
            if os.path.basename(class_file) != "io.class":
                try:
                    os.remove(class_file)
                except OSError:
                    pass

    def generate_and_run(self, ast, input_data: str = "") -> str:
        """Emit code for ``ast``, assemble, run ``MAIN_CLASS``, return stdout."""
        from src.codegen.codegen import CodeGenerator as CG

        try:
            self._cleanup_generated_files()

            io_java = os.path.join(self.runtime_dir, "io.java")
            io_class = os.path.join(self.runtime_dir, "io.class")
            if os.path.exists(io_java) and not os.path.exists(io_class):
                compile_result = subprocess.run(
                    ["javac", "io.java"],
                    cwd=self.runtime_dir,
                    capture_output=True,
                    text=True,
                    timeout=10,
                )
                if compile_result.returncode != 0:
                    return f"Runtime compile error: {compile_result.stderr}"

            CG(ast, output_dir=self.runtime_dir).generate()

            j_files = glob.glob(os.path.join(self.runtime_dir, "*.j"))
            if not j_files:
                return "Error: No .j files generated"

            jasmin_jar = os.path.join(self.runtime_dir, "jasmin.jar")
            if not os.path.exists(jasmin_jar):
                return "Error: jasmin.jar not found in src/runtime/"

            for j_file in j_files:
                result = subprocess.run(
                    ["java", "-jar", "jasmin.jar", os.path.basename(j_file)],
                    cwd=self.runtime_dir,
                    capture_output=True,
                    text=True,
                    timeout=10,
                )
                if result.returncode != 0:
                    return (
                        f"Assembly error for {os.path.basename(j_file)}: "
                        f"{result.stderr}"
                    )

            main_class = os.path.join(self.runtime_dir, f"{MAIN_CLASS}.class")
            if not os.path.exists(main_class):
                return f"Error: {MAIN_CLASS}.class not found"

            result = subprocess.run(
                ["java", "-cp", self.runtime_dir, MAIN_CLASS],
                input=input_data,
                capture_output=True,
                text=True,
                timeout=10,
            )
            if result.returncode != 0:
                return f"Runtime error: {result.stderr}"

            return result.stdout.strip()

        except subprocess.TimeoutExpired:
            return "Timeout"
        except FileNotFoundError:
            return "Java not found"
        except Exception as e:
            return f"Code generation error: {str(e)}"

    @staticmethod
    def run(source: str, input_data: str = "") -> str:
        """Parse ``source``, build an AST, then assemble and run the program."""
        from src.astgen.ast_generation import ASTGeneration

        parser = _make_parser(source)
        tree = parser.program()
        ast = ASTGeneration().visit(tree)
        return CodeGenerator().generate_and_run(ast, input_data)

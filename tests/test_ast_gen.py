"""
AST generation test cases for MKotlin compiler.
TODO: Implement 100 test cases for AST generation

Compare ``repr()`` of the generated AST against the expected strings defined
in ``src/utils/nodes.py`` and ``mkotlin-ast_representation.md``.  These tests fail until ``ASTGeneration`` is
implemented and the grammar is complete.
"""

from tests.utils import ASTGenerator
from src.utils import nodes


def test_001_empty_program():
    """1. Empty program"""
    assert repr(ASTGenerator.gen("")) == "Program([])"


def test_002_simple_val():
    """2. Variable declaration with inferred type"""
    src = "fun main() {\n  val x = 10\n}"
    expected = nodes.Program([
        nodes.FuncDecl("main", [], None,
            nodes.Block([
                nodes.VarDecl("x", False, None, nodes.IntLit(10))
            ]))
    ])
    assert repr(ASTGenerator.gen(src)) == repr(expected)


def test_003_data_class():
    """3. Data class declaration"""
    src = "data class Point(x: Int, y: Int)"
    expected = nodes.Program([
        nodes.DataClassDecl("Point", [
            nodes.MemberDecl("x", nodes.IntType()),
            nodes.MemberDecl("y", nodes.IntType()),
        ])
    ])
    assert repr(ASTGenerator.gen(src)) == repr(expected)


def test_004_binary_expr():
    """4. Binary expression in return"""
    src = "fun f(x: Int, y: Int): Int {\n  return x + y\n}"
    expected = nodes.Program([
        nodes.FuncDecl("f",
            [nodes.Param("x", nodes.IntType()), nodes.Param("y", nodes.IntType())],
            nodes.IntType(),
            nodes.Block([
                nodes.Return(nodes.BinaryOp("+", nodes.Id("x"), nodes.Id("y")))
            ]))
    ])
    assert repr(ASTGenerator.gen(src)) == repr(expected)


def test_005_expr_stmt():
    """5. Expression statement (function call)"""
    src = 'fun main() {\n  printString("hi")\n}'
    expected = nodes.Program([
        nodes.FuncDecl("main", [], None,
            nodes.Block([
                nodes.ExprStmt(
                    nodes.CallExpr("printString", [nodes.StringLit("hi")])
                )
            ]))
    ])
    assert repr(ASTGenerator.gen(src)) == repr(expected)

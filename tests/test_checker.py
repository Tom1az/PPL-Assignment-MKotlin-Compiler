"""Static checker tests for MKotlin (Assignment 3).

Run with:  python3 run.py test-checker

``Checker.check`` returns the str() of the first raised StaticError, or
``"Static checking passed"``.  These fail until StaticChecker is implemented.
Add up to 100 test cases.

Error messages use the exact ``repr()`` of the offending AST node as ``ctx``
(see ``mkotlin-semantic_constraints_and_errors.md``).
"""

from tests.utils import Checker
from src.utils import nodes as n


# ========== Valid programs ==========
def test_001_valid_hello():
    """1. Valid: printString call"""
    src = 'fun main() {\n  printString("hi")\n}'
    assert Checker.check(src) == "Static checking passed"


def test_002_valid_arithmetic():
    """2. Valid: val with arithmetic and printInt"""
    src = "fun main() {\n  val x = 1 + 2\n  printInt(x)\n}"
    assert Checker.check(src) == "Static checking passed"


# ========== Eight error types (exact messages) ==========
def test_003_undeclared_identifier():
    """3. UndeclaredIdentifier"""
    src = "fun main() {\n  printInt(y)\n}"
    assert Checker.check(src) == "Undeclared Identifier: y"


def test_004_undeclared_function():
    """4. UndeclaredFunction"""
    src = "fun main() {\n  val a = compute(3)\n}"
    assert Checker.check(src) == "Undeclared Function: compute"


def test_005_undeclared_class():
    """5. UndeclaredClass in type position"""
    src = "fun main() {\n  var p: Vec\n}"
    assert Checker.check(src) == "Undeclared Class: Vec"


def test_006_redeclared_variable():
    """6. Redeclared (parameter vs body variable)"""
    src = "fun f(x: Int) {\n  val x = 5\n}"
    assert Checker.check(src) == "Redeclared Variable: x"


def test_007_type_cannot_be_inferred():
    """7. TypeCannotBeInferred"""
    src = "fun main() {\n  var a\n  var b\n  val c = a * b\n}"
    ctx = n.BinaryOp("*", n.Id("a"), n.Id("b"))
    assert Checker.check(src) == f"Type Cannot Be Inferred: {repr(ctx)}"


def test_008_reassign_val():
    """8. TypeMismatchInStatement (reassign val)"""
    src = "fun main() {\n  val x = 1\n  x = 2\n}"
    ctx = n.Assign(n.Id("x"), n.IntLit(2))
    assert Checker.check(src) == f"Type Mismatch In Statement: {repr(ctx)}"


def test_009_condition_not_boolean():
    """9. TypeMismatchInStatement (while condition)"""
    src = "fun main() {\n  var i = 0\n  while (i) {\n    i++\n  }\n}"
    ctx = n.While(
        n.Id("i"),
        n.Block([n.ExprStmt(n.PostfixOp("++", n.Id("i")))]),
    )
    assert Checker.check(src) == f"Type Mismatch In Statement: {repr(ctx)}"


def test_010_logical_needs_boolean():
    """10. TypeMismatchInExpression (&& operand types)"""
    src = "fun main() {\n  val b = true && 1\n}"
    ctx = n.BinaryOp("&&", n.BoolLit(True), n.IntLit(1))
    assert Checker.check(src) == f"Type Mismatch In Expression: {repr(ctx)}"


def test_011_break_outside_loop():
    """11. MustInLoop"""
    src = "fun main() {\n  when (1) {\n    1 -> break\n    else -> printInt(0)\n  }\n}"
    assert Checker.check(src) == f"Must In Loop: {repr(n.Break())}"

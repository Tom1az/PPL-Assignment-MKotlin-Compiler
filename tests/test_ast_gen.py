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


# --------------------------------------------------------------------------- #
#  Supplemental tests 006–100                                                 #
# --------------------------------------------------------------------------- #


def test_006_leading_trailing_newlines():
    """Leading/trailing newlines around empty decls"""
    assert repr(ASTGenerator.gen("\n\n")) == "Program([])"


def test_007_empty_function():
    """Empty function body"""
    src = "fun main() {}"
    expected = nodes.Program([
        nodes.FuncDecl("main", [], None, nodes.Block([]))
    ])
    assert repr(ASTGenerator.gen(src)) == repr(expected)


def test_008_function_unit_return():
    """Explicit Unit return type"""
    src = "fun main(): Unit {}"
    expected = nodes.Program([
        nodes.FuncDecl("main", [], nodes.UnitType(), nodes.Block([]))
    ])
    assert repr(ASTGenerator.gen(src)) == repr(expected)


def test_009_function_all_param_types():
    """Parameters of every built-in type"""
    src = "fun f(a: Int, b: Float, c: Boolean, d: String): Unit {}"
    expected = nodes.Program([
        nodes.FuncDecl("f",
            [nodes.Param("a", nodes.IntType()),
             nodes.Param("b", nodes.FloatType()),
             nodes.Param("c", nodes.BoolType()),
             nodes.Param("d", nodes.StringType())],
            nodes.UnitType(),
            nodes.Block([]))
    ])
    assert repr(ASTGenerator.gen(src)) == repr(expected)


def test_010_function_class_param():
    """Parameter with data-class type"""
    src = "fun f(p: Point) {}"
    expected = nodes.Program([
        nodes.FuncDecl("f",
            [nodes.Param("p", nodes.ClassType("Point"))],
            None,
            nodes.Block([]))
    ])
    assert repr(ASTGenerator.gen(src)) == repr(expected)


def test_011_multiple_functions_sep_newline():
    """Two functions separated by newline"""
    src = "fun a() {}\nfun b() {}"
    expected = nodes.Program([
        nodes.FuncDecl("a", [], None, nodes.Block([])),
        nodes.FuncDecl("b", [], None, nodes.Block([])),
    ])
    assert repr(ASTGenerator.gen(src)) == repr(expected)


def test_012_multiple_functions_sep_semi():
    """Two functions separated by semicolon"""
    src = "fun a() {}; fun b() {}"
    expected = nodes.Program([
        nodes.FuncDecl("a", [], None, nodes.Block([])),
        nodes.FuncDecl("b", [], None, nodes.Block([])),
    ])
    assert repr(ASTGenerator.gen(src)) == repr(expected)


def test_013_trailing_sep_after_decl():
    """Trailing separator after last declaration"""
    src = "fun main() {}\n"
    expected = nodes.Program([
        nodes.FuncDecl("main", [], None, nodes.Block([]))
    ])
    assert repr(ASTGenerator.gen(src)) == repr(expected)


def test_014_data_class_empty():
    """Data class with zero members"""
    src = "data class Empty()"
    expected = nodes.Program([
        nodes.DataClassDecl("Empty", [])
    ])
    assert repr(ASTGenerator.gen(src)) == repr(expected)


def test_015_data_class_all_types():
    """Data class members of all primitive types"""
    src = "data class Person(name: String, age: Int, height: Float, active: Boolean)"
    expected = nodes.Program([
        nodes.DataClassDecl("Person", [
            nodes.MemberDecl("name", nodes.StringType()),
            nodes.MemberDecl("age", nodes.IntType()),
            nodes.MemberDecl("height", nodes.FloatType()),
            nodes.MemberDecl("active", nodes.BoolType()),
        ])
    ])
    assert repr(ASTGenerator.gen(src)) == repr(expected)


def test_016_data_class_nested_type():
    """Member typed as another data class"""
    src = "data class Line(a: Point, b: Point)"
    expected = nodes.Program([
        nodes.DataClassDecl("Line", [
            nodes.MemberDecl("a", nodes.ClassType("Point")),
            nodes.MemberDecl("b", nodes.ClassType("Point")),
        ])
    ])
    assert repr(ASTGenerator.gen(src)) == repr(expected)


def test_017_data_class_then_function():
    """Data class followed by function"""
    src = "data class P(x: Int)\nfun main() {}"
    expected = nodes.Program([
        nodes.DataClassDecl("P", [nodes.MemberDecl("x", nodes.IntType())]),
        nodes.FuncDecl("main", [], None, nodes.Block([])),
    ])
    assert repr(ASTGenerator.gen(src)) == repr(expected)


def test_018_data_class_multiline_members():
    """Members split across newlines after commas"""
    src = "data class P(x: Int,\ny: Int)"
    expected = nodes.Program([
        nodes.DataClassDecl("P", [
            nodes.MemberDecl("x", nodes.IntType()),
            nodes.MemberDecl("y", nodes.IntType()),
        ])
    ])
    assert repr(ASTGenerator.gen(src)) == repr(expected)


def test_019_single_member_data_class():
    """Single-member data class"""
    src = "data class Box(value: Int)"
    expected = nodes.Program([
        nodes.DataClassDecl("Box", [nodes.MemberDecl("value", nodes.IntType())])
    ])
    assert repr(ASTGenerator.gen(src)) == repr(expected)


def test_020_constructor_call():
    """Constructor call as initializer"""
    src = "fun main() {\n  val p = Point(10, 20)\n}"
    expected = nodes.Program([
        nodes.FuncDecl("main", [], None,
            nodes.Block([
                nodes.VarDecl("p", False, None,
                    nodes.CallExpr("Point", [nodes.IntLit(10), nodes.IntLit(20)]))
            ]))
    ])
    assert repr(ASTGenerator.gen(src)) == repr(expected)


def test_021_nested_constructor():
    """Nested constructor calls"""
    src = "fun main() {\n  val l = Line(Point(1, 2), Point(3, 4))\n}"
    expected = nodes.Program([
        nodes.FuncDecl("main", [], None,
            nodes.Block([
                nodes.VarDecl("l", False, None,
                    nodes.CallExpr("Line", [
                        nodes.CallExpr("Point", [nodes.IntLit(1), nodes.IntLit(2)]),
                        nodes.CallExpr("Point", [nodes.IntLit(3), nodes.IntLit(4)]),
                    ]))
            ]))
    ])
    assert repr(ASTGenerator.gen(src)) == repr(expected)


def test_022_member_access():
    """Simple member access"""
    src = "fun main() {\n  val x = p.x\n}"
    expected = nodes.Program([
        nodes.FuncDecl("main", [], None,
            nodes.Block([
                nodes.VarDecl("x", False, None, nodes.MemberAccess(nodes.Id("p"), "x"))
            ]))
    ])
    assert repr(ASTGenerator.gen(src)) == repr(expected)


def test_023_val_explicit_int():
    """val with explicit Int type"""
    src = "fun main() {\n  val x: Int = 10\n}"
    expected = nodes.Program([
        nodes.FuncDecl("main", [], None,
            nodes.Block([
                nodes.VarDecl("x", False, nodes.IntType(), nodes.IntLit(10))
            ]))
    ])
    assert repr(ASTGenerator.gen(src)) == repr(expected)


def test_024_var_inferred():
    """var with inferred type"""
    src = "fun main() {\n  var count = 0\n}"
    expected = nodes.Program([
        nodes.FuncDecl("main", [], None,
            nodes.Block([
                nodes.VarDecl("count", True, None, nodes.IntLit(0))
            ]))
    ])
    assert repr(ASTGenerator.gen(src)) == repr(expected)


def test_025_var_explicit_with_init():
    """var with explicit type and initializer"""
    src = "fun main() {\n  var x: Float = 3.14\n}"
    expected = nodes.Program([
        nodes.FuncDecl("main", [], None,
            nodes.Block([
                nodes.VarDecl("x", True, nodes.FloatType(), nodes.FloatLit(3.14))
            ]))
    ])
    assert repr(ASTGenerator.gen(src)) == repr(expected)


def test_026_var_explicit_no_init():
    """var with type, no initializer"""
    src = "fun main() {\n  var total: Float\n}"
    expected = nodes.Program([
        nodes.FuncDecl("main", [], None,
            nodes.Block([
                nodes.VarDecl("total", True, nodes.FloatType(), None)
            ]))
    ])
    assert repr(ASTGenerator.gen(src)) == repr(expected)


def test_027_var_bare():
    """var with neither type nor initializer"""
    src = "fun main() {\n  var n\n}"
    expected = nodes.Program([
        nodes.FuncDecl("main", [], None,
            nodes.Block([
                nodes.VarDecl("n", True, None, None)
            ]))
    ])
    assert repr(ASTGenerator.gen(src)) == repr(expected)


def test_028_val_float():
    """val initialized with float"""
    src = "fun main() {\n  val y = 3.14\n}"
    expected = nodes.Program([
        nodes.FuncDecl("main", [], None,
            nodes.Block([
                nodes.VarDecl("y", False, None, nodes.FloatLit(3.14))
            ]))
    ])
    assert repr(ASTGenerator.gen(src)) == repr(expected)


def test_029_val_bool():
    """val initialized with boolean"""
    src = "fun main() {\n  val ok = true\n}"
    expected = nodes.Program([
        nodes.FuncDecl("main", [], None,
            nodes.Block([
                nodes.VarDecl("ok", False, None, nodes.BoolLit(True))
            ]))
    ])
    assert repr(ASTGenerator.gen(src)) == repr(expected)


def test_030_val_string():
    """val initialized with string"""
    src = 'fun main() {\n  val msg = "hello"\n}'
    expected = nodes.Program([
        nodes.FuncDecl("main", [], None,
            nodes.Block([
                nodes.VarDecl("msg", False, None, nodes.StringLit("hello"))
            ]))
    ])
    assert repr(ASTGenerator.gen(src)) == repr(expected)


def test_031_val_explicit_all_types():
    """Explicit typed vals for each primitive"""
    src = """fun main() {
  val a: Int = 1
  val b: Float = 2.0
  val c: Boolean = false
  val d: String = "s"
}"""
    expected = nodes.Program([
        nodes.FuncDecl("main", [], None,
            nodes.Block([
                nodes.VarDecl("a", False, nodes.IntType(), nodes.IntLit(1)),
                nodes.VarDecl("b", False, nodes.FloatType(), nodes.FloatLit(2.0)),
                nodes.VarDecl("c", False, nodes.BoolType(), nodes.BoolLit(False)),
                nodes.VarDecl("d", False, nodes.StringType(), nodes.StringLit("s")),
            ]))
    ])
    assert repr(ASTGenerator.gen(src)) == repr(expected)


def test_032_val_class_type():
    """val with ClassType annotation"""
    src = "fun main() {\n  val p: Point = Point(0, 0)\n}"
    expected = nodes.Program([
        nodes.FuncDecl("main", [], None,
            nodes.Block([
                nodes.VarDecl("p", False, nodes.ClassType("Point"),
                    nodes.CallExpr("Point", [nodes.IntLit(0), nodes.IntLit(0)]))
            ]))
    ])
    assert repr(ASTGenerator.gen(src)) == repr(expected)


def test_033_two_vals_semicolon():
    """Two declarations on one line with semicolon"""
    src = "fun main() {\n  val x = 10; val y = 20\n}"
    expected = nodes.Program([
        nodes.FuncDecl("main", [], None,
            nodes.Block([
                nodes.VarDecl("x", False, None, nodes.IntLit(10)),
                nodes.VarDecl("y", False, None, nodes.IntLit(20)),
            ]))
    ])
    assert repr(ASTGenerator.gen(src)) == repr(expected)


def test_034_trailing_semi_in_block():
    """Trailing semicolon after last statement"""
    src = "fun main() {\n  val x = 1;\n}"
    expected = nodes.Program([
        nodes.FuncDecl("main", [], None,
            nodes.Block([
                nodes.VarDecl("x", False, None, nodes.IntLit(1))
            ]))
    ])
    assert repr(ASTGenerator.gen(src)) == repr(expected)


def test_035_double_sep():
    """Multiple separators between statements"""
    src = "fun main() {\n  val x = 1 ;; val y = 2\n}"
    expected = nodes.Program([
        nodes.FuncDecl("main", [], None,
            nodes.Block([
                nodes.VarDecl("x", False, None, nodes.IntLit(1)),
                nodes.VarDecl("y", False, None, nodes.IntLit(2)),
            ]))
    ])
    assert repr(ASTGenerator.gen(src)) == repr(expected)


def test_036_comments_ignored():
    """Line and block comments do not appear in AST"""
    src = "fun main() {\n  /* c */ val x = 5 // line\n}"
    expected = nodes.Program([
        nodes.FuncDecl("main", [], None,
            nodes.Block([
                nodes.VarDecl("x", False, None, nodes.IntLit(5))
            ]))
    ])
    assert repr(ASTGenerator.gen(src)) == repr(expected)


def test_037_int_zero():
    """Integer literal 0"""
    src = "fun main() {\n  val x = 0\n}"
    expected = nodes.Program([
        nodes.FuncDecl("main", [], None,
            nodes.Block([
                nodes.VarDecl("x", False, None, nodes.IntLit(0))
            ]))
    ])
    assert repr(ASTGenerator.gen(src)) == repr(expected)


def test_038_int_underscore():
    """Integer with underscores"""
    src = "fun main() {\n  val x = 1_000_000\n}"
    expected = nodes.Program([
        nodes.FuncDecl("main", [], None,
            nodes.Block([
                nodes.VarDecl("x", False, None, nodes.IntLit(1000000))
            ]))
    ])
    assert repr(ASTGenerator.gen(src)) == repr(expected)


def test_039_float_trailing_dot():
    """Float literal 1."""
    src = "fun main() {\n  val x = 1.\n}"
    expected = nodes.Program([
        nodes.FuncDecl("main", [], None,
            nodes.Block([
                nodes.VarDecl("x", False, None, nodes.FloatLit(1.0))
            ]))
    ])
    assert repr(ASTGenerator.gen(src)) == repr(expected)


def test_040_float_leading_dot():
    """Float literal .5"""
    src = "fun main() {\n  val x = .5\n}"
    expected = nodes.Program([
        nodes.FuncDecl("main", [], None,
            nodes.Block([
                nodes.VarDecl("x", False, None, nodes.FloatLit(0.5))
            ]))
    ])
    assert repr(ASTGenerator.gen(src)) == repr(expected)


def test_041_float_exponent():
    """Float with exponent"""
    src = "fun main() {\n  val x = 1.23e4\n}"
    expected = nodes.Program([
        nodes.FuncDecl("main", [], None,
            nodes.Block([
                nodes.VarDecl("x", False, None, nodes.FloatLit(12300.0))
            ]))
    ])
    assert repr(ASTGenerator.gen(src)) == repr(expected)


def test_042_float_suffix_f():
    """Float with f suffix"""
    src = "fun main() {\n  val x = 3.14f\n}"
    expected = nodes.Program([
        nodes.FuncDecl("main", [], None,
            nodes.Block([
                nodes.VarDecl("x", False, None, nodes.FloatLit(3.14))
            ]))
    ])
    assert repr(ASTGenerator.gen(src)) == repr(expected)


def test_043_float_exp_no_dot():
    """Float like 1e4"""
    src = "fun main() {\n  val x = 1e4\n}"
    expected = nodes.Program([
        nodes.FuncDecl("main", [], None,
            nodes.Block([
                nodes.VarDecl("x", False, None, nodes.FloatLit(10000.0))
            ]))
    ])
    assert repr(ASTGenerator.gen(src)) == repr(expected)


def test_044_bool_false():
    """Boolean false literal"""
    src = "fun main() {\n  val x = false\n}"
    expected = nodes.Program([
        nodes.FuncDecl("main", [], None,
            nodes.Block([
                nodes.VarDecl("x", False, None, nodes.BoolLit(False))
            ]))
    ])
    assert repr(ASTGenerator.gen(src)) == repr(expected)


def test_045_string_escapes():
    """String with escape sequences (lexeme after quote strip)"""
    src = 'fun main() {\n  val s = "a\\nb\\t\\"c"\n}'
    expected = nodes.Program([
        nodes.FuncDecl("main", [], None,
            nodes.Block([
                nodes.VarDecl("s", False, None, nodes.StringLit('a\\nb\\t\\"c'))
            ]))
    ])
    assert repr(ASTGenerator.gen(src)) == repr(expected)


def test_046_empty_string():
    """Empty string literal"""
    src = 'fun main() {\n  val s = ""\n}'
    expected = nodes.Program([
        nodes.FuncDecl("main", [], None,
            nodes.Block([
                nodes.VarDecl("s", False, None, nodes.StringLit(""))
            ]))
    ])
    assert repr(ASTGenerator.gen(src)) == repr(expected)


def test_047_parenthesized_unwrap():
    """Parentheses are unwrapped"""
    src = "fun main() {\n  val x = (1 + 2)\n}"
    expected = nodes.Program([
        nodes.FuncDecl("main", [], None,
            nodes.Block([
                nodes.VarDecl("x", False, None,
                    nodes.BinaryOp("+", nodes.IntLit(1), nodes.IntLit(2)))
            ]))
    ])
    assert repr(ASTGenerator.gen(src)) == repr(expected)


def test_048_nested_parens():
    """Nested parentheses unwrapped"""
    src = "fun main() {\n  val x = ((42))\n}"
    expected = nodes.Program([
        nodes.FuncDecl("main", [], None,
            nodes.Block([
                nodes.VarDecl("x", False, None, nodes.IntLit(42))
            ]))
    ])
    assert repr(ASTGenerator.gen(src)) == repr(expected)


def test_049_id_expr():
    """Bare identifier expression"""
    src = "fun main() {\n  val y = x\n}"
    expected = nodes.Program([
        nodes.FuncDecl("main", [], None,
            nodes.Block([
                nodes.VarDecl("y", False, None, nodes.Id("x"))
            ]))
    ])
    assert repr(ASTGenerator.gen(src)) == repr(expected)


def test_050_call_no_args():
    """Function call with no arguments"""
    src = "fun main() {\n  val x = readInt()\n}"
    expected = nodes.Program([
        nodes.FuncDecl("main", [], None,
            nodes.Block([
                nodes.VarDecl("x", False, None, nodes.CallExpr("readInt", []))
            ]))
    ])
    assert repr(ASTGenerator.gen(src)) == repr(expected)


def test_051_call_multi_args():
    """Function call with multiple arguments"""
    src = "fun main() {\n  val s = add(1, 2)\n}"
    expected = nodes.Program([
        nodes.FuncDecl("main", [], None,
            nodes.Block([
                nodes.VarDecl("s", False, None,
                    nodes.CallExpr("add", [nodes.IntLit(1), nodes.IntLit(2)]))
            ]))
    ])
    assert repr(ASTGenerator.gen(src)) == repr(expected)


def test_052_arithmetic_ops():
    """Binary + - * / %"""
    src = "fun main() {\n  val a = 1 + 2\n  val b = 3 - 4\n  val c = 5 * 6\n  val d = 7 / 8\n  val e = 9 % 10\n}"
    expected = nodes.Program([
        nodes.FuncDecl("main", [], None,
            nodes.Block([
                nodes.VarDecl("a", False, None, nodes.BinaryOp("+", nodes.IntLit(1), nodes.IntLit(2))),
                nodes.VarDecl("b", False, None, nodes.BinaryOp("-", nodes.IntLit(3), nodes.IntLit(4))),
                nodes.VarDecl("c", False, None, nodes.BinaryOp("*", nodes.IntLit(5), nodes.IntLit(6))),
                nodes.VarDecl("d", False, None, nodes.BinaryOp("/", nodes.IntLit(7), nodes.IntLit(8))),
                nodes.VarDecl("e", False, None, nodes.BinaryOp("%", nodes.IntLit(9), nodes.IntLit(10))),
            ]))
    ])
    assert repr(ASTGenerator.gen(src)) == repr(expected)


def test_053_relational_ops():
    """Ordering operators"""
    src = "fun main() {\n  val a = 1 < 2\n  val b = 3 <= 4\n  val c = 5 > 6\n  val d = 7 >= 8\n}"
    expected = nodes.Program([
        nodes.FuncDecl("main", [], None,
            nodes.Block([
                nodes.VarDecl("a", False, None, nodes.BinaryOp("<", nodes.IntLit(1), nodes.IntLit(2))),
                nodes.VarDecl("b", False, None, nodes.BinaryOp("<=", nodes.IntLit(3), nodes.IntLit(4))),
                nodes.VarDecl("c", False, None, nodes.BinaryOp(">", nodes.IntLit(5), nodes.IntLit(6))),
                nodes.VarDecl("d", False, None, nodes.BinaryOp(">=", nodes.IntLit(7), nodes.IntLit(8))),
            ]))
    ])
    assert repr(ASTGenerator.gen(src)) == repr(expected)


def test_054_equality_ops():
    """Equality operators"""
    src = "fun main() {\n  val a = 1 == 2\n  val b = true != false\n}"
    expected = nodes.Program([
        nodes.FuncDecl("main", [], None,
            nodes.Block([
                nodes.VarDecl("a", False, None, nodes.BinaryOp("==", nodes.IntLit(1), nodes.IntLit(2))),
                nodes.VarDecl("b", False, None, nodes.BinaryOp("!=", nodes.BoolLit(True), nodes.BoolLit(False))),
            ]))
    ])
    assert repr(ASTGenerator.gen(src)) == repr(expected)


def test_055_logical_ops():
    """Logical && || !"""
    src = "fun main() {\n  val a = true && false\n  val b = true || false\n  val c = !true\n}"
    expected = nodes.Program([
        nodes.FuncDecl("main", [], None,
            nodes.Block([
                nodes.VarDecl("a", False, None, nodes.BinaryOp("&&", nodes.BoolLit(True), nodes.BoolLit(False))),
                nodes.VarDecl("b", False, None, nodes.BinaryOp("||", nodes.BoolLit(True), nodes.BoolLit(False))),
                nodes.VarDecl("c", False, None, nodes.UnaryOp("!", nodes.BoolLit(True))),
            ]))
    ])
    assert repr(ASTGenerator.gen(src)) == repr(expected)


def test_056_unary_plus_minus():
    """Unary + and -"""
    src = "fun main() {\n  val a = -1\n  val b = +2\n}"
    expected = nodes.Program([
        nodes.FuncDecl("main", [], None,
            nodes.Block([
                nodes.VarDecl("a", False, None, nodes.UnaryOp("-", nodes.IntLit(1))),
                nodes.VarDecl("b", False, None, nodes.UnaryOp("+", nodes.IntLit(2))),
            ]))
    ])
    assert repr(ASTGenerator.gen(src)) == repr(expected)


def test_057_prefix_inc_dec():
    """Prefix ++ and --"""
    src = "fun main() {\n  val a = ++x\n  val b = --y\n}"
    expected = nodes.Program([
        nodes.FuncDecl("main", [], None,
            nodes.Block([
                nodes.VarDecl("a", False, None, nodes.UnaryOp("++", nodes.Id("x"))),
                nodes.VarDecl("b", False, None, nodes.UnaryOp("--", nodes.Id("y"))),
            ]))
    ])
    assert repr(ASTGenerator.gen(src)) == repr(expected)


def test_058_postfix_inc_dec():
    """Postfix ++ and --"""
    src = "fun main() {\n  val a = x++\n  val b = y--\n}"
    expected = nodes.Program([
        nodes.FuncDecl("main", [], None,
            nodes.Block([
                nodes.VarDecl("a", False, None, nodes.PostfixOp("++", nodes.Id("x"))),
                nodes.VarDecl("b", False, None, nodes.PostfixOp("--", nodes.Id("y"))),
            ]))
    ])
    assert repr(ASTGenerator.gen(src)) == repr(expected)


def test_059_mul_before_add():
    """Precedence: * binds tighter than +"""
    src = "fun main() {\n  val x = 1 + 2 * 3\n}"
    expected = nodes.Program([
        nodes.FuncDecl("main", [], None,
            nodes.Block([
                nodes.VarDecl("x", False, None,
                    nodes.BinaryOp("+", nodes.IntLit(1),
                        nodes.BinaryOp("*", nodes.IntLit(2), nodes.IntLit(3))))
            ]))
    ])
    assert repr(ASTGenerator.gen(src)) == repr(expected)


def test_060_add_left_assoc():
    """Left associativity of +"""
    src = "fun main() {\n  val x = 1 + 2 + 3\n}"
    expected = nodes.Program([
        nodes.FuncDecl("main", [], None,
            nodes.Block([
                nodes.VarDecl("x", False, None,
                    nodes.BinaryOp("+",
                        nodes.BinaryOp("+", nodes.IntLit(1), nodes.IntLit(2)),
                        nodes.IntLit(3)))
            ]))
    ])
    assert repr(ASTGenerator.gen(src)) == repr(expected)


def test_061_and_before_or():
    """Precedence: && binds tighter than ||"""
    src = "fun main() {\n  val x = a || b && c\n}"
    expected = nodes.Program([
        nodes.FuncDecl("main", [], None,
            nodes.Block([
                nodes.VarDecl("x", False, None,
                    nodes.BinaryOp("||", nodes.Id("a"),
                        nodes.BinaryOp("&&", nodes.Id("b"), nodes.Id("c"))))
            ]))
    ])
    assert repr(ASTGenerator.gen(src)) == repr(expected)


def test_062_rel_before_eq():
    """Precedence: < before =="""
    src = "fun main() {\n  val x = a < b == c < d\n}"
    expected = nodes.Program([
        nodes.FuncDecl("main", [], None,
            nodes.Block([
                nodes.VarDecl("x", False, None,
                    nodes.BinaryOp("==",
                        nodes.BinaryOp("<", nodes.Id("a"), nodes.Id("b")),
                        nodes.BinaryOp("<", nodes.Id("c"), nodes.Id("d"))))
            ]))
    ])
    assert repr(ASTGenerator.gen(src)) == repr(expected)


def test_063_unary_before_mul():
    """Unary binds tighter than *"""
    src = "fun main() {\n  val x = -a * b\n}"
    expected = nodes.Program([
        nodes.FuncDecl("main", [], None,
            nodes.Block([
                nodes.VarDecl("x", False, None,
                    nodes.BinaryOp("*", nodes.UnaryOp("-", nodes.Id("a")), nodes.Id("b")))
            ]))
    ])
    assert repr(ASTGenerator.gen(src)) == repr(expected)


def test_064_member_before_call_chain():
    """getPoint().x → MemberAccess(CallExpr(...), x)"""
    src = "fun main() {\n  val x = getPoint().x\n}"
    expected = nodes.Program([
        nodes.FuncDecl("main", [], None,
            nodes.Block([
                nodes.VarDecl("x", False, None,
                    nodes.MemberAccess(nodes.CallExpr("getPoint", []), "x"))
            ]))
    ])
    assert repr(ASTGenerator.gen(src)) == repr(expected)


def test_065_postfix_member():
    """a++.x → MemberAccess(PostfixOp(...), x)"""
    src = "fun main() {\n  val x = a++.x\n}"
    expected = nodes.Program([
        nodes.FuncDecl("main", [], None,
            nodes.Block([
                nodes.VarDecl("x", False, None,
                    nodes.MemberAccess(nodes.PostfixOp("++", nodes.Id("a")), "x"))
            ]))
    ])
    assert repr(ASTGenerator.gen(src)) == repr(expected)


def test_066_member_then_postfix():
    """x.a++ → PostfixOp on MemberAccess"""
    src = "fun main() {\n  val y = x.a++\n}"
    expected = nodes.Program([
        nodes.FuncDecl("main", [], None,
            nodes.Block([
                nodes.VarDecl("y", False, None,
                    nodes.PostfixOp("++", nodes.MemberAccess(nodes.Id("x"), "a")))
            ]))
    ])
    assert repr(ASTGenerator.gen(src)) == repr(expected)


def test_067_assign_stmt():
    """Assignment statement → Assign"""
    src = "fun main() {\n  x = 5\n}"
    expected = nodes.Program([
        nodes.FuncDecl("main", [], None,
            nodes.Block([
                nodes.Assign(nodes.Id("x"), nodes.IntLit(5))
            ]))
    ])
    assert repr(ASTGenerator.gen(src)) == repr(expected)


def test_068_member_assign():
    """Member assignment"""
    src = "fun main() {\n  p.x = 99\n}"
    expected = nodes.Program([
        nodes.FuncDecl("main", [], None,
            nodes.Block([
                nodes.Assign(nodes.MemberAccess(nodes.Id("p"), "x"), nodes.IntLit(99))
            ]))
    ])
    assert repr(ASTGenerator.gen(src)) == repr(expected)


def test_069_chained_assign():
    """Chained assignment right-associative"""
    src = "fun main() {\n  x = y = z = 10\n}"
    expected = nodes.Program([
        nodes.FuncDecl("main", [], None,
            nodes.Block([
                nodes.Assign(nodes.Id("x"),
                    nodes.AssignExpr(nodes.Id("y"),
                        nodes.AssignExpr(nodes.Id("z"), nodes.IntLit(10))))
            ]))
    ])
    assert repr(ASTGenerator.gen(src)) == repr(expected)


def test_070_assign_in_expr():
    """Assignment used as expression (RHS of val)"""
    src = "fun main() {\n  val a = (x = 1)\n}"
    expected = nodes.Program([
        nodes.FuncDecl("main", [], None,
            nodes.Block([
                nodes.VarDecl("a", False, None,
                    nodes.AssignExpr(nodes.Id("x"), nodes.IntLit(1)))
            ]))
    ])
    assert repr(ASTGenerator.gen(src)) == repr(expected)


def test_071_inc_as_stmt():
    """Postfix increment as expression statement"""
    src = "fun main() {\n  x++\n}"
    expected = nodes.Program([
        nodes.FuncDecl("main", [], None,
            nodes.Block([
                nodes.ExprStmt(nodes.PostfixOp("++", nodes.Id("x")))
            ]))
    ])
    assert repr(ASTGenerator.gen(src)) == repr(expected)


def test_072_prefix_inc_as_stmt():
    """Prefix increment as expression statement"""
    src = "fun main() {\n  ++x\n}"
    expected = nodes.Program([
        nodes.FuncDecl("main", [], None,
            nodes.Block([
                nodes.ExprStmt(nodes.UnaryOp("++", nodes.Id("x")))
            ]))
    ])
    assert repr(ASTGenerator.gen(src)) == repr(expected)


def test_073_print_builtins():
    """Built-in print* calls"""
    src = """fun main() {
  printInt(1)
  printFloat(2.0)
  printBool(true)
  printString("s")
}"""
    expected = nodes.Program([
        nodes.FuncDecl("main", [], None,
            nodes.Block([
                nodes.ExprStmt(nodes.CallExpr("printInt", [nodes.IntLit(1)])),
                nodes.ExprStmt(nodes.CallExpr("printFloat", [nodes.FloatLit(2.0)])),
                nodes.ExprStmt(nodes.CallExpr("printBool", [nodes.BoolLit(True)])),
                nodes.ExprStmt(nodes.CallExpr("printString", [nodes.StringLit("s")])),
            ]))
    ])
    assert repr(ASTGenerator.gen(src)) == repr(expected)


def test_074_read_builtins():
    """Built-in read* calls"""
    src = """fun main() {
  val a = readInt()
  val b = readFloat()
  val c = readBool()
  val d = readString()
}"""
    expected = nodes.Program([
        nodes.FuncDecl("main", [], None,
            nodes.Block([
                nodes.VarDecl("a", False, None, nodes.CallExpr("readInt", [])),
                nodes.VarDecl("b", False, None, nodes.CallExpr("readFloat", [])),
                nodes.VarDecl("c", False, None, nodes.CallExpr("readBool", [])),
                nodes.VarDecl("d", False, None, nodes.CallExpr("readString", [])),
            ]))
    ])
    assert repr(ASTGenerator.gen(src)) == repr(expected)


def test_075_assign_expr_with_binop():
    """Assignment of binary expression"""
    src = "fun main() {\n  x = x + 1\n}"
    expected = nodes.Program([
        nodes.FuncDecl("main", [], None,
            nodes.Block([
                nodes.Assign(nodes.Id("x"),
                    nodes.BinaryOp("+", nodes.Id("x"), nodes.IntLit(1)))
            ]))
    ])
    assert repr(ASTGenerator.gen(src)) == repr(expected)


def test_076_if_then():
    """If without else"""
    src = "fun main() {\n  if (flag) printInt(1)\n}"
    expected = nodes.Program([
        nodes.FuncDecl("main", [], None,
            nodes.Block([
                nodes.If(nodes.Id("flag"),
                    nodes.ExprStmt(nodes.CallExpr("printInt", [nodes.IntLit(1)])),
                    None)
            ]))
    ])
    assert repr(ASTGenerator.gen(src)) == repr(expected)


def test_077_if_else():
    """If with else"""
    src = "fun main() {\n  if (flag) {\n    printInt(1)\n  } else {\n    printInt(0)\n  }\n}"
    expected = nodes.Program([
        nodes.FuncDecl("main", [], None,
            nodes.Block([
                nodes.If(nodes.Id("flag"),
                    nodes.Block([nodes.ExprStmt(nodes.CallExpr("printInt", [nodes.IntLit(1)]))]),
                    nodes.Block([nodes.ExprStmt(nodes.CallExpr("printInt", [nodes.IntLit(0)]))]))
            ]))
    ])
    assert repr(ASTGenerator.gen(src)) == repr(expected)


def test_078_nested_if_else_bind():
    """else binds to nearest if"""
    src = "fun main() {\n  if (a) if (b) s1 else s2\n}"
    expected = nodes.Program([
        nodes.FuncDecl("main", [], None,
            nodes.Block([
                nodes.If(nodes.Id("a"),
                    nodes.If(nodes.Id("b"),
                        nodes.ExprStmt(nodes.Id("s1")),
                        nodes.ExprStmt(nodes.Id("s2"))),
                    None)
            ]))
    ])
    assert repr(ASTGenerator.gen(src)) == repr(expected)


def test_079_if_expr():
    """If expression"""
    src = "fun main() {\n  val m = if (a > b) a else b\n}"
    expected = nodes.Program([
        nodes.FuncDecl("main", [], None,
            nodes.Block([
                nodes.VarDecl("m", False, None,
                    nodes.IfExpr(
                        nodes.BinaryOp(">", nodes.Id("a"), nodes.Id("b")),
                        nodes.Id("a"), nodes.Id("b")))
            ]))
    ])
    assert repr(ASTGenerator.gen(src)) == repr(expected)


def test_080_while():
    """While loop"""
    src = "fun main() {\n  while (i < 10) {\n    i++\n  }\n}"
    expected = nodes.Program([
        nodes.FuncDecl("main", [], None,
            nodes.Block([
                nodes.While(
                    nodes.BinaryOp("<", nodes.Id("i"), nodes.IntLit(10)),
                    nodes.Block([nodes.ExprStmt(nodes.PostfixOp("++", nodes.Id("i")))]))
            ]))
    ])
    assert repr(ASTGenerator.gen(src)) == repr(expected)


def test_081_for_range():
    """For loop over range"""
    src = "fun main() {\n  for (i in 0..9) {\n    printInt(i)\n  }\n}"
    expected = nodes.Program([
        nodes.FuncDecl("main", [], None,
            nodes.Block([
                nodes.For("i", nodes.IntLit(0), nodes.IntLit(9),
                    nodes.Block([nodes.ExprStmt(nodes.CallExpr("printInt", [nodes.Id("i")]))]))
            ]))
    ])
    assert repr(ASTGenerator.gen(src)) == repr(expected)


def test_082_for_expr_bounds():
    """For with expression bounds"""
    src = "fun main() {\n  for (j in a..b) printInt(j)\n}"
    expected = nodes.Program([
        nodes.FuncDecl("main", [], None,
            nodes.Block([
                nodes.For("j", nodes.Id("a"), nodes.Id("b"),
                    nodes.ExprStmt(nodes.CallExpr("printInt", [nodes.Id("j")])))
            ]))
    ])
    assert repr(ASTGenerator.gen(src)) == repr(expected)


def test_083_break_continue():
    """break and continue in while"""
    src = "fun main() {\n  while (true) {\n    break\n    continue\n  }\n}"
    expected = nodes.Program([
        nodes.FuncDecl("main", [], None,
            nodes.Block([
                nodes.While(nodes.BoolLit(True),
                    nodes.Block([nodes.Break(), nodes.Continue()]))
            ]))
    ])
    assert repr(ASTGenerator.gen(src)) == repr(expected)


def test_084_return_value():
    """return with expression"""
    src = "fun f(): Int {\n  return 42\n}"
    expected = nodes.Program([
        nodes.FuncDecl("f", [], nodes.IntType(),
            nodes.Block([
                nodes.Return(nodes.IntLit(42))
            ]))
    ])
    assert repr(ASTGenerator.gen(src)) == repr(expected)


def test_085_return_bare():
    """Bare return"""
    src = "fun main() {\n  return\n}"
    expected = nodes.Program([
        nodes.FuncDecl("main", [], None,
            nodes.Block([
                nodes.Return(None)
            ]))
    ])
    assert repr(ASTGenerator.gen(src)) == repr(expected)


def test_086_when_subject_stmt():
    """when subject form as statement"""
    src = """fun main() {
  when (day) {
    1 -> printInt(1)
    else -> printInt(0)
  }
}"""
    expected = nodes.Program([
        nodes.FuncDecl("main", [], None,
            nodes.Block([
                nodes.When(nodes.Id("day"), [
                    nodes.WhenBranch([nodes.IntLit(1)],
                        nodes.ExprStmt(nodes.CallExpr("printInt", [nodes.IntLit(1)]))),
                    nodes.WhenBranch(None,
                        nodes.ExprStmt(nodes.CallExpr("printInt", [nodes.IntLit(0)]))),
                ])
            ]))
    ])
    assert repr(ASTGenerator.gen(src)) == repr(expected)


def test_087_when_multi_labels():
    """Subject branch with comma-separated labels"""
    src = """fun main() {
  when (day) {
    2, 3 -> printInt(2)
  }
}"""
    expected = nodes.Program([
        nodes.FuncDecl("main", [], None,
            nodes.Block([
                nodes.When(nodes.Id("day"), [
                    nodes.WhenBranch([nodes.IntLit(2), nodes.IntLit(3)],
                        nodes.ExprStmt(nodes.CallExpr("printInt", [nodes.IntLit(2)]))),
                ])
            ]))
    ])
    assert repr(ASTGenerator.gen(src)) == repr(expected)


def test_088_when_conditionless_stmt():
    """Conditionless when statement"""
    src = """fun main() {
  when {
    n > 0 -> printString("pos")
    else -> printString("other")
  }
}"""
    expected = nodes.Program([
        nodes.FuncDecl("main", [], None,
            nodes.Block([
                nodes.When(None, [
                    nodes.WhenBranch(
                        [nodes.BinaryOp(">", nodes.Id("n"), nodes.IntLit(0))],
                        nodes.ExprStmt(nodes.CallExpr("printString", [nodes.StringLit("pos")]))),
                    nodes.WhenBranch(None,
                        nodes.ExprStmt(nodes.CallExpr("printString", [nodes.StringLit("other")]))),
                ])
            ]))
    ])
    assert repr(ASTGenerator.gen(src)) == repr(expected)


def test_089_when_empty():
    """Empty when statement"""
    src = "fun main() {\n  when (a) { }\n}"
    expected = nodes.Program([
        nodes.FuncDecl("main", [], None,
            nodes.Block([
                nodes.When(nodes.Id("a"), [])
            ]))
    ])
    assert repr(ASTGenerator.gen(src)) == repr(expected)


def test_090_when_semi_between_branches():
    """Semicolon separators between when branches"""
    src = "fun main() {\n  when (d) { 1 -> printInt(10); else -> printInt(0) }\n}"
    expected = nodes.Program([
        nodes.FuncDecl("main", [], None,
            nodes.Block([
                nodes.When(nodes.Id("d"), [
                    nodes.WhenBranch([nodes.IntLit(1)],
                        nodes.ExprStmt(nodes.CallExpr("printInt", [nodes.IntLit(10)]))),
                    nodes.WhenBranch(None,
                        nodes.ExprStmt(nodes.CallExpr("printInt", [nodes.IntLit(0)]))),
                ])
            ]))
    ])
    assert repr(ASTGenerator.gen(src)) == repr(expected)


def test_091_when_branch_block():
    """when branch body is a block"""
    src = """fun main() {
  when (x) {
    1 -> { printInt(1); printInt(2) }
  }
}"""
    expected = nodes.Program([
        nodes.FuncDecl("main", [], None,
            nodes.Block([
                nodes.When(nodes.Id("x"), [
                    nodes.WhenBranch([nodes.IntLit(1)], nodes.Block([
                        nodes.ExprStmt(nodes.CallExpr("printInt", [nodes.IntLit(1)])),
                        nodes.ExprStmt(nodes.CallExpr("printInt", [nodes.IntLit(2)])),
                    ])),
                ])
            ]))
    ])
    assert repr(ASTGenerator.gen(src)) == repr(expected)


def test_092_when_expr_conditionless():
    """when expression (conditionless) with else"""
    src = """fun main() {
  val sign = when {
    n > 0 -> 1
    n < 0 -> -1
    else -> 0
  }
}"""
    expected = nodes.Program([
        nodes.FuncDecl("main", [], None,
            nodes.Block([
                nodes.VarDecl("sign", False, None, nodes.WhenExpr(None, [
                    nodes.WhenBranch(
                        [nodes.BinaryOp(">", nodes.Id("n"), nodes.IntLit(0))],
                        nodes.IntLit(1)),
                    nodes.WhenBranch(
                        [nodes.BinaryOp("<", nodes.Id("n"), nodes.IntLit(0))],
                        nodes.UnaryOp("-", nodes.IntLit(1))),
                    nodes.WhenBranch(None, nodes.IntLit(0)),
                ]))
            ]))
    ])
    assert repr(ASTGenerator.gen(src)) == repr(expected)


def test_093_when_expr_subject():
    """when expression with subject"""
    src = "fun main() {\n  val x = when (d) { 1 -> 10; else -> 0 }\n}"
    expected = nodes.Program([
        nodes.FuncDecl("main", [], None,
            nodes.Block([
                nodes.VarDecl("x", False, None, nodes.WhenExpr(nodes.Id("d"), [
                    nodes.WhenBranch([nodes.IntLit(1)], nodes.IntLit(10)),
                    nodes.WhenBranch(None, nodes.IntLit(0)),
                ]))
            ]))
    ])
    assert repr(ASTGenerator.gen(src)) == repr(expected)


def test_094_when_expr_multi_labels():
    """when expression subject with multi labels"""
    src = "fun main() {\n  val x = when (d) { 1, 2 -> 10; else -> 0 }\n}"
    expected = nodes.Program([
        nodes.FuncDecl("main", [], None,
            nodes.Block([
                nodes.VarDecl("x", False, None, nodes.WhenExpr(nodes.Id("d"), [
                    nodes.WhenBranch([nodes.IntLit(1), nodes.IntLit(2)], nodes.IntLit(10)),
                    nodes.WhenBranch(None, nodes.IntLit(0)),
                ]))
            ]))
    ])
    assert repr(ASTGenerator.gen(src)) == repr(expected)


def test_095_return_when_expr():
    """return when-expression"""
    src = """fun classify(n: Int): String {
  return when {
    n > 0 -> "positive"
    else -> "zero"
  }
}"""
    expected = nodes.Program([
        nodes.FuncDecl("classify",
            [nodes.Param("n", nodes.IntType())],
            nodes.StringType(),
            nodes.Block([
                nodes.Return(nodes.WhenExpr(None, [
                    nodes.WhenBranch(
                        [nodes.BinaryOp(">", nodes.Id("n"), nodes.IntLit(0))],
                        nodes.StringLit("positive")),
                    nodes.WhenBranch(None, nodes.StringLit("zero")),
                ]))
            ]))
    ])
    assert repr(ASTGenerator.gen(src)) == repr(expected)


def test_096_nested_block():
    """Nested block statement"""
    src = "fun main() {\n  {\n    val x = 1\n  }\n}"
    expected = nodes.Program([
        nodes.FuncDecl("main", [], None,
            nodes.Block([
                nodes.Block([nodes.VarDecl("x", False, None, nodes.IntLit(1))])
            ]))
    ])
    assert repr(ASTGenerator.gen(src)) == repr(expected)


def test_097_if_newline_before_body():
    """Newline allowed before if body block"""
    src = "fun main() {\n  if (a)\n  {\n    printInt(1)\n  }\n}"
    expected = nodes.Program([
        nodes.FuncDecl("main", [], None,
            nodes.Block([
                nodes.If(nodes.Id("a"),
                    nodes.Block([nodes.ExprStmt(nodes.CallExpr("printInt", [nodes.IntLit(1)]))]),
                    None)
            ]))
    ])
    assert repr(ASTGenerator.gen(src)) == repr(expected)


def test_098_params_multiline():
    """Parameters with newlines after commas"""
    src = "fun f(a: Int,\nb: Int): Int {\n  return a\n}"
    expected = nodes.Program([
        nodes.FuncDecl("f",
            [nodes.Param("a", nodes.IntType()), nodes.Param("b", nodes.IntType())],
            nodes.IntType(),
            nodes.Block([
                nodes.Return(nodes.Id("a"))
            ]))
    ])
    assert repr(ASTGenerator.gen(src)) == repr(expected)


def test_099_structural_equality():
    """Data class structural equality expression"""
    src = "fun main() {\n  val same = Point(10, 20) == p1\n}"
    expected = nodes.Program([
        nodes.FuncDecl("main", [], None,
            nodes.Block([
                nodes.VarDecl("same", False, None,
                    nodes.BinaryOp("==",
                        nodes.CallExpr("Point", [nodes.IntLit(10), nodes.IntLit(20)]),
                        nodes.Id("p1")))
            ]))
    ])
    assert repr(ASTGenerator.gen(src)) == repr(expected)


def test_100_complex_program():
    """Integration: data class + functions + control flow"""
    src = """data class Point(x: Int, y: Int)
fun add(x: Int, y: Int): Int {
  return x + y
}
fun main() {
  var p = Point(1, 2)
  val s = add(p.x, p.y)
  if (s > 0) {
    printInt(s)
  }
  for (i in 0..2) {
    printInt(i)
  }
}"""
    expected = nodes.Program([
        nodes.DataClassDecl("Point", [
            nodes.MemberDecl("x", nodes.IntType()),
            nodes.MemberDecl("y", nodes.IntType()),
        ]),
        nodes.FuncDecl("add",
            [nodes.Param("x", nodes.IntType()), nodes.Param("y", nodes.IntType())],
            nodes.IntType(),
            nodes.Block([
                nodes.Return(nodes.BinaryOp("+", nodes.Id("x"), nodes.Id("y")))
            ])),
        nodes.FuncDecl("main", [], None, nodes.Block([
            nodes.VarDecl("p", True, None,
                nodes.CallExpr("Point", [nodes.IntLit(1), nodes.IntLit(2)])),
            nodes.VarDecl("s", False, None,
                nodes.CallExpr("add", [
                    nodes.MemberAccess(nodes.Id("p"), "x"),
                    nodes.MemberAccess(nodes.Id("p"), "y"),
                ])),
            nodes.If(
                nodes.BinaryOp(">", nodes.Id("s"), nodes.IntLit(0)),
                nodes.Block([nodes.ExprStmt(nodes.CallExpr("printInt", [nodes.Id("s")]))]),
                None),
            nodes.For("i", nodes.IntLit(0), nodes.IntLit(2),
                nodes.Block([nodes.ExprStmt(nodes.CallExpr("printInt", [nodes.Id("i")]))])),
        ])),
    ])
    assert repr(ASTGenerator.gen(src)) == repr(expected)

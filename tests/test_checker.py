"""Static checker tests for MKotlin (Assignment 3).

Run with:  python3 run.py test-checker

``Checker.check`` returns the str() of the first raised StaticError, or
``"Static checking passed"``.  These fail until StaticChecker is implemented.
Add up to 100 test cases.

Error messages use the exact ``repr()`` of the offending AST node as ``ctx``
(see ``mkotlin-semantic_constraints_and_errors.md``).

Layout of this file:

    001-015  valid programs (happy path)
    016-026  Redeclared
    027-034  UndeclaredIdentifier
    035-040  UndeclaredFunction
    041-047  UndeclaredClass
    048-056  TypeCannotBeInferred
    057-077  TypeMismatchInStatement
    078-096  TypeMismatchInExpression
    097-100  MustInLoop
    101-118  operator typing, accepted combinations
    119-143  operator typing, rejected combinations
    144-168  control flow and when
    169-188  data classes
    189-203  scope and redeclaration
    204-227  type inference
    228-234  return statements
    235-248  calls and arguments
    249-254  MustInLoop, further cases
    255-260  traversal order (first error wins)
    261-273  lexical surface and remaining constructs
    274-306  cases settled by the course forum Q&A (Forum_QA_ASM3.md)
"""

from tests.utils import Checker
from src.utils import nodes as n


# =========================================================================== #
#  001-015  Valid programs                                                    #
# =========================================================================== #
def test_001_valid_hello():
    """1. Valid: printString call"""
    src = 'fun main() {\n  printString("hi")\n}'
    assert Checker.check(src) == "Static checking passed"


def test_002_valid_arithmetic():
    """2. Valid: val with arithmetic and printInt"""
    src = "fun main() {\n  val x = 1 + 2\n  printInt(x)\n}"
    assert Checker.check(src) == "Static checking passed"


def test_003_valid_var_decl_then_assign():
    """3. Valid: var with explicit type, assigned later"""
    src = "fun main() {\n  var x: Int\n  x = 1\n  printInt(x)\n}"
    assert Checker.check(src) == "Static checking passed"


def test_004_valid_data_class_member_access():
    """4. Valid: construct a data class and read a member"""
    src = (
        "data class Point(x: Int, y: Int)\n"
        "fun main() {\n"
        "  val p = Point(1, 2)\n"
        "  printInt(p.x)\n"
        "  printInt(p.y)\n"
        "}"
    )
    assert Checker.check(src) == "Static checking passed"


def test_005_valid_recursion():
    """5. Valid: recursive function with if/else and return"""
    src = (
        "fun factorial(k: Int): Int {\n"
        "  if (k <= 1) {\n"
        "    return 1\n"
        "  } else {\n"
        "    return k * factorial(k - 1)\n"
        "  }\n"
        "}\n"
        "fun main() {\n"
        "  printInt(factorial(5))\n"
        "}"
    )
    assert Checker.check(src) == "Static checking passed"


def test_006_valid_inferred_return_type():
    """6. Valid: return type inferred from the first value-returning return"""
    src = (
        "fun add(x: Int, y: Int) {\n"
        "  return x + y\n"
        "}\n"
        "fun main() {\n"
        "  val s = add(1, 2)\n"
        "  printInt(s)\n"
        "}"
    )
    assert Checker.check(src) == "Static checking passed"


def test_007_valid_for_loop():
    """7. Valid: for over an Int range"""
    src = "fun main() {\n  for (i in 0..9) {\n    printInt(i)\n  }\n}"
    assert Checker.check(src) == "Static checking passed"


def test_008_valid_while_break_continue():
    """8. Valid: break and continue inside a while loop"""
    src = (
        "fun main() {\n"
        "  var i = 0\n"
        "  while (i < 10) {\n"
        "    if (i == 5) {\n"
        "      break\n"
        "    }\n"
        "    i++\n"
        "    continue\n"
        "  }\n"
        "}"
    )
    assert Checker.check(src) == "Static checking passed"


def test_009_valid_when_statement_subject_form():
    """9. Valid: when statement, subject form with a multi-label branch"""
    src = (
        "fun main() {\n"
        "  val d = readInt()\n"
        "  when (d) {\n"
        "    1 -> printInt(1)\n"
        "    2, 3 -> printInt(2)\n"
        "    else -> printInt(0)\n"
        "  }\n"
        "}"
    )
    assert Checker.check(src) == "Static checking passed"


def test_010_valid_when_expression_conditionless():
    """10. Valid: conditionless when used as an expression"""
    src = (
        "fun classify(k: Int): String {\n"
        "  return when {\n"
        '    k > 0 -> "positive"\n'
        '    k < 0 -> "negative"\n'
        '    else -> "zero"\n'
        "  }\n"
        "}\n"
        "fun main() {\n"
        "  printString(classify(1))\n"
        "}"
    )
    assert Checker.check(src) == "Static checking passed"


def test_011_valid_if_expression():
    """11. Valid: if used as an expression"""
    src = (
        "fun main() {\n"
        "  val a = 1\n"
        "  val b = 2\n"
        "  val m = if (a > b) a else b\n"
        "  printInt(m)\n"
        "}"
    )
    assert Checker.check(src) == "Static checking passed"


def test_012_valid_nested_data_class():
    """12. Valid: data class member of another data class type"""
    src = (
        "data class Point(x: Int, y: Int)\n"
        "data class Line(a: Point, b: Point)\n"
        "fun main() {\n"
        "  val l = Line(Point(1, 2), Point(3, 4))\n"
        "  printInt(l.a.x)\n"
        "}"
    )
    assert Checker.check(src) == "Static checking passed"


def test_013_valid_var_inferred_from_first_assignment():
    """13. Valid: un-annotated var inferred from its first assignment"""
    src = "fun main() {\n  var v\n  v = 10\n  printInt(v)\n}"
    assert Checker.check(src) == "Static checking passed"


def test_014_valid_int_to_float_widening():
    """14. Valid: Int widens to Float in declaration, assignment and call"""
    src = (
        "fun main() {\n"
        "  val f: Float = 1\n"
        "  var g: Float = 2\n"
        "  g = 3\n"
        "  printFloat(f)\n"
        "  printFloat(g)\n"
        "  printFloat(4)\n"
        "}"
    )
    assert Checker.check(src) == "Static checking passed"


def test_015_valid_all_builtin_io():
    """15. Valid: every predeclared read/print built-in"""
    src = (
        "fun main() {\n"
        "  val a = readInt()\n"
        "  val b = readFloat()\n"
        "  val c = readBool()\n"
        "  val d = readString()\n"
        "  printInt(a)\n"
        "  printFloat(b)\n"
        "  printBool(c)\n"
        "  printString(d)\n"
        "}"
    )
    assert Checker.check(src) == "Static checking passed"


# =========================================================================== #
#  016-026  Redeclared                                                        #
# =========================================================================== #
def test_016_redeclared_param_vs_body_variable():
    """16. Redeclared: body variable reuses a parameter name"""
    src = "fun f(x: Int) {\n  val x = 5\n}"
    assert Checker.check(src) == "Redeclared Variable: x"


def test_017_redeclared_val_then_var_same_scope():
    """17. Redeclared: val then var with the same name in one scope"""
    src = "fun main() {\n  val x = 1\n  var x = 2\n}"
    assert Checker.check(src) == "Redeclared Variable: x"


def test_018_redeclared_parameter():
    """18. Redeclared: duplicate parameter name"""
    src = "fun f(a: Int, a: Int) {\n}"
    assert Checker.check(src) == "Redeclared Parameter: a"


def test_019_redeclared_function():
    """19. Redeclared: two functions with the same name"""
    src = "fun f() {\n}\nfun f() {\n}"
    assert Checker.check(src) == "Redeclared Function: f"


def test_020_redeclared_data_class():
    """20. Redeclared: two data classes with the same name"""
    src = "data class A(x: Int)\ndata class A(y: Int)"
    assert Checker.check(src) == "Redeclared Class: A"


def test_021_redeclared_function_collides_with_class():
    """21. Redeclared: function name already used by a data class"""
    src = "data class P(x: Int)\nfun P() {\n}"
    assert Checker.check(src) == "Redeclared Function: P"


def test_022_redeclared_class_collides_with_function():
    """22. Redeclared: data class name already used by a function"""
    src = "fun P() {\n}\ndata class P(x: Int)"
    assert Checker.check(src) == "Redeclared Class: P"


def test_023_redeclared_builtin_function():
    """23. Redeclared: user function reuses a built-in name"""
    src = "fun printInt(v: Int) {\n}"
    assert Checker.check(src) == "Redeclared Function: printInt"


def test_024_redeclared_member():
    """24. Redeclared: duplicate data class member"""
    src = "data class P(x: Int, x: Int)"
    assert Checker.check(src) == "Redeclared Member: x"


def test_025_redeclared_inside_block():
    """25. Redeclared: two declarations in the same inner block scope"""
    src = "fun main() {\n  if (true) {\n    val y = 1\n    val y = 2\n  }\n}"
    assert Checker.check(src) == "Redeclared Variable: y"


def test_026_shadowing_in_inner_scopes_is_allowed():
    """26. Not Redeclared: inner block and for body may shadow outer names"""
    src = (
        "fun f(x: Int) {\n"
        "  if (true) {\n"
        "    val x = 2\n"
        "    printInt(x)\n"
        "  }\n"
        "  for (i in 0..3) {\n"
        "    val i = 5\n"
        "    printInt(i)\n"
        "  }\n"
        "  printInt(x)\n"
        "}"
    )
    assert Checker.check(src) == "Static checking passed"


# =========================================================================== #
#  027-034  UndeclaredIdentifier                                              #
# =========================================================================== #
def test_027_undeclared_identifier():
    """27. UndeclaredIdentifier: plain unknown name"""
    src = "fun main() {\n  printInt(y)\n}"
    assert Checker.check(src) == "Undeclared Identifier: y"


def test_028_use_before_declaration():
    """28. UndeclaredIdentifier: used above its declaration"""
    src = "fun main() {\n  printInt(x)\n  val x = 1\n}"
    assert Checker.check(src) == "Undeclared Identifier: x"


def test_029_name_not_in_scope_of_own_initializer():
    """29. UndeclaredIdentifier: a name is not visible in its own initializer"""
    src = "fun main() {\n  val x = x + 1\n}"
    assert Checker.check(src) == "Undeclared Identifier: x"


def test_030_block_local_not_visible_outside():
    """30. UndeclaredIdentifier: block-local escapes its scope"""
    src = "fun main() {\n  if (true) {\n    val z = 1\n  }\n  printInt(z)\n}"
    assert Checker.check(src) == "Undeclared Identifier: z"


def test_031_loop_variable_not_visible_after_loop():
    """31. UndeclaredIdentifier: loop variable used after the for"""
    src = (
        "fun main() {\n"
        "  for (i in 0..3) {\n"
        "    printInt(i)\n"
        "  }\n"
        "  printInt(i)\n"
        "}"
    )
    assert Checker.check(src) == "Undeclared Identifier: i"


def test_032_assign_to_undeclared_target():
    """32. UndeclaredIdentifier: assignment target is unknown"""
    src = "fun main() {\n  q = 1\n}"
    assert Checker.check(src) == "Undeclared Identifier: q"


def test_033_parameter_of_other_function_not_visible():
    """33. UndeclaredIdentifier: another function's parameter is not global"""
    src = "fun f(a: Int) {\n  printInt(a)\n}\nfun main() {\n  printInt(a)\n}"
    assert Checker.check(src) == "Undeclared Identifier: a"


def test_034_undeclared_in_range_bound():
    """34. UndeclaredIdentifier: unknown name in a for range bound"""
    src = "fun main() {\n  for (i in 0..k) {\n    printInt(i)\n  }\n}"
    assert Checker.check(src) == "Undeclared Identifier: k"


# =========================================================================== #
#  035-040  UndeclaredFunction                                                #
# =========================================================================== #
def test_035_undeclared_function():
    """35. UndeclaredFunction: unknown callee"""
    src = "fun main() {\n  val a = compute(3)\n}"
    assert Checker.check(src) == "Undeclared Function: compute"


def test_036_calling_a_variable():
    """36. UndeclaredFunction: a variable name is not callable"""
    src = "fun main() {\n  val f = 1\n  printInt(f(2))\n}"
    assert Checker.check(src) == "Undeclared Function: f"


def test_037_calling_a_parameter():
    """37. UndeclaredFunction: a parameter name is not callable"""
    src = "fun f(g: Int) {\n  printInt(g(1))\n}"
    assert Checker.check(src) == "Undeclared Function: g"


def test_038_forward_function_reference():
    """38. UndeclaredFunction: no forward references at global scope"""
    src = (
        "fun main() {\n"
        "  printInt(later())\n"
        "}\n"
        "fun later(): Int {\n"
        "  return 1\n"
        "}"
    )
    assert Checker.check(src) == "Undeclared Function: later"


def test_039_forward_constructor_reference():
    """39. UndeclaredFunction: constructor used before its data class"""
    src = (
        "fun main() {\n"
        "  val p = Point(1, 2)\n"
        "}\n"
        "data class Point(x: Int, y: Int)"
    )
    assert Checker.check(src) == "Undeclared Function: Point"


def test_040_operands_checked_before_operator():
    """40. UndeclaredFunction: operand errors surface before operator typing"""
    src = "fun main() {\n  val x = 1 && foo()\n}"
    assert Checker.check(src) == "Undeclared Function: foo"


# =========================================================================== #
#  041-047  UndeclaredClass                                                   #
# =========================================================================== #
def test_041_undeclared_class_in_var_annotation():
    """41. UndeclaredClass: unknown type on a variable"""
    src = "fun main() {\n  var p: Vec\n}"
    assert Checker.check(src) == "Undeclared Class: Vec"


def test_042_undeclared_class_in_parameter_type():
    """42. UndeclaredClass: unknown parameter type"""
    src = "fun f(p: Vec) {\n}"
    assert Checker.check(src) == "Undeclared Class: Vec"


def test_043_undeclared_class_in_return_type():
    """43. UndeclaredClass: unknown return type"""
    src = "fun f(): Vec {\n  return 1\n}"
    assert Checker.check(src) == "Undeclared Class: Vec"


def test_044_undeclared_class_in_member_type():
    """44. UndeclaredClass: unknown data class member type"""
    src = "data class A(p: Vec)"
    assert Checker.check(src) == "Undeclared Class: Vec"


def test_045_self_referential_member_type():
    """45. UndeclaredClass: a class is not declared for its own members"""
    src = "data class Node(next: Node)"
    assert Checker.check(src) == "Undeclared Class: Node"


def test_046_forward_class_in_member_type():
    """46. UndeclaredClass: member type declared later in the file"""
    src = "data class A(b: B)\ndata class B(x: Int)"
    assert Checker.check(src) == "Undeclared Class: B"


def test_047_declared_class_in_every_type_position():
    """47. Valid: a declared data class as member, param, return and var type"""
    src = (
        "data class Point(x: Int, y: Int)\n"
        "data class Line(a: Point, b: Point)\n"
        "fun mk(p: Point): Point {\n"
        "  return p\n"
        "}\n"
        "fun main() {\n"
        "  val p: Point = mk(Point(1, 2))\n"
        "  printInt(p.x)\n"
        "}"
    )
    assert Checker.check(src) == "Static checking passed"


# =========================================================================== #
#  048-056  TypeCannotBeInferred                                              #
# =========================================================================== #
def test_048_two_unknowns_multiplied():
    """48. TypeCannotBeInferred: two undetermined vars, no anchor"""
    src = "fun main() {\n  var a\n  var b\n  val c = a * b\n}"
    ctx = n.BinaryOp("*", n.Id("a"), n.Id("b"))
    assert Checker.check(src) == f"Type Cannot Be Inferred: {repr(ctx)}"


def test_049_two_unknowns_compared():
    """49. TypeCannotBeInferred: equality between two undetermined vars"""
    src = "fun main() {\n  var a\n  var b\n  val c = a == b\n}"
    ctx = n.BinaryOp("==", n.Id("a"), n.Id("b"))
    assert Checker.check(src) == f"Type Cannot Be Inferred: {repr(ctx)}"


def test_051_integer_literal_anchor():
    """51. Valid: an integer literal anchors an undetermined var to Int"""
    src = "fun main() {\n  var a\n  val c = a * 2\n  printInt(c)\n}"
    assert Checker.check(src) == "Static checking passed"


def test_052_float_literal_does_not_anchor():
    """52. TypeCannotBeInferred: only integer literals anchor an unknown var"""
    src = "fun main() {\n  var a\n  val c = a * 2.0\n}"
    ctx = n.BinaryOp("*", n.Id("a"), n.FloatLit(2.0))
    assert Checker.check(src) == f"Type Cannot Be Inferred: {repr(ctx)}"


def test_053_no_deep_propagation_from_annotation():
    """53. TypeCannotBeInferred: an annotation does not type nested unknowns"""
    src = "fun main() {\n  var a\n  var b\n  val c: Int = a + b\n}"
    ctx = n.BinaryOp("+", n.Id("a"), n.Id("b"))
    assert Checker.check(src) == f"Type Cannot Be Inferred: {repr(ctx)}"


def test_054_compound_argument_with_two_unknowns():
    """54. TypeCannotBeInferred: parameter type does not reach argument leaves"""
    src = "fun main() {\n  var a\n  var b\n  printInt(a + b)\n}"
    ctx = n.BinaryOp("+", n.Id("a"), n.Id("b"))
    assert Checker.check(src) == f"Type Cannot Be Inferred: {repr(ctx)}"


def test_055_unary_minus_on_unknown():
    """55. TypeCannotBeInferred: unary minus supplies no type information"""
    src = "fun main() {\n  var a\n  val c = -a\n}"
    ctx = n.UnaryOp("-", n.Id("a"))
    assert Checker.check(src) == f"Type Cannot Be Inferred: {repr(ctx)}"


def test_056_argument_and_return_positions_fix_a_var():
    """56. Valid: whole-argument and whole-return positions fix a lone var"""
    src = (
        "fun f(): Float {\n"
        "  var a\n"
        "  return a\n"
        "}\n"
        "fun main() {\n"
        "  var b\n"
        "  printFloat(b)\n"
        "  printFloat(f())\n"
        "}"
    )
    assert Checker.check(src) == "Static checking passed"


# =========================================================================== #
#  057-077  TypeMismatchInStatement                                           #
# =========================================================================== #
def test_057_reassign_val():
    """57. TypeMismatchInStatement: a val cannot be reassigned"""
    src = "fun main() {\n  val x = 1\n  x = 2\n}"
    ctx = n.Assign(n.Id("x"), n.IntLit(2))
    assert Checker.check(src) == f"Type Mismatch In Statement: {repr(ctx)}"


def test_058_while_condition_not_boolean():
    """58. TypeMismatchInStatement: while condition is Int"""
    src = "fun main() {\n  var i = 0\n  while (i) {\n    i++\n  }\n}"
    ctx = n.While(
        n.Id("i"),
        n.Block([n.ExprStmt(n.PostfixOp("++", n.Id("i")))]),
    )
    assert Checker.check(src) == f"Type Mismatch In Statement: {repr(ctx)}"


def test_059_if_condition_not_boolean():
    """59. TypeMismatchInStatement: if condition is Int"""
    src = "fun main() {\n  if (1) {\n    printInt(1)\n  }\n}"
    ctx = n.If(
        n.IntLit(1),
        n.Block([n.ExprStmt(n.CallExpr("printInt", [n.IntLit(1)]))]),
        None,
    )
    assert Checker.check(src) == f"Type Mismatch In Statement: {repr(ctx)}"


def test_060_for_start_bound_not_int():
    """60. TypeMismatchInStatement: range start is Float"""
    src = "fun main() {\n  for (i in 1.5..3) {\n    printInt(i)\n  }\n}"
    ctx = n.For(
        "i",
        n.FloatLit(1.5),
        n.IntLit(3),
        n.Block([n.ExprStmt(n.CallExpr("printInt", [n.Id("i")]))]),
    )
    assert Checker.check(src) == f"Type Mismatch In Statement: {repr(ctx)}"


def test_061_for_end_bound_not_int():
    """61. TypeMismatchInStatement: range end is String"""
    src = (
        "fun main() {\n"
        '  val s = "a"\n'
        "  for (i in 0..s) {\n"
        "    printInt(i)\n"
        "  }\n"
        "}"
    )
    ctx = n.For(
        "i",
        n.IntLit(0),
        n.Id("s"),
        n.Block([n.ExprStmt(n.CallExpr("printInt", [n.Id("i")]))]),
    )
    assert Checker.check(src) == f"Type Mismatch In Statement: {repr(ctx)}"


def test_062_return_value_from_unit_function():
    """62. TypeMismatchInStatement: a Unit function returns a value"""
    src = "fun f(): Unit {\n  return 1\n}"
    ctx = n.Return(n.IntLit(1))
    assert Checker.check(src) == f"Type Mismatch In Statement: {repr(ctx)}"


def test_063_return_without_value_from_typed_function():
    """63. TypeMismatchInStatement: a non-Unit function returns nothing"""
    src = "fun f(): Int {\n  return\n}"
    ctx = n.Return(None)
    assert Checker.check(src) == f"Type Mismatch In Statement: {repr(ctx)}"


def test_064_return_wrong_type():
    """64. TypeMismatchInStatement: returned String where Int is declared"""
    src = 'fun f(): Int {\n  return "s"\n}'
    ctx = n.Return(n.StringLit("s"))
    assert Checker.check(src) == f"Type Mismatch In Statement: {repr(ctx)}"


def test_065_return_float_from_int_function():
    """65. TypeMismatchInStatement: Float does not narrow to Int"""
    src = "fun f(): Int {\n  return 1.5\n}"
    ctx = n.Return(n.FloatLit(1.5))
    assert Checker.check(src) == f"Type Mismatch In Statement: {repr(ctx)}"


def test_066_inconsistent_inferred_returns():
    """66. TypeMismatchInStatement: later return disagrees with the inferred type"""
    src = (
        "fun f(c: Boolean) {\n"
        "  if (c) {\n"
        "    return 1\n"
        "  }\n"
        '  return "x"\n'
        "}"
    )
    ctx = n.Return(n.StringLit("x"))
    assert Checker.check(src) == f"Type Mismatch In Statement: {repr(ctx)}"


def test_067_consistent_returns_and_widening():
    """67. Valid: agreeing returns, Int widened to Float, bare return for Unit"""
    src = (
        "fun g(c: Boolean): Int {\n"
        "  if (c) {\n"
        "    return 1\n"
        "  }\n"
        "  return 2\n"
        "}\n"
        "fun h(): Float {\n"
        "  return 1\n"
        "}\n"
        "fun u() {\n"
        "  return\n"
        "}\n"
        "fun main() {\n"
        "  printInt(g(true))\n"
        "  printFloat(h())\n"
        "  u()\n"
        "}"
    )
    assert Checker.check(src) == "Static checking passed"


def test_068_assign_string_to_int_variable():
    """68. TypeMismatchInStatement: String assigned to an Int var"""
    src = 'fun main() {\n  var x = 1\n  x = "s"\n}'
    ctx = n.Assign(n.Id("x"), n.StringLit("s"))
    assert Checker.check(src) == f"Type Mismatch In Statement: {repr(ctx)}"


def test_069_assign_float_to_int_variable():
    """69. TypeMismatchInStatement: Float does not narrow to Int on assignment"""
    src = "fun main() {\n  var x: Int = 0\n  x = 1.5\n}"
    ctx = n.Assign(n.Id("x"), n.FloatLit(1.5))
    assert Checker.check(src) == f"Type Mismatch In Statement: {repr(ctx)}"


def test_070_assign_conflicts_with_first_inference():
    """70. TypeMismatchInStatement: an un-annotated var is fixed by first usage"""
    src = "fun main() {\n  var a\n  a = 1\n  a = 2.5\n}"
    ctx = n.Assign(n.Id("a"), n.FloatLit(2.5))
    assert Checker.check(src) == f"Type Mismatch In Statement: {repr(ctx)}"


def test_071_annotation_mismatch_float_into_int():
    """71. TypeMismatchInStatement: initializer disagrees with the annotation"""
    src = "fun main() {\n  val x: Int = 3.14\n}"
    ctx = n.VarDecl("x", False, n.IntType(), n.FloatLit(3.14))
    assert Checker.check(src) == f"Type Mismatch In Statement: {repr(ctx)}"


def test_072_annotation_mismatch_int_into_boolean():
    """72. TypeMismatchInStatement: Int initializer for a Boolean var"""
    src = "fun main() {\n  var b: Boolean = 1\n}"
    ctx = n.VarDecl("b", True, n.BoolType(), n.IntLit(1))
    assert Checker.check(src) == f"Type Mismatch In Statement: {repr(ctx)}"


def test_075_assign_to_loop_variable():
    """75. TypeMismatchInStatement: the loop variable is immutable"""
    src = "fun main() {\n  for (i in 0..3) {\n    i = 5\n  }\n}"
    ctx = n.Assign(n.Id("i"), n.IntLit(5))
    assert Checker.check(src) == f"Type Mismatch In Statement: {repr(ctx)}"


def test_076_assign_member_of_val():
    """76. TypeMismatchInStatement: a member rooted at a val is not assignable"""
    src = (
        "data class Point(x: Int, y: Int)\n"
        "fun main() {\n"
        "  val p = Point(1, 2)\n"
        "  p.x = 5\n"
        "}"
    )
    ctx = n.Assign(n.MemberAccess(n.Id("p"), "x"), n.IntLit(5))
    assert Checker.check(src) == f"Type Mismatch In Statement: {repr(ctx)}"


def test_077_member_assignment_type_mismatch():
    """77. TypeMismatchInStatement: wrong value type for a var-rooted member"""
    src = (
        "data class Point(x: Int, y: Int)\n"
        "fun main() {\n"
        "  var p = Point(1, 2)\n"
        '  p.x = "a"\n'
        "}"
    )
    ctx = n.Assign(n.MemberAccess(n.Id("p"), "x"), n.StringLit("a"))
    assert Checker.check(src) == f"Type Mismatch In Statement: {repr(ctx)}"


# =========================================================================== #
#  078-096  TypeMismatchInExpression                                          #
# =========================================================================== #
def test_078_logical_and_needs_boolean():
    """78. TypeMismatchInExpression: && requires Boolean operands"""
    src = "fun main() {\n  val b = true && 1\n}"
    ctx = n.BinaryOp("&&", n.BoolLit(True), n.IntLit(1))
    assert Checker.check(src) == f"Type Mismatch In Expression: {repr(ctx)}"


def test_079_no_string_concatenation():
    """79. TypeMismatchInExpression: + does not apply to String"""
    src = 'fun main() {\n  val s = "a" + "b"\n}'
    ctx = n.BinaryOp("+", n.StringLit("a"), n.StringLit("b"))
    assert Checker.check(src) == f"Type Mismatch In Expression: {repr(ctx)}"


def test_080_no_string_ordering():
    """80. TypeMismatchInExpression: < does not apply to String"""
    src = 'fun main() {\n  val b = "a" < "b"\n}'
    ctx = n.BinaryOp("<", n.StringLit("a"), n.StringLit("b"))
    assert Checker.check(src) == f"Type Mismatch In Expression: {repr(ctx)}"


def test_081_modulus_requires_int():
    """81. TypeMismatchInExpression: % is Int only"""
    src = "fun main() {\n  val x = 3.14 % 2\n}"
    ctx = n.BinaryOp("%", n.FloatLit(3.14), n.IntLit(2))
    assert Checker.check(src) == f"Type Mismatch In Expression: {repr(ctx)}"


def test_082_not_requires_boolean():
    """82. TypeMismatchInExpression: ! is Boolean only"""
    src = "fun main() {\n  val b = !1\n}"
    ctx = n.UnaryOp("!", n.IntLit(1))
    assert Checker.check(src) == f"Type Mismatch In Expression: {repr(ctx)}"


def test_083_unary_minus_on_boolean():
    """83. TypeMismatchInExpression: unary minus needs Int or Float"""
    src = "fun main() {\n  val x = -true\n}"
    ctx = n.UnaryOp("-", n.BoolLit(True))
    assert Checker.check(src) == f"Type Mismatch In Expression: {repr(ctx)}"


def test_084_postfix_increment_on_float():
    """84. TypeMismatchInExpression: ++ is Int only"""
    src = "fun main() {\n  var f = 1.5\n  f++\n}"
    ctx = n.PostfixOp("++", n.Id("f"))
    assert Checker.check(src) == f"Type Mismatch In Expression: {repr(ctx)}"


def test_085_prefix_decrement_on_string():
    """85. TypeMismatchInExpression: -- is Int only"""
    src = 'fun main() {\n  var s = "a"\n  --s\n}'
    ctx = n.UnaryOp("--", n.Id("s"))
    assert Checker.check(src) == f"Type Mismatch In Expression: {repr(ctx)}"


def test_086_equality_between_int_and_string():
    """86. TypeMismatchInExpression: == needs the same comparable type"""
    src = 'fun main() {\n  val b = 1 == "a"\n}'
    ctx = n.BinaryOp("==", n.IntLit(1), n.StringLit("a"))
    assert Checker.check(src) == f"Type Mismatch In Expression: {repr(ctx)}"


def test_087_equality_between_different_data_classes():
    """87. TypeMismatchInExpression: == needs the same data class on both sides"""
    src = (
        "data class A(x: Int)\n"
        "data class B(x: Int)\n"
        "fun main() {\n"
        "  val b = A(1) == B(2)\n"
        "}"
    )
    ctx = n.BinaryOp(
        "==",
        n.CallExpr("A", [n.IntLit(1)]),
        n.CallExpr("B", [n.IntLit(2)]),
    )
    assert Checker.check(src) == f"Type Mismatch In Expression: {repr(ctx)}"


def test_088_member_access_on_non_class():
    """88. TypeMismatchInExpression: receiver must be a data class value"""
    src = "fun main() {\n  val x = 1\n  val y = x.a && true\n}"
    ctx = n.MemberAccess(n.Id("x"), "a")
    assert Checker.check(src) == f"Type Mismatch In Expression: {repr(ctx)}"


def test_089_unknown_member():
    """89. TypeMismatchInExpression: member does not belong to the data class"""
    src = (
        "data class Point(x: Int, y: Int)\n"
        "fun main() {\n"
        "  val p = Point(1, 2)\n"
        "  printInt(p.z)\n"
        "}"
    )
    ctx = n.MemberAccess(n.Id("p"), "z")
    assert Checker.check(src) == f"Type Mismatch In Expression: {repr(ctx)}"


def test_090_wrong_argument_count():
    """90. TypeMismatchInExpression: too few arguments"""
    src = "fun f(a: Int, b: Int) {\n}\nfun main() {\n  f(1)\n}"
    ctx = n.CallExpr("f", [n.IntLit(1)])
    assert Checker.check(src) == f"Type Mismatch In Expression: {repr(ctx)}"


def test_091_float_argument_for_int_parameter():
    """91. TypeMismatchInExpression: Float does not narrow to an Int parameter"""
    src = "fun main() {\n  printInt(1.5)\n}"
    ctx = n.CallExpr("printInt", [n.FloatLit(1.5)])
    assert Checker.check(src) == f"Type Mismatch In Expression: {repr(ctx)}"


def test_092_constructor_wrong_argument_count():
    """92. TypeMismatchInExpression: constructor arity must match the members"""
    src = "data class Point(x: Int, y: Int)\nfun main() {\n  val p = Point(1)\n}"
    ctx = n.CallExpr("Point", [n.IntLit(1)])
    assert Checker.check(src) == f"Type Mismatch In Expression: {repr(ctx)}"


def test_093_constructor_argument_order():
    """93. TypeMismatchInExpression: constructor arguments follow member order"""
    src = (
        "data class Person(name: String, age: Int)\n"
        "fun main() {\n"
        '  val p = Person(25, "John")\n'
        "}"
    )
    ctx = n.CallExpr("Person", [n.IntLit(25), n.StringLit("John")])
    assert Checker.check(src) == f"Type Mismatch In Expression: {repr(ctx)}"


def test_094_when_label_type_mismatch():
    """94. TypeMismatchInExpression: label type must match the subject type"""
    src = (
        "fun main() {\n"
        "  when (1) {\n"
        '    "a" -> printInt(1)\n'
        "    else -> printInt(0)\n"
        "  }\n"
        "}"
    )
    ctx = n.StringLit("a")
    assert Checker.check(src) == f"Type Mismatch In Expression: {repr(ctx)}"


def test_095_when_guard_not_boolean():
    """95. TypeMismatchInExpression: conditionless when guards must be Boolean"""
    src = (
        "fun main() {\n"
        "  when {\n"
        "    1 -> printInt(1)\n"
        "    else -> printInt(0)\n"
        "  }\n"
        "}"
    )
    ctx = n.IntLit(1)
    assert Checker.check(src) == f"Type Mismatch In Expression: {repr(ctx)}"


def test_096_if_expression_branch_types_differ():
    """96. TypeMismatchInExpression: if-expression branches must agree"""
    src = 'fun main() {\n  val x = if (true) 1 else "a"\n}'
    ctx = n.IfExpr(n.BoolLit(True), n.IntLit(1), n.StringLit("a"))
    assert Checker.check(src) == f"Type Mismatch In Expression: {repr(ctx)}"


# =========================================================================== #
#  097-100  MustInLoop                                                        #
# =========================================================================== #
def test_097_break_inside_when():
    """97. MustInLoop: when is not a loop"""
    src = "fun main() {\n  when (1) {\n    1 -> break\n    else -> printInt(0)\n  }\n}"
    assert Checker.check(src) == f"Must In Loop: {repr(n.Break())}"

def test_098_continue_at_function_top_level():
    """98. MustInLoop: continue directly in a function body"""
    src = "fun main() {\n  continue\n}"
    assert Checker.check(src) == f"Must In Loop: {repr(n.Continue())}"


def test_099_break_inside_if_outside_loop():
    """99. MustInLoop: an if does not create a loop context"""
    src = "fun main() {\n  if (true) {\n    break\n  }\n}"
    assert Checker.check(src) == f"Must In Loop: {repr(n.Break())}"


def test_100_break_and_continue_nested_in_loops():
    """100. Valid: break/continue inside when and if nested in loops"""
    src = (
        "fun main() {\n"
        "  while (true) {\n"
        "    when (1) {\n"
        "      1 -> break\n"
        "      else -> printInt(0)\n"
        "    }\n"
        "  }\n"
        "  for (i in 0..3) {\n"
        "    if (i == 2) {\n"
        "      continue\n"
        "    }\n"
        "    printInt(i)\n"
        "  }\n"
        "}"
    )
    assert Checker.check(src) == "Static checking passed"


# =========================================================================== #
#  101-118  Operator typing - accepted combinations                           #
# =========================================================================== #
def test_101_int_arithmetic_all_operators():
    """101. Valid: Int op Int yields Int for + - * / %"""
    src = (
        "fun main() {\n"
        "  val a: Int = 1 + 2\n"
        "  val b: Int = 3 - 4\n"
        "  val c: Int = 5 * 6\n"
        "  val d: Int = 7 / 8\n"
        "  val e: Int = 9 % 2\n"
        "  printInt(a + b + c + d + e)\n"
        "}"
    )
    assert Checker.check(src) == "Static checking passed"


def test_102_mixed_arithmetic_yields_float():
    """102. Valid: one Float operand makes the whole arithmetic Float"""
    src = (
        "fun main() {\n"
        "  val a: Float = 1 + 2.0\n"
        "  val b: Float = 2.0 - 1\n"
        "  val c: Float = 1.5 * 2\n"
        "  val d: Float = 3 / 1.5\n"
        "  printFloat(a + b + c + d)\n"
        "}"
    )
    assert Checker.check(src) == "Static checking passed"


def test_103_float_arithmetic():
    """103. Valid: Float op Float yields Float"""
    src = "fun main() {\n  val a = 1.5 + 2.5\n  printFloat(a * 2.0)\n}"
    assert Checker.check(src) == "Static checking passed"


def test_104_int_annotation_cannot_hold_float_result():
    """104. TypeMismatchInStatement: a mixed arithmetic result is Float"""
    src = "fun main() {\n  val x: Int = 1 + 2.0\n}"
    ctx = n.VarDecl(
        "x", False, n.IntType(), n.BinaryOp("+", n.IntLit(1), n.FloatLit(2.0))
    )
    assert Checker.check(src) == f"Type Mismatch In Statement: {repr(ctx)}"


def test_105_int_division_stays_int():
    """105. Valid: Int / Int is Int, not Float"""
    src = "fun main() {\n  val x: Int = 7 / 2\n  printInt(x)\n}"
    assert Checker.check(src) == "Static checking passed"


def test_106_all_ordering_operators():
    """106. Valid: < <= > >= on Int produce Boolean"""
    src = (
        "fun main() {\n"
        "  printBool(1 < 2)\n"
        "  printBool(1 <= 2)\n"
        "  printBool(1 > 2)\n"
        "  printBool(1 >= 2)\n"
        "}"
    )
    assert Checker.check(src) == "Static checking passed"


def test_107_ordering_mixes_int_and_float():
    """107. Valid: ordering allows Int/Float promotion"""
    src = "fun main() {\n  printBool(1 < 2.0)\n  printBool(2.0 >= 1)\n}"
    assert Checker.check(src) == "Static checking passed"


def test_108_equality_on_every_comparable_type():
    """108. Valid: == and != on Int, Float, Boolean, String and mixed numbers"""
    src = (
        "fun main() {\n"
        "  printBool(1 == 2)\n"
        "  printBool(1.0 != 2.0)\n"
        "  printBool(true == false)\n"
        '  printBool("a" != "b")\n'
        "  printBool(1 == 2.0)\n"
        "  printBool(1.5 != 2)\n"
        "}"
    )
    assert Checker.check(src) == "Static checking passed"


def test_109_structural_equality_of_same_data_class():
    """109. Valid: == and != between values of the same data class"""
    src = (
        "data class P(x: Int)\n"
        "fun main() {\n"
        "  printBool(P(1) == P(2))\n"
        "  printBool(P(1) != P(2))\n"
        "}"
    )
    assert Checker.check(src) == "Static checking passed"


def test_110_logical_operators():
    """110. Valid: && || ! on Boolean operands"""
    src = (
        "fun main() {\n"
        "  printBool(true && false)\n"
        "  printBool(true || false)\n"
        "  printBool(!true)\n"
        "  printBool(!(1 < 2) && (3 > 2))\n"
        "}"
    )
    assert Checker.check(src) == "Static checking passed"


def test_111_unary_plus_and_minus():
    """111. Valid: unary + and - on Int and Float"""
    src = (
        "fun main() {\n"
        "  printInt(-1)\n"
        "  printInt(+1)\n"
        "  printFloat(-1.5)\n"
        "  printFloat(+1.5)\n"
        "}"
    )
    assert Checker.check(src) == "Static checking passed"


def test_112_prefix_increment_and_decrement():
    """112. Valid: prefix ++ and -- on an Int var"""
    src = "fun main() {\n  var i = 0\n  printInt(++i)\n  printInt(--i)\n}"
    assert Checker.check(src) == "Static checking passed"


def test_113_postfix_increment_and_decrement():
    """113. Valid: postfix ++ and -- on an Int var"""
    src = "fun main() {\n  var i = 0\n  printInt(i++)\n  printInt(i--)\n}"
    assert Checker.check(src) == "Static checking passed"


def test_114_increment_a_var_rooted_member():
    """114. Valid: ++ on an Int member reached through a var"""
    src = (
        "data class C(k: Int)\n"
        "fun main() {\n"
        "  var c = C(0)\n"
        "  c.k++\n"
        "  printInt(c.k)\n"
        "}"
    )
    assert Checker.check(src) == "Static checking passed"


def test_115_range_bounds_may_be_expressions():
    """115. Valid: any Int expression works as a range bound"""
    src = (
        "fun main() {\n"
        "  val a = 1\n"
        "  var b = 10\n"
        "  for (i in a..b) {\n"
        "    printInt(i)\n"
        "  }\n"
        "  for (j in (a + 1)..(b - 1)) {\n"
        "    printInt(j)\n"
        "  }\n"
        "}"
    )
    assert Checker.check(src) == "Static checking passed"


def test_116_chained_assignment():
    """116. Valid: assignment is right-associative and chainable"""
    src = (
        "fun main() {\n"
        "  var x = 0\n"
        "  var y = 0\n"
        "  var z = 0\n"
        "  x = y = z = 10\n"
        "  printInt(x)\n"
        "}"
    )
    assert Checker.check(src) == "Static checking passed"


def test_117_operator_precedence_typing():
    """117. Valid: precedence produces well-typed sub-expressions"""
    src = (
        "fun main() {\n"
        "  val x: Int = 1 + 2 * 3\n"
        "  val b: Boolean = 1 + 2 < 4 && true\n"
        "  printInt(x)\n"
        "  printBool(b)\n"
        "}"
    )
    assert Checker.check(src) == "Static checking passed"


def test_118_deeply_nested_boolean_expression():
    """118. Valid: relational results combined with logical operators"""
    src = (
        "fun main() {\n"
        "  val a = 1\n"
        "  val b = 2\n"
        "  printBool(a < b && b < 3 || !(a == b))\n"
        "}"
    )
    assert Checker.check(src) == "Static checking passed"


# =========================================================================== #
#  119-143  Operator typing - rejected combinations                           #
# =========================================================================== #
def test_119_subtraction_on_boolean():
    """119. TypeMismatchInExpression: - needs Int or Float"""
    src = "fun main() {\n  val x = true - false\n}"
    ctx = n.BinaryOp("-", n.BoolLit(True), n.BoolLit(False))
    assert Checker.check(src) == f"Type Mismatch In Expression: {repr(ctx)}"


def test_120_multiplication_on_string():
    """120. TypeMismatchInExpression: * needs Int or Float"""
    src = 'fun main() {\n  val x = "a" * 2\n}'
    ctx = n.BinaryOp("*", n.StringLit("a"), n.IntLit(2))
    assert Checker.check(src) == f"Type Mismatch In Expression: {repr(ctx)}"


def test_121_division_by_string():
    """121. TypeMismatchInExpression: the right operand of / must be numeric"""
    src = 'fun main() {\n  val x = 1 / "a"\n}'
    ctx = n.BinaryOp("/", n.IntLit(1), n.StringLit("a"))
    assert Checker.check(src) == f"Type Mismatch In Expression: {repr(ctx)}"


def test_122_modulus_with_float_right_operand():
    """122. TypeMismatchInExpression: both operands of % must be Int"""
    src = "fun main() {\n  val x = 5 % 2.0\n}"
    ctx = n.BinaryOp("%", n.IntLit(5), n.FloatLit(2.0))
    assert Checker.check(src) == f"Type Mismatch In Expression: {repr(ctx)}"


def test_123_modulus_on_boolean():
    """123. TypeMismatchInExpression: % does not accept Boolean"""
    src = "fun main() {\n  val x = true % 2\n}"
    ctx = n.BinaryOp("%", n.BoolLit(True), n.IntLit(2))
    assert Checker.check(src) == f"Type Mismatch In Expression: {repr(ctx)}"


def test_124_ordering_int_against_boolean():
    """124. TypeMismatchInExpression: < does not accept Boolean"""
    src = "fun main() {\n  val b = 1 < true\n}"
    ctx = n.BinaryOp("<", n.IntLit(1), n.BoolLit(True))
    assert Checker.check(src) == f"Type Mismatch In Expression: {repr(ctx)}"


def test_125_ordering_two_booleans():
    """125. TypeMismatchInExpression: Boolean has no ordering"""
    src = "fun main() {\n  val b = true <= false\n}"
    ctx = n.BinaryOp("<=", n.BoolLit(True), n.BoolLit(False))
    assert Checker.check(src) == f"Type Mismatch In Expression: {repr(ctx)}"


def test_126_ordering_float_against_string():
    """126. TypeMismatchInExpression: > does not accept String"""
    src = 'fun main() {\n  val b = 1.5 > "a"\n}'
    ctx = n.BinaryOp(">", n.FloatLit(1.5), n.StringLit("a"))
    assert Checker.check(src) == f"Type Mismatch In Expression: {repr(ctx)}"


def test_127_ordering_two_data_class_values():
    """127. TypeMismatchInExpression: data classes have no ordering"""
    src = (
        "data class P(x: Int)\n"
        "fun main() {\n"
        "  val b = P(1) < P(2)\n"
        "}"
    )
    ctx = n.BinaryOp(
        "<", n.CallExpr("P", [n.IntLit(1)]), n.CallExpr("P", [n.IntLit(2)])
    )
    assert Checker.check(src) == f"Type Mismatch In Expression: {repr(ctx)}"


def test_128_logical_and_with_string_left_operand():
    """128. TypeMismatchInExpression: && does not accept String"""
    src = 'fun main() {\n  val b = "a" && true\n}'
    ctx = n.BinaryOp("&&", n.StringLit("a"), n.BoolLit(True))
    assert Checker.check(src) == f"Type Mismatch In Expression: {repr(ctx)}"


def test_129_logical_or_with_float_right_operand():
    """129. TypeMismatchInExpression: || does not accept Float"""
    src = "fun main() {\n  val b = true || 1.5\n}"
    ctx = n.BinaryOp("||", n.BoolLit(True), n.FloatLit(1.5))
    assert Checker.check(src) == f"Type Mismatch In Expression: {repr(ctx)}"


def test_130_not_on_string():
    """130. TypeMismatchInExpression: ! does not accept String"""
    src = 'fun main() {\n  val b = !"a"\n}'
    ctx = n.UnaryOp("!", n.StringLit("a"))
    assert Checker.check(src) == f"Type Mismatch In Expression: {repr(ctx)}"


def test_131_not_on_float():
    """131. TypeMismatchInExpression: ! does not accept Float"""
    src = "fun main() {\n  val b = !1.5\n}"
    ctx = n.UnaryOp("!", n.FloatLit(1.5))
    assert Checker.check(src) == f"Type Mismatch In Expression: {repr(ctx)}"


def test_132_not_on_data_class():
    """132. TypeMismatchInExpression: ! does not accept a data class value"""
    src = "data class P(x: Int)\nfun main() {\n  val b = !P(1)\n}"
    ctx = n.UnaryOp("!", n.CallExpr("P", [n.IntLit(1)]))
    assert Checker.check(src) == f"Type Mismatch In Expression: {repr(ctx)}"


def test_133_equality_int_and_boolean():
    """133. TypeMismatchInExpression: Int and Boolean are not comparable"""
    src = "fun main() {\n  val b = 1 == true\n}"
    ctx = n.BinaryOp("==", n.IntLit(1), n.BoolLit(True))
    assert Checker.check(src) == f"Type Mismatch In Expression: {repr(ctx)}"


def test_134_inequality_float_and_string():
    """134. TypeMismatchInExpression: Float and String are not comparable"""
    src = 'fun main() {\n  val b = 1.5 != "a"\n}'
    ctx = n.BinaryOp("!=", n.FloatLit(1.5), n.StringLit("a"))
    assert Checker.check(src) == f"Type Mismatch In Expression: {repr(ctx)}"


def test_135_equality_boolean_and_string():
    """135. TypeMismatchInExpression: Boolean and String are not comparable"""
    src = 'fun main() {\n  val b = true == "a"\n}'
    ctx = n.BinaryOp("==", n.BoolLit(True), n.StringLit("a"))
    assert Checker.check(src) == f"Type Mismatch In Expression: {repr(ctx)}"


def test_136_equality_data_class_and_int():
    """136. TypeMismatchInExpression: a data class only compares to its own type"""
    src = "data class P(x: Int)\nfun main() {\n  val b = P(1) == 1\n}"
    ctx = n.BinaryOp("==", n.CallExpr("P", [n.IntLit(1)]), n.IntLit(1))
    assert Checker.check(src) == f"Type Mismatch In Expression: {repr(ctx)}"


def test_137_postfix_increment_on_boolean():
    """137. TypeMismatchInExpression: ++ does not accept Boolean"""
    src = "fun main() {\n  var b = true\n  b++\n}"
    ctx = n.PostfixOp("++", n.Id("b"))
    assert Checker.check(src) == f"Type Mismatch In Expression: {repr(ctx)}"


def test_138_prefix_increment_on_float():
    """138. TypeMismatchInExpression: prefix ++ does not accept Float"""
    src = "fun main() {\n  var f = 1.5\n  ++f\n}"
    ctx = n.UnaryOp("++", n.Id("f"))
    assert Checker.check(src) == f"Type Mismatch In Expression: {repr(ctx)}"


def test_139_unary_minus_on_string():
    """139. TypeMismatchInExpression: unary - does not accept String"""
    src = 'fun main() {\n  val x = -"a"\n}'
    ctx = n.UnaryOp("-", n.StringLit("a"))
    assert Checker.check(src) == f"Type Mismatch In Expression: {repr(ctx)}"


def test_140_unary_plus_on_boolean():
    """140. TypeMismatchInExpression: unary + does not accept Boolean"""
    src = "fun main() {\n  val x = +true\n}"
    ctx = n.UnaryOp("+", n.BoolLit(True))
    assert Checker.check(src) == f"Type Mismatch In Expression: {repr(ctx)}"


def test_141_unary_minus_on_data_class():
    """141. TypeMismatchInExpression: unary - does not accept a data class"""
    src = "data class P(x: Int)\nfun main() {\n  val x = -P(1)\n}"
    ctx = n.UnaryOp("-", n.CallExpr("P", [n.IntLit(1)]))
    assert Checker.check(src) == f"Type Mismatch In Expression: {repr(ctx)}"


def test_142_range_with_float_variable():
    """142. TypeMismatchInStatement: range bounds must be Int"""
    src = (
        "fun main() {\n"
        "  val a = 1.5\n"
        "  for (i in a..3) {\n"
        "    printInt(i)\n"
        "  }\n"
        "}"
    )
    ctx = n.For(
        "i",
        n.Id("a"),
        n.IntLit(3),
        n.Block([n.ExprStmt(n.CallExpr("printInt", [n.Id("i")]))]),
    )
    assert Checker.check(src) == f"Type Mismatch In Statement: {repr(ctx)}"


def test_143_range_with_boolean_bound():
    """143. TypeMismatchInStatement: Boolean is not a valid range bound"""
    src = "fun main() {\n  for (i in true..3) {\n    printInt(i)\n  }\n}"
    ctx = n.For(
        "i",
        n.BoolLit(True),
        n.IntLit(3),
        n.Block([n.ExprStmt(n.CallExpr("printInt", [n.Id("i")]))]),
    )
    assert Checker.check(src) == f"Type Mismatch In Statement: {repr(ctx)}"


# =========================================================================== #
#  144-168  Control flow and when                                             #
# =========================================================================== #
def test_144_empty_program():
    """144. Valid: an empty program has nothing to check"""
    src = ""
    assert Checker.check(src) == "Static checking passed"


def test_145_program_without_main():
    """145. Valid: a missing main is not a static error"""
    src = "fun helper(): Int {\n  return 1\n}"
    assert Checker.check(src) == "Static checking passed"


def test_146_empty_bodies_and_blocks():
    """146. Valid: empty function bodies and empty blocks"""
    src = "fun f() {\n}\nfun main() {\n  f()\n  {\n  }\n}"
    assert Checker.check(src) == "Static checking passed"


def test_147_empty_when_statement():
    """147. Valid: a when with no branches"""
    src = "fun main() {\n  when (1) { }\n}"
    assert Checker.check(src) == "Static checking passed"


def test_148_when_statement_without_else():
    """148. Valid: else is optional in a when statement"""
    src = (
        "fun main() {\n"
        "  when (1) {\n"
        "    1 -> printInt(1)\n"
        "    2 -> printInt(2)\n"
        "  }\n"
        "}"
    )
    assert Checker.check(src) == "Static checking passed"


def test_149_conditionless_when_statement_without_else():
    """149. Valid: guard-only when statement without else"""
    src = (
        "fun main() {\n"
        "  val a = 1\n"
        "  when {\n"
        "    a > 0 -> printInt(1)\n"
        "  }\n"
        "}"
    )
    assert Checker.check(src) == "Static checking passed"


def test_150_when_expression_requires_else():
    """150. TypeMismatchInExpression: a when expression needs an else branch"""
    src = "fun main() {\n  val x = when (1) { 1 -> 10 }\n}"
    ctx = n.WhenExpr(n.IntLit(1), [n.WhenBranch([n.IntLit(1)], n.IntLit(10))])
    assert Checker.check(src) == f"Type Mismatch In Expression: {repr(ctx)}"


def test_151_when_expression_branch_types_differ():
    """151. TypeMismatchInExpression: every when-expression branch has one type"""
    src = 'fun main() {\n  val x = when (1) { 1 -> 10; else -> "a" }\n}'
    ctx = n.WhenExpr(
        n.IntLit(1),
        [
            n.WhenBranch([n.IntLit(1)], n.IntLit(10)),
            n.WhenBranch(None, n.StringLit("a")),
        ],
    )
    assert Checker.check(src) == f"Type Mismatch In Expression: {repr(ctx)}"


def test_152_two_else_branches():
    """152. TypeMismatchInStatement: at most one else branch is allowed"""
    src = (
        "fun main() {\n"
        "  when (1) {\n"
        "    1 -> printInt(1)\n"
        "    else -> printInt(2)\n"
        "    else -> printInt(3)\n"
        "  }\n"
        "}"
    )
    ctx = n.When(
        n.IntLit(1),
        [
            n.WhenBranch(
                [n.IntLit(1)], n.ExprStmt(n.CallExpr("printInt", [n.IntLit(1)]))
            ),
            n.WhenBranch(None, n.ExprStmt(n.CallExpr("printInt", [n.IntLit(2)]))),
            n.WhenBranch(None, n.ExprStmt(n.CallExpr("printInt", [n.IntLit(3)]))),
        ],
    )
    assert Checker.check(src) == f"Type Mismatch In Statement: {repr(ctx)}"


def test_153_nested_when():
    """153. Valid: a when statement as the body of another when branch"""
    src = (
        "fun main() {\n"
        "  val a = 1\n"
        "  when (a) {\n"
        "    1 -> when (a) { 1 -> printInt(1); else -> printInt(0) }\n"
        "    else -> printInt(2)\n"
        "  }\n"
        "}"
    )
    assert Checker.check(src) == "Static checking passed"


def test_154_nested_for_loops_with_break_and_continue():
    """154. Valid: break and continue bind to the innermost loop"""
    src = (
        "fun main() {\n"
        "  for (i in 0..3) {\n"
        "    for (j in 0..3) {\n"
        "      if (j == 1) {\n"
        "        break\n"
        "      }\n"
        "      continue\n"
        "    }\n"
        "  }\n"
        "}"
    )
    assert Checker.check(src) == "Static checking passed"


def test_155_while_nested_inside_for():
    """155. Valid: a while loop inside a for body"""
    src = (
        "fun main() {\n"
        "  for (i in 0..3) {\n"
        "    var k = 0\n"
        "    while (k < 3) {\n"
        "      k++\n"
        "      if (k == 2) {\n"
        "        break\n"
        "      }\n"
        "    }\n"
        "  }\n"
        "}"
    )
    assert Checker.check(src) == "Static checking passed"


def test_156_if_else_if_chain():
    """156. Valid: chained else-if branches"""
    src = (
        "fun main() {\n"
        "  val a = 1\n"
        "  if (a > 0) {\n"
        "    printInt(1)\n"
        "  } else if (a < 0) {\n"
        "    printInt(-1)\n"
        "  } else {\n"
        "    printInt(0)\n"
        "  }\n"
        "}"
    )
    assert Checker.check(src) == "Static checking passed"


def test_157_dangling_else_binds_to_nearest_if():
    """157. Valid: nested ifs without braces"""
    src = (
        "fun main() {\n"
        "  val a = true\n"
        "  val b = true\n"
        "  if (a) if (b) printInt(1) else printInt(2)\n"
        "}"
    )
    assert Checker.check(src) == "Static checking passed"


def test_158_deeply_nested_block_shadowing():
    """158. Valid: each nested block may shadow the enclosing name"""
    src = (
        "fun main() {\n"
        "  val x = 1\n"
        "  {\n"
        "    val x = 2\n"
        "    {\n"
        "      val x = 3\n"
        "      printInt(x)\n"
        "    }\n"
        "    printInt(x)\n"
        "  }\n"
        "  printInt(x)\n"
        "}"
    )
    assert Checker.check(src) == "Static checking passed"


def test_159_single_statement_loop_and_if_bodies():
    """159. Valid: bodies without braces"""
    src = (
        "fun main() {\n"
        "  var i = 0\n"
        "  while (i < 3) i++\n"
        "  for (j in 0..2) printInt(j)\n"
        "  if (i > 0) printInt(i) else printInt(0)\n"
        "}"
    )
    assert Checker.check(src) == "Static checking passed"


def test_160_when_branch_with_block_body():
    """160. Valid: a block groups several statements in one branch"""
    src = (
        "fun main() {\n"
        "  when (1) {\n"
        "    1 -> {\n"
        "      val a = 1\n"
        "      printInt(a)\n"
        "    }\n"
        "    else -> printInt(0)\n"
        "  }\n"
        "}"
    )
    assert Checker.check(src) == "Static checking passed"


def test_161_when_subject_float():
    """161. Valid: a Float subject with Float labels"""
    src = (
        "fun main() {\n"
        "  when (1.5) {\n"
        "    1.5 -> printInt(1)\n"
        "    else -> printInt(0)\n"
        "  }\n"
        "}"
    )
    assert Checker.check(src) == "Static checking passed"


def test_162_when_subject_string():
    """162. Valid: a String subject with String labels"""
    src = (
        "fun main() {\n"
        "  when (\"a\") {\n"
        '    "a" -> printInt(1)\n'
        "    else -> printInt(0)\n"
        "  }\n"
        "}"
    )
    assert Checker.check(src) == "Static checking passed"


def test_163_when_subject_boolean():
    """163. Valid: a Boolean subject with Boolean labels"""
    src = (
        "fun main() {\n"
        "  when (true) {\n"
        "    true -> printInt(1)\n"
        "    else -> printInt(0)\n"
        "  }\n"
        "}"
    )
    assert Checker.check(src) == "Static checking passed"


def test_164_when_label_promotes_int_to_float():
    """164. Valid: an Int label matches a Float subject by promotion"""
    src = (
        "fun main() {\n"
        "  when (1.5) {\n"
        "    1 -> printInt(1)\n"
        "    else -> printInt(0)\n"
        "  }\n"
        "}"
    )
    assert Checker.check(src) == "Static checking passed"


def test_165_when_subject_is_data_class():
    """165. TypeMismatchInStatement: the subject must be a comparable type"""
    src = (
        "data class P(x: Int)\n"
        "fun main() {\n"
        "  when (P(1)) {\n"
        "    else -> printInt(0)\n"
        "  }\n"
        "}"
    )
    ctx = n.When(
        n.CallExpr("P", [n.IntLit(1)]),
        [n.WhenBranch(None, n.ExprStmt(n.CallExpr("printInt", [n.IntLit(0)])))],
    )
    assert Checker.check(src) == f"Type Mismatch In Statement: {repr(ctx)}"


def test_166_when_boolean_label_for_int_subject():
    """166. TypeMismatchInExpression: Boolean label against an Int subject"""
    src = (
        "fun main() {\n"
        "  when (1) {\n"
        "    true -> printInt(1)\n"
        "    else -> printInt(0)\n"
        "  }\n"
        "}"
    )
    ctx = n.BoolLit(True)
    assert Checker.check(src) == f"Type Mismatch In Expression: {repr(ctx)}"


def test_167_second_label_of_a_branch_is_wrong():
    """167. TypeMismatchInExpression: every label in a branch is checked"""
    src = (
        "fun main() {\n"
        "  when (1) {\n"
        '    1, "b" -> printInt(1)\n'
        "    else -> printInt(0)\n"
        "  }\n"
        "}"
    )
    ctx = n.StringLit("b")
    assert Checker.check(src) == f"Type Mismatch In Expression: {repr(ctx)}"


def test_168_conditionless_when_guard_is_string():
    """168. TypeMismatchInExpression: guards must be Boolean"""
    src = (
        "fun main() {\n"
        "  when {\n"
        '    "a" -> printInt(1)\n'
        "    else -> printInt(0)\n"
        "  }\n"
        "}"
    )
    ctx = n.StringLit("a")
    assert Checker.check(src) == f"Type Mismatch In Expression: {repr(ctx)}"


# =========================================================================== #
#  169-188  Data classes                                                      #
# =========================================================================== #
def test_169_empty_data_class():
    """169. Valid: a data class with zero members"""
    src = (
        "data class Empty()\n"
        "fun main() {\n"
        "  val e = Empty()\n"
        "  printBool(e == Empty())\n"
        "}"
    )
    assert Checker.check(src) == "Static checking passed"


def test_170_empty_data_class_called_with_arguments():
    """170. TypeMismatchInExpression: an empty data class takes no arguments"""
    src = "data class Empty()\nfun main() {\n  val e = Empty(1)\n}"
    ctx = n.CallExpr("Empty", [n.IntLit(1)])
    assert Checker.check(src) == f"Type Mismatch In Expression: {repr(ctx)}"


def test_171_data_class_with_every_primitive_member():
    """171. Valid: Int, Float, Boolean and String members"""
    src = (
        "data class All(i: Int, f: Float, b: Boolean, s: String)\n"
        "fun main() {\n"
        '  val a = All(1, 1.5, true, "x")\n'
        "  printInt(a.i)\n"
        "  printFloat(a.f)\n"
        "  printBool(a.b)\n"
        "  printString(a.s)\n"
        "}"
    )
    assert Checker.check(src) == "Static checking passed"


def test_172_constructor_argument_widening():
    """172. Valid: an Int argument widens to a Float member"""
    src = (
        "data class P(f: Float)\n"
        "fun main() {\n"
        "  val p = P(1)\n"
        "  printFloat(p.f)\n"
        "}"
    )
    assert Checker.check(src) == "Static checking passed"


def test_173_constructor_arguments_may_be_any_expression():
    """173. Valid: literals, variables, arithmetic and calls as arguments"""
    src = (
        "data class P(x: Int, y: Int)\n"
        "fun mk(): Int {\n"
        "  return 3\n"
        "}\n"
        "fun main() {\n"
        "  val a = 1\n"
        "  val p = P(a + 1, mk())\n"
        "  printInt(p.x)\n"
        "}"
    )
    assert Checker.check(src) == "Static checking passed"


def test_174_three_level_member_chain():
    """174. Valid: member access chained through nested data classes"""
    src = (
        "data class A(v: Int)\n"
        "data class B(a: A)\n"
        "data class C(b: B)\n"
        "fun main() {\n"
        "  val c = C(B(A(1)))\n"
        "  printInt(c.b.a.v)\n"
        "}"
    )
    assert Checker.check(src) == "Static checking passed"


def test_175_member_access_on_a_call_result():
    """175. Valid: getPoint().x when the call returns a data class"""
    src = (
        "data class P(x: Int, y: Int)\n"
        "fun getPoint(): P {\n"
        "  return P(1, 2)\n"
        "}\n"
        "fun main() {\n"
        "  printInt(getPoint().x)\n"
        "}"
    )
    assert Checker.check(src) == "Static checking passed"


def test_176_nested_member_assignment():
    """176. Valid: assigning through a var-rooted member chain"""
    src = (
        "data class A(v: Int)\n"
        "data class B(a: A)\n"
        "fun main() {\n"
        "  var b = B(A(1))\n"
        "  b.a.v = 5\n"
        "  printInt(b.a.v)\n"
        "}"
    )
    assert Checker.check(src) == "Static checking passed"


def test_177_data_class_as_parameter_and_return_type():
    """177. Valid: passing and returning data class values"""
    src = (
        "data class P(x: Int)\n"
        "fun idp(p: P): P {\n"
        "  return p\n"
        "}\n"
        "fun main() {\n"
        "  printInt(idp(P(1)).x)\n"
        "}"
    )
    assert Checker.check(src) == "Static checking passed"


def test_178_data_class_var_without_initializer():
    """178. Valid: var of a data class type assigned later"""
    src = (
        "data class P(x: Int)\n"
        "fun main() {\n"
        "  var p: P\n"
        "  p = P(1)\n"
        "  printInt(p.x)\n"
        "}"
    )
    assert Checker.check(src) == "Static checking passed"


def test_179_wrong_data_class_as_argument():
    """179. TypeMismatchInExpression: data class types are not interchangeable"""
    src = (
        "data class A(x: Int)\n"
        "data class B(x: Int)\n"
        "fun f(a: A) {\n"
        "}\n"
        "fun main() {\n"
        "  f(B(1))\n"
        "}"
    )
    ctx = n.CallExpr("f", [n.CallExpr("B", [n.IntLit(1)])])
    assert Checker.check(src) == f"Type Mismatch In Expression: {repr(ctx)}"


def test_180_returning_the_wrong_data_class():
    """180. TypeMismatchInStatement: return type must be the declared class"""
    src = (
        "data class A(x: Int)\n"
        "data class B(x: Int)\n"
        "fun f(): A {\n"
        "  return B(1)\n"
        "}"
    )
    ctx = n.Return(n.CallExpr("B", [n.IntLit(1)]))
    assert Checker.check(src) == f"Type Mismatch In Statement: {repr(ctx)}"


def test_181_assigning_a_different_data_class():
    """181. TypeMismatchInStatement: assignment needs the same data class"""
    src = (
        "data class A(x: Int)\n"
        "data class B(x: Int)\n"
        "fun main() {\n"
        "  var a = A(1)\n"
        "  a = B(2)\n"
        "}"
    )
    ctx = n.Assign(n.Id("a"), n.CallExpr("B", [n.IntLit(2)]))
    assert Checker.check(src) == f"Type Mismatch In Statement: {repr(ctx)}"


def test_182_member_access_on_boolean():
    """182. TypeMismatchInExpression: Boolean has no members"""
    src = "fun main() {\n  val b = true\n  printBool(b.v)\n}"
    ctx = n.MemberAccess(n.Id("b"), "v")
    assert Checker.check(src) == f"Type Mismatch In Expression: {repr(ctx)}"


def test_183_member_access_on_string_literal():
    """183. TypeMismatchInExpression: String has no members"""
    src = 'fun main() {\n  printInt("abc".length)\n}'
    ctx = n.MemberAccess(n.StringLit("abc"), "length")
    assert Checker.check(src) == f"Type Mismatch In Expression: {repr(ctx)}"


def test_184_member_access_on_unit_call_result():
    """184. TypeMismatchInExpression: a Unit result has no members"""
    src = "fun f() {\n}\nfun main() {\n  printInt(f().x)\n}"
    ctx = n.MemberAccess(n.CallExpr("f", []), "x")
    assert Checker.check(src) == f"Type Mismatch In Expression: {repr(ctx)}"


def test_185_primitive_argument_for_data_class_member():
    """185. TypeMismatchInExpression: a data class member needs a constructor call"""
    src = (
        "data class A(x: Int)\n"
        "data class B(a: A)\n"
        "fun main() {\n"
        "  val b = B(1)\n"
        "}"
    )
    ctx = n.CallExpr("B", [n.IntLit(1)])
    assert Checker.check(src) == f"Type Mismatch In Expression: {repr(ctx)}"


def test_186_chained_member_access_unknown_member():
    """186. TypeMismatchInExpression: unknown member deep in a chain"""
    src = (
        "data class Point(x: Int, y: Int)\n"
        "data class Line(a: Point, b: Point)\n"
        "fun main() {\n"
        "  val l = Line(Point(1, 2), Point(3, 4))\n"
        "  printInt(l.a.z)\n"
        "}"
    )
    ctx = n.MemberAccess(n.MemberAccess(n.Id("l"), "a"), "z")
    assert Checker.check(src) == f"Type Mismatch In Expression: {repr(ctx)}"


def test_187_increment_member_of_a_val():
    """187. TypeMismatchInStatement: a member of a val is not assignable"""
    src = (
        "data class P(x: Int)\n"
        "fun main() {\n"
        "  val p = P(1)\n"
        "  p.x++\n"
        "}"
    )
    ctx = n.PostfixOp("++", n.MemberAccess(n.Id("p"), "x"))
    assert Checker.check(src) == f"Type Mismatch In Statement: {repr(ctx)}"


def test_188_increment_a_float_member():
    """188. TypeMismatchInExpression: ++ needs an Int member"""
    src = (
        "data class P(f: Float)\n"
        "fun main() {\n"
        "  var p = P(1.5)\n"
        "  p.f++\n"
        "}"
    )
    ctx = n.PostfixOp("++", n.MemberAccess(n.Id("p"), "f"))
    assert Checker.check(src) == f"Type Mismatch In Expression: {repr(ctx)}"


# =========================================================================== #
#  189-203  Scope and redeclaration                                           #
# =========================================================================== #
def test_189_redeclare_in_while_body():
    """189. Redeclared: two declarations in one while body scope"""
    src = "fun main() {\n  while (true) {\n    val a = 1\n    val a = 2\n  }\n}"
    assert Checker.check(src) == "Redeclared Variable: a"


def test_190_redeclare_in_when_branch_block():
    """190. Redeclared: two declarations in one when branch block"""
    src = (
        "fun main() {\n"
        "  when (1) {\n"
        "    1 -> {\n"
        "      val a = 1\n"
        "      val a = 2\n"
        "    }\n"
        "    else -> printInt(0)\n"
        "  }\n"
        "}"
    )
    assert Checker.check(src) == "Redeclared Variable: a"


def test_191_redeclare_in_else_branch():
    """191. Redeclared: the else branch is its own scope but still one scope"""
    src = (
        "fun main() {\n"
        "  if (true) {\n"
        "    printInt(1)\n"
        "  } else {\n"
        "    val b = 1\n"
        "    var b = 2\n"
        "  }\n"
        "}"
    )
    assert Checker.check(src) == "Redeclared Variable: b"


def test_192_third_parameter_duplicates_the_first():
    """192. Redeclared: duplicate detected anywhere in the parameter list"""
    src = "fun f(a: Int, b: Int, a: Int) {\n}"
    assert Checker.check(src) == "Redeclared Parameter: a"


def test_193_third_member_duplicates_the_first():
    """193. Redeclared: duplicate detected anywhere in the member list"""
    src = "data class P(x: Int, y: Int, x: Int)"
    assert Checker.check(src) == "Redeclared Member: x"


def test_194_shadowing_in_while_body():
    """194. Valid: a while body may shadow an outer local"""
    src = (
        "fun main() {\n"
        "  val a = 1\n"
        "  while (true) {\n"
        "    val a = 2\n"
        "    printInt(a)\n"
        "  }\n"
        "  printInt(a)\n"
        "}"
    )
    assert Checker.check(src) == "Static checking passed"


def test_195_sibling_blocks_may_reuse_a_name():
    """195. Valid: two disjoint blocks may declare the same name"""
    src = (
        "fun main() {\n"
        "  if (true) {\n"
        "    val a = 1\n"
        "    printInt(a)\n"
        "  }\n"
        "  if (true) {\n"
        "    val a = 2\n"
        "    printInt(a)\n"
        "  }\n"
        "}"
    )
    assert Checker.check(src) == "Static checking passed"


def test_196_nested_for_loops_reuse_the_loop_variable_name():
    """196. Valid: an inner loop variable shadows the outer one"""
    src = (
        "fun main() {\n"
        "  for (i in 0..2) {\n"
        "    for (i in 0..2) {\n"
        "      printInt(i)\n"
        "    }\n"
        "  }\n"
        "}"
    )
    assert Checker.check(src) == "Static checking passed"


def test_197_parameter_shadowed_in_a_for_body():
    """197. Valid: the for body is nested below the parameter scope"""
    src = (
        "fun f(i: Int) {\n"
        "  for (j in 0..2) {\n"
        "    val i = 5\n"
        "    printInt(i + j)\n"
        "  }\n"
        "}"
    )
    assert Checker.check(src) == "Static checking passed"


def test_198_outer_loop_variable_visible_in_inner_range():
    """198. Valid: the loop variable is usable inside the loop construct"""
    src = (
        "fun main() {\n"
        "  for (i in 0..3) {\n"
        "    for (j in i..3) {\n"
        "      printInt(j)\n"
        "    }\n"
        "  }\n"
        "}"
    )
    assert Checker.check(src) == "Static checking passed"


def test_199_member_name_may_match_a_variable_name():
    """199. Valid: member names live in the data class, not the local scope"""
    src = (
        "data class P(v: Int)\n"
        "fun main() {\n"
        "  val v = 1\n"
        "  val p = P(v)\n"
        "  printInt(p.v)\n"
        "}"
    )
    assert Checker.check(src) == "Static checking passed"


def test_200_for_body_local_not_visible_after_the_loop():
    """200. UndeclaredIdentifier: for body declarations do not escape"""
    src = "fun main() {\n  for (i in 0..3) {\n    val t = 1\n  }\n  printInt(t)\n}"
    assert Checker.check(src) == "Undeclared Identifier: t"


def test_201_when_branch_local_not_visible_after_the_when():
    """201. UndeclaredIdentifier: when branch declarations do not escape"""
    src = (
        "fun main() {\n"
        "  when (1) {\n"
        "    1 -> {\n"
        "      val w = 1\n"
        "    }\n"
        "    else -> printInt(0)\n"
        "  }\n"
        "  printInt(w)\n"
        "}"
    )
    assert Checker.check(src) == "Undeclared Identifier: w"


def test_202_then_branch_local_not_visible_in_else():
    """202. UndeclaredIdentifier: the two if branches are separate scopes"""
    src = (
        "fun main() {\n"
        "  if (true) {\n"
        "    val e = 1\n"
        "  } else {\n"
        "    printInt(e)\n"
        "  }\n"
        "}"
    )
    assert Checker.check(src) == "Undeclared Identifier: e"


def test_203_while_body_local_not_visible_after_the_loop():
    """203. UndeclaredIdentifier: while body declarations do not escape"""
    src = "fun main() {\n  while (false) {\n    val u = 1\n  }\n  printInt(u)\n}"
    assert Checker.check(src) == "Undeclared Identifier: u"


# =========================================================================== #
#  204-227  Type inference                                                    #
# =========================================================================== #
def test_204_integer_anchor_on_the_left_operand():
    """204. Valid: the anchor works on either side of the operator"""
    src = "fun main() {\n  var a\n  val c = 2 + a\n  printInt(c)\n}"
    assert Checker.check(src) == "Static checking passed"


def test_205_integer_anchor_with_minus_and_divide():
    """205. Valid: the anchor applies to all of + - * /"""
    src = (
        "fun main() {\n"
        "  var a\n"
        "  var b\n"
        "  val c = a - 1\n"
        "  val d = 3 / b\n"
        "  printInt(c + d)\n"
        "}"
    )
    assert Checker.check(src) == "Static checking passed"


def test_206_var_fixed_by_constructor_argument():
    """206. Valid: a member type fixes a lone var argument"""
    src = (
        "data class P(f: Float)\n"
        "fun main() {\n"
        "  var a\n"
        "  val p = P(a)\n"
        "  printFloat(p.f)\n"
        "}"
    )
    assert Checker.check(src) == "Static checking passed"


def test_207_var_fixed_by_user_function_argument():
    """207. Valid: a parameter type fixes a lone var argument"""
    src = (
        "fun f(s: String) {\n"
        "  printString(s)\n"
        "}\n"
        "fun main() {\n"
        "  var a\n"
        "  f(a)\n"
        "}"
    )
    assert Checker.check(src) == "Static checking passed"


def test_208_var_fixed_as_boolean_then_used_as_condition():
    """208. Valid: after inference the var is usable at its inferred type"""
    src = (
        "fun main() {\n"
        "  var a\n"
        "  printBool(a)\n"
        "  if (a) {\n"
        "    printInt(1)\n"
        "  }\n"
        "}"
    )
    assert Checker.check(src) == "Static checking passed"


def test_209_var_fixed_by_assignment_from_a_call():
    """209. Valid: the return type of the call fixes the var"""
    src = "fun main() {\n  var d\n  d = readFloat()\n  printFloat(d)\n}"
    assert Checker.check(src) == "Static checking passed"


def test_210_var_fixed_by_assignment_from_another_variable():
    """210. Valid: a typed variable on the right-hand side fixes the var"""
    src = "fun main() {\n  var a = 1\n  var b\n  b = a\n  printInt(b)\n}"
    assert Checker.check(src) == "Static checking passed"


def test_211_use_conflicting_with_the_inferred_type():
    """211. TypeMismatchInExpression: the var is Int after its first usage"""
    src = "fun main() {\n  var a\n  a = 1\n  printString(a)\n}"
    ctx = n.CallExpr("printString", [n.Id("a")])
    assert Checker.check(src) == f"Type Mismatch In Expression: {repr(ctx)}"


def test_212_inferred_float_return_type():
    """212. Valid: the call site sees the inferred Float return type"""
    src = "fun f() {\n  return 1.5\n}\nfun main() {\n  printFloat(f())\n}"
    assert Checker.check(src) == "Static checking passed"


def test_213_inferred_boolean_return_type():
    """213. Valid: an inferred Boolean return type works as a condition"""
    src = (
        "fun f() {\n"
        "  return true\n"
        "}\n"
        "fun main() {\n"
        "  if (f()) {\n"
        "    printInt(1)\n"
        "  }\n"
        "}"
    )
    assert Checker.check(src) == "Static checking passed"


def test_214_inferred_string_return_type():
    """214. Valid: an inferred String return type"""
    src = 'fun f() {\n  return "a"\n}\nfun main() {\n  printString(f())\n}'
    assert Checker.check(src) == "Static checking passed"


def test_215_inferred_data_class_return_type():
    """215. Valid: an inferred data class return type supports member access"""
    src = (
        "data class P(x: Int)\n"
        "fun f() {\n"
        "  return P(1)\n"
        "}\n"
        "fun main() {\n"
        "  printInt(f().x)\n"
        "}"
    )
    assert Checker.check(src) == "Static checking passed"


def test_216_inferred_unit_result_in_arithmetic():
    """216. TypeMismatchInExpression: a Unit result has no arithmetic"""
    src = (
        "fun f() {\n"
        "  printInt(1)\n"
        "}\n"
        "fun main() {\n"
        "  val x = f() + 1\n"
        "}"
    )
    ctx = n.BinaryOp("+", n.CallExpr("f", []), n.IntLit(1))
    assert Checker.check(src) == f"Type Mismatch In Expression: {repr(ctx)}"


def test_217_unit_result_bound_to_a_variable():
    """217. TypeMismatchInStatement: Unit is not a variable type"""
    src = "fun f(): Unit {\n}\nfun main() {\n  val x = f()\n}"
    ctx = n.VarDecl("x", False, None, n.CallExpr("f", []))
    assert Checker.check(src) == f"Type Mismatch In Statement: {repr(ctx)}"


def test_218_unit_result_passed_as_an_argument():
    """218. TypeMismatchInExpression: a Unit result is not an Int argument"""
    src = "fun f() {\n}\nfun main() {\n  printInt(f())\n}"
    ctx = n.CallExpr("printInt", [n.CallExpr("f", [])])
    assert Checker.check(src) == f"Type Mismatch In Expression: {repr(ctx)}"


def test_219_later_return_disagrees_with_the_first():
    """219. TypeMismatchInStatement: Boolean after an inferred Int return type"""
    src = (
        "fun f(c: Boolean) {\n"
        "  if (c) {\n"
        "    return 1\n"
        "  }\n"
        "  return true\n"
        "}"
    )
    ctx = n.Return(n.BoolLit(True))
    assert Checker.check(src) == f"Type Mismatch In Statement: {repr(ctx)}"


def test_220_annotated_var_used_before_assignment():
    """220. Valid: an annotated var has a type even before its first assignment"""
    src = "fun main() {\n  var x: Int\n  printInt(x)\n}"
    assert Checker.check(src) == "Static checking passed"


def test_221_widening_on_assignment_to_a_float_var():
    """221. Valid: Int widens to Float on assignment"""
    src = "fun main() {\n  var f: Float\n  f = 1\n  printFloat(f)\n}"
    assert Checker.check(src) == "Static checking passed"


def test_222_assign_int_to_a_string_variable():
    """222. TypeMismatchInStatement: String is not assignable from Int"""
    src = 'fun main() {\n  var s: String = "a"\n  s = 1\n}'
    ctx = n.Assign(n.Id("s"), n.IntLit(1))
    assert Checker.check(src) == f"Type Mismatch In Statement: {repr(ctx)}"


def test_223_assign_int_to_a_boolean_variable():
    """223. TypeMismatchInStatement: Boolean is not assignable from Int"""
    src = "fun main() {\n  var b = true\n  b = 1\n}"
    ctx = n.Assign(n.Id("b"), n.IntLit(1))
    assert Checker.check(src) == f"Type Mismatch In Statement: {repr(ctx)}"


def test_224_matching_explicit_types_for_every_primitive():
    """224. Valid: annotation and initializer agree for all four primitives"""
    src = (
        "fun main() {\n"
        "  val a: Int = 1\n"
        "  val b: Float = 1.5\n"
        "  val c: Boolean = true\n"
        '  val d: String = "x"\n'
        "  printInt(a)\n"
        "  printFloat(b)\n"
        "  printBool(c)\n"
        "  printString(d)\n"
        "}"
    )
    assert Checker.check(src) == "Static checking passed"


def test_225_string_annotation_with_int_initializer():
    """225. TypeMismatchInStatement: Int initializer for a String annotation"""
    src = "fun main() {\n  val s: String = 1\n}"
    ctx = n.VarDecl("s", False, n.StringType(), n.IntLit(1))
    assert Checker.check(src) == f"Type Mismatch In Statement: {repr(ctx)}"


def test_226_data_class_annotation_with_primitive_initializer():
    """226. TypeMismatchInStatement: Int initializer for a data class annotation"""
    src = "data class P(x: Int)\nfun main() {\n  val p: P = 1\n}"
    ctx = n.VarDecl("p", False, n.ClassType("P"), n.IntLit(1))
    assert Checker.check(src) == f"Type Mismatch In Statement: {repr(ctx)}"


def test_227_inference_from_a_member_access():
    """227. Valid: the member type becomes the inferred variable type"""
    src = (
        "data class P(f: Float)\n"
        "fun main() {\n"
        "  val p = P(1.5)\n"
        "  val q = p.f\n"
        "  printFloat(q)\n"
        "}"
    )
    assert Checker.check(src) == "Static checking passed"


# =========================================================================== #
#  228-234  Return statements                                                 #
# =========================================================================== #
def test_228_return_inside_a_loop():
    """228. Valid: return from within a for body"""
    src = (
        "fun f(): Int {\n"
        "  for (i in 0..3) {\n"
        "    return i\n"
        "  }\n"
        "  return 0\n"
        "}\n"
        "fun main() {\n"
        "  printInt(f())\n"
        "}"
    )
    assert Checker.check(src) == "Static checking passed"


def test_229_return_inside_a_when_branch():
    """229. Valid: return from within a when branch"""
    src = (
        "fun f(c: Int): Int {\n"
        "  when (c) {\n"
        "    1 -> return 1\n"
        "    else -> return 0\n"
        "  }\n"
        "  return 2\n"
        "}\n"
        "fun main() {\n"
        "  printInt(f(1))\n"
        "}"
    )
    assert Checker.check(src) == "Static checking passed"


def test_230_return_inside_a_nested_block():
    """230. Valid: return from within a bare block"""
    src = "fun f(): Int {\n  {\n    return 1\n  }\n}\nfun main() {\n  printInt(f())\n}"
    assert Checker.check(src) == "Static checking passed"


def test_231_typed_function_without_any_return():
    """231. Valid: MKotlin does not require a definite return on every path"""
    src = "fun f(): Int {\n  printInt(1)\n}\nfun main() {\n  printInt(f())\n}"
    assert Checker.check(src) == "Static checking passed"


def test_232_return_boolean_from_a_float_function():
    """232. TypeMismatchInStatement: Boolean is not a Float"""
    src = "fun f(): Float {\n  return true\n}"
    ctx = n.Return(n.BoolLit(True))
    assert Checker.check(src) == f"Type Mismatch In Statement: {repr(ctx)}"


def test_233_wrong_return_type_inside_a_loop():
    """233. TypeMismatchInStatement: returns inside loops are checked too"""
    src = (
        "fun f(): String {\n"
        "  for (i in 0..3) {\n"
        "    return i\n"
        "  }\n"
        '  return "a"\n'
        "}"
    )
    ctx = n.Return(n.Id("i"))
    assert Checker.check(src) == f"Type Mismatch In Statement: {repr(ctx)}"


def test_234_bare_return_inside_a_loop_of_a_unit_function():
    """234. Valid: a value-less return in an inferred Unit function"""
    src = (
        "fun f() {\n"
        "  for (i in 0..3) {\n"
        "    return\n"
        "  }\n"
        "}\n"
        "fun main() {\n"
        "  f()\n"
        "}"
    )
    assert Checker.check(src) == "Static checking passed"


# =========================================================================== #
#  235-248  Calls and arguments                                               #
# =========================================================================== #
def test_235_function_with_four_parameters():
    """235. Valid: one parameter of each primitive type"""
    src = (
        "fun f(a: Int, b: Float, c: Boolean, d: String): Int {\n"
        "  return a\n"
        "}\n"
        "fun main() {\n"
        '  printInt(f(1, 1.5, true, "x"))\n'
        "}"
    )
    assert Checker.check(src) == "Static checking passed"


def test_236_widening_on_a_middle_argument():
    """236. Valid: an Int argument widens to a Float parameter"""
    src = (
        "fun f(a: Int, b: Float): Float {\n"
        "  return b\n"
        "}\n"
        "fun main() {\n"
        "  printFloat(f(1, 2))\n"
        "}"
    )
    assert Checker.check(src) == "Static checking passed"


def test_237_too_many_arguments():
    """237. TypeMismatchInExpression: argument count must match"""
    src = "fun f(a: Int) {\n}\nfun main() {\n  f(1, 2)\n}"
    ctx = n.CallExpr("f", [n.IntLit(1), n.IntLit(2)])
    assert Checker.check(src) == f"Type Mismatch In Expression: {repr(ctx)}"


def test_238_arguments_to_a_zero_parameter_function():
    """238. TypeMismatchInExpression: a zero-parameter function takes nothing"""
    src = "fun f() {\n}\nfun main() {\n  f(1)\n}"
    ctx = n.CallExpr("f", [n.IntLit(1)])
    assert Checker.check(src) == f"Type Mismatch In Expression: {repr(ctx)}"


def test_239_missing_argument_for_a_builtin():
    """239. TypeMismatchInExpression: printInt requires one argument"""
    src = "fun main() {\n  printInt()\n}"
    ctx = n.CallExpr("printInt", [])
    assert Checker.check(src) == f"Type Mismatch In Expression: {repr(ctx)}"


def test_240_argument_passed_to_readint():
    """240. TypeMismatchInExpression: readInt takes no arguments"""
    src = "fun main() {\n  printInt(readInt(1))\n}"
    ctx = n.CallExpr("readInt", [n.IntLit(1)])
    assert Checker.check(src) == f"Type Mismatch In Expression: {repr(ctx)}"


def test_241_wrong_argument_type_for_printbool():
    """241. TypeMismatchInExpression: printBool needs a Boolean"""
    src = "fun main() {\n  printBool(1)\n}"
    ctx = n.CallExpr("printBool", [n.IntLit(1)])
    assert Checker.check(src) == f"Type Mismatch In Expression: {repr(ctx)}"


def test_242_wrong_argument_type_for_printstring():
    """242. TypeMismatchInExpression: printString needs a String"""
    src = "fun main() {\n  printString(1)\n}"
    ctx = n.CallExpr("printString", [n.IntLit(1)])
    assert Checker.check(src) == f"Type Mismatch In Expression: {repr(ctx)}"


def test_243_wrong_argument_type_for_printfloat():
    """243. TypeMismatchInExpression: printFloat needs a number"""
    src = 'fun main() {\n  printFloat("a")\n}'
    ctx = n.CallExpr("printFloat", [n.StringLit("a")])
    assert Checker.check(src) == f"Type Mismatch In Expression: {repr(ctx)}"


def test_244_nested_calls_with_matching_types():
    """244. Valid: the result of a call feeds another call"""
    src = (
        "fun sq(x: Int): Int {\n"
        "  return x * x\n"
        "}\n"
        "fun main() {\n"
        "  printInt(sq(sq(2)))\n"
        "}"
    )
    assert Checker.check(src) == "Static checking passed"


def test_245_nested_call_with_a_wrong_inner_argument():
    """245. TypeMismatchInExpression: the inner call is checked first"""
    src = (
        "fun sq(x: Int): Int {\n"
        "  return x * x\n"
        "}\n"
        "fun main() {\n"
        "  printInt(sq(1.5))\n"
        "}"
    )
    ctx = n.CallExpr("sq", [n.FloatLit(1.5)])
    assert Checker.check(src) == f"Type Mismatch In Expression: {repr(ctx)}"


def test_246_second_argument_has_the_wrong_type():
    """246. TypeMismatchInExpression: every argument position is checked"""
    src = "fun f(a: Int, b: String) {\n}\nfun main() {\n  f(1, 2)\n}"
    ctx = n.CallExpr("f", [n.IntLit(1), n.IntLit(2)])
    assert Checker.check(src) == f"Type Mismatch In Expression: {repr(ctx)}"


def test_247_call_result_as_a_loop_condition():
    """247. Valid: a Boolean-returning call drives a while loop"""
    src = (
        "fun ok(): Boolean {\n"
        "  return true\n"
        "}\n"
        "fun main() {\n"
        "  while (ok()) {\n"
        "    break\n"
        "  }\n"
        "}"
    )
    assert Checker.check(src) == "Static checking passed"


def test_248_int_returning_call_as_a_condition():
    """248. TypeMismatchInStatement: the condition must be Boolean"""
    src = (
        "fun num(): Int {\n"
        "  return 1\n"
        "}\n"
        "fun main() {\n"
        "  if (num()) {\n"
        "    printInt(1)\n"
        "  }\n"
        "}"
    )
    ctx = n.If(
        n.CallExpr("num", []),
        n.Block([n.ExprStmt(n.CallExpr("printInt", [n.IntLit(1)]))]),
        None,
    )
    assert Checker.check(src) == f"Type Mismatch In Statement: {repr(ctx)}"


# =========================================================================== #
#  249-254  MustInLoop                                                        #
# =========================================================================== #
def test_249_break_inside_a_block_inside_a_loop():
    """249. Valid: a bare block does not break the loop context"""
    src = "fun main() {\n  while (true) {\n    {\n      break\n    }\n  }\n}"
    assert Checker.check(src) == "Static checking passed"


def test_250_continue_inside_a_when_inside_a_for():
    """250. Valid: a when inside a loop still has the loop context"""
    src = (
        "fun main() {\n"
        "  for (i in 0..3) {\n"
        "    when (i) {\n"
        "      1 -> continue\n"
        "      else -> printInt(i)\n"
        "    }\n"
        "  }\n"
        "}"
    )
    assert Checker.check(src) == "Static checking passed"


def test_251_break_in_an_else_branch_outside_a_loop():
    """251. MustInLoop: an else branch is not a loop"""
    src = (
        "fun main() {\n"
        "  if (true) {\n"
        "    printInt(1)\n"
        "  } else {\n"
        "    break\n"
        "  }\n"
        "}"
    )
    assert Checker.check(src) == f"Must In Loop: {repr(n.Break())}"


def test_252_loop_context_does_not_leak_across_functions():
    """252. MustInLoop: another function's loop does not help"""
    src = (
        "fun a() {\n"
        "  while (true) {\n"
        "    break\n"
        "  }\n"
        "}\n"
        "fun b() {\n"
        "  continue\n"
        "}"
    )
    assert Checker.check(src) == f"Must In Loop: {repr(n.Continue())}"


def test_253_break_in_a_conditionless_when_outside_a_loop():
    """253. MustInLoop: the guard-only when form is not a loop either"""
    src = (
        "fun main() {\n"
        "  when {\n"
        "    true -> break\n"
        "    else -> printInt(0)\n"
        "  }\n"
        "}"
    )
    assert Checker.check(src) == f"Must In Loop: {repr(n.Break())}"


def test_254_break_after_the_loop_has_ended():
    """254. MustInLoop: the loop context ends with the loop"""
    src = "fun main() {\n  while (true) {\n    printInt(1)\n  }\n  break\n}"
    assert Checker.check(src) == f"Must In Loop: {repr(n.Break())}"


# =========================================================================== #
#  255-260  Traversal order (first error wins)                                #
# =========================================================================== #
def test_255_declarations_are_checked_top_to_bottom():
    """255. The error in the first function is reported"""
    src = (
        "fun f() {\n"
        '  val a = 1 + "a"\n'
        "}\n"
        "fun g() {\n"
        "  val b = true && 1\n"
        "}"
    )
    ctx = n.BinaryOp("+", n.IntLit(1), n.StringLit("a"))
    assert Checker.check(src) == f"Type Mismatch In Expression: {repr(ctx)}"


def test_256_left_operand_is_checked_before_the_right():
    """256. The left sub-expression reports first"""
    src = 'fun main() {\n  val x = (1 + "a") + (2 + true)\n}'
    ctx = n.BinaryOp("+", n.IntLit(1), n.StringLit("a"))
    assert Checker.check(src) == f"Type Mismatch In Expression: {repr(ctx)}"


def test_257_statements_are_checked_in_source_order():
    """257. The first statement reports before the second"""
    src = "fun main() {\n  printInt(y)\n  val b = true && 1\n}"
    assert Checker.check(src) == "Undeclared Identifier: y"


def test_258_arguments_are_checked_left_to_right():
    """258. The first bad argument reports first"""
    src = "fun f(a: Int, b: Int) {\n}\nfun main() {\n  f(undefinedOne, undefinedTwo)\n}"
    assert Checker.check(src) == "Undeclared Identifier: undefinedOne"


def test_259_condition_is_checked_before_the_body():
    """259. The loop condition reports before statements in the body"""
    src = "fun main() {\n  while (1) {\n    printInt(undefinedName)\n  }\n}"
    ctx = n.While(
        n.IntLit(1),
        n.Block([n.ExprStmt(n.CallExpr("printInt", [n.Id("undefinedName")]))]),
    )
    assert Checker.check(src) == f"Type Mismatch In Statement: {repr(ctx)}"


def test_260_members_are_checked_in_declaration_order():
    """260. The first bad member type reports first"""
    src = "data class P(a: Vec, b: Wat)"
    assert Checker.check(src) == "Undeclared Class: Vec"


# =========================================================================== #
#  261-270  Lexical surface and remaining constructs                          #
# =========================================================================== #
def test_261_identifiers_are_case_sensitive():
    """261. UndeclaredIdentifier: myVar and MyVar are different names"""
    src = "fun main() {\n  val myVar = 1\n  printInt(MyVar)\n}"
    assert Checker.check(src) == "Undeclared Identifier: MyVar"


def test_262_underscore_identifiers():
    """262. Valid: identifiers may start with or contain underscores"""
    src = "fun main() {\n  val _x = 1\n  val y_2 = 2\n  printInt(_x + y_2)\n}"
    assert Checker.check(src) == "Static checking passed"


def test_263_integer_literal_with_underscores():
    """263. Valid: readability underscores inside an Int literal"""
    src = "fun main() {\n  val x = 1_000_000\n  printInt(x)\n}"
    assert Checker.check(src) == "Static checking passed"


def test_264_every_float_literal_form():
    """264. Valid: all float literal spellings have type Float"""
    src = (
        "fun main() {\n"
        "  printFloat(1.)\n"
        "  printFloat(.5)\n"
        "  printFloat(1e4)\n"
        "  printFloat(2E-3)\n"
        "  printFloat(3.14f)\n"
        "}"
    )
    assert Checker.check(src) == "Static checking passed"


def test_265_string_with_escape_sequences():
    """265. Valid: escapes do not change the String type"""
    src = 'fun main() {\n  printString("a\\tb\\nc")\n}'
    assert Checker.check(src) == "Static checking passed"


def test_266_comments_are_ignored():
    """266. Valid: line and block comments carry no semantics"""
    src = (
        "// leading comment\n"
        "fun main() { /* inline */\n"
        "  val x = 1 // trailing\n"
        "  printInt(x)\n"
        "}\n"
        "/* block\n"
        "   comment */"
    )
    assert Checker.check(src) == "Static checking passed"


def test_267_semicolon_separated_statements():
    """267. Valid: two statements on one line"""
    src = "fun main() {\n  val x = 1; val y = 2\n  printInt(x + y)\n}"
    assert Checker.check(src) == "Static checking passed"


def test_268_redeclaration_across_a_semicolon():
    """268. Redeclared: the separator does not create a new scope"""
    src = "fun main() {\n  val x = 1; val x = 2\n}"
    assert Checker.check(src) == "Redeclared Variable: x"


def test_269_multiple_separators_between_declarations():
    """269. Valid: sep+ allows repeated semicolons between declarations"""
    src = "fun a() { } ;; fun main() { a() }"
    assert Checker.check(src) == "Static checking passed"


def test_271_main_may_declare_parameters():
    """271. Valid: parameters on main are not a static error"""
    src = "fun main(x: Int) {\n  printInt(x)\n}"
    assert Checker.check(src) == "Static checking passed"


def test_272_function_name_used_as_a_value():
    """272. UndeclaredIdentifier: a bare function name is not a variable"""
    src = "fun f(): Int {\n  return 1\n}\nfun main() {\n  val x = f\n}"
    assert Checker.check(src) == "Undeclared Identifier: f"


def test_273_data_class_name_used_as_a_value():
    """273. UndeclaredIdentifier: a bare data class name is not a variable"""
    src = "data class P(x: Int)\nfun main() {\n  val x = P\n}"
    assert Checker.check(src) == "Undeclared Identifier: P"


# =========================================================================== #
#  274-306  Cases settled by the course forum Q&A                             #
#                                                                             #
#  Each test names the forum question it comes from so the expectation can    #
#  be traced back to the ruling that fixed it.                                #
# =========================================================================== #
def test_274_annotation_checked_before_initializer():
    """274. Q2: the type position reports before the call position"""
    src = "fun main() {\n  val p: Vec = Vec(1, 2)\n}"
    assert Checker.check(src) == "Undeclared Class: Vec"


def test_275_unknown_name_in_call_position():
    """275. Q2/Q17: a call to an unknown name is an unknown function call"""
    src = "fun main() {\n  val p = Vec(1, 2)\n}"
    assert Checker.check(src) == "Undeclared Function: Vec"


def test_276_loop_variable_shadowed_by_a_braceless_body():
    """276. Q5: for (i in 0..3) var i = 4 declares in a nested scope"""
    src = "fun main() {\n  for (i in 0..3) var i = 4\n}"
    assert Checker.check(src) == "Static checking passed"


def test_277_increment_a_val():
    """277. Q7: only assignability fails, so the statement error uses PostfixOp"""
    src = "fun main() {\n  val x = 1\n  x++\n}"
    ctx = n.PostfixOp("++", n.Id("x"))
    assert Checker.check(src) == f"Type Mismatch In Statement: {repr(ctx)}"


def test_278_prefix_increment_a_val():
    """278. Q7: the prefix form reports on the UnaryOp node"""
    src = "fun main() {\n  val i = 0\n  ++i\n}"
    ctx = n.UnaryOp("++", n.Id("i"))
    assert Checker.check(src) == f"Type Mismatch In Statement: {repr(ctx)}"


def test_279_increment_inside_a_larger_expression():
    """279. Q7: the node is the ++ itself, not the enclosing declaration"""
    src = "fun main() {\n  val i = 0\n  val x = i++ + 1\n}"
    ctx = n.PostfixOp("++", n.Id("i"))
    assert Checker.check(src) == f"Type Mismatch In Statement: {repr(ctx)}"


def test_280_increment_wrong_type_and_not_assignable():
    """280. Q7: the type check runs first, so this is an expression error"""
    src = "fun main() {\n  val f = 1.0\n  f++\n}"
    ctx = n.PostfixOp("++", n.Id("f"))
    assert Checker.check(src) == f"Type Mismatch In Expression: {repr(ctx)}"


def test_281_decrement_the_loop_variable():
    """281. Q7: a loop variable is Int but not assignable"""
    src = "fun main() {\n  for (i in 0..3) {\n    i--\n  }\n}"
    ctx = n.PostfixOp("--", n.Id("i"))
    assert Checker.check(src) == f"Type Mismatch In Statement: {repr(ctx)}"


def test_282_recursion_with_an_inferred_return_type():
    """282. Q11: multiple passes resolve the recursive call to Int"""
    src = (
        "fun fact(k: Int) {\n"
        "  if (k > 1) {\n"
        "    return k * fact(k - 1)\n"
        "  }\n"
        "  return 1\n"
        "}\n"
        "fun main() {\n"
        "  printInt(fact(3))\n"
        "}"
    )
    assert Checker.check(src) == "Static checking passed"


def test_283_bare_return_mixed_with_a_value_return():
    """283. Q11: return 5 makes the type Int, so the bare return is illegal"""
    src = (
        "fun f(k: Int) {\n"
        "  if (k > 0) {\n"
        "    return\n"
        "  }\n"
        "  return 5\n"
        "}"
    )
    ctx = n.Return(None)
    assert Checker.check(src) == f"Type Mismatch In Statement: {repr(ctx)}"


def test_284_unknown_var_in_a_compound_argument():
    """284. Q12: the parameter type does not reach inside -a"""
    src = (
        "fun foo(x: Int) {\n"
        "}\n"
        "fun main() {\n"
        "  var a\n"
        "  foo(-a)\n"
        "}"
    )
    ctx = n.UnaryOp("-", n.Id("a"))
    assert Checker.check(src) == f"Type Cannot Be Inferred: {repr(ctx)}"


def test_285_member_access_on_an_uninferred_var():
    """285. Q12: inference fails before the receiver kind is checked"""
    src = "fun main() {\n  var obj\n  val x = obj.m\n}"
    ctx = n.MemberAccess(n.Id("obj"), "m")
    assert Checker.check(src) == f"Type Cannot Be Inferred: {repr(ctx)}"


def test_286_uninferred_var_as_an_if_condition():
    """286. Q13: the node is the condition expression, not the If"""
    src = "fun main() {\n  var a\n  if (a) { }\n}"
    ctx = n.Id("a")
    assert Checker.check(src) == f"Type Cannot Be Inferred: {repr(ctx)}"


def test_287_uninferred_var_as_a_while_condition():
    """287. Q13: a condition is not an inference context"""
    src = "fun main() {\n  var a\n  while (a) { }\n}"
    ctx = n.Id("a")
    assert Checker.check(src) == f"Type Cannot Be Inferred: {repr(ctx)}"


def test_288_uninferred_var_as_a_when_subject():
    """288. Q13: a subject is not an inference context"""
    src = "fun main() {\n  var a\n  when (a) { else -> printInt(0) }\n}"
    ctx = n.Id("a")
    assert Checker.check(src) == f"Type Cannot Be Inferred: {repr(ctx)}"


def test_289_uninferred_var_as_a_when_guard():
    """289. Q13: a guard is not an inference context"""
    src = "fun main() {\n  var a\n  when { a -> printInt(1); else -> printInt(0) }\n}"
    ctx = n.Id("a")
    assert Checker.check(src) == f"Type Cannot Be Inferred: {repr(ctx)}"


def test_290_uninferred_var_as_a_range_bound():
    """290. Q13: a range bound is not an inference context"""
    src = "fun main() {\n  var a\n  for (i in a..3) {\n    printInt(i)\n  }\n}"
    ctx = n.Id("a")
    assert Checker.check(src) == f"Type Cannot Be Inferred: {repr(ctx)}"


def test_291_typed_target_anchors_the_right_hand_side():
    """291. Q14: b is already Int, so a is fixed by the assignment"""
    src = "fun main() {\n  var a\n  var b = 1\n  b = a\n  printInt(b)\n}"
    assert Checker.check(src) == "Static checking passed"


def test_292_float_literal_never_anchors():
    """292. Q14: 1.0 is not an integer literal, so a stays unknown"""
    src = "fun main() {\n  var a\n  var b = a + 1.0\n}"
    ctx = n.BinaryOp("+", n.Id("a"), n.FloatLit(1.0))
    assert Checker.check(src) == f"Type Cannot Be Inferred: {repr(ctx)}"


def test_293_assignment_between_two_unknowns():
    """293. Q15: the right-hand side must be checkable on its own"""
    src = "fun main() {\n  var a\n  var b\n  a = b\n}"
    ctx = n.Id("b")
    assert Checker.check(src) == f"Type Cannot Be Inferred: {repr(ctx)}"


def test_294_uninferred_var_as_an_initializer():
    """294. Q13/Q15: another declaration's initializer does not anchor a var"""
    src = "fun main() {\n  var a\n  val b = a\n}"
    ctx = n.Id("a")
    assert Checker.check(src) == f"Type Cannot Be Inferred: {repr(ctx)}"


def test_295_when_expression_with_a_non_comparable_subject():
    """295. Q16: the expression form reports on the WhenExpr node"""
    src = (
        "data class P(x: Int)\n"
        "fun main() {\n"
        "  val x = when (P(1)) { else -> 0 }\n"
        "}"
    )
    ctx = n.WhenExpr(
        n.CallExpr("P", [n.IntLit(1)]), [n.WhenBranch(None, n.IntLit(0))]
    )
    assert Checker.check(src) == f"Type Mismatch In Expression: {repr(ctx)}"


def test_296_when_statement_with_a_unit_subject():
    """296. Q16: any non-comparable subject reports on the When node"""
    src = (
        "fun u() {\n"
        "}\n"
        "fun main() {\n"
        "  when (u()) {\n"
        "    else -> printInt(0)\n"
        "  }\n"
        "}"
    )
    ctx = n.When(
        n.CallExpr("u", []),
        [n.WhenBranch(None, n.ExprStmt(n.CallExpr("printInt", [n.IntLit(0)])))],
    )
    assert Checker.check(src) == f"Type Mismatch In Statement: {repr(ctx)}"


def test_297_self_recursive_return_cannot_anchor_the_type():
    """297. Q18: the node is the first value-returning return"""
    src = "fun f() {\n  return f()\n}"
    ctx = n.Return(n.CallExpr("f", []))
    assert Checker.check(src) == f"Type Cannot Be Inferred: {repr(ctx)}"


def test_298_unused_var_without_annotation_or_initializer():
    """298. Q19: an unused var still has to be inferable"""
    src = "fun main() {\n  var x\n}"
    ctx = n.VarDecl("x", True, None, None)
    assert Checker.check(src) == f"Type Cannot Be Inferred: {repr(ctx)}"


def test_300_when_expression_branches_int_and_float():
    """300. Q19: branches must have the same type, promotion does not merge them"""
    src = "fun main() {\n  val x = when (1) { 1 -> 10; else -> 20.0 }\n}"
    ctx = n.WhenExpr(
        n.IntLit(1),
        [
            n.WhenBranch([n.IntLit(1)], n.IntLit(10)),
            n.WhenBranch(None, n.FloatLit(20.0)),
        ],
    )
    assert Checker.check(src) == f"Type Mismatch In Expression: {repr(ctx)}"


def test_301_float_label_for_an_int_subject():
    """301. Q10: Int/Float promotion makes the label match"""
    src = (
        "fun main() {\n"
        "  when (1) {\n"
        "    1.0 -> printInt(1)\n"
        "    else -> printInt(0)\n"
        "  }\n"
        "}"
    )
    assert Checker.check(src) == "Static checking passed"


def test_302_int_returned_from_a_float_function():
    """302. Q9: return widens Int to the declared Float return type"""
    src = "fun f(): Float {\n  return 1\n}\nfun main() {\n  printFloat(f())\n}"
    assert Checker.check(src) == "Static checking passed"


def test_303_float_returned_from_an_int_function():
    """303. Q9: the reverse direction is still rejected"""
    src = "fun g(): Int {\n  return 1.0\n}"
    ctx = n.Return(n.FloatLit(1.0))
    assert Checker.check(src) == f"Type Mismatch In Statement: {repr(ctx)}"


def test_304_string_equality_is_supported():
    """304. Q6: == and != work on String, ordering does not"""
    src = (
        "fun main() {\n"
        '  val ok = "a" == "b"\n'
        '  val diff = "a" != "b"\n'
        "  printBool(ok)\n"
        "  printBool(diff)\n"
        "}"
    )
    assert Checker.check(src) == "Static checking passed"


def test_305_var_widens_after_being_inferred_as_int():
    """305. An inferred Int var still widens at a Float parameter"""
    src = "fun main() {\n  var a\n  printInt(a)\n  printFloat(a)\n}"
    assert Checker.check(src) == "Static checking passed"


def test_306_var_inferred_as_float_cannot_narrow():
    """306. The first usage fixes Float, so printInt then fails"""
    src = "fun main() {\n  var a\n  printFloat(a)\n  printInt(a)\n}"
    ctx = n.CallExpr("printInt", [n.Id("a")])
    assert Checker.check(src) == f"Type Mismatch In Expression: {repr(ctx)}"


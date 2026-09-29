"""Static checker tests for MKotlin (Assignment 3).

Run with:  python3 run.py test-checker

``Checker.check`` returns the str() of the first raised StaticError, or
``"Static checking passed"``.

Layout:

    001-011  valid programs (kept as baseline happy path)
    012-111  100 independent cases (Redeclared, Undeclared*,
             TypeCannotBeInferred, TypeMismatch*, MustInLoop, forum)
"""

from tests.utils import Checker
from src.utils import nodes as n


# =========================================================================== #
#  001-011  Valid programs (baseline — do not change)                         #
# =========================================================================== #
def test_001_valid_hello_and_builtins():
    """1. Valid: all eight I/O builtins"""
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


def test_002_valid_arithmetic_and_logic():
    """2. Valid: Int/Float arithmetic, ordering, equality, logic, unary, ++/--"""
    src = (
        "fun main() {\n"
        "  var i = 0\n"
        "  val a: Int = 1 + 2 * 3 - 4 / 2 % 2\n"
        "  val f: Float = 1 + 2.0\n"
        "  printBool(1 < 2 && 2.0 >= 1 || !(a == 0))\n"
        '  printBool("a" != "b")\n'
        "  printInt(-1 + +i)\n"
        "  printInt(++i)\n"
        "  printInt(i--)\n"
        "  printFloat(f)\n"
        "}"
    )
    assert Checker.check(src) == "Static checking passed"


def test_003_valid_vars_widening_and_inference():
    """3. Valid: annotated var, first-assignment inference, Int→Float widening"""
    src = (
        "fun main() {\n"
        "  var x: Int\n"
        "  x = 1\n"
        "  var v\n"
        "  v = 10\n"
        "  val f: Float = 1\n"
        "  var g: Float\n"
        "  g = 2\n"
        "  printInt(x + v)\n"
        "  printFloat(f + g)\n"
        "  printFloat(3)\n"
        "}"
    )
    assert Checker.check(src) == "Static checking passed"


def test_004_valid_data_class_nested_and_members():
    """4. Valid: nested data class, member chain, mutable member, structural =="""
    src = (
        "data class Point(x: Int, y: Int)\n"
        "data class Line(a: Point, b: Point)\n"
        "fun main() {\n"
        "  var p = Point(1, 2)\n"
        "  val l = Line(Point(1, 2), Point(3, 4))\n"
        "  p.x = 5\n"
        "  p.x++\n"
        "  printInt(l.a.x)\n"
        "  printBool(Point(1, 2) == Point(1, 2))\n"
        "}"
    )
    assert Checker.check(src) == "Static checking passed"


def test_005_valid_recursion_and_inferred_return():
    """5. Valid: recursive fact with inferred Int return (forum Q11)"""
    src = (
        "fun fact(k: Int) {\n"
        "  if (k > 1) {\n"
        "    return k * fact(k - 1)\n"
        "  }\n"
        "  return 1\n"
        "}\n"
        "fun main() {\n"
        "  printInt(fact(5))\n"
        "}"
    )
    assert Checker.check(src) == "Static checking passed"


def test_006_valid_control_flow_loops():
    """6. Valid: while/for, break/continue nested in if/when inside loops"""
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
        "  for (j in 0..9) {\n"
        "    when (j) {\n"
        "      1 -> continue\n"
        "      else -> printInt(j)\n"
        "    }\n"
        "  }\n"
        "}"
    )
    assert Checker.check(src) == "Static checking passed"


def test_007_valid_when_statement_and_expression():
    """7. Valid: subject when, conditionless when-expr, multi-label, Float subject"""
    src = (
        "fun classify(k: Int): String {\n"
        "  return when {\n"
        '    k > 0 -> "positive"\n'
        '    k < 0 -> "negative"\n'
        '    else -> "zero"\n'
        "  }\n"
        "}\n"
        "fun main() {\n"
        "  val d = readInt()\n"
        "  when (d) {\n"
        "    1 -> printInt(1)\n"
        "    2, 3 -> printInt(2)\n"
        "    else -> printInt(0)\n"
        "  }\n"
        "  when (1.5) {\n"
        "    1 -> printInt(1)\n"
        "    else -> printInt(0)\n"
        "  }\n"
        "  printString(classify(1))\n"
        "}"
    )
    assert Checker.check(src) == "Static checking passed"


def test_008_valid_if_expression_and_shadowing():
    """8. Valid: if-expr, shadowing in block/for body (not Redeclared)"""
    src = (
        "fun f(x: Int) {\n"
        "  val m = if (x > 0) x else 0\n"
        "  if (true) {\n"
        "    val x = 2\n"
        "    printInt(x + m)\n"
        "  }\n"
        "  for (i in 0..3) {\n"
        "    val i = 5\n"
        "    printInt(i)\n"
        "  }\n"
        "}"
    )
    assert Checker.check(src) == "Static checking passed"


def test_009_valid_inference_contexts():
    """9. Valid: int-literal anchor, arg/return fix var, typed LHS fixes RHS"""
    src = (
        "fun f(): Float {\n"
        "  var a\n"
        "  return a\n"
        "}\n"
        "fun main() {\n"
        "  var b\n"
        "  printFloat(b)\n"
        "  var c\n"
        "  val d = c * 2\n"
        "  var e\n"
        "  var g = 1\n"
        "  g = e\n"
        "  printInt(d + e)\n"
        "  printFloat(f())\n"
        "}"
    )
    assert Checker.check(src) == "Static checking passed"


def test_010_valid_returns_and_unit():
    """10. Valid: consistent returns, Int→Float return widening, bare Unit return"""
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


def test_011_valid_calls_and_constructor():
    """11. Valid: multi-param call, constructor with expressions, getPoint().x"""
    src = (
        "data class P(x: Int, y: Int)\n"
        "fun mk(): Int {\n"
        "  return 3\n"
        "}\n"
        "fun getPoint(): P {\n"
        "  return P(1, 2)\n"
        "}\n"
        "fun main() {\n"
        "  val a = 1\n"
        "  val p = P(a + 1, mk())\n"
        "  printInt(p.x)\n"
        "  printInt(getPoint().x)\n"
        "}"
    )
    assert Checker.check(src) == "Static checking passed"


# =========================================================================== #
#  012-111  100 independent cases                                             #
# =========================================================================== #
def test_012_empty_program():
    """12. Valid: empty program"""
    assert Checker.check("") == "Static checking passed"


def test_013_first_error_source_order():
    """13. First error wins: UndeclaredIdentifier before later type error"""
    src = "fun main() {\n  printInt(y)\n  val b = true && 1\n}"
    assert Checker.check(src) == "Undeclared Identifier: y"


def test_014_empty_data_class():
    """14. Valid: zero-member data class"""
    src = "data class Empty()\nfun main() {\n  val e = Empty()\n  printBool(e == Empty())\n}"
    assert Checker.check(src) == "Static checking passed"


def test_015_break_after_loop():
    """15. MustInLoop: loop context ends with the loop"""
    src = "fun main() {\n  while (true) {\n    printInt(1)\n  }\n  break\n}"
    assert Checker.check(src) == f"Must In Loop: {repr(n.Break())}"


def test_016_when_expression_requires_else():
    """16. TypeMismatchInExpression: when-expr needs else"""
    src = "fun main() {\n  val x = when (1) { 1 -> 10 }\n}"
    ctx = n.WhenExpr(n.IntLit(1), [n.WhenBranch([n.IntLit(1)], n.IntLit(10))])
    assert Checker.check(src) == f"Type Mismatch In Expression: {repr(ctx)}"


def test_017_float_label_for_int_subject():
    """17. Valid: Int/Float promotion on when label (forum Q10)"""
    src = "fun main() {\n  when (1) {\n    1.0 -> printInt(1)\n    else -> printInt(0)\n  }\n}"
    assert Checker.check(src) == "Static checking passed"


def test_018_string_equality():
    """18. Valid: String == / != (forum Q6)"""
    src = 'fun main() {\n  printBool("a" == "b")\n  printBool("a" != "b")\n}'
    assert Checker.check(src) == "Static checking passed"


def test_019_for_braceless_shadow_loop_var():
    """19. Valid: for (i in 0..3) var i = 4 shadows (forum Q5)"""
    src = "fun main() {\n  for (i in 0..3) var i = 4\n}"
    assert Checker.check(src) == "Static checking passed"


def test_020_break_inside_when():
    """20. MustInLoop: break in when"""
    src = "fun main() {\n  when (1) {\n    1 -> break\n    else -> printInt(0)\n  }\n}"
    assert Checker.check(src) == f"Must In Loop: {repr(n.Break())}"


def test_021_continue_at_top_level():
    """21. MustInLoop: continue in function body"""
    src = "fun main() {\n  continue\n}"
    assert Checker.check(src) == f"Must In Loop: {repr(n.Continue())}"


def test_022_redeclared_param_vs_body():
    """22. Redeclared Variable: param vs body val"""
    src = "fun f(x: Int) {\n  val x = 5\n}"
    assert Checker.check(src) == "Redeclared Variable: x"


def test_023_redeclared_val_then_var():
    """23. Redeclared Variable: same scope"""
    src = "fun main() {\n  val x = 1\n  var x = 2\n}"
    assert Checker.check(src) == "Redeclared Variable: x"


def test_024_redeclared_parameter():
    """24. Redeclared Parameter"""
    src = "fun f(a: Int, a: Int) {\n}"
    assert Checker.check(src) == "Redeclared Parameter: a"


def test_025_redeclared_function():
    """25. Redeclared Function"""
    src = "fun f() {\n}\nfun f() {\n}"
    assert Checker.check(src) == "Redeclared Function: f"


def test_026_redeclared_class():
    """26. Redeclared Class"""
    src = "data class A(x: Int)\ndata class A(y: Int)"
    assert Checker.check(src) == "Redeclared Class: A"


def test_027_redeclared_function_vs_class():
    """27. Redeclared Function: collides with data class"""
    src = "data class P(x: Int)\nfun P() {\n}"
    assert Checker.check(src) == "Redeclared Function: P"


def test_028_redeclared_class_vs_function():
    """28. Redeclared Class: collides with function"""
    src = "fun P() {\n}\ndata class P(x: Int)"
    assert Checker.check(src) == "Redeclared Class: P"


def test_029_redeclared_builtin():
    """29. Redeclared Function: shadows built-in"""
    src = "fun printInt(v: Int) {\n}"
    assert Checker.check(src) == "Redeclared Function: printInt"


def test_030_redeclared_member():
    """30. Redeclared Member"""
    src = "data class P(x: Int, x: Int)"
    assert Checker.check(src) == "Redeclared Member: x"


def test_031_redeclared_inside_block():
    """31. Redeclared Variable: inner block"""
    src = "fun main() {\n  if (true) {\n    val y = 1\n    val y = 2\n  }\n}"
    assert Checker.check(src) == "Redeclared Variable: y"


def test_032_undeclared_identifier():
    """32. UndeclaredIdentifier"""
    src = "fun main() {\n  printInt(y)\n}"
    assert Checker.check(src) == "Undeclared Identifier: y"


def test_033_use_before_declaration():
    """33. UndeclaredIdentifier: use before declare"""
    src = "fun main() {\n  printInt(x)\n  val x = 1\n}"
    assert Checker.check(src) == "Undeclared Identifier: x"


def test_034_self_in_initializer():
    """34. UndeclaredIdentifier: name not in own initializer"""
    src = "fun main() {\n  val x = x + 1\n}"
    assert Checker.check(src) == "Undeclared Identifier: x"


def test_035_block_local_escapes():
    """35. UndeclaredIdentifier: block local escapes"""
    src = "fun main() {\n  if (true) {\n    val z = 1\n  }\n  printInt(z)\n}"
    assert Checker.check(src) == "Undeclared Identifier: z"


def test_036_loop_var_after_for():
    """36. UndeclaredIdentifier: loop var after for"""
    src = "fun main() {\n  for (i in 0..3) {\n    printInt(i)\n  }\n  printInt(i)\n}"
    assert Checker.check(src) == "Undeclared Identifier: i"


def test_037_assign_undeclared():
    """37. UndeclaredIdentifier: assign unknown target"""
    src = "fun main() {\n  q = 1\n}"
    assert Checker.check(src) == "Undeclared Identifier: q"


def test_038_param_of_other_function():
    """38. UndeclaredIdentifier: other function's param"""
    src = "fun f(a: Int) {\n  printInt(a)\n}\nfun main() {\n  printInt(a)\n}"
    assert Checker.check(src) == "Undeclared Identifier: a"


def test_039_undeclared_in_range():
    """39. UndeclaredIdentifier: unknown in range bound"""
    src = "fun main() {\n  for (i in 0..k) {\n    printInt(i)\n  }\n}"
    assert Checker.check(src) == "Undeclared Identifier: k"


def test_040_break_inside_if_outside_loop():
    """40. MustInLoop: if does not create loop context"""
    src = "fun main() {\n  if (true) {\n    break\n  }\n}"
    assert Checker.check(src) == f"Must In Loop: {repr(n.Break())}"


def test_041_undeclared_function():
    """41. UndeclaredFunction"""
    src = "fun main() {\n  val a = compute(3)\n}"
    assert Checker.check(src) == "Undeclared Function: compute"


def test_042_unknown_constructor_call():
    """42. UndeclaredFunction: Vec(...) in call position (forum Q2/Q17)"""
    src = "fun main() {\n  val p = Vec(1, 2)\n}"
    assert Checker.check(src) == "Undeclared Function: Vec"


def test_043_calling_a_variable():
    """43. UndeclaredFunction: variable not callable"""
    src = "fun main() {\n  val f = 1\n  printInt(f(2))\n}"
    assert Checker.check(src) == "Undeclared Function: f"


def test_044_forward_function():
    """44. UndeclaredFunction: no forward reference"""
    src = (
        "fun main() {\n"
        "  printInt(later())\n"
        "}\n"
        "fun later(): Int {\n"
        "  return 1\n"
        "}"
    )
    assert Checker.check(src) == "Undeclared Function: later"


def test_045_forward_constructor():
    """45. UndeclaredFunction: constructor before data class"""
    src = (
        "fun main() {\n"
        "  val p = Point(1, 2)\n"
        "}\n"
        "data class Point(x: Int, y: Int)"
    )
    assert Checker.check(src) == "Undeclared Function: Point"


def test_046_operand_error_before_operator():
    """46. UndeclaredFunction: operand checked before operator"""
    src = "fun main() {\n  val x = 1 && foo()\n}"
    assert Checker.check(src) == "Undeclared Function: foo"


def test_047_undeclared_class_var():
    """47. UndeclaredClass: var annotation"""
    src = "fun main() {\n  var p: Vec\n}"
    assert Checker.check(src) == "Undeclared Class: Vec"


def test_048_annotation_before_call():
    """48. UndeclaredClass: annotation before initializer call (forum Q2)"""
    src = "fun main() {\n  val p: Vec = Vec(1, 2)\n}"
    assert Checker.check(src) == "Undeclared Class: Vec"


def test_049_undeclared_class_param():
    """49. UndeclaredClass: parameter type"""
    src = "fun f(p: Vec) {\n}"
    assert Checker.check(src) == "Undeclared Class: Vec"


def test_050_undeclared_class_return():
    """50. UndeclaredClass: return type"""
    src = "fun f(): Vec {\n  return 1\n}"
    assert Checker.check(src) == "Undeclared Class: Vec"


def test_051_undeclared_class_member():
    """51. UndeclaredClass: member type"""
    src = "data class A(p: Vec)"
    assert Checker.check(src) == "Undeclared Class: Vec"


def test_052_self_referential_member():
    """52. UndeclaredClass: self member type"""
    src = "data class Node(next: Node)"
    assert Checker.check(src) == "Undeclared Class: Node"


def test_053_forward_class_member():
    """53. UndeclaredClass: forward member type"""
    src = "data class A(b: B)\ndata class B(x: Int)"
    assert Checker.check(src) == "Undeclared Class: B"


def test_054_two_unknowns_multiplied():
    """54. TypeCannotBeInferred: a * b"""
    src = "fun main() {\n  var a\n  var b\n  val c = a * b\n}"
    ctx = n.BinaryOp("*", n.Id("a"), n.Id("b"))
    assert Checker.check(src) == f"Type Cannot Be Inferred: {repr(ctx)}"


def test_055_two_unknowns_compared():
    """55. TypeCannotBeInferred: a == b"""
    src = "fun main() {\n  var a\n  var b\n  val c = a == b\n}"
    ctx = n.BinaryOp("==", n.Id("a"), n.Id("b"))
    assert Checker.check(src) == f"Type Cannot Be Inferred: {repr(ctx)}"


def test_056_val_without_initializer():
    """56. TypeCannotBeInferred: val without init (forum Q1)"""
    src = "fun main() {\n  val x: Int\n}"
    ctx = n.VarDecl("x", False, n.IntType(), None)
    assert Checker.check(src) == f"Type Cannot Be Inferred: {repr(ctx)}"


def test_057_unused_var():
    """57. TypeCannotBeInferred: unused var x (forum Q19)"""
    src = "fun main() {\n  var x\n}"
    ctx = n.VarDecl("x", True, None, None)
    assert Checker.check(src) == f"Type Cannot Be Inferred: {repr(ctx)}"


def test_058_float_literal_no_anchor():
    """58. TypeCannotBeInferred: float literal does not anchor (forum Q14)"""
    src = "fun main() {\n  var a\n  val c = a * 2.0\n}"
    ctx = n.BinaryOp("*", n.Id("a"), n.FloatLit(2.0))
    assert Checker.check(src) == f"Type Cannot Be Inferred: {repr(ctx)}"


def test_059_no_deep_propagation():
    """59. TypeCannotBeInferred: annotation does not type nested unknowns"""
    src = "fun main() {\n  var a\n  var b\n  val c: Int = a + b\n}"
    ctx = n.BinaryOp("+", n.Id("a"), n.Id("b"))
    assert Checker.check(src) == f"Type Cannot Be Inferred: {repr(ctx)}"


def test_060_compound_argument_unknowns():
    """60. TypeCannotBeInferred: printInt(a + b)"""
    src = "fun main() {\n  var a\n  var b\n  printInt(a + b)\n}"
    ctx = n.BinaryOp("+", n.Id("a"), n.Id("b"))
    assert Checker.check(src) == f"Type Cannot Be Inferred: {repr(ctx)}"


def test_061_unary_minus_unknown():
    """61. TypeCannotBeInferred: UnaryOp(-, Id(a)) (forum Q12)"""
    src = "fun main() {\n  var a\n  val c = -a\n}"
    ctx = n.UnaryOp("-", n.Id("a"))
    assert Checker.check(src) == f"Type Cannot Be Inferred: {repr(ctx)}"


def test_062_compound_arg_unary():
    """62. TypeCannotBeInferred: foo(-a) (forum Q12)"""
    src = "fun foo(x: Int) {\n}\nfun main() {\n  var a\n  foo(-a)\n}"
    ctx = n.UnaryOp("-", n.Id("a"))
    assert Checker.check(src) == f"Type Cannot Be Inferred: {repr(ctx)}"


def test_063_member_on_uninferred():
    """63. TypeCannotBeInferred: obj.m (forum Q12)"""
    src = "fun main() {\n  var obj\n  val x = obj.m\n}"
    ctx = n.MemberAccess(n.Id("obj"), "m")
    assert Checker.check(src) == f"Type Cannot Be Inferred: {repr(ctx)}"


def test_064_uninferred_if_condition():
    """64. TypeCannotBeInferred: Id(a) in if (forum Q13)"""
    src = "fun main() {\n  var a\n  if (a) { }\n}"
    ctx = n.Id("a")
    assert Checker.check(src) == f"Type Cannot Be Inferred: {repr(ctx)}"


def test_065_uninferred_while_condition():
    """65. TypeCannotBeInferred: Id(a) in while (forum Q13)"""
    src = "fun main() {\n  var a\n  while (a) { }\n}"
    ctx = n.Id("a")
    assert Checker.check(src) == f"Type Cannot Be Inferred: {repr(ctx)}"


def test_066_uninferred_when_subject():
    """66. TypeCannotBeInferred: Id(a) as when subject (forum Q13)"""
    src = "fun main() {\n  var a\n  when (a) { else -> printInt(0) }\n}"
    ctx = n.Id("a")
    assert Checker.check(src) == f"Type Cannot Be Inferred: {repr(ctx)}"


def test_067_assignment_two_unknowns():
    """67. TypeCannotBeInferred: a = b both unknown (forum Q15)"""
    src = "fun main() {\n  var a\n  var b\n  a = b\n}"
    ctx = n.Id("b")
    assert Checker.check(src) == f"Type Cannot Be Inferred: {repr(ctx)}"


def test_068_self_recursive_return():
    """68. TypeCannotBeInferred: return f() (forum Q18)"""
    src = "fun f() {\n  return f()\n}"
    ctx = n.Return(n.CallExpr("f", []))
    assert Checker.check(src) == f"Type Cannot Be Inferred: {repr(ctx)}"


def test_069_reassign_val():
    """69. TypeMismatchInStatement: reassign val"""
    src = "fun main() {\n  val x = 1\n  x = 2\n}"
    ctx = n.Assign(n.Id("x"), n.IntLit(2))
    assert Checker.check(src) == f"Type Mismatch In Statement: {repr(ctx)}"


def test_070_while_cond_not_bool():
    """70. TypeMismatchInStatement: while Int condition"""
    src = "fun main() {\n  var i = 0\n  while (i) {\n    i++\n  }\n}"
    ctx = n.While(
        n.Id("i"),
        n.Block([n.ExprStmt(n.PostfixOp("++", n.Id("i")))]),
    )
    assert Checker.check(src) == f"Type Mismatch In Statement: {repr(ctx)}"


def test_071_if_cond_not_bool():
    """71. TypeMismatchInStatement: if Int condition"""
    src = "fun main() {\n  if (1) {\n    printInt(1)\n  }\n}"
    ctx = n.If(
        n.IntLit(1),
        n.Block([n.ExprStmt(n.CallExpr("printInt", [n.IntLit(1)]))]),
        None,
    )
    assert Checker.check(src) == f"Type Mismatch In Statement: {repr(ctx)}"


def test_072_for_start_not_int():
    """72. TypeMismatchInStatement: range start Float"""
    src = "fun main() {\n  for (i in 1.5..3) {\n    printInt(i)\n  }\n}"
    ctx = n.For(
        "i",
        n.FloatLit(1.5),
        n.IntLit(3),
        n.Block([n.ExprStmt(n.CallExpr("printInt", [n.Id("i")]))]),
    )
    assert Checker.check(src) == f"Type Mismatch In Statement: {repr(ctx)}"


def test_073_for_end_not_int():
    """73. TypeMismatchInStatement: range end String"""
    src = 'fun main() {\n  val s = "a"\n  for (i in 0..s) {\n    printInt(i)\n  }\n}'
    ctx = n.For(
        "i",
        n.IntLit(0),
        n.Id("s"),
        n.Block([n.ExprStmt(n.CallExpr("printInt", [n.Id("i")]))]),
    )
    assert Checker.check(src) == f"Type Mismatch In Statement: {repr(ctx)}"


def test_074_return_value_from_unit():
    """74. TypeMismatchInStatement: Unit returns value"""
    src = "fun f(): Unit {\n  return 1\n}"
    ctx = n.Return(n.IntLit(1))
    assert Checker.check(src) == f"Type Mismatch In Statement: {repr(ctx)}"


def test_075_bare_return_from_int():
    """75. TypeMismatchInStatement: bare return from Int function"""
    src = "fun f(): Int {\n  return\n}"
    ctx = n.Return(None)
    assert Checker.check(src) == f"Type Mismatch In Statement: {repr(ctx)}"


def test_076_return_wrong_type():
    """76. TypeMismatchInStatement: String where Int"""
    src = 'fun f(): Int {\n  return "s"\n}'
    ctx = n.Return(n.StringLit("s"))
    assert Checker.check(src) == f"Type Mismatch In Statement: {repr(ctx)}"


def test_077_return_float_from_int():
    """77. TypeMismatchInStatement: Float↛Int return (forum Q9)"""
    src = "fun g(): Int {\n  return 1.0\n}"
    ctx = n.Return(n.FloatLit(1.0))
    assert Checker.check(src) == f"Type Mismatch In Statement: {repr(ctx)}"


def test_078_bare_mixed_with_value_return():
    """78. TypeMismatchInStatement: bare + value return (forum Q11)"""
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


def test_079_inconsistent_inferred_returns():
    """79. TypeMismatchInStatement: Int then String return"""
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


def test_080_assign_string_to_int():
    """80. TypeMismatchInStatement: String to Int"""
    src = 'fun main() {\n  var x = 1\n  x = "s"\n}'
    ctx = n.Assign(n.Id("x"), n.StringLit("s"))
    assert Checker.check(src) == f"Type Mismatch In Statement: {repr(ctx)}"


def test_081_assign_float_to_int():
    """81. TypeMismatchInStatement: Float↛Int assign"""
    src = "fun main() {\n  var x: Int = 0\n  x = 1.5\n}"
    ctx = n.Assign(n.Id("x"), n.FloatLit(1.5))
    assert Checker.check(src) == f"Type Mismatch In Statement: {repr(ctx)}"


def test_082_assign_conflicts_inference():
    """82. TypeMismatchInStatement: var fixed then wrong assign"""
    src = "fun main() {\n  var a\n  a = 1\n  a = 2.5\n}"
    ctx = n.Assign(n.Id("a"), n.FloatLit(2.5))
    assert Checker.check(src) == f"Type Mismatch In Statement: {repr(ctx)}"


def test_083_annotation_mismatch():
    """83. TypeMismatchInStatement: Float init for Int"""
    src = "fun main() {\n  val x: Int = 3.14\n}"
    ctx = n.VarDecl("x", False, n.IntType(), n.FloatLit(3.14))
    assert Checker.check(src) == f"Type Mismatch In Statement: {repr(ctx)}"


def test_084_unit_as_variable():
    """84. TypeMismatchInStatement: Unit as var type"""
    src = "fun main() {\n  var u: Unit\n}"
    ctx = n.VarDecl("u", True, n.UnitType(), None)
    assert Checker.check(src) == f"Type Mismatch In Statement: {repr(ctx)}"


def test_085_unit_as_member():
    """85. TypeMismatchInStatement: Unit as member type"""
    src = "data class A(u: Unit)"
    ctx = n.MemberDecl("u", n.UnitType())
    assert Checker.check(src) == f"Type Mismatch In Statement: {repr(ctx)}"


def test_086_unit_as_parameter():
    """86. TypeMismatchInStatement: Unit as parameter type"""
    src = "fun f(u: Unit) {\n}"
    ctx = n.Param("u", n.UnitType())
    assert Checker.check(src) == f"Type Mismatch In Statement: {repr(ctx)}"


def test_087_assign_loop_variable():
    """87. TypeMismatchInStatement: assign loop var"""
    src = "fun main() {\n  for (i in 0..3) {\n    i = 5\n  }\n}"
    ctx = n.Assign(n.Id("i"), n.IntLit(5))
    assert Checker.check(src) == f"Type Mismatch In Statement: {repr(ctx)}"


def test_088_assign_member_of_val():
    """88. TypeMismatchInStatement: member of val"""
    src = (
        "data class Point(x: Int, y: Int)\n"
        "fun main() {\n"
        "  val p = Point(1, 2)\n"
        "  p.x = 5\n"
        "}"
    )
    ctx = n.Assign(n.MemberAccess(n.Id("p"), "x"), n.IntLit(5))
    assert Checker.check(src) == f"Type Mismatch In Statement: {repr(ctx)}"


def test_089_increment_val():
    """89. TypeMismatchInStatement: ++ on val — PostfixOp (forum Q7)"""
    src = "fun main() {\n  val x = 1\n  x++\n}"
    ctx = n.PostfixOp("++", n.Id("x"))
    assert Checker.check(src) == f"Type Mismatch In Statement: {repr(ctx)}"


def test_090_increment_in_expression():
    """90. TypeMismatchInStatement: ++ node not VarDecl (forum Q7)"""
    src = "fun main() {\n  val i = 0\n  val x = i++ + 1\n}"
    ctx = n.PostfixOp("++", n.Id("i"))
    assert Checker.check(src) == f"Type Mismatch In Statement: {repr(ctx)}"


def test_091_when_subject_data_class():
    """91. TypeMismatchInStatement: When node (forum Q16)"""
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


def test_092_two_else_branches():
    """92. TypeMismatchInStatement: more than one else"""
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


def test_093_logical_and_needs_bool():
    """93. TypeMismatchInExpression: &&"""
    src = "fun main() {\n  val b = true && 1\n}"
    ctx = n.BinaryOp("&&", n.BoolLit(True), n.IntLit(1))
    assert Checker.check(src) == f"Type Mismatch In Expression: {repr(ctx)}"


def test_094_no_string_concat():
    """94. TypeMismatchInExpression: String +"""
    src = 'fun main() {\n  val s = "a" + "b"\n}'
    ctx = n.BinaryOp("+", n.StringLit("a"), n.StringLit("b"))
    assert Checker.check(src) == f"Type Mismatch In Expression: {repr(ctx)}"


def test_095_no_string_ordering():
    """95. TypeMismatchInExpression: String <"""
    src = 'fun main() {\n  val b = "a" < "b"\n}'
    ctx = n.BinaryOp("<", n.StringLit("a"), n.StringLit("b"))
    assert Checker.check(src) == f"Type Mismatch In Expression: {repr(ctx)}"


def test_096_modulus_float():
    """96. TypeMismatchInExpression: % Float"""
    src = "fun main() {\n  val x = 3.14 % 2\n}"
    ctx = n.BinaryOp("%", n.FloatLit(3.14), n.IntLit(2))
    assert Checker.check(src) == f"Type Mismatch In Expression: {repr(ctx)}"


def test_097_not_on_int():
    """97. TypeMismatchInExpression: ! Int"""
    src = "fun main() {\n  val b = !1\n}"
    ctx = n.UnaryOp("!", n.IntLit(1))
    assert Checker.check(src) == f"Type Mismatch In Expression: {repr(ctx)}"


def test_098_unary_minus_bool():
    """98. TypeMismatchInExpression: -true"""
    src = "fun main() {\n  val x = -true\n}"
    ctx = n.UnaryOp("-", n.BoolLit(True))
    assert Checker.check(src) == f"Type Mismatch In Expression: {repr(ctx)}"


def test_099_postfix_inc_float():
    """99. TypeMismatchInExpression: ++ Float"""
    src = "fun main() {\n  var f = 1.5\n  f++\n}"
    ctx = n.PostfixOp("++", n.Id("f"))
    assert Checker.check(src) == f"Type Mismatch In Expression: {repr(ctx)}"


def test_100_inc_float_val_tiebreak():
    """100. TypeMismatchInExpression: type before assignability (forum Q7)"""
    src = "fun main() {\n  val f = 1.0\n  f++\n}"
    ctx = n.PostfixOp("++", n.Id("f"))
    assert Checker.check(src) == f"Type Mismatch In Expression: {repr(ctx)}"


def test_101_eq_int_string():
    """101. TypeMismatchInExpression: Int == String"""
    src = 'fun main() {\n  val b = 1 == "a"\n}'
    ctx = n.BinaryOp("==", n.IntLit(1), n.StringLit("a"))
    assert Checker.check(src) == f"Type Mismatch In Expression: {repr(ctx)}"


def test_102_eq_different_classes():
    """102. TypeMismatchInExpression: different data classes =="""
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


def test_103_member_on_non_class():
    """103. TypeMismatchInExpression: Int.a"""
    src = "fun main() {\n  val x = 1\n  val y = x.a && true\n}"
    ctx = n.MemberAccess(n.Id("x"), "a")
    assert Checker.check(src) == f"Type Mismatch In Expression: {repr(ctx)}"


def test_104_unknown_member():
    """104. TypeMismatchInExpression: unknown member"""
    src = (
        "data class Point(x: Int, y: Int)\n"
        "fun main() {\n"
        "  val p = Point(1, 2)\n"
        "  printInt(p.z)\n"
        "}"
    )
    ctx = n.MemberAccess(n.Id("p"), "z")
    assert Checker.check(src) == f"Type Mismatch In Expression: {repr(ctx)}"


def test_105_wrong_arg_count():
    """105. TypeMismatchInExpression: too few args"""
    src = "fun f(a: Int, b: Int) {\n}\nfun main() {\n  f(1)\n}"
    ctx = n.CallExpr("f", [n.IntLit(1)])
    assert Checker.check(src) == f"Type Mismatch In Expression: {repr(ctx)}"


def test_106_float_arg_for_int_param():
    """106. TypeMismatchInExpression: Float arg for Int param"""
    src = "fun main() {\n  printInt(1.5)\n}"
    ctx = n.CallExpr("printInt", [n.FloatLit(1.5)])
    assert Checker.check(src) == f"Type Mismatch In Expression: {repr(ctx)}"


def test_107_ctor_wrong_order():
    """107. TypeMismatchInExpression: constructor arg order"""
    src = (
        "data class Person(name: String, age: Int)\n"
        "fun main() {\n"
        '  val p = Person(25, "John")\n'
        "}"
    )
    ctx = n.CallExpr("Person", [n.IntLit(25), n.StringLit("John")])
    assert Checker.check(src) == f"Type Mismatch In Expression: {repr(ctx)}"


def test_108_when_label_mismatch():
    """108. TypeMismatchInExpression: when label type"""
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


def test_109_when_guard_not_bool():
    """109. TypeMismatchInExpression: when guard Int"""
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


def test_110_if_expr_branch_mismatch():
    """110. TypeMismatchInExpression: if-expr branches"""
    src = 'fun main() {\n  val x = if (true) 1 else "a"\n}'
    ctx = n.IfExpr(n.BoolLit(True), n.IntLit(1), n.StringLit("a"))
    assert Checker.check(src) == f"Type Mismatch In Expression: {repr(ctx)}"


def test_111_when_expr_int_float_branches():
    """111. TypeMismatchInExpression: when-expr Int/Float (forum Q19)"""
    src = "fun main() {\n  val x = when (1) { 1 -> 10; else -> 20.0 }\n}"
    ctx = n.WhenExpr(
        n.IntLit(1),
        [
            n.WhenBranch([n.IntLit(1)], n.IntLit(10)),
            n.WhenBranch(None, n.FloatLit(20.0)),
        ],
    )
    assert Checker.check(src) == f"Type Mismatch In Expression: {repr(ctx)}"

"""
Parser test cases for MKotlin compiler.
TODO: Implement 100 test cases for parser
"""

from tests.utils import Parser


# ========== Simple Test Cases (10 types) ==========
def test_empty_program():
    """1. Empty program"""
    assert Parser.parse("") == "success"


def test_hello_world():
    """2. Program with main function"""
    src = 'fun main() {\n    printString("Hello, World!")\n}'
    assert Parser.parse(src) == "success"


def test_data_class():
    """3. Data class declaration"""
    assert Parser.parse("data class Point(x: Int, y: Int)") == "success"


def test_val_decl():
    """4. Variable declaration"""
    assert Parser.parse("fun main() {\n  val x = 10\n}") == "success"


def test_var_with_type():
    """5. Variable with type annotation"""
    assert Parser.parse("fun main() {\n  var x: Int = 10\n}") == "success"


def test_if_else():
    """6. If statement"""
    src = "fun main() {\n  if (x > 0) printInt(1) else printInt(0)\n}"
    assert Parser.parse(src) == "success"


def test_while():
    """7. While statement"""
    src = "fun main() {\n  while (i < 10) {\n    i++\n  }\n}"
    assert Parser.parse(src) == "success"


def test_for_in_range():
    """8. For-in-range statement"""
    src = "fun main() {\n  for (i in 0 .. 9) {\n    printInt(i)\n  }\n}"
    assert Parser.parse(src) == "success"


def test_when():
    """9. When statement"""
    src = "fun main() {\n  when (d) {\n    1 -> printInt(1)\n    else -> printInt(0)\n  }\n}"
    assert Parser.parse(src) == "success"


def test_syntax_error():
    """10. Syntax error"""
    assert Parser.parse("fun main( {\n}") != "success"


# ========== Declarations (easy) ==========
def test_011():
    """Multiple function declarations"""
    assert Parser.parse("fun foo() {\n}\nfun bar() {\n}") == "success"

def test_012():
    """Function with explicit return type"""
    assert Parser.parse("fun add(x: Int, y: Int): Int {\n  return x + y\n}") == "success"

def test_013():
    """Function with omitted (inferred) return type"""
    assert Parser.parse("fun add(x: Int, y: Int) {\n  return x + y\n}") == "success"

def test_014():
    """Function with no parameters and explicit Unit return"""
    assert Parser.parse("fun main(): Unit {\n}") == "success"

def test_015():
    """Data class with a single member"""
    assert Parser.parse("data class Box(v: Int)") == "success"

def test_016():
    """Data class with zero members"""
    assert Parser.parse("data class Empty()") == "success"

def test_017():
    """Data class with many members of different types"""
    assert Parser.parse(
        "data class Person(name: String, age: Int, height: Float, ok: Boolean)"
    ) == "success"

def test_018():
    """Data class member whose type is another data class"""
    src = "data class Point(x: Int, y: Int)\ndata class Line(a: Point, b: Point)"
    assert Parser.parse(src) == "success"

def test_019():
    """Data classes and functions interleaved in any order"""
    src = "data class P(x: Int)\nfun f(): Int {\n  return 1\n}\ndata class Q(y: Int)\nfun main() {\n}"
    assert Parser.parse(src) == "success"

def test_020():
    """Function returning a data class type"""
    src = "data class Point(x: Int, y: Int)\nfun origin(): Point {\n  return Point(0, 0)\n}"
    assert Parser.parse(src) == "success"


# ========== Variable declaration forms ==========
def test_021():
    """val with inferred type"""
    assert Parser.parse("fun main() {\n  val x = 10\n}") == "success"

def test_022():
    """val with explicit type"""
    assert Parser.parse("fun main() {\n  val x: Float = 3.14\n}") == "success"

def test_023():
    """var with explicit type and no initializer"""
    assert Parser.parse("fun main() {\n  var total: Float\n}") == "success"

def test_024():
    """var with no type and no initializer"""
    assert Parser.parse("fun main() {\n  var n\n}") == "success"

def test_025():
    """Two statements on one line separated by a semicolon"""
    assert Parser.parse("fun main() {\n  val x = 10; val y = 20\n}") == "success"


# ========== Statements ==========
def test_026():
    """if without else"""
    assert Parser.parse("fun main() {\n  if (a > 0) printInt(1)\n}") == "success"

def test_027():
    """if with else"""
    assert Parser.parse("fun main() {\n  if (a > 0) printInt(1) else printInt(0)\n}") == "success"

def test_028():
    """Nested if with dangling else (binds to nearest if)"""
    assert Parser.parse("fun main() {\n  if (a) if (b) s1() else s2()\n}") == "success"

def test_029():
    """while with a block body"""
    assert Parser.parse("fun main() {\n  while (i < 10) {\n    i++\n  }\n}") == "success"

def test_030():
    """for over a range"""
    assert Parser.parse("fun main() {\n  for (i in 0 .. 9) {\n    printInt(i)\n  }\n}") == "success"

def test_031():
    """when in subject form with multiple labels and else"""
    src = "fun main() {\n  when (d) {\n    1 -> printInt(1)\n    2, 3 -> printInt(2)\n    else -> printInt(0)\n  }\n}"
    assert Parser.parse(src) == "success"

def test_032():
    """when in conditionless (guard) form"""
    src = 'fun main() {\n  when {\n    n > 0 -> printString("p")\n    else -> printString("z")\n  }\n}'
    assert Parser.parse(src) == "success"

def test_033():
    """break and continue inside a loop"""
    src = "fun main() {\n  while (true) {\n    if (a) break\n    continue\n  }\n}"
    assert Parser.parse(src) == "success"

def test_034():
    """return with a value and bare return"""
    src = "fun f(): Int {\n  return 1\n}\nfun g() {\n  return\n}"
    assert Parser.parse(src) == "success"

def test_035():
    """Standalone empty block statement"""
    assert Parser.parse("fun main() {\n  {\n  }\n}") == "success"

def test_036():
    """Expression statements: call, assignment, increment"""
    src = "fun main() {\n  printInt(x)\n  x = 5\n  x = x + 1\n  x++\n}"
    assert Parser.parse(src) == "success"

def test_037():
    """Chained assignment (right associative)"""
    assert Parser.parse("fun main() {\n  x = y = z = 10\n}") == "success"

def test_038():
    """Member assignment via dot"""
    assert Parser.parse("fun main() {\n  p.x = 99\n}") == "success"

def test_039():
    """Prefix and postfix increment/decrement statements"""
    src = "fun main() {\n  ++x\n  --x\n  x++\n  x--\n}"
    assert Parser.parse(src) == "success"

def test_040():
    """Deeply nested member access as an assignment target"""
    assert Parser.parse("fun main() {\n  person.address.city.zip = 70000\n}") == "success"


# ========== Expressions and precedence ==========
def test_041():
    """Arithmetic precedence mix"""
    assert Parser.parse("fun main() {\n  val r = 1 + 2 * 3 - 4 / 2 % 3\n}") == "success"

def test_042():
    """Unary plus and unary minus"""
    assert Parser.parse("fun main() {\n  val r = -a + +b\n}") == "success"

def test_043():
    """Logical operators combined with not"""
    assert Parser.parse("fun main() {\n  val r = !a && b || !c\n}") == "success"

def test_044():
    """Relational and equality operators together"""
    assert Parser.parse("fun main() {\n  val r = a < b == c > d\n}") == "success"

def test_045():
    """Nested function calls"""
    assert Parser.parse("fun main() {\n  val r = f(g(h(x)))\n}") == "success"

def test_046():
    """Constructor call with expression arguments"""
    src = "data class Point(x: Int, y: Int)\nfun main() {\n  val p = Point(1 + 1, 2 * 2)\n}"
    assert Parser.parse(src) == "success"

def test_047():
    """Nested constructor calls"""
    src = ("data class Point(x: Int, y: Int)\n"
           "data class Line(a: Point, b: Point)\n"
           "fun main() {\n  val l = Line(Point(1, 2), Point(3, 4))\n}")
    assert Parser.parse(src) == "success"

def test_048():
    """when used as an expression assigned to a val"""
    src = "fun main() {\n  val sign = when {\n    n > 0 -> 1\n    n < 0 -> -1\n    else -> 0\n  }\n}"
    assert Parser.parse(src) == "success"

def test_049():
    """if used as an expression"""
    assert Parser.parse("fun main() {\n  val m = if (a > b) a else b\n}") == "success"

def test_050():
    """Parentheses overriding precedence"""
    assert Parser.parse("fun main() {\n  val r = (1 + 2) * (3 - 4)\n}") == "success"


# ========== Harder combinations ==========
def test_051():
    """Range with expression bounds inside for"""
    assert Parser.parse(
        "fun main() {\n  for (i in start + 1 .. end - 1) {\n    printInt(i)\n  }\n}"
    ) == "success"

def test_052():
    """Mixed argument expressions including postfix increment"""
    assert Parser.parse("fun main() {\n  foo(a && b, !c, x++)\n}") == "success"

def test_053():
    """Empty and multi-argument calls"""
    assert Parser.parse("fun main() {\n  f()\n  g(1, 2, 3)\n}") == "success"

def test_054():
    """Double logical negation"""
    assert Parser.parse("fun main() {\n  val r = !!flag\n}") == "success"

def test_055():
    """Long right-associative assignment chain"""
    assert Parser.parse("fun main() {\n  a = b = c = d = 1\n}") == "success"

def test_056():
    """when subject form with several labels and no else"""
    src = "fun main() {\n  when (x) {\n    1, 2, 3 -> printInt(1)\n    4, 5 -> printInt(2)\n  }\n}"
    assert Parser.parse(src) == "success"

def test_057():
    """Member access on a function-call result"""
    src = ("data class Point(x: Int, y: Int)\n"
           "fun getPoint(): Point {\n  return Point(1, 2)\n}\n"
           "fun main() {\n  printInt(getPoint().x)\n}")
    assert Parser.parse(src) == "success"

def test_058():
    """when nested inside a when branch"""
    src = ("fun main() {\n  when (a) {\n    1 -> when (b) {\n"
           "      2 -> printInt(2)\n      else -> printInt(0)\n    }\n"
           "    else -> printInt(9)\n  }\n}")
    assert Parser.parse(src) == "success"

def test_059():
    """for inside while inside if"""
    src = ("fun main() {\n  if (ok) {\n    while (run) {\n"
           "      for (i in 0 .. n) {\n        printInt(i)\n      }\n    }\n  }\n}")
    assert Parser.parse(src) == "success"

def test_060():
    """Every primitive parameter type"""
    assert Parser.parse("fun f(a: Int, b: Float, c: Boolean, d: String): Unit {\n}") == "success"

def test_061():
    """Chained assignment of member accesses"""
    assert Parser.parse("fun main() {\n  p.x = p.y = 0\n}") == "success"

def test_062():
    """Blank lines between statements are allowed"""
    assert Parser.parse("fun main() {\n\n  val x = 1\n\n\n  val y = 2\n\n}") == "success"

def test_063():
    """if-else-if ladder"""
    assert Parser.parse(
        "fun main() {\n  if (a) printInt(1) else if (b) printInt(2) else printInt(3)\n}"
    ) == "success"

def test_064():
    """when expression as a return value"""
    src = ('fun classify(n: Int): String {\n  return when {\n'
           '    n > 0 -> "pos"\n    n < 0 -> "neg"\n    else -> "zero"\n  }\n}')
    assert Parser.parse(src) == "success"

def test_065():
    """Complex boolean expression with parentheses"""
    assert Parser.parse("fun main() {\n  val r = (a < b) && (c >= d) || !(e == f)\n}") == "success"

def test_066():
    """for range bounds that are function calls"""
    assert Parser.parse("fun main() {\n  for (i in readInt() .. readInt()) {\n  }\n}") == "success"

def test_067():
    """Unary minus applied to parenthesized expr and call result"""
    assert Parser.parse("fun main() {\n  val r = -(a + b) * -f(x)\n}") == "success"

def test_068():
    """Deeply nested parentheses"""
    assert Parser.parse("fun main() {\n  val r = ((((1))))\n}") == "success"

def test_069():
    """Assignment whose rhs is an if-expression"""
    assert Parser.parse("fun main() {\n  x = if (c) 1 else 2\n}") == "success"

def test_070():
    """Nested standalone blocks (new scopes)"""
    src = "fun main() {\n  {\n    val x = 1\n    {\n      val y = 2\n    }\n  }\n}"
    assert Parser.parse(src) == "success"


# ========== Full programs / stress ==========
def test_071():
    """Recursive factorial function"""
    src = ("fun factorial(n: Int): Int {\n  if (n <= 1) {\n    return 1\n  } else {\n"
           "    return n * factorial(n - 1)\n  }\n}")
    assert Parser.parse(src) == "success"

def test_072():
    """Complete program with data classes, helper function and main"""
    src = ("data class Point(x: Int, y: Int)\n"
           "fun dist(a: Point, b: Point): Int {\n"
           "  return (a.x - b.x) * (a.x - b.x) + (a.y - b.y) * (a.y - b.y)\n"
           "}\n"
           "fun main() {\n"
           "  val p = Point(0, 0)\n"
           "  val q = Point(3, 4)\n"
           "  printInt(dist(p, q))\n"
           "}")
    assert Parser.parse(src) == "success"

def test_073():
    """when subject form with string labels"""
    src = ('fun main() {\n  when (s) {\n    "a" -> printInt(1)\n'
           '    "b", "c" -> printInt(2)\n    else -> printInt(0)\n  }\n}')
    assert Parser.parse(src) == "success"

def test_074():
    """Nested for loops with break and continue"""
    src = ("fun main() {\n  for (i in 0 .. 9) {\n    for (j in 0 .. 9) {\n"
           "      if (i == j) continue\n      if (i + j > 10) break\n    }\n  }\n}")
    assert Parser.parse(src) == "success"

def test_075():
    """Chained member assignment through nested data classes"""
    src = ("data class Inner(v: Int)\ndata class Outer(a: Inner)\n"
           "fun main() {\n  var o = Outer(Inner(1))\n  o.a.v = 5\n}")
    assert Parser.parse(src) == "success"

def test_076():
    """var declared then assigned a when-expression"""
    src = ('fun main() {\n  var grade\n  grade = when (score) {\n'
           '    1 -> "A"\n    else -> "F"\n  }\n}')
    assert Parser.parse(src) == "success"

def test_077():
    """Multiple returns in different branches"""
    src = ("fun sign(n: Int): Int {\n  if (n > 0) return 1\n"
           "  if (n < 0) return -1\n  return 0\n}")
    assert Parser.parse(src) == "success"

def test_078():
    """Comments interspersed with code"""
    src = ("fun main() {\n  // a line comment\n  val x = 10 /* inline */ + 5\n"
           "  /* block\n     spanning\n     lines */\n  printInt(x)\n}")
    assert Parser.parse(src) == "success"

def test_079():
    """when with one normal branch and an else"""
    src = "fun main() {\n  when {\n    ready -> start()\n    else -> wait()\n  }\n}"
    assert Parser.parse(src) == "success"

def test_080():
    """Member target assigned the result of a call"""
    assert Parser.parse("fun main() {\n  obj.field = compute(1, 2, 3)\n}") == "success"

def test_081():
    """Long additive/multiplicative chain"""
    assert Parser.parse("fun main() {\n  val r = 1 + 2 + 3 + 4 * 5 * 6 - 7 - 8 / 9\n}") == "success"

def test_082():
    """Nested if-expressions on the rhs"""
    assert Parser.parse("fun main() {\n  val r = if (a) if (b) 1 else 2 else 3\n}") == "success"

def test_083():
    """Statement list mixing newlines and semicolons"""
    src = ("fun main() {\n  val a = 1; val b = 2\n  val c = 3\n"
           "  printInt(a); printInt(b); printInt(c)\n}")
    assert Parser.parse(src) == "success"

def test_084():
    """for body is a single non-block statement"""
    assert Parser.parse("fun main() {\n  for (i in 0 .. 5) printInt(i)\n}") == "success"

def test_085():
    """while body is a single non-block statement"""
    assert Parser.parse("fun main() {\n  while (go) step()\n}") == "success"


# ========== Syntax errors ==========
def test_086():
    """Missing closing parenthesis in function header"""
    assert Parser.parse("fun main( {\n}") != "success"

def test_087():
    """Missing closing brace in function body"""
    assert Parser.parse("fun main() {\n  val x = 1\n") != "success"

def test_088():
    """Data class without parameter parentheses"""
    assert Parser.parse("data class Point") != "success"

def test_089():
    """Statement at top level (outside any function)"""
    assert Parser.parse("val x = 10") != "success"

def test_090():
    """Function without a name"""
    assert Parser.parse("fun () {\n}") != "success"

def test_091():
    """for without the 'in' keyword"""
    assert Parser.parse("fun main() {\n  for (i 0 .. 9) {\n  }\n}") != "success"

def test_092():
    """when branch missing the arrow"""
    assert Parser.parse("fun main() {\n  when (x) {\n    1 printInt(1)\n  }\n}") != "success"

def test_093():
    """Parameter missing its type annotation"""
    assert Parser.parse("fun f(x) {\n}") != "success"

def test_094():
    """Double comma in an argument list"""
    assert Parser.parse("fun main() {\n  foo(1, , 2)\n}") != "success"

def test_095():
    """Missing right operand of a binary operator"""
    assert Parser.parse("fun main() {\n  val x = 1 +\n}") != "success"

def test_096():
    """Nested data class declaration inside a function"""
    assert Parser.parse("fun main() {\n  data class P(x: Int)\n}") != "success"

def test_097():
    """else without a matching if"""
    assert Parser.parse("fun main() {\n  else printInt(0)\n}") != "success"

def test_098():
    """Unbalanced parentheses inside an expression"""
    assert Parser.parse("fun main() {\n  printInt((1 + 2)\n}") != "success"

def test_099():
    """when without braces"""
    assert Parser.parse("fun main() {\n  when (x) 1 -> printInt(1)\n}") != "success"

def test_100():
    """Extra closing brace after a complete function"""
    assert Parser.parse("fun main() {\n}\n}") != "success"

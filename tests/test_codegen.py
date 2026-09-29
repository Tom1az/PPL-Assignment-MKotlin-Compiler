"""Code generation tests for MKotlin (Assignment 4).

Run with:  python3 run.py test-codegen

``CodeGenerator.run`` returns the program's stdout after assembling & running.
These fail until CodeGenerator is implemented.  Add up to 100 test cases.
"""

from tests.utils import CodeGenerator

def test_001_hello_world():
    src = 'fun main() {\n  printString("Hello, World!")\n}'
    assert CodeGenerator.run(src) == "Hello, World!"


def test_002_print_int():
    src = "fun main() {\n  printInt(42)\n}"
    assert CodeGenerator.run(src) == "42"


def test_003_print_float_literal():
    src = """
fun main() {
    printFloat(3.5)
}
"""
    assert CodeGenerator.run(src) == "3.5"


def test_004_print_bool_literals():
    src = """
fun main() {
    printBool(true)
    printBool(false)
}
"""
    assert CodeGenerator.run(src) == "truefalse"


def test_005_several_print_string_calls():
    src = """
fun main() {
    printString("a")
    printString("b")
    printString("c")
}
"""
    assert CodeGenerator.run(src) == "abc"


def test_006_int_literal_with_underscores():
    src = """
fun main() {
    printInt(1_000_000)
    printString(" ")
    printInt(0)
}
"""
    assert CodeGenerator.run(src) == "1000000 0"


def test_007_float_literal_forms():
    src = """
fun main() {
    printFloat(1.)
    printString(" ")
    printFloat(.5)
    printString(" ")
    printFloat(1e3)
    printString(" ")
    printFloat(3.14f)
}
"""
    assert CodeGenerator.run(src) == "1.0 0.5 1000.0 3.14"


def test_008_int_argument_widened_to_float():
    src = """
fun main() {
    printFloat(3)
    printString(" ")
    val n = 7
    printFloat(n)
}
"""
    assert CodeGenerator.run(src) == "3.0 7.0"


def test_009_read_int():
    src = """
fun main() {
    printInt(readInt())
}
"""
    assert CodeGenerator.run(src, "7\n") == "7"


def test_010_read_float():
    src = """
fun main() {
    val x = readFloat()
    printFloat(x * 2.0)
}
"""
    assert CodeGenerator.run(src, "2.5\n") == "5.0"


def test_011_read_bool_and_read_string():
    src = """
fun main() {
    printBool(readBool())
    printString(" ")
    printString(readString())
}
"""
    assert CodeGenerator.run(src, "true\nhi there\n") == "true hi there"


# --------------------------------------------------------------------------- #
#  Arithmetic                                                                 #
# --------------------------------------------------------------------------- #
def test_012_multiplicative_precedence():
    src = """
fun main() {
    printInt(2 + 3 * 4)
}
"""
    assert CodeGenerator.run(src) == "14"


def test_013_parentheses_override_precedence():
    src = """
fun main() {
    printInt((2 + 3) * 4)
}
"""
    assert CodeGenerator.run(src) == "20"


def test_014_additive_left_associativity():
    src = """
fun main() {
    printInt(10 - 3 - 2)
    printString(" ")
    printInt(100 - (30 - 20))
}
"""
    assert CodeGenerator.run(src) == "5 90"


def test_015_int_division_and_modulus():
    src = """
fun main() {
    printInt(100 / 7)
    printString(" ")
    printInt(100 % 7)
}
"""
    assert CodeGenerator.run(src) == "14 2"


def test_016_negative_division_and_modulus():
    src = """
fun main() {
    printInt(-7 / 2)
    printString(" ")
    printInt(-7 % 2)
    printString(" ")
    printInt(7 % -2)
}
"""
    assert CodeGenerator.run(src) == "-3 -1 1"


def test_017_unary_plus_and_minus():
    src = """
fun main() {
    printInt(-(-5))
    printInt(+7)
    printFloat(-2.5)
}
"""
    assert CodeGenerator.run(src) == "57-2.5"


def test_018_float_arithmetic():
    src = """
fun main() {
    printFloat(1.5 + 2.25)
    printString(" ")
    printFloat(7.0 / 2.0)
    printString(" ")
    printFloat(1.5 * 4.0)
    printString(" ")
    printFloat(5.5 - 0.25)
}
"""
    assert CodeGenerator.run(src) == "3.75 3.5 6.0 5.25"


def test_019_mixed_int_float_promotion():
    src = """
fun main() {
    printFloat(1 + 2.5)
    printString(" ")
    printFloat(3 * 1.5)
    printString(" ")
    printFloat(2.5 - 1)
}
"""
    assert CodeGenerator.run(src) == "3.5 4.5 1.5"


def test_020_int_division_versus_float_division():
    src = """
fun main() {
    printInt(7 / 2)
    printString(" ")
    printFloat(7 / 2.0)
    printString(" ")
    printFloat(7.0 / 2)
}
"""
    assert CodeGenerator.run(src) == "3 3.5 3.5"


def test_021_modulus_left_associativity():
    src = """
fun main() {
    printInt(17 % 5 % 2)
    printString(" ")
    printInt(2 * 10 % 7)
}
"""
    assert CodeGenerator.run(src) == "0 6"


def test_022_nested_arithmetic_expression():
    src = """
fun main() {
    printInt(((1 + 2) * (3 + 4) - (5 * 2)) / 2)
    printString(" ")
    printInt(-2 * 3 + 4)
}
"""
    assert CodeGenerator.run(src) == "5 -2"


# --------------------------------------------------------------------------- #
#  Relational, equality and logical operators                                 #
# --------------------------------------------------------------------------- #
def test_023_int_ordering_operators():
    src = """
fun main() {
    printBool(3 < 5)
    printBool(5 <= 5)
    printBool(5 > 5)
    printBool(4 >= 2)
}
"""
    assert CodeGenerator.run(src) == "truetruefalsetrue"


def test_024_float_and_mixed_ordering():
    src = """
fun main() {
    printBool(2.5 < 3.5)
    printBool(2 < 2.5)
    printBool(3.0 >= 3)
    printBool(1.5 > 2.5)
}
"""
    assert CodeGenerator.run(src) == "truetruetruefalse"


def test_025_int_equality():
    src = """
fun main() {
    printBool(3 == 3)
    printBool(3 != 3)
    printBool(2 + 2 == 4)
}
"""
    assert CodeGenerator.run(src) == "truefalsetrue"


def test_026_float_and_mixed_equality():
    src = """
fun main() {
    printBool(1.5 == 1.5)
    printBool(1.5 != 1.5)
    printBool(2 == 2.0)
    printBool(2.5 == 2)
}
"""
    assert CodeGenerator.run(src) == "truefalsetruefalse"


def test_027_boolean_equality():
    src = """
fun main() {
    printBool(true == true)
    printBool(true != false)
    printBool((3 < 5) == (2 < 4))
}
"""
    assert CodeGenerator.run(src) == "truetruetrue"


def test_028_string_equality_literals():
    src = """
fun main() {
    printBool("abc" == "abc")
    printBool("abc" != "abd")
    printBool("" == "")
}
"""
    assert CodeGenerator.run(src) == "truetruetrue"


def test_029_string_equality_with_input():
    src = """
fun main() {
    val s = readString()
    if (s == "hello") {
        printString("yes")
    } else {
        printString("no")
    }
    printBool(s != "world")
}
"""
    assert CodeGenerator.run(src, "hello\n") == "yestrue"


def test_030_logical_not():
    src = """
fun main() {
    printBool(!true)
    printBool(!(3 > 5))
    printBool(!!true)
}
"""
    assert CodeGenerator.run(src) == "falsetruetrue"


def test_031_and_or_combinations():
    src = """
fun main() {
    printBool(true && false)
    printBool(true || false)
    printBool(false || false)
    printBool(true && true)
    printBool((3 < 5) && (5 < 3))
}
"""
    assert CodeGenerator.run(src) == "falsetruefalsetruefalse"


def test_032_short_circuit_evaluation():
    src = """
fun yes(): Boolean {
    printString("Y")
    return true
}

fun no(): Boolean {
    printString("N")
    return false
}

fun main() {
    printBool(false && yes())
    printBool(true || no())
    printBool(true && yes())
    printBool(false || no())
    printBool(true || false && false)
}
"""
    assert CodeGenerator.run(src) == "falsetrueYtrueNfalsetrue"


# --------------------------------------------------------------------------- #
#  Declarations and assignment                                                #
# --------------------------------------------------------------------------- #
def test_033_val_with_inferred_types():
    src = """
fun main() {
    val a = 10
    val b = 2.5
    val c = true
    val d = "hi"
    printInt(a)
    printString(" ")
    printFloat(b)
    printString(" ")
    printBool(c)
    printString(" ")
    printString(d)
}
"""
    assert CodeGenerator.run(src) == "10 2.5 true hi"


def test_034_val_with_explicit_types():
    src = """
fun main() {
    val a: Int = 10
    val b: Float = 2.5
    val c: Boolean = false
    val d: String = "ok"
    val e: Float = 4
    printInt(a)
    printString(" ")
    printFloat(b)
    printString(" ")
    printBool(c)
    printString(" ")
    printString(d)
    printString(" ")
    printFloat(e)
}
"""
    assert CodeGenerator.run(src) == "10 2.5 false ok 4.0"


def test_035_var_reassignment():
    src = """
fun main() {
    var x = 1
    x = x + 5
    x = x * 2
    printInt(x)
}
"""
    assert CodeGenerator.run(src) == "12"


def test_036_var_declared_without_initializer():
    src = """
fun main() {
    var x: Int
    x = 9
    var f: Float
    f = 1.5
    var g: Float
    g = 5
    printInt(x)
    printString(" ")
    printFloat(f)
    printString(" ")
    printFloat(g)
}
"""
    assert CodeGenerator.run(src) == "9 1.5 5.0"


def test_037_var_without_type_or_initializer():
    src = """
fun main() {
    var n
    n = 12
    printInt(n)
    var s
    s = "str"
    printString(s)
}
"""
    assert CodeGenerator.run(src) == "12str"


def test_038_chained_assignment():
    src = """
fun main() {
    var a = 0
    var b = 0
    var c = 0
    a = b = c = 5
    printInt(a)
    printInt(b)
    printInt(c)
}
"""
    assert CodeGenerator.run(src) == "555"


def test_039_assignment_used_as_expression():
    src = """
fun main() {
    var x = 0
    printInt(x = 7)
    printInt(x)
}
"""
    assert CodeGenerator.run(src) == "77"


def test_040_block_scope_shadowing():
    src = """
fun main() {
    val x = 1
    {
        val x = 2
        printInt(x)
    }
    printInt(x)
}
"""
    assert CodeGenerator.run(src) == "21"


# --------------------------------------------------------------------------- #
#  Increment / decrement                                                      #
# --------------------------------------------------------------------------- #
def test_041_postfix_increment_statement():
    src = """
fun main() {
    var i = 5
    i++
    i++
    printInt(i)
}
"""
    assert CodeGenerator.run(src) == "7"


def test_042_prefix_increment_value():
    src = """
fun main() {
    var i = 5
    printInt(++i)
    printInt(i)
}
"""
    assert CodeGenerator.run(src) == "66"


def test_043_postfix_increment_value():
    src = """
fun main() {
    var i = 5
    printInt(i++)
    printInt(i)
}
"""
    assert CodeGenerator.run(src) == "56"


def test_044_prefix_and_postfix_decrement():
    src = """
fun main() {
    var i = 5
    printInt(--i)
    printInt(i--)
    printInt(i)
}
"""
    assert CodeGenerator.run(src) == "443"


def test_045_increment_evaluation_order():
    src = """
fun main() {
    var i = 1
    printInt(i++ + i++)
    printInt(i)
    var j = 10
    printInt(j-- - --j)
    printInt(j)
}
"""
    assert CodeGenerator.run(src) == "3328"


# --------------------------------------------------------------------------- #
#  If statement / if expression                                               #
# --------------------------------------------------------------------------- #
def test_046_if_without_else():
    src = """
fun main() {
    val a = 5
    if (a > 0) {
        printString("pos")
    }
    printString("|")
    if (a > 0) printString("short")
}
"""
    assert CodeGenerator.run(src) == "pos|short"


def test_047_if_condition_false():
    src = """
fun main() {
    if (1 > 2) {
        printString("never")
    }
    printString("after")
}
"""
    assert CodeGenerator.run(src) == "after"


def test_048_if_else():
    src = """
fun main() {
    val n = 4
    if (n % 2 == 0) {
        printString("even")
    } else {
        printString("odd")
    }
}
"""
    assert CodeGenerator.run(src) == "even"


def test_049_if_else_if_chain():
    src = """
fun grade(score: Int): String {
    if (score >= 90) {
        return "A"
    } else if (score >= 80) {
        return "B"
    } else if (score >= 70) {
        return "C"
    } else {
        return "F"
    }
}

fun main() {
    printString(grade(95))
    printString(grade(85))
    printString(grade(75))
    printString(grade(65))
}
"""
    assert CodeGenerator.run(src) == "ABCF"


def test_050_dangling_else_binds_to_nearest_if():
    src = """
fun main() {
    val a = true
    val b = false
    if (a) if (b) printString("1") else printString("2")
    printString("|")
    val c = false
    if (c) if (b) printString("3") else printString("4")
    printString("end")
}
"""
    assert CodeGenerator.run(src) == "2|end"


def test_051_if_expression():
    src = """
fun main() {
    val x = 3
    val y = 7
    val m = if (x > y) x else y
    printInt(m)
    printInt(if (x < y) x else y)
    printFloat(if (x > 0) 1.5 else 2.5)
}
"""
    assert CodeGenerator.run(src) == "731.5"


def test_052_if_with_multi_statement_blocks():
    src = """
fun main() {
    var total = 0
    val n = 7
    if (n > 5) {
        total = total + n
        printString("big ")
    } else {
        total = total - n
        printString("small ")
    }
    printInt(total)
    if (n < 0) {
        printString("neg")
        total = 0
    } else {
        printString(" ok")
    }
}
"""
    assert CodeGenerator.run(src) == "big 7 ok"


# --------------------------------------------------------------------------- #
#  While statement                                                            #
# --------------------------------------------------------------------------- #
def test_053_while_counting():
    src = """
fun main() {
    var i = 0
    while (i < 5) {
        printInt(i)
        i++
    }
}
"""
    assert CodeGenerator.run(src) == "01234"


def test_054_while_accumulating():
    src = """
fun main() {
    var i = 1
    var sum = 0
    while (i <= 10) {
        sum = sum + i
        i++
    }
    printInt(sum)
}
"""
    assert CodeGenerator.run(src) == "55"


def test_055_while_body_never_runs_and_compound_condition():
    src = """
fun main() {
    var i = 10
    while (i < 5) {
        printInt(i)
        i++
    }
    var s = 0
    var k = 0
    while (k < 10 && s < 12) {
        s = s + k
        k++
    }
    printInt(k)
    printString(" ")
    printInt(s)
    printString(" done")
}
"""
    assert CodeGenerator.run(src) == "6 15 done"


def test_056_while_with_break():
    src = """
fun main() {
    var i = 0
    while (i < 10) {
        if (i == 5) {
            break
        }
        printInt(i)
        i++
    }
    printString("|")
    printInt(i)
}
"""
    assert CodeGenerator.run(src) == "01234|5"


def test_057_while_with_continue():
    src = """
fun main() {
    var i = 0
    while (i < 6) {
        i++
        if (i % 2 == 0) {
            continue
        }
        printInt(i)
    }
    printString("|")
    printInt(i)
}
"""
    assert CodeGenerator.run(src) == "135|6"


def test_058_nested_while():
    src = """
fun main() {
    var i = 0
    while (i < 3) {
        var j = 0
        while (j < 2) {
            printInt(i * 10 + j)
            printString(" ")
            j++
        }
        i++
    }
}
"""
    assert CodeGenerator.run(src) == "0 1 10 11 20 21"


def test_059_break_only_leaves_inner_while():
    src = """
fun main() {
    var i = 0
    while (i < 3) {
        var j = 0
        while (j < 5) {
            if (j == 2) {
                break
            }
            printInt(j)
            j++
        }
        printString("|")
        i++
    }
}
"""
    assert CodeGenerator.run(src) == "01|01|01|"


# --------------------------------------------------------------------------- #
#  For statement (range)                                                      #
# --------------------------------------------------------------------------- #
def test_060_for_basic_and_single_statement_body():
    src = """
fun main() {
    for (i in 0..4) {
        printInt(i)
    }
    for (i in 0..2) printString("x")
}
"""
    assert CodeGenerator.run(src) == "01234xxx"


def test_061_for_accumulating():
    src = """
fun main() {
    var sum = 0
    for (i in 1..100) {
        sum = sum + i
    }
    printInt(sum)
}
"""
    assert CodeGenerator.run(src) == "5050"


def test_062_for_empty_range():
    src = """
fun main() {
    for (i in 5..1) {
        printInt(i)
    }
    printString("empty")
}
"""
    assert CodeGenerator.run(src) == "empty"


def test_063_for_single_iteration():
    src = """
fun main() {
    for (i in 3..3) {
        printInt(i)
    }
    for (i in 0..0) {
        printInt(i)
    }
}
"""
    assert CodeGenerator.run(src) == "30"


def test_064_for_bounds_from_expressions():
    src = """
fun main() {
    val a = 2
    var b = 5
    for (i in a..b - 1) {
        printInt(i)
    }
    printString("|")
    for (i in a * 2..a * 2 + 1) {
        printInt(i)
    }
}
"""
    assert CodeGenerator.run(src) == "234|45"


def test_065_for_bounds_evaluated_once():
    src = """
fun lo(): Int {
    printString("L")
    return 1
}

fun hi(): Int {
    printString("H")
    return 3
}

fun main() {
    for (i in lo()..hi()) {
        printInt(i)
    }
}
"""
    assert CodeGenerator.run(src) == "LH123"


def test_066_nested_for_with_inner_break():
    src = """
fun main() {
    for (i in 1..3) {
        for (j in 1..3) {
            if (j == 2) {
                break
            }
            printInt(i)
            printInt(j)
        }
        printString(".")
    }
}
"""
    assert CodeGenerator.run(src) == "11.21.31."


def test_067_for_with_continue():
    src = """
fun main() {
    for (i in 1..5) {
        if (i == 3) {
            continue
        }
        printInt(i)
    }
    printString("|")
    for (i in 1..6) {
        if (i % 2 == 0) {
            continue
        }
        printInt(i)
    }
}
"""
    assert CodeGenerator.run(src) == "1245|135"


def test_068_for_loop_variable_scope():
    src = """
fun main() {
    for (i in 1..2) {
        printInt(i)
    }
    val i = 9
    printInt(i)
    for (k in 3..3) {
        val m = 7
        printInt(k * m)
    }
}
"""
    assert CodeGenerator.run(src) == "12921"


def test_069_nested_for_multiplication_table():
    src = """
fun main() {
    for (i in 1..3) {
        for (j in 1..3) {
            printInt(i * j)
            printString(" ")
        }
        printString("| ")
    }
}
"""
    assert CodeGenerator.run(src) == "1 2 3 | 2 4 6 | 3 6 9 |"


# --------------------------------------------------------------------------- #
#  When statement / when expression                                           #
# --------------------------------------------------------------------------- #
def test_070_when_subject_match():
    src = """
fun main() {
    val d = 2
    when (d) {
        1 -> printString("one")
        2 -> printString("two")
        3 -> printString("three")
    }
}
"""
    assert CodeGenerator.run(src) == "two"


def test_071_when_multiple_labels_per_branch():
    src = """
fun main() {
    val d = 3
    when (d) {
        1 -> printString("low")
        2, 3, 4 -> printString("mid")
        else -> printString("high")
    }
}
"""
    assert CodeGenerator.run(src) == "mid"


def test_072_when_else_branch_and_float_subject():
    src = """
fun main() {
    when (9) { 1 -> printString("a"); 2 -> printString("b"); else -> printString("z") }
    when (2.5) {
        1.5 -> printString("p")
        2.5 -> printString("q")
        else -> printString("r")
    }
}
"""
    assert CodeGenerator.run(src) == "zq"


def test_073_when_without_matching_branch():
    src = """
fun main() {
    when (7) {
        1 -> printString("a")
        2 -> printString("b")
    }
    printString("done")
}
"""
    assert CodeGenerator.run(src) == "done"


def test_074_when_with_empty_branch_list():
    src = """
fun main() {
    val a = 5
    when (a) { }
    printString("done")
}
"""
    assert CodeGenerator.run(src) == "done"


def test_075_when_conditionless_form():
    src = """
fun sign(n: Int) {
    when {
        n > 0 -> printString("+")
        n < 0 -> printString("-")
        else -> printString("0")
    }
}

fun main() {
    sign(5); sign(-5); sign(0)
}
"""
    assert CodeGenerator.run(src) == "+-0"


def test_076_when_expression_with_subject():
    src = """
fun name(d: Int): String {
    return when (d) {
        1 -> "one"
        2 -> "two"
        else -> "many"
    }
}

fun main() {
    printString(name(1))
    printString(name(2))
    printString(name(9))
}
"""
    assert CodeGenerator.run(src) == "onetwomany"


def test_077_when_expression_conditionless():
    src = """
fun main() {
    val n = -3
    val sign = when { n > 0 -> 1; n < 0 -> -1; else -> 0 }
    printInt(sign)
    val m = 0
    printInt(when { m > 0 -> 1; m < 0 -> -1; else -> 0 })
}
"""
    assert CodeGenerator.run(src) == "-10"


def test_078_when_with_string_and_boolean_subject():
    src = """
fun main() {
    val s = "b"
    when (s) {
        "a" -> printString("A")
        "b" -> printString("B")
        else -> printString("?")
    }
    val flag = true
    when (flag) {
        true -> printString("T")
        false -> printString("F")
    }
}
"""
    assert CodeGenerator.run(src) == "BT"


def test_079_when_with_blocks_and_nested_when():
    src = """
fun main() {
    val x = 2
    when (x) {
        1 -> {
            printString("one")
        }
        2 -> {
            printString("two")
            when {
                x > 1 -> printString("+")
                else -> printString("-")
            }
        }
        else -> printString("other")
    }
}
"""
    assert CodeGenerator.run(src) == "two+"


def test_080_continue_inside_when_inside_for():
    src = """
fun main() {
    for (i in 1..5) {
        when {
            i == 3 -> continue
            else -> printInt(i)
        }
    }
}
"""
    assert CodeGenerator.run(src) == "1245"


def test_081_break_inside_when_inside_while():
    src = """
fun main() {
    var i = 0
    while (i < 10) {
        when (i) {
            5 -> break
            else -> printInt(i)
        }
        i++
    }
    printString("end")
}
"""
    assert CodeGenerator.run(src) == "01234end"


# --------------------------------------------------------------------------- #
#  Functions                                                                  #
# --------------------------------------------------------------------------- #
def test_082_functions_with_declared_return_types():
    src = """
fun addI(a: Int, b: Int): Int {
    return a + b
}

fun addF(a: Float, b: Float): Float {
    return a + b
}

fun echo(s: String): String {
    return s
}

fun main() {
    printInt(addI(2, 3))
    printString(" ")
    printFloat(addF(1.5, 2))
    printString(" ")
    printString(echo("x"))
}
"""
    assert CodeGenerator.run(src) == "5 3.5 x"


def test_083_inferred_return_types():
    src = """
fun add(x: Int, y: Int) { return x + y }

fun scale(x: Float) { return x * 2.0 }

fun flag(x: Int) { return x > 0 }

fun main() {
    printInt(add(3, 4))
    printString(" ")
    printFloat(scale(1.25))
    printString(" ")
    printBool(flag(1))
}
"""
    assert CodeGenerator.run(src) == "7 2.5 true"


def test_084_unit_functions_and_bare_return():
    src = """
fun greet(name: String) {
    printString("hi ")
    printString(name)
}

fun maybe(n: Int) {
    if (n < 0) {
        return
    }
    printInt(n)
}

fun main() {
    greet("bob")
    maybe(-1)
    maybe(5)
}
"""
    assert CodeGenerator.run(src) == "hi bob5"


def test_085_recursive_factorial():
    src = """
fun factorial(n: Int): Int {
    if (n <= 1) {
        return 1
    } else {
        return n * factorial(n - 1)
    }
}

fun main() {
    printInt(factorial(5))
    printString(" ")
    printInt(factorial(10))
}
"""
    assert CodeGenerator.run(src) == "120 3628800"


def test_086_recursive_fibonacci():
    src = """
fun fib(n: Int): Int {
    if (n < 2) {
        return n
    }
    return fib(n - 1) + fib(n - 2)
}

fun main() {
    printInt(fib(10))
    printString(" ")
    printInt(fib(15))
}
"""
    assert CodeGenerator.run(src) == "55 610"


def test_087_recursive_gcd_and_power():
    src = """
fun gcd(a: Int, b: Int): Int {
    if (b == 0) {
        return a
    }
    return gcd(b, a % b)
}

fun power(base: Int, exp: Int): Int {
    if (exp == 0) {
        return 1
    }
    return base * power(base, exp - 1)
}

fun main() {
    printInt(gcd(48, 18))
    printString(" ")
    printInt(power(3, 4))
}
"""
    assert CodeGenerator.run(src) == "6 81"


def test_088_call_result_discarded_and_nested_calls():
    src = """
fun tick(): Int {
    printString("t")
    return 1
}

fun addv(a: Int, b: Int): Int {
    return a + b
}

fun main() {
    tick()
    printInt(addv(addv(1, 2), addv(3, 4)))
}
"""
    assert CodeGenerator.run(src) == "t10"


def test_089_many_parameters_and_return_from_loop():
    src = """
fun sum8(a: Int, b: Int, c: Int, d: Int, e: Int, f: Int, g: Int, h: Int): Int {
    return a + b + c + d + e + f + g + h
}

fun firstDivisor(n: Int): Int {
    for (i in 2..n) {
        if (n % i == 0) {
            return i
        }
    }
    return n
}

fun main() {
    printInt(sum8(1, 2, 3, 4, 5, 6, 7, 8))
    printString(" ")
    printInt(firstDivisor(91))
}
"""
    assert CodeGenerator.run(src) == "36 7"


def test_090_function_with_float_parameters_and_locals():
    src = """
fun average(a: Float, b: Float, c: Float): Float {
    val sum = a + b + c
    return sum / 3.0
}

fun half(n: Int): Float {
    return n / 2.0
}

fun truncHalf(n: Int): Float {
    return n / 2
}

fun main() {
    printFloat(average(1.0, 2.0, 3.0))
    printString(" ")
    printFloat(half(7))
    printString(" ")
    printFloat(truncHalf(7))
}
"""
    assert CodeGenerator.run(src) == "2.0 3.5 3.0"


# --------------------------------------------------------------------------- #
#  Data classes                                                               #
# --------------------------------------------------------------------------- #
def test_091_data_class_construction_and_member_read():
    src = """
data class Point(x: Int, y: Int)

fun main() {
    val p = Point(10, 20)
    printInt(p.x)
    printString(" ")
    printInt(p.y)
    printString(" ")
    printInt(p.x + p.y)
}
"""
    assert CodeGenerator.run(src) == "10 20 30"


def test_092_data_class_member_assignment():
    src = """
data class Counter(n: Int, label: String)

fun main() {
    var c = Counter(0, "c")
    c.n = 5
    printInt(c.n)
    c.n++
    printInt(c.n)
    printInt(++c.n)
    printString(c.label)
}
"""
    assert CodeGenerator.run(src) == "567c"


def test_093_nested_data_classes():
    src = """
data class Point(x: Int, y: Int)

data class Line(a: Point, b: Point)

fun main() {
    var l = Line(Point(1, 2), Point(3, 4))
    printInt(l.a.x)
    printInt(l.b.y)
    l.a.x = 9
    printInt(l.a.x)
    l.b = Point(7, 8)
    printInt(l.b.x)
}
"""
    assert CodeGenerator.run(src) == "1497"


def test_094_data_class_structural_equality():
    src = """
data class Point(x: Int, y: Int)

data class Line(a: Point, b: Point)

fun main() {
    printBool(Point(1, 2) == Point(1, 2))
    printBool(Point(1, 2) != Point(1, 3))
    printBool(Line(Point(1, 2), Point(3, 4)) == Line(Point(1, 2), Point(3, 4)))
    printBool(Line(Point(1, 2), Point(3, 4)) == Line(Point(1, 2), Point(0, 4)))
}
"""
    assert CodeGenerator.run(src) == "truetruetruefalse"


def test_095_data_class_as_parameter_and_return():
    src = """
data class Point(x: Int, y: Int)

fun makePoint(a: Int, b: Int): Point {
    return Point(a, b)
}

fun norm1(p: Point): Int {
    return p.x + p.y
}

fun main() {
    printInt(makePoint(3, 4).x)
    printString(" ")
    printInt(norm1(makePoint(3, 4)))
    printString(" ")
    printInt(norm1(Point(10, 1)))
}
"""
    assert CodeGenerator.run(src) == "3 7 11"


def test_096_empty_data_class_and_member_widening():
    src = """
data class Empty()

data class Person(name: String, age: Int, height: Float)

fun main() {
    printBool(Empty() == Empty())
    val p = Person("John", 25, 2)
    printString(p.name)
    printInt(p.age)
    printFloat(p.height)
}
"""
    assert CodeGenerator.run(src) == "trueJohn252.0"


def test_097_data_class_reference_assignment():
    src = """
data class Box(v: Int)

fun main() {
    var a = Box(1)
    var b = a
    b.v = 9
    printInt(a.v)
    printInt(b.v)
    var c: Box
    c = Box(3)
    printInt(c.v)
}
"""
    assert CodeGenerator.run(src) == "993"


# --------------------------------------------------------------------------- #
#  Integration programs                                                       #
# --------------------------------------------------------------------------- #
def test_098_primes_up_to_twenty():
    src = """
fun isPrime(n: Int): Boolean {
    if (n < 2) {
        return false
    }
    var i = 2
    while (i * i <= n) {
        if (n % i == 0) {
            return false
        }
        i++
    }
    return true
}

fun main() {
    for (k in 2..20) {
        if (isPrime(k)) {
            printInt(k)
            printString(" ")
        }
    }
}
"""
    assert CodeGenerator.run(src) == "2 3 5 7 11 13 17 19"


def test_099_digit_manipulation():
    src = """
fun sumDigits(n: Int): Int {
    var s = 0
    var m = n
    while (m > 0) {
        s = s + m % 10
        m = m / 10
    }
    return s
}

fun reverse(n: Int): Int {
    var r = 0
    var m = n
    while (m > 0) {
        r = r * 10 + m % 10
        m = m / 10
    }
    return r
}

fun isPalindrome(n: Int): Boolean {
    return n == reverse(n)
}

fun main() {
    printInt(sumDigits(12345))
    printString(" ")
    printInt(reverse(12345))
    printString(" ")
    printBool(isPalindrome(12321))
    printBool(isPalindrome(12345))
}
"""
    assert CodeGenerator.run(src) == "15 54321 truefalse"


def test_100_read_and_summarize_input():
    src = """
fun main() {
    val n = readInt()
    var sum = 0
    var max = 0
    var first = true
    for (i in 1..n) {
        val v = readInt()
        sum = sum + v
        if (first) {
            max = v
            first = false
        } else {
            if (v > max) {
                max = v
            }
        }
    }
    printInt(sum)
    printString(" ")
    printInt(max)
    printString(" ")
    printFloat(sum * 1.0 / n)
}
"""
    assert CodeGenerator.run(src, "3\n4\n9\n2\n") == "15 9 5.0"

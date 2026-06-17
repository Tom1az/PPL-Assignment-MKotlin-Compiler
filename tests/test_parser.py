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

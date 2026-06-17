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


def test_003_arithmetic():
    src = "fun main() {\n  printInt(2 + 3 * 4)\n}"
    assert CodeGenerator.run(src) == "14"

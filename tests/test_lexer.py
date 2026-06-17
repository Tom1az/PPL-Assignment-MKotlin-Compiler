"""
Lexer test cases for MKotlin compiler.
TODO: Implement 100 test cases for lexer
"""

from tests.utils import Tokenizer


# ========== Simple Test Cases (10 types) ==========
def test_keyword_val():
    """1. Keyword"""
    assert Tokenizer.tokens("val") == "val,EOF"


def test_operator_eq():
    """2. Operator"""
    assert Tokenizer.tokens("==") == "==,EOF"


def test_separator_semi():
    """3. Separator"""
    assert Tokenizer.tokens(";") == ";,EOF"


def test_integer_with_underscores():
    """4. Integer literal"""
    assert Tokenizer.tokens("1_000") == "1_000,EOF"


def test_float_literal():
    """5. Float literal"""
    assert Tokenizer.tokens("3.14") == "3.14,EOF"


def test_string_simple():
    """6. String literal"""
    assert Tokenizer.tokens('"hello"') == "hello,EOF"


def test_identifier_simple():
    """7. Identifier"""
    assert Tokenizer.tokens("foo") == "foo,EOF"


def test_line_comment():
    """8. Line comment"""
    assert Tokenizer.tokens("val x // comment") == "val,x,EOF"


def test_mixed_expression():
    """9. Mixed: operators and literals"""
    assert Tokenizer.tokens("1 + 2") == "1,+,2,EOF"


def test_unrecognized_char():
    """10. Lexical error"""
    assert Tokenizer.tokens("@") == "@"

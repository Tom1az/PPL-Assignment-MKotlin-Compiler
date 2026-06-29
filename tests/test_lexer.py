"""
Lexer test cases for MKotlin compiler.
TODO: Implement 100 test cases for lexer
"""

from tests.utils import Tokenizer


# ========== Simple Test Cases (10 types) ==========
def test_keyword_val():
    """1. Keyword"""
    assert Tokenizer.tokens("val") == "val,EOF"

def test_keyword_var():
    """2. Keyword"""
    assert Tokenizer.tokens("var") == "var,EOF"

def test_keyword_break():
    """3. Keyword"""
    assert Tokenizer.tokens("break") == "break,EOF"

def test_keyword_continue():
    """4. Keyword"""
    assert Tokenizer.tokens("continue") == "continue,EOF"

def test_keyword_if():
    """5. Keyword"""
    assert Tokenizer.tokens("if") == "if,EOF"

def test_keyword_else():
    """6. Keyword"""
    assert Tokenizer.tokens("else") == "else,EOF"

def test_keyword_while():
    """7. Keyword"""
    assert Tokenizer.tokens("while") == "while,EOF"

def test_operator_eq():
    """2. Operator"""
    assert Tokenizer.tokens("==") == "==,EOF"

def test_separator_semi():
    """3. Separator"""
    assert Tokenizer.tokens(";") == ";,EOF"


def test_integer_with_underscores_1():
    """4. Integer literal"""
    assert Tokenizer.tokens("1_000") == "1_000,EOF"

def test_float_literal():
    """5. Float literal"""
    assert Tokenizer.tokens("3.14") == "3.14,EOF"


def test_string_simple_1():
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

def test_integer_with_underscores_2():
    """11. Integer literal with multiple underscores"""
    assert Tokenizer.tokens("123_456_789") == "123_456_789,EOF"

def test_string_simple_2():
    """12. String literal"""
    assert Tokenizer.tokens('"hello kkk"') == "hello kkk,EOF"

def test_block_comment():
    """13. Block comment"""
    assert Tokenizer.tokens("val x /* comment */") == "val,x,EOF"

def test_line_comment():
    """14. Line comment"""
    assert Tokenizer.tokens("val x // comment") == "val,x,EOF"

def test_float_missing_integer_part():
    """Float bắt đầu bằng dấu chấm"""
    assert Tokenizer.tokens(".5") == ".5,EOF"

def test_float_missing_fraction_part():
    """Float kết thúc bằng dấu chấm"""
    assert Tokenizer.tokens("1.") == "1.,EOF"

def test_float_with_exponent_only():
    """Float chỉ có số mũ, không có dấu chấm"""
    assert Tokenizer.tokens("1e4") == "1e4,EOF"

def test_float_with_exponent_and_sign():
    """Float có số mũ âm và hậu tố F"""
    assert Tokenizer.tokens("2.5E-3F") == "2.5E-3F,EOF" 

def test_operator_range():
    """Toán tử Range (..)"""
    assert Tokenizer.tokens("a..b") == "a,..,b,EOF"

def test_operator_arrow():
    """Mũi tên trong biểu thức when"""
    assert Tokenizer.tokens("->") == "->,EOF"

def test_operator_longest_match():
    """Phân biệt == và = đứng cạnh nhau"""
    # Không được bắt nhầm thành =, =, =
    assert Tokenizer.tokens("x == =") == "x,==,=,EOF"

def test_string_with_escapes():
    """Chuỗi chứa escape hợp lệ: tab, newline, dấu nháy kép"""
    # Ký tự \ trong Python string phải viết là \\
    assert Tokenizer.tokens('"Hello\\tWorld\\n\\"MKotlin\\""') == 'Hello\\tWorld\\n\\"MKotlin\\",EOF'

def test_string_empty():
    """Chuỗi rỗng"""
    assert Tokenizer.tokens('""') == ",EOF"

def test_error_illegal_escape():
    """Ký tự escape không hợp lệ (vd: \\x)"""
    # Chuỗi gốc: "abc \x xyz" -> Lỗi phải dừng ở abc \x
    assert Tokenizer.tokens('"abc \\x xyz"') == "abc \\x"

def test_error_illegal_escape_dollar():
    """Bắt lỗi unescaped dollar sign theo đặc tả"""
    # Nếu $ không đi kèm \, nó được xem là ký tự lỗi (nếu đứng trước chữ/ngoặc)
    assert Tokenizer.tokens('"price is $100"') == "price is "

def test_error_unrecognized_char():
    """Ký tự không thuộc bảng mã của MKotlin"""
    assert Tokenizer.tokens("val x = 10 #") == "val,x,=,10,#"

def test_newline_as_separator():
    """Xuống dòng đóng vai trò tách 2 câu lệnh"""
    # Lưu ý: Tokenizer có thể in ra '\n' dạng literal trong output
    assert Tokenizer.tokens("val x\nval y") == "val,x,\n,val,y,EOF"

def test_multiple_newlines():
    """Nhiều dấu xuống dòng liên tiếp"""
    assert Tokenizer.tokens("a\n\n\nb") == "a,\n,\n,\n,b,EOF"

def test_dollar_sign_escaped():
    """Dấu $ được escape bằng \\"""
    assert Tokenizer.tokens('"kkk\\$lll"') == "kkk\\$lll,EOF"

def test_dollar_sign_unescaped():
    """Dấu $ không được escape"""
    assert Tokenizer.tokens('"kkk$lll"') == "kkk"

def test_string_double_error_escape_wins():
    """Chuỗi vừa sai escape, vừa chưa đóng -> Ưu tiên báo lỗi Escape trước"""
    # Chuỗi gốc: "abc \x def \n
    assert Tokenizer.tokens('"abc \\x def \n') == "abc \\x"

def test_float_literal_only_f():
    """Số Float chỉ có hậu tố f, không có chấm hay mũ"""
    assert Tokenizer.tokens("1f") == "1f,EOF"

def test_float_vs_member_access():
    """Bẫy Longest Match: 1.x sẽ bị tách thành Float(1.) và Ident(x)"""
    assert Tokenizer.tokens("1.x") == "1.,x,EOF"

def test_integer_underscore_trailing():
    """Dấu gạch dưới ở cuối số nguyên -> Tách thành Int và Ident"""
    assert Tokenizer.tokens("100_") == "100,_,EOF"

def test_integer_underscore_consecutive():
    """Gạch dưới đứng liền nhau -> Tách thành Int và Ident"""
    assert Tokenizer.tokens("1__000") == "1,__000,EOF"

def test_comment_line_contains_block():
    """Line comment vô hiệu hóa các dấu của Block comment"""
    # Mọi thứ sau // đều bị skip, không báo lỗi thiếu */
    assert Tokenizer.tokens("val x // /* \n val y") == "val,x,\n,val,y,EOF"

def test_comment_block_contains_line():
    """Block comment vô hiệu hóa các dấu của Line comment"""
    # Dấu // bị bỏ qua, comment kết thúc ở */
    assert Tokenizer.tokens("val x /* // */ val y") == "val,x,val,y,EOF"

def test_case_sensitive_keyword_vs_ident():
    """Phân biệt từ khóa và identifier dựa trên viết hoa/thường"""
    assert Tokenizer.tokens("if IF If iF") == "if,IF,If,iF,EOF"

def float_with_exponent_and_sign():
    """Float có số mũ âm và hậu tố F"""
    assert Tokenizer.tokens("2.5E-3F") == "2.5E-3F,EOF"

def test_err_error_char_attached():
    """Ký tự rác dính liền vào Identifier"""
    # Lexer lấy 'val', lấy 'x', rồi mới ném lỗi '@'
    assert Tokenizer.tokens("val x@y") == "val,x,@"

def test_err_error_char_multiple():
    """Nhiều ký tự rác liên tiếp"""
    # Lexer sẽ dừng ngay ở ký tự rác đầu tiên (#), không quan tâm phần sau
    assert Tokenizer.tokens("100 # @ ?") == "100,#"

def test_edge_case_float_with_float():
    """Hai số thực dính liền vào nhau qua dấu chấm của phần mũ"""
    assert Tokenizer.tokens("2.5e-3.333") == "2.5e-3,.333,EOF"


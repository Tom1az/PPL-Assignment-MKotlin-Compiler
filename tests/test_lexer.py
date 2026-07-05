"""
Lexer test cases for MKotlin compiler.
105 curated test cases, ordered by increasing difficulty.
"""

from tests.utils import Tokenizer


# ========== Keywords & reserved type names ==========
def test_001():
    """Keyword val"""
    assert Tokenizer.tokens("val") == "val,EOF"

def test_002():
    """Keyword var"""
    assert Tokenizer.tokens("var") == "var,EOF"

def test_003():
    """Keyword fun"""
    assert Tokenizer.tokens("fun") == "fun,EOF"

def test_004():
    """Keyword when"""
    assert Tokenizer.tokens("when") == "when,EOF"

def test_005():
    """data class keywords"""
    assert Tokenizer.tokens("data class") == "data,class,EOF"

def test_006():
    """Control-flow keywords"""
    assert Tokenizer.tokens("if else while for") == "if,else,while,for,EOF"

def test_007():
    """Jump keywords"""
    assert Tokenizer.tokens("break continue return") == "break,continue,return,EOF"

def test_008():
    """Boolean literal keywords"""
    assert Tokenizer.tokens("true false") == "true,false,EOF"

def test_009():
    """Keywords is and in"""
    assert Tokenizer.tokens("is in") == "is,in,EOF"

def test_010():
    """Reserved type names"""
    assert Tokenizer.tokens("Int Float Boolean String Unit") == "Int,Float,Boolean,String,Unit,EOF"


# ========== Identifiers ==========
def test_011():
    """Simple identifier"""
    assert Tokenizer.tokens("foo") == "foo,EOF"

def test_012():
    """Identifiers are case-sensitive"""
    assert Tokenizer.tokens("MyVar myvar MYVAR") == "MyVar,myvar,MYVAR,EOF"

def test_013():
    """Leading and trailing underscores"""
    assert Tokenizer.tokens("_my_identifier_") == "_my_identifier_,EOF"

def test_014():
    """Digits and underscores inside an identifier"""
    assert Tokenizer.tokens("var123a_45") == "var123a_45,EOF"

def test_015():
    """Identifiers that merely start with a keyword prefix"""
    assert Tokenizer.tokens("validate variable funny") == "validate,variable,funny,EOF"

def test_016():
    """A single underscore is a valid identifier"""
    assert Tokenizer.tokens("_") == "_,EOF"

def test_017():
    """Multiple underscores form one identifier"""
    assert Tokenizer.tokens("___") == "___,EOF"

def test_018():
    """Keyword matching is case-sensitive (only lowercase 'if' is a keyword)"""
    assert Tokenizer.tokens("if IF If iF") == "if,IF,If,iF,EOF"


# ========== Separators & operators ==========
def test_019():
    """Bracket separators"""
    assert Tokenizer.tokens("( ) { }") == "(,),{,},EOF"

def test_020():
    """Separators: semicolon, comma, colon, arrow (the lone ',' shows as ',,,')"""
    assert Tokenizer.tokens("; , : ->") == ";,,,:,->,EOF"

def test_021():
    """Range operator"""
    assert Tokenizer.tokens("..") == "..,EOF"

def test_022():
    """Arithmetic operators"""
    assert Tokenizer.tokens("+ - * / %") == "+,-,*,/,%,EOF"

def test_023():
    """Ordering operators"""
    assert Tokenizer.tokens("< <= > >=") == "<,<=,>,>=,EOF"

def test_024():
    """Equality and logical operators"""
    assert Tokenizer.tokens("== != && || !") == "==,!=,&&,||,!,EOF"

def test_025():
    """Increment and decrement operators"""
    assert Tokenizer.tokens("++ --") == "++,--,EOF"

def test_026():
    """Assignment and member access"""
    assert Tokenizer.tokens("= .") == "=,.,EOF"

def test_027():
    """A simple mixed expression"""
    assert Tokenizer.tokens("1 + 2") == "1,+,2,EOF"

def test_028():
    """Maximal munch: '==' then '='"""
    assert Tokenizer.tokens("x == =") == "x,==,=,EOF"


# ========== Whitespace & newlines ==========
def test_029():
    """A newline is emitted as a separator token"""
    assert Tokenizer.tokens("a\nb") == "a,\n,b,EOF"

def test_030():
    """Consecutive newlines each produce a token"""
    assert Tokenizer.tokens("a\n\n\nb") == "a,\n,\n,\n,b,EOF"

def test_031():
    """Tab and form feed are skipped; CRLF is a single newline token"""
    assert Tokenizer.tokens("val\t\fx\r\n") == "val,x,\r\n,EOF"


# ========== Integer literals ==========
def test_032():
    """Zero"""
    assert Tokenizer.tokens("0") == "0,EOF"

def test_033():
    """A plain integer"""
    assert Tokenizer.tokens("123") == "123,EOF"

def test_034():
    """Leading zeros are allowed"""
    assert Tokenizer.tokens("007") == "007,EOF"

def test_035():
    """Underscore separator between digits"""
    assert Tokenizer.tokens("1_000") == "1_000,EOF"

def test_036():
    """Multiple single underscores"""
    assert Tokenizer.tokens("1_2_3") == "1_2_3,EOF"

def test_037():
    """Trailing underscore splits into integer and identifier"""
    assert Tokenizer.tokens("100_") == "100,_,EOF"

def test_038():
    """Adjacent underscores split into integer and identifier"""
    assert Tokenizer.tokens("1__000") == "1,__000,EOF"

def test_039():
    """Integer immediately followed by an identifier"""
    assert Tokenizer.tokens("0abc") == "0,abc,EOF"


# ========== Float literals ==========
def test_040():
    """Standard float"""
    assert Tokenizer.tokens("3.14") == "3.14,EOF"

def test_041():
    """Float ending with a dot"""
    assert Tokenizer.tokens("1.") == "1.,EOF"

def test_042():
    """Float starting with a dot"""
    assert Tokenizer.tokens(".5") == ".5,EOF"

def test_043():
    """Float with exponent and no dot"""
    assert Tokenizer.tokens("1e4") == "1e4,EOF"

def test_044():
    """Integer digit with an f suffix is a float"""
    assert Tokenizer.tokens("3f") == "3f,EOF"

def test_045():
    """Exponent with an explicit plus sign"""
    assert Tokenizer.tokens("1e+5") == "1e+5,EOF"

def test_046():
    """Dot, signed exponent and F suffix"""
    assert Tokenizer.tokens("2.5E-3F") == "2.5E-3F,EOF"

def test_047():
    """Longest match: '1.' is a float, then identifier 'x'"""
    assert Tokenizer.tokens("1.x") == "1.,x,EOF"

def test_048():
    """Range over integers wins over a float ending in a dot"""
    assert Tokenizer.tokens("1..5") == "1,..,5,EOF"

def test_049():
    """Range between two float literals"""
    assert Tokenizer.tokens("1.5..2.5") == "1.5,..,2.5,EOF"

def test_050():
    """Two floats glued together by a dot in the second"""
    assert Tokenizer.tokens("2.5e-3.333") == "2.5e-3,.333,EOF"


# ========== String literals (valid) ==========
def test_051():
    """Simple string; the quotes are stripped"""
    assert Tokenizer.tokens('"hello"') == "hello,EOF"

def test_052():
    """Empty string"""
    assert Tokenizer.tokens('""') == ",EOF"

def test_053():
    """String of only spaces"""
    assert Tokenizer.tokens('"   "') == "   ,EOF"

def test_054():
    """Operators and keywords inside a string are literal content"""
    assert Tokenizer.tokens('"val x = 1 + 2"') == "val x = 1 + 2,EOF"

def test_055():
    """Comment markers inside a string are literal content"""
    assert Tokenizer.tokens('"// not a comment /* also */"') == "// not a comment /* also */,EOF"

def test_056():
    """Every supported escape sequence"""
    assert Tokenizer.tokens('"\\b\\f\\r\\n\\t\\"\\\\\\$"') == r"\b\f\r\n\t\"\\\$" + ",EOF"

def test_057():
    """Escaped backslash followed by a literal n"""
    assert Tokenizer.tokens('"a\\\\nb"') == "a\\\\nb,EOF"

def test_058():
    """Escaped dollar before a letter is valid content"""
    assert Tokenizer.tokens('"escaped \\$letter is ok"') == "escaped \\$letter is ok,EOF"

def test_059():
    """Escaped dollar before a letter and before a brace"""
    assert Tokenizer.tokens('"\\$name \\${var}"') == "\\$name \\${var},EOF"


# ========== String literals (errors) ==========
def test_060():
    """Illegal escape stops at the wrong sequence"""
    assert Tokenizer.tokens('"abc \\x xyz"') == "abc \\x"

def test_061():
    """Illegal escape at the very start of the string"""
    assert Tokenizer.tokens('"\\qrst"') == "\\q"

def test_062():
    """Unicode escapes are not supported"""
    assert Tokenizer.tokens('"bad \\u0041"') == "bad \\u"

def test_063():
    """A digit is not a valid escape character"""
    assert Tokenizer.tokens('"n=\\0"') == "n=\\0"

def test_064():
    """A single quote is not a valid escape character"""
    assert Tokenizer.tokens('"a\\\'b"') == "a\\'"

def test_065():
    """Unescaped '$' before a letter is illegal (template reserved)"""
    assert Tokenizer.tokens('"hello $name"') == "hello $"

def test_066():
    """Unescaped '$' before '{' is illegal"""
    assert Tokenizer.tokens('"value: ${x}"') == "value: $"

def test_067():
    """Unclosed string at end of file"""
    assert Tokenizer.tokens('"missing end quote') == "missing end quote"

def test_068():
    """Unclosed string terminated by a newline (newline excluded)"""
    assert Tokenizer.tokens('"line one\nx') == "line one"

def test_069():
    """A raw newline in a string leaves it unclosed"""
    assert Tokenizer.tokens('"hello\nworld"') == "hello"

def test_070():
    """Illegal escape is detected before unclosed string"""
    assert Tokenizer.tokens('"abc \\x def \n') == "abc \\x"

def test_071():
    """Illegal escape just before end of file"""
    assert Tokenizer.tokens('"oops \\y') == "oops \\y"

def test_072():
    """Backslash before a newline is an illegal escape (includes the newline)"""
    assert Tokenizer.tokens('"ended with backslash \\\n') == "ended with backslash \\\n"


# ========== Comments ==========
def test_073():
    """Line comment is ignored"""
    assert Tokenizer.tokens("val x // comment") == "val,x,EOF"

def test_074():
    """Block comment is ignored"""
    assert Tokenizer.tokens("val x /* comment */") == "val,x,EOF"

def test_075():
    """Block comment spanning multiple lines"""
    assert Tokenizer.tokens("val /* line 1 \n line 2 */ y") == "val,y,EOF"

def test_076():
    """Comments are not nested: closes at the first '*/'"""
    assert Tokenizer.tokens("/* outer /* inner */ class") == "class,EOF"

def test_077():
    """Not nested: leftover after the first '*/' is tokenized"""
    assert Tokenizer.tokens("/* a /* b */ c */ d") == "c,*,/,d,EOF"

def test_078():
    """Line comment neutralizes block markers; the newline is a token"""
    assert Tokenizer.tokens("val x // /* \n val y") == "val,x,\n,val,y,EOF"

def test_079():
    """Block comment neutralizes line markers"""
    assert Tokenizer.tokens("val x /* // */ val y") == "val,x,val,y,EOF"

def test_080():
    """Empty block comment between two identifiers"""
    assert Tokenizer.tokens("a/**/b") == "a,b,EOF"


# ========== Maximal munch (operator adjacency) ==========
def test_081():
    """'===' becomes '==' then '='"""
    assert Tokenizer.tokens("x===y") == "x,==,=,y,EOF"

def test_082():
    """'+++' becomes '++' then '+'"""
    assert Tokenizer.tokens("x+++y") == "x,++,+,y,EOF"

def test_083():
    """'---' becomes '--' then '-'"""
    assert Tokenizer.tokens("x---y") == "x,--,-,y,EOF"

def test_084():
    """'!==' becomes '!=' then '='"""
    assert Tokenizer.tokens("a!==b") == "a,!=,=,b,EOF"

def test_085():
    """'-->' is decrement then greater-than"""
    assert Tokenizer.tokens("-->") == "--,>,EOF"

def test_086():
    """Arrows and minus/greater-than packed together"""
    assert Tokenizer.tokens("->->- >") == "->,->,-,>,EOF"

def test_087():
    """A dense chain of logical/relational operators"""
    assert Tokenizer.tokens("a&&b||c!=d==e<=f") == "a,&&,b,||,c,!=,d,==,e,<=,f,EOF"

def test_088():
    """'...' becomes range then member-access dot"""
    assert Tokenizer.tokens("...") == "..,.,EOF"


# ========== Unrecognized characters (error stops lexing) ==========
def test_089():
    """A lone unrecognized character"""
    assert Tokenizer.tokens("@") == "@"

def test_090():
    """Valid tokens are emitted before the error"""
    assert Tokenizer.tokens("val x = 10 #") == "val,x,=,10,#"

def test_091():
    """Unrecognized character glued to an identifier"""
    assert Tokenizer.tokens("val x@y") == "val,x,@"

def test_092():
    """A single '&' is unrecognized (only '&&' is an operator)"""
    assert Tokenizer.tokens("a & b") == "a,&"

def test_093():
    """A single '|' is unrecognized (only '||' is an operator)"""
    assert Tokenizer.tokens("x | y") == "x,|"

def test_094():
    """Lexing stops at the first unrecognized character"""
    assert Tokenizer.tokens("ok = 1 ? 2 # 3") == "ok,=,1,?"


# ========== Compound / realistic snippets ==========
def test_095():
    """A typed variable declaration"""
    assert Tokenizer.tokens("val x: Int = 10") == "val,x,:,Int,=,10,EOF"

def test_096():
    """A data class header"""
    assert Tokenizer.tokens("data class Point(x: Int, y: Int)") == \
        "data,class,Point,(,x,:,Int,,,y,:,Int,),EOF"

def test_097():
    """A function header with parameters and return type"""
    assert Tokenizer.tokens("fun compute(x: Int, y: Float, s: String): Unit") == \
        "fun,compute,(,x,:,Int,,,y,:,Float,,,s,:,String,),:,Unit,EOF"

def test_098():
    """A for-range header with arithmetic bounds"""
    assert Tokenizer.tokens("for(i in start+1..end-1)") == \
        "for,(,i,in,start,+,1,..,end,-,1,),EOF"

def test_099():
    """A when arm with multiple labels and a call"""
    assert Tokenizer.tokens("when(value){1, 2, 3 -> printInt(1)}") == \
        "when,(,value,),{,1,,,2,,,3,->,printInt,(,1,),},EOF"

def test_100():
    """A deep member-access assignment"""
    assert Tokenizer.tokens("person.address.city.zip = 70000") == \
        "person,.,address,.,city,.,zip,=,70000,EOF"

def test_101():
    """Forum Q10: unclosed block comment tokenizes as / * then content, not ERROR_TOKEN"""
    assert Tokenizer.tokens("/* abc") == "/,*,abc,EOF"

def test_102():
    """Spec: unprintable ASCII (e.g. tab) may appear directly in a string literal"""
    assert Tokenizer.tokens('"a\tb"') == "a\tb,EOF"

def test_103():
    """Integer literal with multiple underscore groups: 1_000_000"""
    assert Tokenizer.tokens("1_000_000") == "1_000_000,EOF"

def test_104():
    """Float literal with decimal point and exponent: 1.23e4"""
    assert Tokenizer.tokens("1.23e4") == "1.23e4,EOF"

def test_105():
    """Chuỗi kết thúc bằng dấu backslash (\\) ngay sát EOF là UNCLOSE_STRING, không phải ILLEGAL_ESCAPE"""
    # Python string '"text\\' tương đương chuỗi: " t e x t \ (hết file)
    input_code = '"text\\'
    expected = "text\\"
    assert Tokenizer.tokens(input_code) == expected
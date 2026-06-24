grammar MKotlin;

@lexer::header {
from src.grammar.lexererr import (
    ErrorToken,
    UncloseString,
    IllegalEscape,
)
}

@lexer::members {
def emit(self):
    tk = self.type
    if tk == self.UNCLOSE_STRING:
        result = super().emit()
        raise UncloseString(result.text)
    elif tk == self.ILLEGAL_ESCAPE:
        result = super().emit()
        raise IllegalEscape(result.text)
    elif tk == self.ERROR_CHAR:
        result = super().emit()
        raise ErrorToken(result.text)
    else:
        return super().emit()
}

options {
    language = Python3;
}

// TODO: Define parser rules here
// See mkotlin_specification.md — Grammar Summary
//
// Hints:
// - program: optional leading newlines, declList, EOF
// - decl: dataClassDecl | funcDecl
// - statements separated by sep (NEWLINE | SEMI)
// - expression precedence (low -> high): assignment, ||, &&, ==/!=,
//   </<=/>/>=, +/-, */%, unary, postfix (. / call / ++/--), primary
// - when/if as both statement and expression forms

program
    : EOF
    ;

// TODO: Define lexer rules here
// Keywords, operators, literals, comments, NEWLINE (statement separator), ...
//
// Hints:
// - Error detection order: ILLEGAL_ESCAPE -> UNCLOSE_STRING -> STRINGLIT -> ...
// - STRINGLIT must strip enclosing quotes: self.text = self.text[1:-1]
// - FLOATLIT must precede INTLIT
// - Keyword/type rules must precede IDENT
// - NEWLINE is a real token — do NOT skip newlines in WS

//Keywords
BREAK : 'break' ;
CLASS : 'class' ;
CONTINUE: 'continue' ;
DATA : 'data' ;
ELSE : 'else' ;
FALSE : 'false' ;
FOR : 'for' ;
FUN : 'fun' ;
IF : 'if' ;
IN : 'in' ;
IS : 'is' ;
RETURN : 'return' ;
TRUE : 'true' ;
VAL : 'val' ;
WHEN : 'when' ;
WHILE : 'while' ;

// Built-in types
INT : 'Int' ;
FLOAT : 'Float' ;
BOOLEAN : 'Boolean' ;
UNIT : 'Unit' ;

// operator
ADD : '+' ;
SUB : '-' ;
MUL : '*' ;
DIV : '/' ;
MOD : '%' ;
EQ : '==' ;
NEQ : '!=' ;
LT : '<' ;
GT : '>' ;
LTE : '<=' ;
GTE : '>=' ;

AND : '&&' ;
OR : '||' ;
NOT : '!' ;
INC : '++' ;
DEC : '--' ;
ASGN : '=' ;
MEMACC : '.' ;
RANGE : '..' ;

// Literals
INT : [0-9]+ ('_' [0-9]+)* { 
    self.text = self.text.replace('_','')
};
FLOAT : DEC EXP? [fF]? | [0-9]+ (EXP [fF]? | [fF]);
fragment DEC : [0-9]+ '.' [0-9]* | [0-9]* '.' [0-9]+ ;
fragment EXP : [eE] [+-]? [0-9]+ ;


WS : [ \t\f]+ -> skip ;

ERROR_CHAR     : . ;
ILLEGAL_ESCAPE : . ;
UNCLOSE_STRING : . ;

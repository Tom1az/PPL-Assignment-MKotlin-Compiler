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

program : newlineList declList EOF ;
newlineList : NEWLINE newlineList | ;
declList : decl newlineList declList | ;
decl : dataClassDecl | funcDecl;
dataClassDecl : DATA CLASS IDENT LP memList RP | DATA CLASS 'Empty' LP RP;
memList : mem COMMA memList | mem ;
mem : IDENT COLON typ ;
typ : INT | FLOAT | BOOLEAN | STRING | IDENT ;


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
VAR : 'var' ;
WHEN : 'when' ;
WHILE : 'while' ;

// Built-in types
INT : 'Int' ;
FLOAT : 'Float' ;
BOOLEAN : 'Boolean' ;
STRING : 'String' ;
UNIT : 'Unit' ;

// Identifier
IDENT : [a-zA-Z_] [a-zA-Z_0-9]* ;

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
INCREMENT : '++' ;
DECREMENT : '--' ;
ASGN : '=' ;
MEMACC : '.' ;
RANGE : '..' ;

//Separator
LB : '{' ;
RB : '}' ;
LP : '(' ;
RP : ')' ;
SEMI : ';' ;
COMMA : ',' ;
COLON : ':' ;
ARROW : '->' ;

// Literals
FLOATLIT : DEC EXP? [fF]? | [0-9]+ (EXP [fF]? | [fF]);
fragment DEC : [0-9]+ '.' [0-9]* | '.' [0-9]+ ;
fragment EXP : [eE] [+-]? [0-9]+ ;
INTLIT : [0-9]+ ('_' [0-9]+)* ;
ILLEGAL_ESCAPE : ["] (NORMAL_CHAR | ESCAPE_CHAR)* '\\' ~[bfrnt"\\$] {
    self.text = self.text[1:]
};
UNCLOSE_STRING : ["] (NORMAL_CHAR | ESCAPE_CHAR)* {
    self.text = self.text[1:]
};
STRINGLIT : ["] (NORMAL_CHAR | ESCAPE_CHAR)* ["] {
    self.text = self.text[1:-1]
}; 
fragment NORMAL_CHAR : ~["\\\r\n$] ;
fragment ESCAPE_CHAR : '\\' [bfrnt"\\$] ;

// comments
BLK_CMT : '/*' .*? '*/' -> skip ;
LINE_CMT : '//' ~[\r\n]* -> skip ;

NEWLINE : '\r'?'\n' ;
WS : [ \t\f]+ -> skip ;

ERROR_CHAR     : . ;

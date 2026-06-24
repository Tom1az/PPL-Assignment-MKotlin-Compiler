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

BREAK : 'break';
CLASS : 'class';
CONTINUE " 'continue';
DATA : 'data';
ELSE : 'else';
FALSE : 'false';
FOR : 'for';

WS : [ \t\f]+ -> skip ;

ERROR_CHAR     : . ;
ILLEGAL_ESCAPE : . ;
UNCLOSE_STRING : . ;

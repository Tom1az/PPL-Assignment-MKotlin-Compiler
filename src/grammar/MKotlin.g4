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
// expression
expr : asn ;
asn : lor ASGN asn 
    | lor 
    ;
lor : lor OR land 
    | land 
    ;
land : land AND eq 
     | eq 
     ;
eq : eq EQ ord 
   | eq NEQ ord 
   | ord 
   ;
ord : ord LT range
    | ord LTE range 
    | ord GT range
    | ord GTE range
    | range
    ;
range : range RANGE addsub 
      | addsub 
      ;
addsub : addsub ADD muldivmod 
       | addsub SUB muldivmod 
       | muldivmod 
       ;
muldivmod : muldivmod MUL unary 
          | muldivmod DIV unary 
          | muldivmod MOD unary 
          | unary 
          ; 
unary : NOT unary 
      | SUB unary 
      | ADD unary 
      | prefix 
      ;
prefix : INCREMENT prefix 
       | DECREMENT prefix
       | postfix
       ;
postfix : postfix LP exprList RP
        | postfix MEMACC IDENT
        | postfix INCREMENT 
        | postfix DECREMENT
        | primary 
        ;
exprList : exprPrime | ;
exprPrime : expr COMMA exprPrime | expr ;
primary : INTLIT
        | FLOATLIT
        | TRUE
        | FALSE
        | STRINGLIT
        | ifexpr 
        | whenexpr
        | IDENT
        | LP expr RP
        ;
ifexpr : IF LP expr RP stmt ELSE stmt ;
whenexpr : WHEN LP expr RP LB newlineList whenBranchList newlineList RB 
         | WHEN LB newlineList whenBranchList newlineList RB
         ;
newlineList : NEWLINE newlineList 
            | 
            ;
declList : decl newlineList declList 
         | 
         ;
decl : dataClassDecl 
     | funcDecl
     ;

// Data Class Declare
dataClassDecl : DATA CLASS IDENT LP newlineList memList newlineList RP 
              | DATA CLASS IDENT LP newlineList RP
              ;
memList : mem COMMA newlineList memList 
        | mem 
        ;
mem : IDENT COLON typ ;
typ : INT 
    | FLOAT 
    | BOOLEAN 
    | STRING 
    | IDENT 
    ;

// Function Declare
funcDecl : FUN IDENT LP newlineList paramList newlineList RP rettype body ;    
paramList : paramPrime 
          | 
          ;
paramPrime : param COMMA newlineList paramPrime 
           | param 
           ;
param : IDENT COLON typ ;
body : LB newlineList stmtList newlineList RB ; 
rettype : COLON returnableTyp 
        |
        ;
returnableTyp : typ 
              | UNIT 
              ;
sep : newlineList | SEMI ;
stmtList : stmt sep stmtList | stmt sep | ;
stmt : valdecl 
     | blkstmt 
     | ifstmt 
     | whilestmt 
     | forstmt 
     | whenstmt 
     | brkstmt 
     | contstmt 
     | retstmt 
     | exprstmt 
     ;
valdecl : VAL IDENT ASGN expr 
        | VAL IDENT COLON typ ASGN expr 
        | VAR IDENT ASGN expr 
        | VAR IDENT COLON typ ASGN expr 
        | VAR IDENT COLON typ 
        | VAR IDENT
        ;
blkstmt : LB newlineList stmtList newlineList RB | LB RB;
ifstmt : IF LP expr RP stmt 
       | IF LP expr RP stmt ELSE stmt
       ;
whilestmt :  WHILE LP expr RP stmt ;
forstmt : FOR LP IDENT IN addsub RANGE addsub RP stmt ;
whenstmt : WHEN LP expr RP LB newlineList whenBranchList newlineList RB 
         | WHEN LB newlineList whenBranchList newlineList RB
         ;
whenBranchList : whenBranch sep whenBranchList 
               | 
               ;
whenBranch : whenBranchLabel ARROW stmt
           | ELSE ARROW stmt
           ;
whenBranchLabel : exprPrime ;
brkstmt : BREAK ;
contstmt : CONTINUE ; 
retstmt : RETURN expr 
        | RETURN 
        ;
exprstmt : expr ;

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
RANGE : '..' ;
MEMACC : '.' ;

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
FLOATLIT : [0-9]+ '.' {self._input.LA(1) != ord('.')}? [0-9]* EXP? [fF]?
         | '.' [0-9]+ EXP? [fF]?
         | [0-9]+ (EXP [fF]? | [fF])
         ;
fragment EXP : [eE] [+-]? [0-9]+ ;
INTLIT : [0-9]+ ('_' [0-9]+)* ;
ILLEGAL_ESCAPE : ["] (NORMAL_CHAR | ESCAPE_CHAR)* ('\\' ~[bfrnt"\\] | '$' [a-zA-Z{]) {
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

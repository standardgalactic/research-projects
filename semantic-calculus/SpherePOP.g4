
// SpherePOP.g4 - ANTLR4 grammar for SpherePOP (initial scaffold)

grammar SpherePOP;

program : statement+ EOF ;

statement
    : letBinding
    | sphereDecl
    | policyExec
    ;

letBinding : 'let' IDENT '=' expr ;

sphereDecl : 'sphere' IDENT '=' sphere ;

policyExec : 'apply' policy 'to' IDENT ;

expr
    : sphere
    | policy
    | expr 'merge' expr
    | policy '(' expr ')'
    ;

sphere : '{' 'field' ':' fieldMap ',' 'boundary' ':' boundary ',' 'entropy' ':' NUMBER '}' ;

fieldMap : '{' fieldPair (',' fieldPair)* '}' ;
fieldPair : IDENT ':' vector ;
vector : '[' (NUMBER (',' NUMBER)*)? ']' ;
boundary : '∂' IDENT ;

policy : 'pop' | 'collapse' | 'rewrite' IDENT | 'mask' IDENT | 'allocate' NUMBER ;

IDENT : [a-zA-Z_] [a-zA-Z_0-9]* ;
NUMBER : [0-9]+ ('.' [0-9]+)? ;
WS : [ \t\r\n]+ -> skip ;
LINE_COMMENT : '//' ~[\r\n]* -> skip ;

grammar Calculator;

// Reglas del parser (sintácticas)
expr: term ((PLUS | MINUS) term)*;
term: factor ((MUL | DIV) factor)*;
factor: NUMBER | '(' expr ')';

// Reglas del lexer (léxicas)
NUMBER: [0-9]+('.'[0-9]+)?;
PLUS: '+';
MINUS: '-';
MUL: '*';
DIV: '/';
WS: [ \t\r\n]+ -> skip;
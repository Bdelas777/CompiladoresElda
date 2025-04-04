/* Archivo: calc.l - Analizador léxico para calculadora simple */

%{
    #include <stdio.h>
    #include <stdlib.h>
    #include "calc.tab.h"  /* Incluir definiciones generadas por Bison */
    
    /* Esta sección incluye el código que se copiará al lexer generado */
    %}
    
    /* Opciones de Flex */
    %option noyywrap
    
    %%
    /* Reglas léxicas */
    
    [0-9]+          { 
                      /* Convertir string a entero */
                      yylval.ival = atoi(yytext); 
                      return NUMBER; 
                    }
    "+"             { return PLUS; }
    "-"             { return MINUS; }
    "*"             { return TIMES; }
    "/"             { return DIVIDE; }
    "("             { return LPAREN; }
    ")"             { return RPAREN; }
    [ \t\n]         { /* Ignorar espacios, tabulaciones y saltos de línea */ }
    .               { printf("Carácter no reconocido: %s\n", yytext); }
    
    %%
    
    /* Archivo: calc.y - Analizador sintáctico para calculadora simple */
    
    %{
    #include <stdio.h>
    #include <stdlib.h>
    
    /* Declaración de funciones */
    void yyerror(const char *s);
    int yylex(void);
    
    /* Esta sección incluye el código que se copiará al parser generado */
    %}
    
    /* Declaración de tipos para los tokens */
    %union {
        int ival;  /* Valor entero para NUMBER */
    }
    
    /* Declaración de tokens */
    %token <ival> NUMBER
    %token PLUS MINUS TIMES DIVIDE LPAREN RPAREN
    
    /* Declaración de tipos para no-terminales */
    %type <ival> expr term factor
    
    /* Declaración de precedencia y asociatividad */
    %left PLUS MINUS
    %left TIMES DIVIDE
    
    %%
    /* Reglas gramaticales */
    
    program:
        program expr '\n'    { printf("Resultado: %d\n", $2); }
        | /* vacío */
        ;
    
    expr:
        term                { $$ = $1; }
        | expr PLUS term    { $$ = $1 + $3; }
        | expr MINUS term   { $$ = $1 - $3; }
        ;
    
    term:
        factor              { $$ = $1; }
        | term TIMES factor { $$ = $1 * $3; }
        | term DIVIDE factor {
            if ($3 == 0) {
                yyerror("Error: División por cero");
                $$ = 0;
            } else {
                $$ = $1 / $3;
            }
        }
        ;
    
    factor:
        NUMBER              { $$ = $1; }
        | LPAREN expr RPAREN { $$ = $2; }
        ;
    
    %%
    
    /* Código adicional en C */
    
    void yyerror(const char *s) {
        fprintf(stderr, "%s\n", s);
    }
    
    int main() {
        printf("Calculadora simple (Ctrl+D para salir)\n");
        printf("> ");
        yyparse();
        return 0;
    }
    
    /* Archivo: Makefile - Para compilar el proyecto */
    
    # Makefile para calculadora con Flex y Bison
    
    CC = gcc
    CFLAGS = -Wall
    
    all: calc
    
    calc: calc.tab.c lex.yy.c
        $(CC) $(CFLAGS) -o calc calc.tab.c lex.yy.c -lfl
    
    calc.tab.c calc.tab.h: calc.y
        bison -d calc.y
    
    lex.yy.c: calc.l calc.tab.h
        flex calc.l
    
    clean:
        rm -f calc calc.tab.c calc.tab.h lex.yy.c
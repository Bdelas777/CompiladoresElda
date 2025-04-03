// Archivo: calc.y
// Ejemplo de una calculadora simple usando goyacc

%{
	package main
	
	import (
		"bufio"
		"fmt"
		"os"
		"strconv"
		"strings"
		"unicode"
	)
	
	// Tipo de valor utilizado por el analizador
	type CalcSymType struct {
		yys int
		val float64
	}
	
	// Lexer mantiene el estado del analizador léxico
	type Lexer struct {
		scanner *bufio.Scanner
		line    string
		pos     int
	}
	
	func NewLexer() *Lexer {
		return &Lexer{
			scanner: bufio.NewScanner(os.Stdin),
		}
	}
	
	// Error reporta un mensaje de error
	func (l *Lexer) Error(s string) {
		fmt.Printf("Error: %s\n", s)
	}
	
	// Lex es la función que goyacc llama para obtener tokens
	func (l *Lexer) Lex(lval *CalcSymType) int {
		for {
			if l.pos >= len(l.line) {
				if !l.scanner.Scan() {
					return 0 // EOF
				}
				l.line = l.scanner.Text()
				l.pos = 0
				
				// Salir si el usuario escribe "exit"
				if strings.TrimSpace(l.line) == "exit" {
					return 0
				}
			}
			
			// Omitir espacios en blanco
			for l.pos < len(l.line) && unicode.IsSpace(rune(l.line[l.pos])) {
				l.pos++
			}
			
			if l.pos >= len(l.line) {
				continue // Línea vacía
			}
			
			// Identificar tokens
			switch c := l.line[l.pos]; c {
			case '+':
				l.pos++
				return PLUS
			case '-':
				l.pos++
				return MINUS
			case '*':
				l.pos++
				return TIMES
			case '/':
				l.pos++
				return DIVIDE
			case '(':
				l.pos++
				return LPAREN
			case ')':
				l.pos++
				return RPAREN
			default:
				// Número
				if unicode.IsDigit(rune(c)) {
					start := l.pos
					for l.pos < len(l.line) && (unicode.IsDigit(rune(l.line[l.pos])) || l.line[l.pos] == '.') {
						l.pos++
					}
					numStr := l.line[start:l.pos]
					num, err := strconv.ParseFloat(numStr, 64)
					if err != nil {
						l.Error(fmt.Sprintf("Número inválido: %s", numStr))
						return 0
					}
					lval.val = num
					return NUMBER
				}
				
				// Carácter inválido
				l.Error(fmt.Sprintf("Carácter inesperado: %c", c))
				l.pos++
				return 0
			}
		}
	}
	
	%}
	
	// Definición de tokens
	%token <val> NUMBER
	%token PLUS MINUS TIMES DIVIDE LPAREN RPAREN
	
	// Tipo de valor asociado a las expresiones
	%type <val> expr term factor
	
	// Precedencia de operadores (de menor a mayor)
	%left PLUS MINUS
	%left TIMES DIVIDE
	
	%%
	
	top:
		expr    { fmt.Printf("Resultado: %.2f\n", $1) }
		;
	
	expr:
		term            { $$ = $1 }
		| expr PLUS term   { $$ = $1 + $3 }
		| expr MINUS term  { $$ = $1 - $3 }
		;
	
	term:
		factor          { $$ = $1 }
		| term TIMES factor { $$ = $1 * $3 }
		| term DIVIDE factor {
			if $3 == 0.0 {
				yylex.(*Lexer).Error("División por cero")
				$$ = 0.0
			} else {
				$$ = $1 / $3
			}
		}
		;
	
	factor:
		NUMBER          { $$ = $1 }
		| LPAREN expr RPAREN { $$ = $2 }
		;
	
	%%
	
	func main() {
		fmt.Println("Calculadora simple en Go (escribe 'exit' para salir)")
		fmt.Print("calc > ")
		
		lexer := NewLexer()
		yyParse(lexer)
	}
	
	// Para compilar este ejemplo:
	// 1. Guardar como calc.y
	// 2. Ejecutar: goyacc -o calc.go calc.y
	// 3. Modificar calc.go para importar los paquetes necesarios
	// 4. Compilar: go build calc.go
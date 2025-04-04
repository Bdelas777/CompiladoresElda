# Generación de Analizadores Léxicos y Sintácticos

Este repositorio contiene ejemplos de implementación de calculadoras simples utilizando tres herramientas para la generación automática de analizadores léxicos y sintácticos.

## 📌 Herramientas Implementadas

### 1️⃣ PLY (Python Lex-Yacc)
- 🚀 Implementación de Lex & Yacc en Python puro.
- ✅ No requiere etapas de compilación adicionales.
- 📂 Archivo principal: `PlyExample.py`.

### 2️⃣ Goyacc (Go)
- 🛠️ Implementación de Yacc para Go.
- 🔄 Sintaxis similar a Yacc tradicional pero con integración con Go.
- 📂 Archivo principal: `calc.y`.

### 3️⃣ ANTLR (con Python)
- 🌐 Herramienta moderna para análisis de lenguajes.
- 🔍 Separación entre gramática y lógica de ejecución.
- 📂 Archivos: `calculator.g4`, `calculator_visitor.py`, `main.py`.

## 🚀 Instalación y Ejecución

### 🐍 PLY
```bash

pip install ply
python PlyExample.py
🦫 Goyacc
bash
goyacc -o calc.go calc.y
go build calc.go
./calc
🏗️ ANTLR
bash
pip install antlr4-python3-runtime
java -jar antlr-4.13.1-complete.jar -Dlanguage=Python3 -visitor calculator.g4
python main.py
🎯 Funcionalidad
Todos los ejemplos implementan una calculadora que:

➕➖✖️➗ Evalúa expresiones aritméticas (suma, resta, multiplicación, división).

🏗️ Maneja paréntesis para control de precedencia.

⚠️ Proporciona manejo básico de errores.

🛠️ Estructura del Código
Cada implementación sigue un patrón similar:

📌 Definición de tokens (análisis léxico).

📖 Especificación de la gramática (análisis sintáctico).

⚙️ Acciones semánticas para evaluar expresiones.

🤝 Contribuciones
Si deseas contribuir, por favor abre un issue o un pull request. Toda ayuda es bienvenida. 🚀

📜 Licencia
Este proyecto está disponible bajo la licencia MIT.




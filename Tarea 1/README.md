# Estructuras de Datos en Python

Este proyecto implementa tres estructuras de datos fundamentales para el curso del Tecnológico de Monterrey: "Desarrollo de Aplicaciones Avanzadas de Ciencias Computacionales", Módulo 3: Compiladores.

## 📌 Estructuras Implementadas

- **Pila (Stack - LIFO):** Estructura de datos "Último en entrar, primero en salir".
- **Cola (Queue - FIFO):** Estructura de datos "Primero en entrar, primero en salir".
- **Tabla Hash (Diccionario):** Almacén de clave-valor con complejidad O(1) en promedio para las operaciones.

## 📂 Archivos

- `stack.py`: Implementación de la estructura de datos Pila.
- `queue.py`: Implementación de la estructura de datos Cola.
- `dictionary.py`: Implementación de la estructura de datos Tabla Hash.
- `test_data_structures.py`: Programa para probar y demostrar la funcionalidad.

## 🛠️ Implementación

### Pila (Stack)

La clase `Stack` proporciona las siguientes operaciones:

- `push(item)`: Agrega un elemento a la parte superior de la pila.
- `pop()`: Elimina y devuelve el elemento superior.
- `peek()`: Devuelve el elemento superior sin eliminarlo.
- `is_empty()`: Verifica si la pila está vacía.
- `size()`: Retorna el número de elementos en la pila.
- `clear()`: Elimina todos los elementos de la pila.

### Cola (Queue)

La clase `Queue` proporciona las siguientes operaciones:

- `enqueue(item)`: Agrega un elemento al final de la cola.
- `dequeue()`: Elimina y devuelve el primer elemento.
- `peek()`: Devuelve el primer elemento sin eliminarlo.
- `is_empty()`: Verifica si la cola está vacía.
- `size()`: Retorna el número de elementos en la cola.
- `clear()`: Elimina todos los elementos de la cola.

### Tabla Hash (Hash Table)

La clase `HashTable` proporciona las siguientes operaciones:

- `insert(key, value)`: Inserta o actualiza un par clave-valor.
- `get(key)`: Obtiene el valor asociado a una clave.
- `delete(key)`: Elimina un par clave-valor.
- `contains(key)`: Verifica si una clave existe.
- `keys()`: Retorna una lista de todas las claves.
- `values()`: Retorna una lista de todos los valores.
- `items()`: Retorna una lista de todos los pares clave-valor.
- `clear()`: Elimina todos los elementos.
- `size_used()`: Retorna el número de pares clave-valor almacenados.

## ✅ Pruebas

El programa de pruebas valida los siguientes aspectos de cada estructura de datos:

### Pruebas de Pila

- Operaciones de `push` y `pop`
- Operación `peek`
- Operaciones `size` y `is_empty`
- Operación `clear`
- Chequeo de excepciones

### Pruebas de Cola

- Operaciones de `enqueue` y `dequeue`
- Operación `peek`
- Operaciones `size` y `is_empty`
- Operación `clear`
- Chequeo de excepciones

### Pruebas de Tabla Hash

- Operaciones `insert` y `get`
-  Actualizción de  una clave existente
- Operación `delete`
- Operación `contains`
- Operaciones `keys`, `values` y `items`
- Operaciones `size` y `clear`
- Chequeo de excepciones
- Manejo de colisiones

## 🚀 Cómo Ejecutar

Ejecuta el programa de pruebas con el siguiente comando:

```sh
python test_data_structures.py
```

## 📌 Notas de Implementación

- La **Pila** y la **Cola** están implementadas usando listas de Python.
- La **Tabla Hash** maneja colisiones mediante encadenamiento separado.
- Todas las implementaciones incluyen manejo de errores adecuado.

## ⏳ Complejidad Temporal

| **Estructura** | **Operación** | **Complejidad** |
|--------------|--------------|--------------|
| **Pila** | `push`, `pop`, `peek` | O(1) |
| **Cola** | `enqueue` | O(1) |
| **Cola** | `dequeue` | O(n) (Limitación de listas en Python) |
| **Tabla Hash** | `insert`, `get`, `delete` | O(1) en promedio |


## Liga Github 

https://github.com/Bdelas777/CompiladoresElda/tree/main/Tarea%201
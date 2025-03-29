# test_data_structures.py
from stack import Stack
from queue import Queue
from  hashtable import HashTable

def test_stack():
    print("\n===== Prueba de Stacks =====")
    s = Stack()
    
    # Test 1: Operaciones de push y pop
    print("Test 1:  Operaciones de push y pop")
    s.push(1)
    s.push(2)
    s.push(3)
    print(f"El stack despues de  hacer la operacion push de  1, 2, 3: {s}")
    
    print(f"Hacemos la operacion pop de un elemento: {s.pop()}")
    print(f"El stack despues de hacer la operacion pop: {s}")
    
    # Test 2: Operacion peek
    print("\nTest 2: operacion peek")
    print(f"Elemento mas arriba (peek): {s.peek()}")
    print(f"El stack despues de hacer la operacion peek: {s}")
    
    # Test 3: Operaciones de size y is_empty
    print("\nTest 3: Operaciones de size and is_empty ")
    print(f"Tamano del stack: {s.size()}")
    print(f"Verificamos si esta vacio? {s.is_empty()}")
    
    # Test 4: Operacion clear
    print("\nTest 4: Operacion clear")
    s.clear()
    print(f"El stack despues de la operacion clear: {s}")
    print(f"Verificamos si esta vacio? {s.is_empty()}")
    
    # Test 5: Chequeo de excepciones
    print("\nTest 5: Chequeo de excepciones")
    try:
        s.pop()
    except IndexError as e:
        print(f"Ocurrio un error: {e}")
    
    try:
        s.peek()
    except IndexError as e:
        print(f"Ocurrio un error: {e}")


def test_queue():
    print("\n===== QUEUE TESTS =====")
    q = Queue()
    
    # Test 1: Operaciones enqueue and dequeue 
    print("Test 1: Operaciones enqueue and dequeue ")
    q.enqueue("A")
    q.enqueue("B")
    q.enqueue("C")
    print(f"La queue despues de hacer la operacion enqueue A, B, C: {q}")
    
    print(f"Hacemos la operacion dequeue: {q.dequeue()}")
    print(f"EL queue despues de hacer la operacion dequeue: {q}")
    
    # Test 2: Operacion peek 
    print("\nTest 2: Operacion peell")
    print(f"Elemento despues de la operacion peek: {q.peek()}")
    print(f"EL queue despues de hacer la operacion queue: {q}")
    
    # Test 3: Operaciones de size y is_empty
    print("\nTest 3: Operaciones de size and is_empty ")
    print(f"Tamano del stack: {q.size()}")
    print(f"Verificamos si esta vacio? {q.is_empty()}")
    
    # Test 4: Operacion clear
    print("\nTest 4: Operacion clear")
    q.clear()
    print(f"El stack despues de la operacion clear: {q}")
    print(f"Verificamos si esta vacio? {q.is_empty()}")
    
    # Test 5: Chequeo de excepciones
    print("\nTest 5: Chequeo de excepciones")
    try:
        q.dequeue()
    except IndexError as e:
        print(f"Ocurrio un error: {e}")
    
    try:
        q.peek()
    except IndexError as e:
        print(f"Ocurrio un error: {e}")

def test_hash_table():
    print("\n===== HASH TABLE TESTS =====")
    ht = HashTable(size=10)  # Definimos una tamaños pequeño para la prueba
    
    # Test 1: Operaciones de insert y get 
    print("Test 1:  Operaciones de insert y get ")
    ht.insert("nombre", "Bernardo de la S")
    ht.insert("edad", 22)
    ht.insert("ciudad", "Teziutlan")
    print(f"El hash table despues de la operaciones de insert: {ht}")
    
    print(f"Valor de la clave nombre: {ht.get('nombre')}")
    print(f"Valor de la clave edad: {ht.get('edad')}")
    
    # Test 2: Actualizcion de  una clave existente
    print("\nTest 2:  Actualizcion de  una clave existente")
    ht.insert("edad", 23)
    print(f"Valor despues de actualizar la clave edad: {ht.get('edad')}")
    
    # Test 3: Operacion delete
    print("\nTest 3: Operacion delete")
    ht.delete("edad")
    print(f"Hash table depues de hacer la operacion delete con edad: {ht}")
    
    # Test 4: Operacion contains
    print("\nTest 4: Operacion contains")
    print(f"Contiene nombre? {ht.contains('nombre')}")
    print(f"Contiene edad? {ht.contains('edad')}")
    
    # Test 5: Claves valores y items
    print("\nTest 5: Claves valores y items")
    print(f"Claves: {ht.keys()}")
    print(f"Valores: {ht.values()}")
    print(f"Items: {ht.items()}")
    
    # Test 6: Operaciones size and clear
    print("\nTest 6: Operaciones size and clear ")
    print(f"Numero de items: {ht.size_used()}")
    ht.clear()
    print(f"Hash table despues de la operacion clear: {ht}")
    print(f"Number de items depues de la operacion clear: {ht.size_used()}")
    
    # Test 7: Chequeo de excepciones
    print("\nTest 7: Chequeo de excepciones")
    try:
        ht.get("No existe")
    except KeyError as e:
        print(f"Ocurrio un error: {e}")
    
    try:
        ht.get("No existe")
    except KeyError as e:
        print(f"Ocurrio un error: {e}")
    
    # Prueba 8: Manejo de colisiones
    print("\nPrueba 8: Manejo de colisiones")
    # Es probable que estos valores se asignen al mismo bucket en nuestra función hash simple
    ht.insert("abc", 1)
    ht.insert("cba", 2)
    print(f"Tabla hash con posibles colisiones: {ht}")
    print(f"Valor para la clave 'abc': {ht.get('abc')}")
    print(f"Valor para la clave 'cba': {ht.get('cba')}")

if __name__ == "__main__":
    test_stack()
    test_queue()
    test_hash_table()
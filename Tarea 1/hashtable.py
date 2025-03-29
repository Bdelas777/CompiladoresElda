class HashTable:
    """
    Implementamos una Hash Table (diccionario) como estrutura de datos
    """
    # Iniciamos un hash table vacio con un tamaño de 100 
    def __init__(self, size=100):
        self.size = size
        self.table = [[] for _ in range(size)]  

    # Generamos un hash con un valor para cierta clave
    def _hash(self, key):
        if isinstance(key, str):
            return sum(ord(c) for c in key) % self.size
        return hash(key) % self.size

    # Insertamos el valor de forma clave valor en el hash table
    def insert(self, key, value):
        index = self._hash(key)
        
        for i, (k, v) in enumerate(self.table[index]):
            if k == key:
                self.table[index][i] = (key, value)
                return
        
        self.table[index].append((key, value))

    #Obtenemos un valor associado con la clave pero si no se encuentra lanzamos un error
    def get(self, key):
        index = self._hash(key)
        
        for k, v in self.table[index]:
            if k == key:
                return v
        
        raise KeyError(f"Key '{key}' not found")

    #Eliminos el par dado una clave si no se encuentra lanzamos un error
    def delete(self, key):
        index = self._hash(key)
        
        for i, (k, v) in enumerate(self.table[index]):
            if k == key:
                del self.table[index][i]
                return
        
        raise KeyError(f"Key '{key}' not found")

    # Checamos si el elementos esta en el hashtable
    def contains(self, key):
        index = self._hash(key)
        
        for k, v in self.table[index]:
            if k == key:
                return True
        
        return False

    # regresamos todas las claves en el hash table
    def keys(self):
        all_keys = []
        for bucket in self.table:
            for k, v in bucket:
                all_keys.append(k)
        return all_keys

    # regresamos todas los valores en el hash table
    def values(self):
        all_values = []
        for bucket in self.table:
            for k, v in bucket:
                all_values.append(v)
        return all_values

    # Retornamos todos los elementos en formato clave valor de hash table
    def items(self):
        all_items = []
        for bucket in self.table:
            for item in bucket:
                all_items.append(item)
        return all_items

    # Remocemos todos los elementos del hash table
    def clear(self):
        self.table = [[] for _ in range(self.size)]

    # Aqui checamos el numero de elementos que estan guardados en el hash table
    def size_used(self):
        count = 0
        for bucket in self.table:
            count += len(bucket)
        return count

    # Regresamos el hash table en formato de texto
    def __str__(self):
        items = self.items()
        return "{" + ", ".join(f"{k}: {v}" for k, v in items) + "}"
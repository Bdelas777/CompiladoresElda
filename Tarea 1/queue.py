class Queue:
    """
    Esta clase busca implementar la estructura First In First Out que es una pila o stack
    """
    
    # Iniciamos la cola vacia
    def __init__(self):
        self.items = []
        
    #Añadimos un elemento al final de la cola
    def enqueue(self, item):
        self.items.append(item)    
    
    # Removemos el primer elemento de la cola y lanzamos un error si la cola esta vacia
    def dequeue(self):
        if self.is_empty():
            raise IndexError("La cola esta vacia")
        return self.items.pop(0)
    
    # Retornamos el primer elemento de la cola y lanzamos un error si esta vacia
    def peek(self):
        if self.is_empty():
            raise IndexError("La cola esta vacia")
        return self.items[0]
    
    # Checamos si la cola esta vacia
    def is_empty(self):
        return len(self.items) == 0

    # Retornamos el numero de elementos en la cola
    def size(self):
        return len(self.items)

    #Limpuamos todos los elementos de la cola
    def clear(self):
        self.items = []

    # Retornamos la cola en formato texto
    def __str__(self):
        return str(self.items)
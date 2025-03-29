class Stack:
    """
    Esta clase busca implementar la estructura Last In First Out que es una pila o stack
    """
    # Inilizamos la pila vacia, ya que no hay nada.
    def __init__(self):
        self.items = []

    #Añadimos un elemento de  arriba de la pila
    def push(self,item):
        self.items.append(item)
    
    # Aqui eliminamos un elemento de arriba y lanzamos un error si la pila ya esta vacia
    def pop(self):
        if self.is_empty():
            raise IndexError("La pila esta vacia")
        return self.items.pop()
    
    #Regresa el elemento de hasta arriba y da un error si esta vacio
    def peek(self):
        if self.is_empty():
            raise IndexError("La pila esta vacia")
        return self.items[-1]
    
    # Checa si la pila esta vacia
    def is_empty(self):
        return len(self.items) == 0

    # Regresa el numero de elementos en la pila
    def size(self):
        return len(self.items)

    # Limpiamos todos los elementos en la pila
    def clear(self):
        self.items = []

    # Refresa la pila en formato de texto
    def __str__(self):
        return str(self.items)
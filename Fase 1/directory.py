# directory.py - Implementación del Directorio de Funciones y Tablas de Variables para BabyDuck

class VariableTable:
    """
    Tabla de variables para BabyDuck.
    Almacena las variables y sus tipos para un scope determinado.
    """
    
    def __init__(self):
        # Diccionario que mapea nombre de variable -> {'type': tipo}
        self.variables = {}
    
    def add_variable(self, name, var_type):
        """
        Añade una variable a la tabla
        
        Args:
            name: Nombre de la variable
            var_type: Tipo de la variable (int, float)
            
        Returns:
            True si se añadió correctamente, False si ya existía (duplicada)
        """
        if name in self.variables:
            return False  # Variable ya declarada
        
        self.variables[name] = {'type': var_type}
        return True
        
    def get_variable(self, name):
        """
        Obtiene la información de una variable
        
        Args:
            name: Nombre de la variable
            
        Returns:
            Diccionario con la información de la variable o None si no existe
        """
        return self.variables.get(name)
    
    def get_variable_type(self, name):
        """
        Obtiene el tipo de una variable
        
        Args:
            name: Nombre de la variable
            
        Returns:
            Tipo de la variable o None si no existe
        """
        var_info = self.get_variable(name)
        if var_info:
            return var_info['type']
        return None
    
    def __str__(self):
        """Representación en string de la tabla de variables"""
        result = "Variables:\n"
        for name, info in self.variables.items():
            result += f"  {name}: {info['type']}\n"
        return result


class FunctionDirectory:
    """
    Directorio de funciones para BabyDuck.
    Almacena información sobre las funciones y sus variables locales.
    """
    
    def __init__(self):
        # Diccionario que mapea nombre de función -> 
        # {'type': tipo_retorno, 'params': lista_parametros, 'vars': tabla_variables}
        self.functions = {}
        
        # Variables globales (programa principal)
        self.global_vars = VariableTable()
        
        # Función actual que se está procesando
        self.current_function = None
    
    def add_function(self, name, return_type='void'):
        """
        Añade una función al directorio
        
        Args:
            name: Nombre de la función
            return_type: Tipo de retorno de la función
            
        Returns:
            True si se añadió correctamente, False si ya existía (duplicada)
        """
        if name in self.functions:
            return False  # Función ya declarada
        
        self.functions[name] = {
            'type': return_type,
            'params': [],
            'vars': VariableTable()
        }
        
        self.current_function = name
        return True
    
    def add_param(self, name, param_type):
        """
        Añade un parámetro a la función actual
        
        Args:
            name: Nombre del parámetro
            param_type: Tipo del parámetro
            
        Returns:
            True si se añadió correctamente, False si hubo un error
        """
        if not self.current_function:
            return False
        
        # Añadir a la lista de parámetros
        self.functions[self.current_function]['params'].append({
            'name': name,
            'type': param_type
        })
        
        # También añadir como variable local
        return self.add_variable(name, param_type)
    
    def add_variable(self, name, var_type):
        """
        Añade una variable a la función actual o al scope global
        
        Args:
            name: Nombre de la variable
            var_type: Tipo de la variable
            
        Returns:
            True si se añadió correctamente, False si ya existía (duplicada)
        """
        if self.current_function:
            # Añadir a las variables de la función actual
            return self.functions[self.current_function]['vars'].add_variable(name, var_type)
        else:
            # Añadir a las variables globales
            return self.global_vars.add_variable(name, var_type)
    
    def get_function(self, name):
        """
        Obtiene la información de una función
        
        Args:
            name: Nombre de la función
            
        Returns:
            Diccionario con la información de la función o None si no existe
        """
        return self.functions.get(name)
    
    def get_variable(self, name):
        """
        Busca una variable primero en el scope actual y luego en el global
        
        Args:
            name: Nombre de la variable
            
        Returns:
            Información de la variable o None si no existe
        """
        if self.current_function:
            # Buscar en las variables de la función actual
            var_info = self.functions[self.current_function]['vars'].get_variable(name)
            if var_info:
                return var_info
        
        # Si no se encontró o no hay función actual, buscar en las variables globales
        return self.global_vars.get_variable(name)
    
    def get_variable_type(self, name):
        """
        Obtiene el tipo de una variable
        
        Args:
            name: Nombre de la variable
            
        Returns:
            Tipo de la variable o None si no existe
        """
        var_info = self.get_variable(name)
        if var_info:
            return var_info['type']
        return None
    
    def end_function(self):
        """Finaliza la definición de la función actual"""
        self.current_function = None
    
    def __str__(self):
        """Representación en string del directorio de funciones"""
        result = "FUNCTION DIRECTORY\n"
        result += "=================\n\n"
        
        result += "Global Scope:\n"
        result += str(self.global_vars)
        result += "\n"
        
        for name, info in self.functions.items():
            result += f"Function: {name} -> {info['type']}\n"
            
            result += "Parameters:\n"
            for param in info['params']:
                result += f"  {param['name']}: {param['type']}\n"
            
            result += "Local Variables:\n"
            result += str(info['vars'])
            result += "\n"
        
        return result
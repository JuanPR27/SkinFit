# models.py
# Define la estructura de datos para el perfil del usuario (Clase PerfilUsuario).

class PerfilUsuario:
    """
    Representa el perfil de un usuario con sus características de piel.
    Utiliza type hints para mayor claridad en el desarrollo.
    """
    
    def __init__(self, nombre: str, edad: int, tipo_piel: str, condiciones: str, frecuencia_rutina: str):
        """Inicializa un nuevo perfil con los datos obtenidos del formulario."""
        
        # Atributos principales
        self.nombre: str = nombre
        self.edad: int = edad
        self.tipo_piel: str = tipo_piel
        
        # Condiciones se guardan como un string separado por comas para SQLite
        self.condiciones: str = condiciones 
        self.frecuencia_rutina: str = frecuencia_rutina

    def get_condiciones_list(self) -> list:
        """
        Divide la cadena de condiciones (ej: "acne, manchas") en una lista de strings.
        Útil para que la IA o la lógica de generación de rutina las procesen.
        """
        if self.condiciones and self.condiciones.lower() != 'ninguna':
            # Limpia y divide la cadena, filtrando entradas vacías
            return [cond.strip() for cond in self.condiciones.split(',') if cond.strip()]
        return []

    def to_dict(self) -> dict:
        """
        Convierte el objeto a un diccionario.
        Aunque no es estrictamente necesario para la función de guardar en BD actual 
        (que usa una tupla), es una buena práctica de POO para serialización.
        """
        return {
            'nombre': self.nombre,
            'edad': self.edad,
            'tipo_piel': self.tipo_piel,
            'condiciones': self.condiciones,
            'frecuencia_rutina': self.frecuencia_rutina
        }

    def __repr__(self) -> str:
        """
        Representación legible del objeto. Útil para la función 'print()'
        y la depuración en la terminal.
        """
        return f"<PerfilUsuario nombre='{self.nombre}', tipo_piel='{self.tipo_piel}', condiciones='{self.condiciones}'>"


class RutinaPersonalizada:
    """
    Nueva clase para representar una rutina general unificada
    """
    def __init__(self, perfil: PerfilUsuario):
        self.perfil = perfil
        self.pasos = []  # Lista de pasos ordenados
        self.productos_recomendados = []  # Productos específicos del CSV
    
    def agregar_paso(self, nombre_paso: str, descripcion: str, tipo_producto: str = None):
        """Agrega un paso a la rutina con información del tipo de producto necesario"""
        self.pasos.append({
            "orden": len(self.pasos) + 1,
            "nombre": nombre_paso,
            "descripcion": descripcion,
            "tipo_producto": tipo_producto  # Ej: "limpiador", "serum", "protector_solar"
        })
    
    def to_dict(self):
        return {
            "perfil": self.perfil.to_dict(),
            "pasos": self.pasos,
            "productos_recomendados": self.productos_recomendados
        }
# models.py
# Define la estructura de datos para el perfil del usuario.

class PerfilUsuario:
    """
    Representa el perfil de un usuario con sus características de piel.
    Utiliza type hints para mayor claridad.
    """
    def __init__(self, nombre: str, edad: int, tipo_piel: str, condiciones: str, frecuencia_rutina: str):
        self.nombre: str = nombre
        self.edad: int = edad
        self.tipo_piel: str = tipo_piel
        # Condiciones se guardan como un string separado por comas
        self.condiciones: str = condiciones 
        self.frecuencia_rutina: str = frecuencia_rutina

    def get_condiciones_list(self) -> list:
        """Retorna las condiciones como una lista de strings."""
        if self.condiciones:
            # Filtra elementos vacíos si hay comas extra
            return [cond.strip() for cond in self.condiciones.split(',') if cond.strip()]
        return []

    def to_dict(self) -> dict:
        """Convierte el objeto a un diccionario para guardar en la BD."""
        return {
            'nombre': self.nombre,
            'edad': self.edad,
            'tipo_piel': self.tipo_piel,
            'condiciones': self.condiciones,
            'frecuencia_rutina': self.frecuencia_rutina
        }

    def __repr__(self) -> str:
        """Representación del objeto para debugging."""
        return f"<PerfilUsuario {self.nombre} ({self.tipo_piel})>"
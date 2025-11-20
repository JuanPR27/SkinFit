# database.py
# Gestiona la conexión y la creación/actualización de la tabla 'perfiles'.
import sqlite3

# Nombre del archivo de la base de datos
DATABASE_NAME = 'skinfit.db'


def get_db_connection():
    """
    Establece y retorna una conexión a la base de datos SQLite.
    Retorna None en caso de error de conexión.
    """
    try:
        conn = sqlite3.connect(DATABASE_NAME)
        # Configuración clave: permite acceder a las filas como diccionarios (por nombre de columna)
        conn.row_factory = sqlite3.Row 
        # print("Conexión a la base de datos establecida.") # Desactivado para no saturar la terminal
        return conn
    except sqlite3.Error as e:
        print(f"Error al conectar con la base de datos: {e}")
        return None

def crear_o_actualizar_tabla_perfiles():
    """
    Crea la tabla 'perfiles' si no existe.
    Define todos los campos necesarios para almacenar la información del formulario.
    """
    conn = get_db_connection()
    if conn:
        try:
            cursor = conn.cursor()
            
            # Sentencia SQL para crear la tabla
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS perfiles (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    nombre TEXT NOT NULL,
                    edad INTEGER NOT NULL,
                    tipo_piel TEXT NOT NULL,
                    condiciones TEXT, -- Almacenado como una cadena de texto (ej: "acne, manchas")
                    frecuencia_rutina TEXT NOT NULL,
                    fecha_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            conn.commit()
            print(" Tabla 'perfiles' verificada/creada exitosamente en skinfit.db.")

        except sqlite3.Error as e:
            print(f" Error al verificar/crear la tabla 'perfiles': {e}")
        finally:
            conn.close()
            # print("Conexión a la base de datos cerrada.")

# ----------------------------------------------------------------------
#  EJECUCIÓN DEL MÓDULO (Para pruebas/setup manual)
# ----------------------------------------------------------------------

if __name__ == '__main__':
    print("Iniciando la configuración de la base de datos SkinFit...")
    crear_o_actualizar_tabla_perfiles()
    print("Proceso de inicialización de base de datos completado.")
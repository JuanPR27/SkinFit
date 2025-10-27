# database.py
# Gestiona la conexión y la creación/actualización de la tabla 'perfiles'.
import sqlite3

DATABASE_NAME = 'skinfit.db'

def get_db_connection():
    """Establece y retorna una conexión a la base de datos SQLite."""
    try:
        conn = sqlite3.connect(DATABASE_NAME)
        # Permite acceder a las filas como diccionarios (por nombre de columna)
        conn.row_factory = sqlite3.Row
        print("Conexión a la base de datos establecida.")
        return conn
    except sqlite3.Error as e:
        print(f"Error al conectar con la base de datos: {e}")
        return None

def crear_o_actualizar_tabla_perfiles():
    """
    Crea la tabla 'perfiles' si no existe o la actualiza si es necesario.
    ¡Importante! En desarrollo, a veces es más fácil borrar y recrear.
    Aquí optamos por crearla si no existe. Asegúrate de borrar skinfit.db si cambias la estructura.
    """
    conn = get_db_connection()
    if conn:
        try:
            cursor = conn.cursor()
            # Crear tabla si no existe (con todos los campos)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS perfiles (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    nombre TEXT NOT NULL,
                    edad INTEGER NOT NULL,
                    tipo_piel TEXT NOT NULL,
                    condiciones TEXT,
                    frecuencia_rutina TEXT NOT NULL,
                    fecha_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            conn.commit()
            print("Tabla 'perfiles' verificada/creada exitosamente.")

            # (Opcional) Aquí podrías añadir lógica para ALTER TABLE si la tabla ya existe
            # pero por simplicidad, asumimos que se borra .db si hay cambios estructurales.

        except sqlite3.Error as e:
            print(f"Error al verificar/crear la tabla 'perfiles': {e}")
        finally:
            conn.close()
            print("Conexión a la base de datos cerrada.")

# Código que se ejecuta cuando corres `python database.py` directamente
if __name__ == '__main__':
    print("Inicializando la base de datos...")
    crear_o_actualizar_tabla_perfiles()
    print("Proceso de inicialización de base de datos completado.")
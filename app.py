# app.py (VERSIÓN CORREGIDA Y MEJORADA)

from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
import sqlite3
import json 

# Importaciones de módulos locales (asumiendo que database.py y models.py están bien)
from database import get_db_connection, crear_o_actualizar_tabla_perfiles 
from models import PerfilUsuario 
# <<< IMPORTANTE >>> Importamos el recomendador
from ai_service.recommender import recommend_products 

app = Flask(__name__)
app.config['SECRET_KEY'] = 'dev_secret_key_skinfit_12345'

# --- 💡 Lógica de Generación de Rutina de Texto ---

def generar_rutina_texto(perfil: PerfilUsuario) -> dict:
    """
    Genera una rutina estándar basada en el tipo de piel (Lógica SIMPLE para texto).
    """
    tipo = perfil.tipo_piel.lower()
    
    # Lógica simplificada basada en Tipo de Piel y Condición principal
    rutina = {
        "mañana": [
            f"Limpiador: Usa un limpiador en { 'gel o espuma' if 'grasa' in tipo or 'mixta' in tipo else 'crema o leche' }.",
            "Antioxidante: Sérum de Vitamina C. Clave para proteger la piel.",
            "Protector Solar: FPS 50+ de amplio espectro (¡El paso más importante!)."
        ],
        "noche": [
            "Doble Limpieza: Si usaste protector solar o maquillaje, comienza con un aceite o bálsamo.",
            f"Tratamiento: Aplica un activo como {'Ácido Salicílico (BHA)' if 'acne' in perfil.condiciones.lower() else 'Retinol o Peptidos'}.",
            "Hidratación: Crema de noche para sellar los tratamientos y restaurar la barrera."
        ]
    }
    return rutina

# --- Funciones de Base de Datos (Se mantienen sin cambios) ---

def guardar_perfil_db(perfil: PerfilUsuario) -> bool:
    """Guarda el objeto PerfilUsuario en la base de datos."""
    # ... (código SQL de guardar_perfil_db se mantiene igual) ...
    conn = get_db_connection()
    if not conn:
        flash("Error crítico: No se pudo conectar a la base de datos.", "error")
        return False

    cursor = conn.cursor()
    sql = """INSERT INTO perfiles (nombre, edad, tipo_piel, condiciones, frecuencia_rutina)
             VALUES (?, ?, ?, ?, ?)"""
    valores = (perfil.nombre, perfil.edad, perfil.tipo_piel, perfil.condiciones, perfil.frecuencia_rutina)

    try:
        cursor.execute(sql, valores)
        conn.commit()
        return True
    except sqlite3.Error as e:
        print(f"Error al guardar en BD: {e}")
        flash(f"Error al guardar en la base de datos: {e}", "error")
        return False
    finally:
        if conn:
            conn.close()

# --- Rutas de la Aplicación Web ---

@app.route('/')
def index():
    """Muestra el formulario principal."""
    return render_template('index.html')

@app.route('/procesar', methods=['POST'])
def procesar_formulario():
    """
    Recibe datos, guarda perfil, genera rutina de texto y LLAMA AL RECOMENDADOR
    para obtener los productos reales.
    """
    productos_recomendados = [] # Inicializamos la lista de productos vacía
    
    try:
        # 1. Extracción y validación básica de datos
        nombre = request.form['nombre']
        edad = int(request.form['edad'])
        tipo_piel = request.form['tipo_piel']
        condiciones_list = request.form.getlist('condiciones')
        condiciones_str = ", ".join(condiciones_list) if condiciones_list else "Ninguna"
        frecuencia = request.form['frecuencia_rutina']

        # 2. Creación del objeto PerfilUsuario
        perfil_usuario = PerfilUsuario(nombre, edad, tipo_piel, condiciones_str, frecuencia)

        # 3. Guardar perfil en la Base de Datos
        if not guardar_perfil_db(perfil_usuario):
            return redirect(url_for('index'))

        # 4. Generar la rutina de TEXTO
        rutina_generada = generar_rutina_texto(perfil_usuario)
        
        # 5. Generar los Productos (Llamada a la Ciencia de Datos/Pandas)
        # ESTE BLOQUE AHORA USA UN TRY/EXCEPT PARA NO DETENER LA APP SI EL CSV FALLA
        try:
            productos_recomendados = recommend_products(perfil_usuario.tipo_piel, perfil_usuario.condiciones, limit=6)
            if not productos_recomendados:
                 # Mensaje amigable si el algoritmo no encontró nada
                 flash("Advertencia: El algoritmo de recomendación no encontró productos específicos para su perfil.", "warning")
        except Exception as e:
            # Si hay un error con el CSV o Pandas, se registra, pero la APP SIGUE
            print(f"ERROR CRÍTICO EN PANDAS/CSV: {e}")
            flash("Advertencia: No se pudieron cargar los productos recomendados. Revisar el archivo de datos (CSV).", "warning")


        # 6. Mostrar la página de resultados
        return render_template('resultados.html', 
                               perfil=perfil_usuario, 
                               rutina=rutina_generada,
                               productos=productos_recomendados) # Enviamos la lista (vacía o llena)
                               
    except ValueError:
        flash("Error de datos: Asegúrate de que la edad sea un número válido.", "error")
        return redirect(url_for('index'))
    except KeyError as e:
        flash(f"Error de formulario: Falta el campo '{e}'. Por favor, completa todos los pasos.", "error")
        return redirect(url_for('index'))
    except Exception as e:
        # Manejo de cualquier otro error inesperado
        import traceback
        traceback.print_exc()
        flash(f"Ocurrió un error inesperado al procesar tu perfil: {e}", "error")
        return redirect(url_for('index'))

# --- Ejecución de la Aplicación ---

if __name__ == '__main__':
    crear_o_actualizar_tabla_perfiles()
    app.run(debug=True, host='0.0.0.0', port=5000)
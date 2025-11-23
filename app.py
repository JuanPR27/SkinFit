# app.py (VERSIÓN FINAL CON RUTINA UNIFICADA)

from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
import sqlite3
import json 

# Importaciones de módulos locales
from database import get_db_connection, crear_o_actualizar_tabla_perfiles 
from models import PerfilUsuario, RutinaPersonalizada
from ai_service.recommender import recommend_products_for_routine, recommend_products

app = Flask(__name__)
app.config['SECRET_KEY'] = 'dev_secret_key_skinfit_12345'

# --- 💡 Lógica de Generación de Rutina General Unificada ---

def generar_rutina_unificada(perfil: PerfilUsuario) -> RutinaPersonalizada:
    """
    Genera una rutina general personalizada basada en el perfil.
    Ahora devuelve un objeto RutinaPersonalizada en lugar de un dict separado.
    """
    rutina = RutinaPersonalizada(perfil)
    tipo = perfil.tipo_piel.lower()
    condiciones_list = perfil.get_condiciones_list()
    
    # Mapeo de compatibilidad con valores antiguos
    frecuencia_map = {
        'diaria': 'intermedia',
        'solo_noche': 'basica', 
        'minima': 'basica',
        'basica': 'basica',
        'intermedia': 'intermedia',
        'avanzada': 'avanzada'
    }
    
    frecuencia = frecuencia_map.get(perfil.frecuencia_rutina, 'basica')
    
    # PASO 1: Limpieza (siempre necesario)
    if 'grasa' in tipo or 'mixta' in tipo:
        rutina.agregar_paso(
            "Limpieza", 
            "Usa un limpiador en gel o espuma para eliminar impurezas sin resecar",
            "limpiador"
        )
    else:
        rutina.agregar_paso(
            "Limpieza", 
            "Usa un limpiador suave en crema o leche para limpiar sin dañar la barrera cutánea",
            "limpiador"
        )
    
    # PASO 2: Exfoliación (depende de frecuencia y condiciones)
    if frecuencia in ['avanzada', 'intermedia'] and len(condiciones_list) > 0:
        if 'acne' in [c.lower() for c in condiciones_list]:
            rutina.agregar_paso(
                "Exfoliación", 
                "Exfolia 2-3 veces por semana con un producto que contenga Ácido Salicílico (BHA)",
                "exfoliante"
            )
        elif 'manchas' in [c.lower() for c in condiciones_list]:
            rutina.agregar_paso(
                "Exfoliación", 
                "Exfolia 1-2 veces por semana con un producto que contenga Ácido Glicólico (AHA)",
                "exfoliante"
            )
        else:
            rutina.agregar_paso(
                "Exfoliación", 
                "Exfolia 1-2 veces por semana con un exfoliante suave para renovar la piel",
                "exfoliante"
            )
    
    # PASO 3: Tratamiento/Serum (personalizado por condiciones)
    if 'acne' in [c.lower() for c in condiciones_list]:
        rutina.agregar_paso(
            "Tratamiento", 
            "Aplica un serum con Niacinamida o Ácido Salicílico para controlar el acné",
            "serum"
        )
    elif 'manchas' in [c.lower() for c in condiciones_list]:
        rutina.agregar_paso(
            "Tratamiento", 
            "Aplica un serum con Vitamina C o Ácido Kójico para uniformar el tono",
            "serum"
        )
    elif 'seca' in tipo:
        rutina.agregar_paso(
            "Tratamiento", 
            "Aplica un serum hidratante con Ácido Hialurónico para reponer humedad",
            "serum"
        )
    else:
        rutina.agregar_paso(
            "Tratamiento", 
            "Aplica un serum antioxidante para proteger y mejorar la textura",
            "serum"
        )
    
    # PASO 4: Hidratación (siempre necesario)
    if 'grasa' in tipo:
        rutina.agregar_paso(
            "Hidratación", 
            "Usa una crema ligera en gel o textura oil-free que no obstruya poros",
            "crema_hidratante"
        )
    elif 'seca' in tipo:
        rutina.agregar_paso(
            "Hidratación", 
            "Usa una crema nutritiva con ceramidas para restaurar la barrera lipídica",
            "crema_hidratante"
        )
    else:  # mixta o normal
        rutina.agregar_paso(
            "Hidratación", 
            "Usa una crema de textura media que equilibre las zonas secas y grasas",
            "crema_hidratante"
        )
    
    # PASO 5: Protección Solar (SOLO si es de día, pero lo mantenemos como paso general)
    rutina.agregar_paso(
        "Protección Solar", 
        "Aplica protector solar FPS 30-50+ cada mañana. ¡Es el paso más importante!",
        "protector_solar"
    )
    
    return rutina

# --- Funciones de Base de Datos ---

def guardar_perfil_db(perfil: PerfilUsuario) -> bool:
    """Guarda el objeto PerfilUsuario en la base de datos."""
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
    Recibe datos, guarda perfil, genera rutina unificada y productos.
    """
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

        # 4. Generar la rutina UNIFICADA (nueva función)
        rutina_personalizada = generar_rutina_unificada(perfil_usuario)
        
        # 5. Generar los Productos Recomendados (USANDO LA NUEVA FUNCIÓN)
        try:
            # Usar la nueva función que se conecta con la rutina
            productos_recomendados = recommend_products_for_routine(
                rutina_personalizada, 
                perfil_usuario.tipo_piel, 
                perfil_usuario.condiciones
            )
            
            # Asignamos los productos a la rutina
            rutina_personalizada.productos_recomendados = productos_recomendados
            
            if not productos_recomendados:
                flash("Advertencia: El algoritmo de recomendación no encontró productos específicos para su perfil.", "warning")
        except Exception as e:
            print(f"ERROR en recommend_products_for_routine: {e}")
            # Fallback a la función original si hay error
            try:
                productos_recomendados = recommend_products(perfil_usuario.tipo_piel, perfil_usuario.condiciones, limit=6)
                rutina_personalizada.productos_recomendados = productos_recomendados
                flash("Advertencia: Se usó el modo de recomendación básico.", "warning")
            except Exception as fallback_error:
                print(f"ERROR en fallback: {fallback_error}")
                flash("Advertencia: No se pudieron cargar los productos recomendados. Revisar el archivo de datos (CSV).", "warning")

        # 6. Mostrar la página de resultados con la rutina unificada
        return render_template('resultados.html', 
                               perfil=perfil_usuario, 
                               rutina=rutina_personalizada,
                               productos=rutina_personalizada.productos_recomendados)
                               
    except ValueError:
        flash("Error de datos: Asegúrate de que la edad sea un número válido.", "error")
        return redirect(url_for('index'))
    except KeyError as e:
        flash(f"Error de formulario: Falta el campo '{e}'. Por favor, completa todos los pasos.", "error")
        return redirect(url_for('index'))
    except Exception as e:
        import traceback
        traceback.print_exc()
        flash(f"Ocurrió un error inesperado al procesar tu perfil: {e}", "error")
        return redirect(url_for('index'))

# --- Ejecución de la Aplicación ---

if __name__ == '__main__':
    crear_o_actualizar_tabla_perfiles()
    app.run(debug=True, host='0.0.0.0', port=5000)
# app.py
# Aplicación web SkinFit con Flask, POO, SQLite y generación de rutina básica.

from flask import Flask, render_template, request, redirect, url_for, flash
import sqlite3
from database import get_db_connection, crear_o_actualizar_tabla_perfiles # Importa funciones de database.py
from models import PerfilUsuario # Importa la clase desde models.py

app = Flask(__name__)
# Necesaria para mensajes flash y seguridad de sesión
app.config['SECRET_KEY'] = 'dev_secret_key_skinfit_12345'

# --- Lógica de Negocio: Generación de Rutina ---

def generar_rutina_basica(perfil: PerfilUsuario) -> dict:
    """
    Genera una rutina de skincare básica basada en el tipo de piel y condiciones.
    Retorna un diccionario con pasos para mañana y noche.
    """
    rutina = {'mañana': [], 'noche': []}
    condiciones = perfil.get_condiciones_list() # Obtiene condiciones como lista

    # --- Rutina Base según Tipo de Piel ---
    if perfil.tipo_piel == 'seca':
        rutina['mañana'].extend(['1. Limpiador Hidratante (Crema o Leche)', '2. Tónico Hidratante (Sin alcohol)', '3. Sérum con Ácido Hialurónico', '4. Crema Hidratante Rica (Ceramidas)', '5. Contorno de Ojos Hidratante', '6. Protector Solar SPF 50+ (Textura cremosa)'])
        rutina['noche'].extend(['1. Doble Limpieza (Aceite/Bálsamo + Limpiador Hidratante)', '2. Tónico Hidratante', '3. Sérum Reparador Nocturno (ej. Péptidos, Aceites nutritivos)', '4. Crema Nutritiva Intensa'])
    elif perfil.tipo_piel == 'grasa':
        rutina['mañana'].extend(['1. Limpiador en Gel (Control sebo, ej. Ácido Salicílico suave)', '2. Tónico Equilibrante / Matificante', '3. Sérum con Niacinamida', '4. Hidratante Ligero (Gel o Fluido)', '5. Protector Solar Oil-Free / Toque Seco SPF 50+'])
        rutina['noche'].extend(['1. Doble Limpieza (Agua Micelar + Limpiador Gel)', '2. Tónico Exfoliante Suave (AHA/BHA, 2-3 veces/semana)', '3. Sérum Específico (ej. Retinol suave si no hay acné activo, Niacinamida)', '4. Hidratante Gel Ligero'])
    elif perfil.tipo_piel == 'mixta':
        rutina['mañana'].extend(['1. Limpiador Suave (Espuma o Gel ligero)', '2. Tónico Equilibrante (Hidratante en zonas secas)', '3. Sérum Antioxidante (ej. Vitamina C)', '4. Hidratante Fluido Equilibrante', '5. Protector Solar SPF 50+ (Textura ligera)'])
        rutina['noche'].extend(['1. Doble Limpieza', '2. Tónico Equilibrante', '3. Sérum Específico (ej. Ácido Hialurónico en zonas secas, Niacinamida en zona T)', '4. Crema Hidratante Ligera / Media'])
    elif perfil.tipo_piel == 'sensible':
        rutina['mañana'].extend(['1. Limpiador Calmante (Syndet, sin sulfatos)', '2. Agua Termal o Tónico Calmante', '3. Sérum Calmante (ej. Centella Asiática, Pantenol)', '4. Crema Hidratante Hipoalergénica', '5. Protector Solar Mineral SPF 50+ (Óxido de Zinc / Dióxido de Titanio)'])
        rutina['noche'].extend(['1. Limpiador Calmante', '2. Agua Termal', '3. Sérum Reparador de Barrera (Ceramidas, Ácidos Grasos)', '4. Crema Hidratante Muy Suave'])
    else: # Default básico
        rutina['mañana'].extend(['Limpiador Suave', 'Hidratante', 'Protector Solar'])
        rutina['noche'].extend(['Limpiador Suave', 'Hidratante'])

    # --- Ajustes Adicionales según Condiciones ---
    if 'acne' in condiciones:
        # Añadir al final de la rutina de noche, o reemplazar paso si es necesario
        rutina['noche'].append('Extra: Tratamiento localizado para acné (ej. Peróxido Benzoilo, Ácido Salicílico)')
        # Considerar si algún producto base necesita cambio (ej. limpiador más específico)
    if 'manchas' in condiciones:
        rutina['mañana'].insert(2, 'Adicional Mañana: Sérum Despigmentante (Vitamina C, Ácido Azelaico, Niacinamida)') # Después del tónico
        rutina['noche'].append('Extra Noche: Tratamiento para manchas (ej. Retinoides suaves, Ácido Kójico - empezar gradualmente)')
    if 'arrugas' in condiciones:
        # Insertar sérum antiedad después del tónico de noche
        rutina['noche'].insert(2, 'Adicional Noche: Sérum Antiedad (Retinol, Péptidos - alternar días)')
    if 'rojeces' in condiciones:
        rutina['mañana'].insert(2, 'Adicional Mañana: Sérum Calmante extra (ej. Niacinamida, Extracto de Regaliz)')
        rutina['noche'].append('Ocasional: Mascarilla Calmante (1-2 veces/semana)')

    # --- Ajuste según Frecuencia ---
    if perfil.frecuencia_rutina == 'solo_noche':
        # Mantener solo lo esencial por la mañana
        rutina['mañana'] = ['1. Limpieza suave con agua (opcional)', '2. Protector Solar SPF 50+']
    elif perfil.frecuencia_rutina == 'minima':
        # Rutina muy simplificada para pocos días
        rutina['mañana'] = ['1. Protector Solar SPF 50+ (Obligatorio)']
        # Noche mínima: Limpiar, tratar (si aplica), hidratar
        rutina['noche'] = ['1. Limpiador Suave', '2. (Opcional) Sérum específico si hay condición', '3. Hidratante Básico']

    # Asegurar que no haya duplicados si se añadieron extras
    rutina['mañana'] = list(dict.fromkeys(rutina['mañana']))
    rutina['noche'] = list(dict.fromkeys(rutina['noche']))

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
        print(f"Perfil de {perfil.nombre} guardado exitosamente en la BD.")
        return True
    except sqlite3.Error as e:
        print(f"Error al guardar en BD: {e}")
        flash(f"Error al guardar en la base de datos: {e}", "error")
        return False
    finally:
        if conn:
            conn.close()
            print("Conexión a BD cerrada después de guardar.")


# --- Rutas de la Aplicación Web ---

@app.route('/')
def index():
    """Muestra el formulario principal."""
    print("Accediendo a la ruta principal /")
    return render_template('index.html')

@app.route('/procesar', methods=['POST'])
def procesar_formulario():
    """
    Recibe los datos del formulario, crea el perfil, lo guarda,
    genera la rutina y muestra la página de resultados.
    """
    print("Recibida solicitud POST en /procesar")
    try:
        # 1. Extraer datos del formulario
        nombre = request.form['nombre']
        edad = int(request.form['edad']) # Validar que sea número
        tipo_piel = request.form['tipo_piel'] # Validar que sea una opción válida
        # Checkboxes: usar getlist y unir con comas si hay selecciones
        condiciones_list = request.form.getlist('condiciones')
        condiciones_str = ", ".join(condiciones_list) if condiciones_list else "Ninguna"
        frecuencia = request.form['frecuencia_rutina']
        print(f"Datos recibidos: {nombre}, {edad}, {tipo_piel}, {condiciones_str}, {frecuencia}")

        # 2. Crear objeto PerfilUsuario (POO)
        perfil_usuario = PerfilUsuario(nombre, edad, tipo_piel, condiciones_str, frecuencia)
        print(f"Objeto PerfilUsuario creado: {perfil_usuario}")

        # 3. Guardar perfil en la Base de Datos
        if not guardar_perfil_db(perfil_usuario):
            # Si falla el guardado, mostrar error y volver al formulario
             print("Fallo al guardar en la BD.")
             return redirect(url_for('index'))
        print("Perfil guardado en BD.")

        # 4. Generar la rutina basada en el perfil
        rutina_generada = generar_rutina_basica(perfil_usuario)
        print(f"Rutina generada: {rutina_generada}")

        # 5. Mostrar la página de resultados
        # Pasamos el objeto perfil y la rutina generada a la plantilla resultados.html
        print("Renderizando página de resultados...")
        return render_template('resultados.html', perfil=perfil_usuario, rutina=rutina_generada)

    except ValueError:
        flash("Error: La edad debe ser un número.", "error")
        print("Error: Edad no es un número.")
        return redirect(url_for('index'))
    except KeyError as e:
        flash(f"Error: Falta el campo requerido '{e}' en el formulario. Asegúrate de seleccionar una opción en todos los desplegables y radios.", "error")
        print(f"Error: Falta el campo {e}.")
        return redirect(url_for('index'))
    except Exception as e:
        flash(f"Ocurrió un error inesperado al procesar tu perfil: {e}", "error")
        # Imprimir el traceback completo en la terminal para depuración
        import traceback
        traceback.print_exc()
        print(f"Error inesperado procesando formulario: {e}")
        return redirect(url_for('index'))

# --- Ejecución de la Aplicación ---

if __name__ == '__main__':
    # Asegura que la tabla exista antes de arrancar el servidor
    print("Verificando/Creando tabla de perfiles antes de iniciar...")
    crear_o_actualizar_tabla_perfiles()
    print("Iniciando servidor Flask...")
    # Ejecuta el servidor Flask en modo debug (se reinicia con cambios)
    # Escucha en todas las interfaces de red (0.0.0.0) para accesibilidad local
    app.run(debug=True, host='0.0.0.0', port=5000)
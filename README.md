  # **SkinFit-AI - Sistema de Recomendación Inteligente de Skincare**


 **Descripción del Proyecto**

SkinFit-AI es una aplicación web inteligente que genera rutinas de skincare personalizadas mediante un cuestionario dermatológico guiado. El sistema combina principios de ciencia de datos con diseño de software robusto para ofrecer recomendaciones precisas y adaptadas a las características únicas de cada usuario.
Valor único: Sistema agnóstico que recomienda productos de múltiples marcas, eliminando la dependencia de recomendaciones comerciales sesgadas.

 📁 **Estructura del Proyecto**
SkinFit-AI/

├── 📄 app.py                 # Aplicación principal Flask

├── 📄 database.py            # Gestión de conexiones BD

├── 📄 models.py              # Modelos de datos (POO)


├── 📁 templates/

│   ├── 📄 index.html         # Formulario de perfilación

│   └── 📄 resultados.html    # Página de resultados


├── 📁 static/

│   └── 📄 style.css          # Estilos personalizados

└── 📄 skinfit.db             # Base de datos (generada)


 **Instalación**

 Prerrequisitos
- Python 3.8 o superior
- pip (gestor de paquetes de Python)


 **Pasos de instalación**

1. Clonar el repositorio

git clone https://github.com/tuusuario/skinfit-ai.git
cd skinfit-ai


2. Crear entorno virtual (recomendado)

python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows


3. Instalar dependencias y versiones que estan en el requirements.txt

pip install -r requirements.txt

Activar la base de datos
py database.py

4. Ejecutar la aplicación

py app.py

5. Acceder a la aplicación
   Abre tu navegador y ve al link proporcionado


Flujo del Usuario

1. Acceso al Sistema
   - Completar formulario de perfilación

2. Perfilación Dermatológica
   - Ingresar datos personales (nombre, edad)
   - Seleccionar tipo de piel principal
   - Identificar condiciones cutáneas específicas
   - Definir frecuencia de rutina deseada

3. Generación de Rutina
   - Sistema procesa información con algoritmo experto
   - Genera rutina personalizada mañana/noche
   - Presenta resultados detallados y fundamentados

4. Resultados y Seguimiento
   - Visualizar rutina 
   - Recibir recomendaciones 

Autores
- Juan Manuel Preciado Rojas - Desarrollo principal y Documentación
- Heiner Pabón - Desarrollo 

 Agradecimientos

- Escuela Tecnológica Instituto Técnico Central
- Profesor Elias Buitrago B.


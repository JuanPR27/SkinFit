# SkinFit AI - Sistema Inteligente de Skincare

## 📋 Descripción del Proyecto

SkinFit AI es una aplicación web inteligente que genera rutinas de skincare personalizadas basadas en las características únicas de cada usuario. Utiliza algoritmos de recomendación para sugerir productos específicos adaptados al tipo de piel, condiciones y preferencias de cada persona.

## 🎯 Objetivo

Resolver la falta de personalización en el mercado de cuidado de la piel mediante un sistema de recomendación inteligente que sugiere rutinas y productos basados en ingredientes activos, no en estrategias de marketing.

## 🏗️ Arquitectura Técnica

### Stack Tecnológico
- **Backend**: Python + Flask
- **Frontend**: HTML5 + Tailwind CSS + JavaScript
- **Base de Datos**: SQLite
- **Motor de IA**: Pandas + Algoritmos Personalizados
- **Arquitectura**: MVC (Modelo-Vista-Controlador)

### Estructura del Proyecto
```
SkinFit-AI/
├── app.py                 # Aplicación principal Flask
├── models.py              # Modelos de datos
├── database.py            # Gestión de base de datos
├── ai_service/
│   └── recommender.py     # Motor de recomendación
├── data/
│   └── skincare.csv       # Dataset de productos
├── templates/
│   ├── index.html         # Formulario multi-paso
│   └── resultados.html    # Página de resultados
└── static/
    ├── formulario.css     # Estilos del formulario
    ├── resultados.css     # Estilos de resultados
    ├── script.js          # Lógica frontend
    └── logo.png           # Assets
```

## ⚙️ Funcionalidades Principales

### 1. Formulario Inteligente Multi-paso
- **Paso 1**: Datos personales (nombre, edad)
- **Paso 2**: Características de la piel (tipo, condiciones)
- **Paso 3**: Nivel de compromiso (básica, intermedia, avanzada)

### 2. Generación de Rutina Unificada
- Rutina personalizada adaptada al perfil
- Pasos específicos por tipo de piel y condiciones
- Recomendaciones diferenciadas día/noche

### 3. Sistema de Recomendación de Productos
- Base de datos con 1,400+ productos
- Algoritmo de matching por categoría y tipo de piel
- Integración con imágenes y precios en múltiples monedas

### 4. Interfaz Profesional
- Diseño responsive y moderno
- Navegación fluida entre pasos
- Visualización clara de resultados

## 🚀 Instalación y Ejecución

### Requisitos
- Python 3.8+
- Flask
- Pandas

### Comandos de Instalación
```bash
# Clonar o descargar el proyecto
cd SkinFit-AI

# Instalar dependencias
python -m pip install -r requirements.txt

# Ejecutar la aplicación
python app.py
```

### Acceso
La aplicación estará disponible en: `http://localhost:5000`


## 🔍 Características Técnicas Destacadas

### Motor de Recomendación
- Filtrado por tipo de piel y condiciones específicas
- Inferencia automática de categorías de productos
- Extracción inteligente de imágenes
- Conversión multi-moneda (USD, COP, INR)

### Experiencia de Usuario
- Validación en tiempo real
- Animaciones fluidas entre pasos
- Diseño mobile-first
- Feedback visual inmediato

### Base de Conocimiento
- Dataset real de productos de skincare
- Información de marcas, precios y enlaces
- Categorización automática por ingredientes

## 📈 Resultados Esperados

Al completar el formulario, los usuarios reciben:
1. **Rutina Personalizada**: Pasos específicos ordenados lógicamente
2. **Productos Recomendados**: Sugerencias basadas en su perfil exacto
3. **Guía Completa**: Instrucciones detalladas para cada paso
4. **Opciones de Compra**: Enlaces directos a productos verificados

## 🔒 Consideraciones

- **Propósito Académico**: Proyecto desarrollado para clase de ciencia de datos
- **Recomendaciones No Médicas**: Las sugerencias son orientativas
- **Prueba de Productos**: Se recomienda introducir nuevos productos gradualmente
- **Consulta Profesional**: Siempre consultar con dermatólogo para condiciones médicas

---

**Desarrollado como proyecto académico - Sistema de recomendación inteligente para skincare personalizado**

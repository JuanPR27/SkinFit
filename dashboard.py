# dashboard.py (CON CSS EXTERNO)

import pandas as pd
import dash
from dash import dcc, html
import plotly.express as px
import plotly.graph_objects as go
import os

# 1. Cargar los datos reales
try:
    DATA_PATH = os.path.join('data', 'skincare.csv')
    df = pd.read_csv(DATA_PATH)
    print(f" Dashboard cargado: {len(df)} productos")
    
    # Limpieza básica
    if 'Price' in df.columns:
        df['Price'] = pd.to_numeric(df['Price'], errors='coerce').fillna(0)
    if 'Brand' in df.columns:
        df['Brand'] = df['Brand'].fillna('Marca desconocida')
    if 'Skin_Type' in df.columns:
        df['Skin_Type'] = df['Skin_Type'].fillna('All')
        df['Skin_Type'] = df['Skin_Type'].str.replace('"', '').str.strip()
    
except Exception as e:
    print(f" Error: {e}")
    df = pd.DataFrame({
        'Brand': ['Nivea', 'Cetaphil', 'Neutrogena'],
        'Price': [300, 400, 350],
        'Skin_Type': ['All', 'Combination', 'Normal']
    })

# 2. Inicializar Dash
app = dash.Dash(__name__, title="SkinFit Dashboard")

# 3. Crear gráficos simples
def create_visualizations():
    """Crea gráficos básicos"""
    
    # Gráfico 1: Distribución de precios
    try:
        fig_price = px.histogram(
            df[df['Price'] > 0], 
            x="Price",
            title="Distribución de Precios",
            nbins=15,
            color_discrete_sequence=['#EC4899']
        )
        fig_price.update_layout(
            xaxis_title="Precio ($)",
            yaxis_title="Cantidad de Productos"
        )
    except:
        fig_price = go.Figure()
        fig_price.add_annotation(text="Datos no disponibles", x=0.5, y=0.5, showarrow=False)

    # Gráfico 2: Marcas más comunes
    try:
        brand_counts = df['Brand'].value_counts().head(6)
        fig_brands = px.bar(
            x=brand_counts.index,
            y=brand_counts.values,
            title="Marcas Más Comunes",
            color_discrete_sequence=['#8B5CF6']
        )
        fig_brands.update_layout(
            xaxis_title="Marca",
            yaxis_title="Cantidad"
        )
    except:
        fig_brands = go.Figure()
        fig_brands.add_annotation(text="Datos no disponibles", x=0.5, y=0.5, showarrow=False)

    return fig_price, fig_brands

# 4. Layout simple con CSS externo
fig_price, fig_brands = create_visualizations()

app.layout = html.Div([
    # Header
    html.Div([
        html.H1("SkinFit Dashboard", className='dashboard-title'),
        html.P("Análisis de datos del catálogo de productos", className='dashboard-subtitle')
    ], className='dashboard-header'),
    
    # Gráficos
    html.Div([
        html.Div([
            dcc.Graph(id='price-distribution', figure=fig_price)
        ], className='graph-container'),
        
        html.Div([
            dcc.Graph(id='top-brands', figure=fig_brands)
        ], className='graph-container')
    ], className='graphs-row'),
    
    # Información
    html.Div([
        html.P([
            f"Total productos: {len(df)} | ",
            f"Marcas únicas: {df['Brand'].nunique() if 'Brand' in df.columns else 'N/A'}"
        ], className='dataset-info')
    ])
])

# 5. CSS externo
app.index_string = '''
<!DOCTYPE html>
<html>
    <head>
        {%metas%}
        <title>{%title%}</title>
        {%favicon%}
        {%css%}
        <link rel="preconnect" href="https://fonts.googleapis.com">
        <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
        <link href="https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,400..900;1,400..900&family=Inter:wght@300;400;600;700;800&display=swap" rel="stylesheet">
        <link rel="stylesheet" href="/static/dashboard.css">
    </head>
    <body>
        {%app_entry%}
        <footer>
            {%config%}
            {%scripts%}
            {%renderer%}
        </footer>
    </body>
</html>
'''

if __name__ == '__main__':
    print("🚀 Dashboard en: http://localhost:8050")
    app.run(debug=True, port=8050)
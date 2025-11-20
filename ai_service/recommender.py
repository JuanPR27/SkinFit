# ai_service/recommender.py (VERSIÓN FINAL FUNCIONAL)

import pandas as pd
import os

# Define la ruta al archivo CSV correcto
DATA_PATH = os.path.join(os.path.dirname(__file__), '..', 'data', 'skincare.csv')

PRODUCTS_DF = pd.DataFrame()  # Inicializamos vacío

try:
    # Intenta cargar el dataset
    print(f"🔍 Cargando dataset desde: {DATA_PATH}")
    df_temp = pd.read_csv(DATA_PATH)
    
    # Verificar que el archivo no esté vacío
    if df_temp.empty:
        raise ValueError("El archivo CSV está vacío")
    
    print(f"✅ CSV cargado: {len(df_temp)} productos encontrados")
    
    # Limpieza básica de datos
    # Asegurar que las columnas críticas existan
    if 'Title' in df_temp.columns:
        df_temp['Title'] = df_temp['Title'].fillna('Producto sin nombre').astype(str).str.strip()
    else:
        df_temp['Title'] = 'Producto sin nombre'
    
    if 'Brand' in df_temp.columns:
        df_temp['Brand'] = df_temp['Brand'].fillna('Marca desconocida').astype(str)
    else:
        df_temp['Brand'] = 'Marca desconocida'
    
    if 'Skin_Type' in df_temp.columns:
        df_temp['Skin_Type'] = df_temp['Skin_Type'].fillna('All').astype(str)
        # Limpiar comillas y espacios
        df_temp['Skin_Type'] = df_temp['Skin_Type'].str.replace('"', '').str.strip()
    else:
        df_temp['Skin_Type'] = 'All'
    
    if 'Link' in df_temp.columns:
        df_temp['Link'] = df_temp['Link'].fillna('#').astype(str)
    else:
        df_temp['Link'] = '#'
    
    if 'Price' in df_temp.columns:
        # Limpiar precios
        df_temp['Price'] = df_temp['Price'].fillna(0)
        try:
            df_temp['Price'] = pd.to_numeric(df_temp['Price'], errors='coerce').fillna(0)
        except:
            df_temp['Price'] = 0
    else:
        df_temp['Price'] = 0
    
    PRODUCTS_DF = df_temp
    print(f"✅ Sistema de recomendación listo con {len(PRODUCTS_DF)} productos")
    
except FileNotFoundError:
    print(f"❌ ERROR: Archivo no encontrado en: {DATA_PATH}")
    print("   Verifica que 'skincare.csv' esté en la carpeta 'data'")
except pd.errors.EmptyDataError:
    print("❌ ERROR: El archivo CSV está vacío")
except Exception as e:
    print(f"❌ ERROR inesperado al cargar el CSV: {e}")

def recommend_products(user_skin_type: str, user_concern: str = "", limit: int = 6):
    """
    Función principal de recomendación - Filtra productos basados en tipo de piel y preocupaciones.
    """
    if PRODUCTS_DF.empty:
        print("⚠️  No hay datos de productos disponibles")
        return []
    
    # Validar parámetros
    if not user_skin_type:
        print("⚠️  No se proporcionó tipo de piel")
        return []
    
    user_skin_type_lower = user_skin_type.lower()
    user_concern_lower = user_concern.lower() if user_concern else ""
    
    print(f"🎯 Generando recomendaciones para: piel {user_skin_type}, preocupación: {user_concern}")
    
    try:
        # 1. MAPEO DE TIPOS DE PIEL (Español → Inglés)
        skin_type_mapping = {
            'seca': ['dry', 'very dry'],
            'mixta': ['combination', 'normal', 'all'],
            'grasa': ['oily', 'acne', 'acne prone'],
            'sensible': ['sensitive', 'all'],
            'normal': ['normal', 'all']
        }
        
        # Obtener los tipos de piel objetivo para buscar
        target_skin_types = skin_type_mapping.get(user_skin_type_lower, ['all'])
        
        # 2. FILTRADO POR TIPO DE PIEL (búsqueda flexible)
        filtered_df = pd.DataFrame()
        
        for skin_type in target_skin_types:
            mask = PRODUCTS_DF['Skin_Type'].str.contains(skin_type, case=False, na=False)
            matching_products = PRODUCTS_DF[mask]
            filtered_df = pd.concat([filtered_df, matching_products])
        
        # Eliminar duplicados
        filtered_df = filtered_df.drop_duplicates()
        
        print(f"   📊 Productos después de filtro por piel: {len(filtered_df)}")
        
        # 3. SI NO HAY COINCIDENCIAS, USAR BÚSQUEDA MÁS AMPLIA
        if filtered_df.empty:
            print("   🔄 No hay coincidencias exactas, usando todos los productos")
            filtered_df = PRODUCTS_DF.copy()
        
        # 4. FILTRADO POR PREOCUPACIÓN (búsqueda en títulos)
        if user_concern_lower and not filtered_df.empty:
            concern_keywords = {
                'acne': ['acne', 'pimple', 'oil-free', 'salicylic', 'tea tree', 'breakout'],
                'manchas': ['bright', 'glow', 'vitamin c', 'pigmentation', 'radiance', 'lightening'],
                'arrugas': ['anti-aging', 'wrinkle', 'firming', 'retinol', 'peptide', 'anti age']
            }
            
            keywords = concern_keywords.get(user_concern_lower, [])
            if keywords:
                concern_mask = filtered_df['Title'].str.contains(
                    '|'.join(keywords), case=False, na=False
                )
                concern_filtered = filtered_df[concern_mask]
                
                if not concern_filtered.empty:
                    filtered_df = concern_filtered
                    print(f"   🔍 Productos después de filtro por '{user_concern}': {len(filtered_df)}")
        
        # 5. SI TODAVÍA NO HAY RESULTADOS, USAR TODOS LOS PRODUCTOS
        if filtered_df.empty:
            print("   🔄 No hay productos que coincidan, mostrando productos generales")
            filtered_df = PRODUCTS_DF.copy()
        
        # 6. SELECCIÓN FINAL
        if filtered_df.empty:
            print("   ❌ No hay productos disponibles en el dataset")
            return []
        
        # Seleccionar aleatoriamente hasta el límite
        if len(filtered_df) > limit:
            recommended = filtered_df.sample(n=limit)
        else:
            recommended = filtered_df
        
        print(f"   ✅ {len(recommended)} productos recomendados para el usuario")
        
        # 7. PREPARAR DATOS PARA EL FRONTEND
        results = []
        for _, product in recommended.iterrows():
            # Formatear precio
            price = product.get('Price', 0)
            if price == 0 or pd.isna(price):
                price_display = "Consultar precio"
            else:
                try:
                    price_display = f"${float(price):.2f}"
                except:
                    price_display = str(price)
            
            # Acortar título si es muy largo
            product_name = product.get('Title', 'Producto sin nombre')
            if len(product_name) > 80:
                product_name = product_name[:77] + "..."
            
            product_dict = {
                'product_name': product_name,
                'brand': product.get('Brand', 'Marca desconocida'),
                'link': product.get('Link', '#'),
                'price': price_display
            }
            results.append(product_dict)
        
        return results
        
    except Exception as e:
        print(f"❌ ERROR durante la recomendación: {e}")
        return []
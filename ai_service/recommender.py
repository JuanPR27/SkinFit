# ai_service/recommender.py (VERSIÓN FINAL FUNCIONAL)

import pandas as pd
import os
import random
import re

# Define la ruta al archivo CSV correcto
DATA_PATH = os.path.join(os.path.dirname(__file__), '..', 'data', 'skincare.csv')

# DEFINIR LA FUNCIÓN PRIMERO, ANTES DE CUALQUIER USO
def infer_product_category(title):
    """
    Infiere la categoría del producto basándose en palabras clave en el título.
    """
    if not isinstance(title, str):
        return "crema_hidratante"  # Default category
    
    title_lower = title.lower()
    
    # Mapeo de palabras clave a categorías - MEJORADO para tu CSV
    category_keywords = {
        "limpiador": ["cleanser", "face wash", "limpiador", "wash", "cleansing", "gel limpiador"],
        "exfoliante": ["exfoliant", "scrub", "exfoliante", "peeling", "gommage", "AHA", "BHA", "ácido", "salicylic"],
        "serum": ["serum", "serum", "esencia", "concentrate", "treatment", "booster", "vitamin c", "niacinamide", "hyaluronic"],
        "crema_hidratante": ["moisturizer", "cream", "crema", "hidratante", "lotion", "emulsion", "balm", "nourishing", "hydrating"],
        "protector_solar": ["sunscreen", "spf", "sun protection", "protector solar", "block", "shield", "sunblock"],
        "mascarilla": ["mask", "mascarilla", "treatment mask", "sheet mask"]
    }
    
    for category, keywords in category_keywords.items():
        if any(keyword in title_lower for keyword in keywords):
            return category
    
    return "crema_hidratante"  # Default si no se encuentra

def extract_amazon_image(amazon_url):
    """
    Intenta extraer la imagen de un producto de Amazon de la URL.
    Devuelve una URL de imagen o una imagen por defecto.
    """
    if not amazon_url or amazon_url == '#':
        return "https://via.placeholder.com/200x200/667eea/ffffff?text=Sin+Imagen"
    
    try:
        # Para enlaces de Amazon, podemos intentar construir la URL de imagen
        # Basado en el ASIN (Amazon Standard Identification Number)
        
        # Extraer ASIN del URL de Amazon (patrón común)
        asin_pattern = r'/([A-Z0-9]{10})(?:[/?]|$)'
        match = re.search(asin_pattern, amazon_url)
        
        if match:
            asin = match.group(1)
            # Construir URL de imagen usando el ASIN
            image_url = f"https://images-na.ssl-images-amazon.com/images/P/{asin}.01._SCLZZZZZZZ_.jpg"
            return image_url
        else:
            # Si no podemos extraer ASIN, usar imagen por categoría
            return "https://via.placeholder.com/200x200/667eea/ffffff?text=Producto"
            
    except Exception as e:
        print(f"⚠️ Error extrayendo imagen de Amazon: {e}")
    
    # Imagen por defecto
    return "https://via.placeholder.com/200x200/667eea/ffffff?text=SkinFit"

PRODUCTS_DF = pd.DataFrame()  # Inicializamos vacío

try:
    # Intenta cargar el dataset
    print(f"🔍 Cargando dataset desde: {DATA_PATH}")
    df_temp = pd.read_csv(DATA_PATH)
    
    # Verificar que el archivo no esté vacío
    if df_temp.empty:
        raise ValueError("El archivo CSV está vacío")
    
    print(f"✅ CSV cargado: {len(df_temp)} productos encontrados")
    
    # LIMPIEZA ESPECÍFICA PARA TU CSV
    # Tu CSV tiene: Title, Product, Category, Brand, Skin_Type, Price, Link
    
    # 1. Title - nombre del producto
    if 'Title' in df_temp.columns:
        df_temp['Title'] = df_temp['Title'].fillna('Producto sin nombre').astype(str).str.strip()
        # Limpiar espacios extra y caracteres raros
        df_temp['Title'] = df_temp['Title'].str.replace(r'\s+', ' ', regex=True)
    else:
        df_temp['Title'] = 'Producto sin nombre'
    
    # 2. Brand - marca
    if 'Brand' in df_temp.columns:
        df_temp['Brand'] = df_temp['Brand'].fillna('Marca desconocida').astype(str).str.strip()
    else:
        df_temp['Brand'] = 'Marca desconocida'
    
    # 3. Skin_Type - tipo de piel (CRÍTICO para las recomendaciones)
    if 'Skin_Type' in df_temp.columns:
        df_temp['Skin_Type'] = df_temp['Skin_Type'].fillna('All').astype(str)
        # Limpiar y estandarizar tipos de piel
        df_temp['Skin_Type'] = df_temp['Skin_Type'].str.replace('"', '').str.strip()
        # Convertir a minúsculas para consistencia
        df_temp['Skin_Type'] = df_temp['Skin_Type'].str.lower()
    else:
        df_temp['Skin_Type'] = 'all'
    
    # 4. Price - precio
    if 'Price' in df_temp.columns:
        # Limpiar precios - convertir a numérico
        df_temp['Price'] = df_temp['Price'].fillna(0)
        try:
            df_temp['Price'] = pd.to_numeric(df_temp['Price'], errors='coerce').fillna(0)
        except:
            df_temp['Price'] = 0
    else:
        df_temp['Price'] = 0
    
    # 5. Link - enlace
    if 'Link' in df_temp.columns:
        df_temp['Link'] = df_temp['Link'].fillna('#').astype(str)
    else:
        df_temp['Link'] = '#'
    
    # 6. Category - categoría del producto (usaremos la inferida)
    print("📦 Inferiendo categorías de productos...")
    df_temp['Category'] = df_temp['Title'].apply(infer_product_category)
    
    # Mostrar distribución de categorías
    category_counts = df_temp['Category'].value_counts()
    print("📊 Distribución de categorías inferidas:")
    for category, count in category_counts.items():
        print(f"   {category}: {count} productos")
    
    PRODUCTS_DF = df_temp
    print(f"✅ Sistema de recomendación listo con {len(PRODUCTS_DF)} productos")
    
except FileNotFoundError:
    print(f"❌ ERROR: Archivo no encontrado en: {DATA_PATH}")
    print("   Verifica que 'skincare.csv' esté en la carpeta 'data'")
except pd.errors.EmptyDataError:
    print("❌ ERROR: El archivo CSV está vacío")
except Exception as e:
    print(f"❌ ERROR inesperado al cargar el CSV: {e}")
    import traceback
    traceback.print_exc()

def recommend_products_by_category(user_skin_type: str, user_concern: str = "", product_category: str = None, limit: int = 3):
    """
    Recomienda productos específicos por categoría.
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
    
    print(f"🎯 Generando recomendaciones para: piel '{user_skin_type}', categoría: '{product_category}'")
    
    try:
        # 1. MAPEO DE TIPOS DE PIEL (Español → Inglés)
        skin_type_mapping = {
            'seca': ['dry', 'very dry', 'all'],
            'mixta': ['combination', 'normal', 'all'],
            'grasa': ['oily', 'acne', 'acne prone', 'all'],
            'sensible': ['sensitive', 'all'],
            'normal': ['normal', 'all']
        }
        
        # Obtener los tipos de piel objetivo para buscar
        target_skin_types = skin_type_mapping.get(user_skin_type_lower, ['all'])
        print(f"   🔍 Buscando tipos de piel: {target_skin_types}")
        
        # 2. FILTRADO INICIAL - empezar con todos los productos
        filtered_df = PRODUCTS_DF.copy()
        
        # 3. FILTRADO POR CATEGORÍA SI SE ESPECIFICA
        if product_category and product_category != "otros":
            category_mask = filtered_df['Category'] == product_category
            filtered_df = filtered_df[category_mask]
            print(f"   📦 Filtrado por categoría '{product_category}': {len(filtered_df)} productos")
        
        # 4. FILTRADO POR TIPO DE PIEL (búsqueda flexible)
        skin_filtered_dfs = []
        for skin_type in target_skin_types:
            # Buscar en la columna Skin_Type
            mask = filtered_df['Skin_Type'].str.contains(skin_type, case=False, na=False)
            matching_products = filtered_df[mask]
            skin_filtered_dfs.append(matching_products)
        
        if skin_filtered_dfs:
            filtered_df = pd.concat(skin_filtered_dfs).drop_duplicates()
        else:
            filtered_df = pd.DataFrame()
        
        print(f"   📊 Productos después de filtro por piel: {len(filtered_df)}")
        
        # 5. SI NO HAY COINCIDENCIAS, RELAJAR FILTROS
        if filtered_df.empty:
            print("   🔄 No hay coincidencias exactas, usando productos de la categoría sin filtro de piel")
            if product_category:
                filtered_df = PRODUCTS_DF[PRODUCTS_DF['Category'] == product_category]
            else:
                filtered_df = PRODUCTS_DF.copy()
        
        # 6. FILTRADO POR PREOCUPACIÓN (búsqueda en títulos)
        if user_concern_lower and not filtered_df.empty:
            concern_keywords = {
                'acne': ['acne', 'pimple', 'oil-free', 'salicylic', 'tea tree', 'breakout', 'blemish', 'acne prone'],
                'manchas': ['bright', 'glow', 'vitamin c', 'pigmentation', 'radiance', 'lightening', 'dark spot', 'brightening'],
                'arrugas': ['anti-aging', 'wrinkle', 'firming', 'retinol', 'peptide', 'anti age', 'anti-wrinkle', 'firming'],
                'seca': ['hydrating', 'moisturizing', 'dry skin', 'hydration', 'moisture', 'nourishing', 'dry'],
                'sensible': ['sensitive', 'calming', 'gentle', 'soothing', 'fragrance-free', 'hypoallergenic']
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
        
        # 7. SI TODAVÍA NO HAY RESULTADOS, USAR TODOS LOS PRODUCTOS DE LA CATEGORÍA
        if filtered_df.empty and product_category:
            print("   🔄 No hay productos que coincidan, mostrando cualquier producto de la categoría")
            filtered_df = PRODUCTS_DF[PRODUCTS_DF['Category'] == product_category]
        
        # 8. SI TODAVÍA NO HAY NADA, USAR TODOS LOS PRODUCTOS
        if filtered_df.empty:
            print("   🔄 No hay productos en la categoría, mostrando productos generales")
            filtered_df = PRODUCTS_DF.copy()
        
        # 9. SELECCIÓN FINAL
        if filtered_df.empty:
            print(f"   ❌ No hay productos de categoría '{product_category}' disponibles")
            return []
        
        # Seleccionar aleatoriamente hasta el límite
        if len(filtered_df) > limit:
            recommended = filtered_df.sample(n=limit)
        else:
            recommended = filtered_df
        
        print(f"   ✅ {len(recommended)} productos recomendados para categoría '{product_category}'")
        
        # 10. PREPARAR DATOS PARA EL FRONTEND
        results = []
        for _, product in recommended.iterrows():
            # Formatear precio - CONVERSIÓN A USD Y COP
            price_inr = product.get('Price', 0)
            
            if price_inr == 0 or pd.isna(price_inr):
                price_display = "Consultar precio"
                price_usd = "Consultar precio"
                price_cop = "Consultar precio"
            else:
                try:
                    price_inr_float = float(price_inr)
                    # Conversiones aproximadas (puedes ajustar las tasas)
                    # 1 INR = 0.012 USD (aproximado)
                    # 1 USD = 4000 COP (aproximado)
                    price_usd = price_inr_float * 0.012
                    price_cop = price_usd * 4000
                    
                    price_display = f"${price_usd:.2f} USD"
                    price_usd = f"${price_usd:.2f}"
                    price_cop = f"${price_cop:,.0f} COP"
                    
                except:
                    price_display = f"₹{price_inr}"
                    price_usd = "Consultar precio"
                    price_cop = "Consultar precio"
            
            # Acortar título si es muy largo
            product_name = product.get('Title', 'Producto sin nombre')
            if len(product_name) > 80:
                product_name = product_name[:77] + "..."
            
            product_dict = {
                'product_name': product_name,
                'brand': product.get('Brand', 'Marca desconocida'),
                'link': product.get('Link', '#'),
                'price_display': price_display,  # Precio principal para mostrar
                'price_usd': price_usd,          # Precio en USD
                'price_cop': price_cop,          # Precio en COP
                'price_inr': f"₹{price_inr}",    # Precio original en INR
                'category': product.get('Category', 'crema_hidratante'),
                'image_url': extract_amazon_image(product.get('Link', '#'))  # URL de imagen
            }
            results.append(product_dict)
        
        return results
        
    except Exception as e:
        print(f"❌ ERROR durante la recomendación por categoría: {e}")
        import traceback
        traceback.print_exc()
        return []

def recommend_products(user_skin_type: str, user_concern: str = "", limit: int = 6):
    """
    FUNCIÓN ORIGINAL MANTENIDA PARA COMPATIBILIDAD
    """
    return recommend_products_by_category(user_skin_type, user_concern, None, limit)

def recommend_products_for_routine(rutina_personalizada, user_skin_type: str, user_concern: str = ""):
    """
    Recomienda productos específicos para cada paso de la rutina.
    """
    all_recommended_products = []
    
    print(f"🔄 Buscando productos para rutina con {len(rutina_personalizada.pasos)} pasos...")
    
    # Para cada paso en la rutina, buscar productos de esa categoría
    for paso in rutina_personalizada.pasos:
        tipo_producto = paso.get('tipo_producto')
        
        if tipo_producto:
            print(f"   🔍 Buscando productos para paso: {paso['nombre']} (categoría: {tipo_producto})")
            
            productos_paso = recommend_products_by_category(
                user_skin_type, 
                user_concern, 
                tipo_producto, 
                limit=2  # 2 productos por categoría
            )
            
            # Agregar información del paso a los productos
            for producto in productos_paso:
                producto['paso_recomendado'] = paso['nombre']
                producto['orden_paso'] = paso['orden']
            
            all_recommended_products.extend(productos_paso)
            print(f"   ✅ Encontrados {len(productos_paso)} productos para {paso['nombre']}")
    
    # Si no encontramos productos por categoría, usar recomendación general
    if not all_recommended_products:
        print("   🔄 No se encontraron productos por categoría, usando recomendación general")
        all_recommended_products = recommend_products(user_skin_type, user_concern, limit=6)
    
    print(f"🎉 Total de productos recomendados: {len(all_recommended_products)}")
    return all_recommended_products
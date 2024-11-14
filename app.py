import streamlit as st
import pandas as pd
from difflib import SequenceMatcher

# Cargar inventario desde Google Sheets
def load_inventory_file():
    inventario_url = "https://docs.google.com/spreadsheets/d/1Y9SgliayP_J5Vi2SdtZmGxKWwf1iY7ma/export?format=xlsx&sheet=Hoja1"
    inventario_df = pd.read_excel(inventario_url)
    inventario_df.columns = inventario_df.columns.str.lower().str.strip()  # Normalizar columnas
    return inventario_df

# Función para comparar nombres de productos
def find_best_match(product_name, inventory_df):
    best_match = None
    highest_similarity = 0

    # Iterar por cada nombre en el inventario para buscar la mejor coincidencia
    for idx, row in inventory_df.iterrows():
        inventory_name = row['nombre']
        
        # Calcular similitud entre palabras
        similarity = SequenceMatcher(None, sorted(product_name.lower().split()), sorted(inventory_name.lower().split())).ratio()

        if similarity > highest_similarity:
            highest_similarity = similarity
            best_match = row  # Guardar la mejor coincidencia encontrada

    return best_match if highest_similarity > 0.5 else None  # Retornar solo coincidencias significativas

# Streamlit UI
st.title('Buscador de Código de Producto')

uploaded_file = st.file_uploader("Sube un archivo con 'nombre' del producto y 'embalaje'", type="xlsx")

if uploaded_file:
    # Leer archivo subido
    user_df = pd.read_excel(uploaded_file)
    user_df.columns = user_df.columns.str.lower().str.strip()  # Normalizar columnas
    
    if 'nombre' in user_df.columns:
        inventario_df = load_inventory_file()
        
        resultados = []
        for _, row in user_df.iterrows():
            product_name = row['nombre']
            embalaje = row.get('embalaje', None)  # Verificar si existe la columna embalaje
            
            best_match = find_best_match(product_name, inventario_df)
            if best_match is not None:
                result_row = {
                    'nombre': product_name,
                    'embalaje': embalaje,
                    'codigo_encontrado': best_match['codigo'] if 'codigo' in best_match else None,
                    'nombre_encontrado': best_match['nombre']
                }
                resultados.append(result_row)
            else:
                resultados.append({'nombre': product_name, 'embalaje': embalaje, 'codigo_encontrado': 'No encontrado'})
        
        # Mostrar resultados
        resultados_df = pd.DataFrame(resultados)
        st.write("Resultados de la búsqueda:")
        st.dataframe(resultados_df)
        
        # Descargar archivo de resultados
        def to_excel(df):
            output = BytesIO()
            with pd.ExcelWriter(output, engine='openpyxl') as writer:
                df.to_excel(writer, index=False, sheet_name='Resultados')
            return output.getvalue()

        st.download_button(
            label="Descargar resultados en Excel",
            data=to_excel(resultados_df),
            file_name='resultados_busqueda.xlsx',
            mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
    else:
        st.error("El archivo subido debe contener la columna 'nombre'.")

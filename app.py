import streamlit as st
import pandas as pd
from fuzzywuzzy import fuzz
from fuzzywuzzy import process

# Función para buscar el producto en la base de datos
def encontrar_similitudes(nombre_producto, base_df):
    # Dividir el nombre ingresado en palabras individuales
    palabras_ingresadas = set(nombre_producto.lower().split())
    
    # Lista para almacenar las coincidencias encontradas
    coincidencias = []
    
    # Comparar cada producto en la base con las palabras del nombre ingresado
    for idx, row in base_df.iterrows():
        base_nombre = row['nomart'].lower()
        base_palabras = set(base_nombre.split())
        
        # Buscar la similitud basada en las palabras
        palabras_comunes = palabras_ingresadas & base_palabras
        
        if palabras_comunes:
            # Se usa fuzz.token_sort_ratio para permitir la comparación a pesar del orden de las palabras
            similitud = fuzz.token_sort_ratio(nombre_producto.lower(), base_nombre)
            coincidencias.append({
                "Producto Base": row['nomart'],
                "Código": row['codart'],
                "Similitud": similitud
            })
    
    # Si se encuentran coincidencias, ordenarlas por similitud y devolver el resultado
    if coincidencias:
        return pd.DataFrame(coincidencias).sort_values(by="Similitud", ascending=False)
    else:
        return None

# Cargar el archivo de Google Sheets como base de datos
@st.cache_data
def cargar_base_de_datos():
    url = "https://docs.google.com/spreadsheets/d/1Y9SgliayP_J5Vi2SdtZmGxKWwf1iY7ma/export?format=csv"
    base_df = pd.read_csv(url)
    return base_df

# Subir el archivo con los nombres de los productos
st.title("Buscar Código de Producto")
nombre = st.text_input("Ingresa el nombre del producto", "")

# Cargar la base de datos
base_df = cargar_base_de_datos()

# Realizar la búsqueda si el nombre del producto está ingresado
if nombre:
    similitudes_df = encontrar_similitudes(nombre, base_df)
    
    if similitudes_df is not None and not similitudes_df.empty:
        # Mostrar las coincidencias
        st.write("Se encontraron las siguientes coincidencias:")
        st.dataframe(similitudes_df)
    else:
        st.write("No se encontraron coincidencias para el producto ingresado.")

import streamlit as st
import pandas as pd
import re

# Función para cargar la base desde Google Sheets
def load_base():
    # Cambia el enlace por el que corresponda a tu Google Sheets
    base_url = "https://docs.google.com/spreadsheets/d/1Y9SgliayP_J5Vi2SdtZmGxKWwf1iY7ma/export?format=xlsx"
    base_df = pd.read_excel(base_url, sheet_name="Hoja1")
    base_df.columns = base_df.columns.str.lower().str.strip()  # Asegura que las columnas estén en minúsculas y sin espacios
    return base_df

# Función para limpiar el texto (eliminar caracteres especiales y números)
def clean_text(text):
    text = text.lower()  # Convertir a minúsculas
    text = re.sub(r'[^\w\s]', '', text)  # Eliminar caracteres especiales
    text = re.sub(r'\d+', '', text)  # Eliminar los números
    return text

# Función para buscar coincidencias de todas las palabras
def buscar_coincidencias(nombre, base_df):
    # Limpiar el nombre ingresado
    nombre_limpio = clean_text(nombre)
    palabras = nombre_limpio.split()  # Dividir el nombre en palabras
    
    # Inicializar la lista de coincidencias
    coincidencias = base_df
    
    # Filtrar por cada palabra en el nombre
    for palabra in palabras:
        coincidencias = coincidencias[coincidencias['nomart'].str.contains(palabra, case=False, na=False)]
    
    return coincidencias

# Streamlit UI
st.title('Buscador de Código de Productos')

# Subir archivo con nombres de productos
uploaded_file = st.file_uploader("Sube un archivo con los nombres de productos", type=["xlsx", "csv"])

if uploaded_file:
    if uploaded_file.name.endswith('xlsx'):
        productos_df = pd.read_excel(uploaded_file)
    else:
        productos_df = pd.read_csv(uploaded_file)

    # Verificar que el archivo tenga la columna 'nombre'
    if 'nombre' in productos_df.columns:
        # Cargar la base de datos desde Google Sheets
        base_df = load_base()

        # Verificar que la base también tenga la columna 'nomart' y 'codart'
        if 'nomart' in base_df.columns and 'codart' in base_df.columns:
            # Lista para almacenar resultados
            resultados = []

            # Iterar sobre los nombres de productos y buscar coincidencias
            for nombre in productos_df['nombre']:
                coincidencias_df = buscar_coincidencias(nombre, base_df)
                if not coincidencias_df.empty:
                    # Guardar todas las coincidencias
                    for _, row in coincidencias_df.iterrows():
                        resultados.append({
                            "Nombre_ingresado": nombre,
                            "Nombre_encontrado": row["nomart"],
                            "Codigo": row["codart"]
                        })
                else:
                    resultados.append({
                        "Nombre_ingresado": nombre,
                        "Nombre_encontrado": "No encontrado",
                        "Codigo": "No disponible"
                    })

            # Convertir resultados a DataFrame y mostrar en la aplicación
            resultados_df = pd.DataFrame(resultados)
            st.write("Resultados de la búsqueda:")
            st.dataframe(resultados_df)

        else:
            st.error("La base de datos no contiene las columnas 'nomart' y/o 'codart'.")
    else:
        st.error("El archivo subido no contiene la columna 'nombre'.")

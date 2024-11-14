import streamlit as st
import pandas as pd
from io import BytesIO
import re

# Función para cargar la base desde Google Sheets
def load_base():
    base_url = "https://docs.google.com/spreadsheets/d/1Y9SgliayP_J5Vi2SdtZmGxKWwf1iY7ma/export?format=xlsx"
    base_df = pd.read_excel(base_url, sheet_name="Hoja1")
    base_df.columns = base_df.columns.str.lower().str.strip()  # Asegura que las columnas estén en minúsculas y sin espacios
    return base_df

# Función para limpiar los nombres y eliminar caracteres especiales
def clean_text(text):
    # Eliminar caracteres especiales y convertir a minúsculas
    text = text.lower()
    text = re.sub(r'[^\w\s]', '', text)  # Elimina caracteres como +, /, ()...
    return text

# Función para buscar coincidencias
def encontrar_similitudes(nombre, base_df):
    # Limpiar el nombre del producto
    nombre_limpio = clean_text(nombre)
    palabras_buscar = nombre_limpio.split()

    coincidencias = []

    for _, row in base_df.iterrows():
        base_nombre_limpio = clean_text(row['nomart'])
        
        # Verificar si todas las palabras del producto ingresado están en el nombre de la base
        if all(palabra in base_nombre_limpio for palabra in palabras_buscar):
            coincidencias.append({
                "Nombre_producto_base": row['nomart'],
                "Codigo": row['codart']
            })

    if coincidencias:
        return pd.DataFrame(coincidencias)
    else:
        return pd.DataFrame(columns=["Nombre_producto_base", "Codigo"])

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
                coincidencias_df = encontrar_similitudes(nombre, base_df)
                if not coincidencias_df.empty:
                    resultados.append({
                        "Nombre_ingresado": nombre,
                        "Nombre_encontrado": coincidencias_df.iloc[0]["Nombre_producto_base"],
                        "Codigo": coincidencias_df.iloc[0]["Codigo"]
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

            # Botón para descargar los resultados como archivo Excel
            def generar_excel(df):
                output = BytesIO()
                with pd.ExcelWriter(output, engine='openpyxl') as writer:
                    df.to_excel(writer, index=False, sheet_name='Resultados')
                output.seek(0)
                return output

            st.download_button(
                label="Descargar resultados como Excel",
                data=generar_excel(resultados_df),
                file_name="resultados_busqueda_productos.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
        else:
            st.error("La base de datos no contiene las columnas 'nomart' y/o 'codart'.")
    else:
        st.error("El archivo subido no contiene la columna 'nombre'.")

import streamlit as st
import pandas as pd
import re
import requests
from io import BytesIO

# Función para cargar la base desde Google Sheets usando requests
def load_base():
    base_url = "https://docs.google.com/spreadsheets/d/1Y9SgliayP_J5Vi2SdtZmGxKWwf1iY7ma/export?format=xlsx"
    response = requests.get(base_url)
    response.raise_for_status()  # Asegura que no haya errores en la descarga
    base_df = pd.read_excel(BytesIO(response.content), sheet_name="Hoja1")
    base_df.columns = base_df.columns.str.lower().str.strip()  # Asegura que las columnas estén en minúsculas y sin espacios
    return base_df

# Función para limpiar texto y preparar palabras clave
def limpiar_texto(texto):
    return re.sub(r'[^\w\s]', '', texto.lower()).split()

# Función para buscar coincidencias
def encontrar_similitudes(nombre, base_df):
    nombre_palabras = limpiar_texto(nombre)
    coincidencias = []

    for _, row in base_df.iterrows():
        base_nombre = row['nomart']
        base_palabras = limpiar_texto(base_nombre)

        # Verifica si todas las palabras del nombre están en base_palabras
        if all(word in base_palabras for word in nombre_palabras):
            coincidencias.append({
                "Nombre_producto_base": base_nombre,
                "Codigo": row['codart']
            })

    # Si hay coincidencias, retornarlas
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

            # Iterar sobre los nombres de productos y buscar similitudes
            for nombre in productos_df['nombre']:
                similitudes_df = encontrar_similitudes(nombre, base_df)
                if not similitudes_df.empty:
                    mejor_coincidencia = similitudes_df.iloc[0]  # Selecciona la mejor coincidencia
                    resultados.append({
                        "Nombre_ingresado": nombre,
                        "Nombre_encontrado": mejor_coincidencia["Nombre_producto_base"],
                        "Codigo": mejor_coincidencia["Codigo"]
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

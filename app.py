import streamlit as st
import pandas as pd
from io import BytesIO
from fuzzywuzzy import fuzz
from fuzzywuzzy import process  # Para ayudar con la comparación avanzada

# Función para cargar la base desde Google Sheets
def load_base():
    base_url = "https://docs.google.com/spreadsheets/d/1Y9SgliayP_J5Vi2SdtZmGxKWwf1iY7ma/export?format=xlsx"
    base_df = pd.read_excel(base_url, sheet_name="Hoja1")
    base_df.columns = base_df.columns.str.lower().str.strip()  # Asegura que las columnas estén en minúsculas y sin espacios
    return base_df

# Función para encontrar la mejor coincidencia de nombre en la base
def encontrar_similitud(nombre, base_df):
    # Buscar la mejor coincidencia en la columna 'nomart'
    mejor_coincidencia = process.extractOne(nombre, base_df['nomart'], scorer=fuzz.token_sort_ratio)
    if mejor_coincidencia and mejor_coincidencia[1] > 60:  # Umbral de similitud (ajustable)
        codigo = base_df.loc[base_df['nomart'] == mejor_coincidencia[0], 'codart'].values[0]
        return mejor_coincidencia[0], codigo, mejor_coincidencia[1]
    else:
        return "No encontrado", "No disponible", 0

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

        # Verificar que la base tenga las columnas 'nomart' y 'codart'
        if 'nomart' in base_df.columns and 'codart' in base_df.columns:
            # Lista para almacenar resultados
            resultados = []

            # Iterar sobre los nombres de productos y buscar similitudes
            for nombre in productos_df['nombre']:
                nombre_encontrado, codigo, similitud = encontrar_similitud(nombre, base_df)
                resultados.append({
                    "Nombre_ingresado": nombre,
                    "Nombre_encontrado": nombre_encontrado,
                    "Codigo": codigo,
                    "Similitud": similitud
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

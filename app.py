import streamlit as st
import pandas as pd
from difflib import SequenceMatcher
from io import BytesIO

# Función para cargar la base desde Google Sheets
def load_base():
    base_url = "https://docs.google.com/spreadsheets/d/1Y9SgliayP_J5Vi2SdtZmGxKWwf1iY7ma/export?format=xlsx"
    base_df = pd.read_excel(base_url, sheet_name="Hoja1")
    base_df.columns = base_df.columns.str.lower().str.strip()
    return base_df

# Función para buscar coincidencias parciales
def encontrar_similitudes(nombre, base_df):
    nombre_palabras = set(nombre.lower().split())
    coincidencias = []

    for _, row in base_df.iterrows():
        base_nombre = row['nombre'].lower()
        base_palabras = set(base_nombre.split())
        # Calcula la similitud
        porcentaje_similitud = SequenceMatcher(None, nombre, base_nombre).ratio()
        
        # Condición: palabras coinciden o porcentaje de similitud es alto
        if nombre_palabras & base_palabras or porcentaje_similitud > 0.6:
            coincidencias.append({
                "Nombre_producto_base": base_nombre,
                "Codigo": row['codigo'],
                "Similitud": porcentaje_similitud
            })

    return pd.DataFrame(coincidencias).sort_values(by="Similitud", ascending=False)

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
                    "Codigo": mejor_coincidencia["Codigo"],
                    "Similitud": mejor_coincidencia["Similitud"]
                })
            else:
                resultados.append({
                    "Nombre_ingresado": nombre,
                    "Nombre_encontrado": "No encontrado",
                    "Codigo": "No disponible",
                    "Similitud": 0
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
        st.error("El archivo subido no contiene la columna 'nombre'.")

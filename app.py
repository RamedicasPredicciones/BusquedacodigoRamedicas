import streamlit as st
import pandas as pd
from io import BytesIO
from fuzzywuzzy import fuzz
import re  # Para limpiar caracteres especiales

# Función para cargar la base desde Google Sheets
def load_base():
    base_url = "https://docs.google.com/spreadsheets/d/1Y9SgliayP_J5Vi2SdtZmGxKWwf1iY7ma/export?format=xlsx"
    base_df = pd.read_excel(base_url, sheet_name="Hoja1")
    base_df.columns = base_df.columns.str.lower().str.strip()  # Asegura que las columnas estén en minúsculas y sin espacios
    return base_df

# Función para limpiar y normalizar texto
def limpiar_texto(texto):
    # Convertir a minúsculas y remover caracteres especiales
    texto = texto.lower()
    texto = re.sub(r'[^\w\s]', '', texto)  # Eliminar todo excepto letras y espacios
    palabras = texto.split()  # Dividir en palabras
    return palabras

# Función para comparar las palabras ignorando el orden
def comparar_palabras(nombre, nombre_base):
    # Limpiar y obtener las listas de palabras
    palabras_nombre = set(limpiar_texto(nombre))
    palabras_nombre_base = set(limpiar_texto(nombre_base))

    # Calcular el porcentaje de palabras en común (intersección)
    interseccion = palabras_nombre.intersection(palabras_nombre_base)
    similitud = len(interseccion) / max(len(palabras_nombre), len(palabras_nombre_base)) * 100
    return similitud

# Función para encontrar la mejor coincidencia de nombre en la base
def encontrar_similitud(nombre, base_df):
    coincidencias = []

    # Buscar en cada fila de la base
    for _, row in base_df.iterrows():
        nombre_base = row['nomart']
        codigo = row['codart']

        # Comparar palabra por palabra
        similitud = comparar_palabras(nombre, nombre_base)

        # Guardar coincidencias que superen el umbral
        if similitud > 60:  # Ajusta el umbral según necesidad
            coincidencias.append({
                "Nombre_producto_base": nombre_base,
                "Codigo": codigo,
                "Similitud": similitud
            })

    # Ordenar las coincidencias por similitud y devolver la mejor
    if coincidencias:
        mejor_coincidencia = max(coincidencias, key=lambda x: x['Similitud'])
        return mejor_coincidencia["Nombre_producto_base"], mejor_coincidencia["Codigo"], mejor_coincidencia["Similitud"]
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

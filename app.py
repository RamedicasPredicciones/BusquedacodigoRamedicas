import streamlit as st
import pandas as pd
from io import BytesIO
from fuzzywuzzy import fuzz
from collections import Counter

# Función para cargar la base desde Google Sheets
def load_base():
    base_url = "https://docs.google.com/spreadsheets/d/1Y9SgliayP_J5Vi2SdtZmGxKWwf1iY7ma/export?format=xlsx"
    base_df = pd.read_excel(base_url, sheet_name="Hoja1")
    base_df.columns = base_df.columns.str.lower().str.strip()  # Asegura que las columnas estén en minúsculas y sin espacios
    return base_df

# Función para comparar listas de palabras (sin importar el orden)
def comparar_palabras(nombre, nombre_base):
    # Convertimos ambos nombres a minúsculas y los dividimos en palabras
    nombre_palabras = set(nombre.lower().split())
    nombre_base_palabras = set(nombre_base.lower().split())
    
    # Comparamos las palabras en los dos conjuntos (calculamos cuántas palabras coinciden)
    interseccion = nombre_palabras.intersection(nombre_base_palabras)
    similitud = len(interseccion) / max(len(nombre_palabras), len(nombre_base_palabras)) * 100
    
    return similitud

# Función para buscar coincidencias
def encontrar_similitudes(nombre, base_df):
    coincidencias = []

    for _, row in base_df.iterrows():
        base_nombre = row['nomart']

        # Calculamos la similitud entre los nombres
        similitud = comparar_palabras(nombre, base_nombre)

        # Solo agregamos si la similitud es mayor al umbral
        if similitud > 60:  # Puedes ajustar este umbral según lo necesites
            coincidencias.append({
                "Nombre_producto_base": base_nombre,
                "Codigo": row['codart'],
                "Similitud": similitud
            })

    # Si hay coincidencias, las retornamos ordenadas por similitud
    if coincidencias:
        return pd.DataFrame(coincidencias).sort_values(by="Similitud", ascending=False)
    else:
        return pd.DataFrame(columns=["Nombre_producto_base", "Codigo", "Similitud"])

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
            st.error("La base de datos no contiene las columnas 'nomart' y/o 'codart'.")
    else:
        st.error("El archivo subido no contiene la columna 'nombre'.")

import streamlit as st
import pandas as pd
import requests
import re
from io import BytesIO

# Función para cargar la base desde Google Sheets
def load_base():
    base_url = "https://docs.google.com/spreadsheets/d/1Y9SgliayP_J5Vi2SdtZmGxKWwf1iY7ma/export?format=xlsx"
    response = requests.get(base_url)
    base_df = pd.read_excel(BytesIO(response.content), sheet_name="Hoja1")
    base_df.columns = base_df.columns.str.lower().str.strip()
    return base_df

# Función para normalizar nombres eliminando caracteres especiales y convirtiendo a minúsculas
def normalizar_nombre(nombre):
    nombre = re.sub(r'[^\w\s]', ' ', nombre)  # Elimina caracteres especiales excepto letras y números
    return nombre.lower()

# Función para verificar si todas las palabras están presentes en un nombre de la base, sin importar el orden
def comparar_palabras(nombre, nombre_base):
    nombre_palabras = set(normalizar_nombre(nombre).split())
    nombre_base_palabras = set(normalizar_nombre(nombre_base).split())
    # Comparamos si todas las palabras de nombre están en el nombre_base
    return nombre_palabras.issubset(nombre_base_palabras)

# Función para buscar coincidencias
def encontrar_similitudes(nombre, base_df):
    coincidencias = []

    for _, row in base_df.iterrows():
        base_nombre = row['nomart']
        if comparar_palabras(nombre, base_nombre):
            coincidencias.append({
                "Nombre_producto_base": base_nombre,
                "Codigo": row['codart']
            })

    if coincidencias:
        return pd.DataFrame(coincidencias)
    else:
        return pd.DataFrame(columns=["Nombre_producto_base", "Codigo"])

# Interfaz de Streamlit
st.title('Buscador de Código de Productos')

uploaded_file = st.file_uploader("Sube un archivo con los nombres de productos", type=["xlsx", "csv"])

if uploaded_file:
    productos_df = pd.read_excel(uploaded_file) if uploaded_file.name.endswith('xlsx') else pd.read_csv(uploaded_file)

    if 'nombre' in productos_df.columns:
        base_df = load_base()

        if 'nomart' in base_df.columns and 'codart' in base_df.columns:
            resultados = []
            for nombre in productos_df['nombre']:
                similitudes_df = encontrar_similitudes(nombre, base_df)
                if not similitudes_df.empty:
                    mejor_coincidencia = similitudes_df.iloc[0]
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

            resultados_df = pd.DataFrame(resultados)
            st.write("Resultados de la búsqueda:")
            st.dataframe(resultados_df)

            # Descargar resultados como Excel
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

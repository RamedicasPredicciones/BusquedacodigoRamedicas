import streamlit as st
import pandas as pd
from io import BytesIO
from fuzzywuzzy import fuzz
from collections import Counter

# Función para cargar la base desde Google Sheets
def load_base():
    base_url = "https://docs.google.com/spreadsheets/d/1Y9SgliayP_J5Vi2SdtZmGxKWwf1iY7ma/export?format=xlsx"
    base_df = pd.read_excel(base_url, sheet_name="Hoja1", engine='openpyxl')
    base_df.columns = base_df.columns.str.lower().str.strip()  # Asegura que las columnas estén en minúsculas y sin espacios
    return base_df

# Función para comparar listas de palabras (sin importar el orden)
def comparar_palabras(nombre, nombre_base):
    nombre_palabras = set(nombre.lower().split())
    nombre_base_palabras = set(nombre_base.lower().split())
    interseccion = nombre_palabras.intersection(nombre_base_palabras)
    similitud = len(interseccion) / max(len(nombre_palabras), len(nombre_base_palabras)) * 100
    return similitud

# Función para buscar coincidencias
def encontrar_similitudes(nombre, base_df):
    coincidencias = []
    for _, row in base_df.iterrows():
        base_nombre = row['nomart']
        similitud = comparar_palabras(nombre, base_nombre)
        if similitud > 60:  # Ajustar el umbral según necesidad
            coincidencias.append({
                "Nombre_producto_base": base_nombre,
                "Codigo": row['codart'],
                "Similitud": similitud
            })
    return pd.DataFrame(coincidencias).sort_values(by="Similitud", ascending=False) if coincidencias else pd.DataFrame(columns=["Nombre_producto_base", "Codigo", "Similitud"])

# Streamlit UI
st.title('Buscador de Código de Productos')

# Subir archivo con nombres de productos
uploaded_file = st.file_uploader("Sube un archivo con los nombres de productos", type=["xlsx", "csv"])

if uploaded_file:
    # Cargar datos del archivo subido
    try:
        if uploaded_file.name.endswith('xlsx'):
            productos_df = pd.read_excel(uploaded_file, engine='openpyxl')
        else:
            productos_df = pd.read_csv(uploaded_file)
        
        # Verificar la columna 'nombre' en el archivo subido
        if 'nombre' in productos_df.columns:
            base_df = load_base()  # Cargar base de datos desde Google Sheets
            if 'nomart' in base_df.columns and 'codart' in base_df.columns:
                resultados = []
                for nombre in productos_df['nombre']:
                    similitudes_df = encontrar_similitudes(nombre, base_df)
                    if not similitudes_df.empty:
                        mejor_coincidencia = similitudes_df.iloc[0]
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
                
                # Mostrar los resultados en un DataFrame
                resultados_df = pd.DataFrame(resultados)
                st.write("Resultados de la búsqueda:")
                st.dataframe(resultados_df)
                
                # Botón para descargar resultados como Excel
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
    except Exception as e:
        st.error(f"Error al procesar el archivo: {e}")


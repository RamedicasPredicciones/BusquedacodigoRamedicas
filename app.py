import pandas as pd
import re

# Función para cargar la base desde un archivo CSV o Excel
def load_base():
    # Asegúrate de poner el enlace correcto para tu Google Sheet o base de datos
    base_url = "ruta/a/tu/archivo.xlsx"
    base_df = pd.read_excel(base_url, sheet_name="Hoja1")
    return base_df

# Función para limpiar el texto (eliminar caracteres especiales y números)
def clean_text(text):
    text = text.lower()  # Convertir a minúsculas
    text = re.sub(r'[^\w\s]', '', text)  # Eliminar caracteres especiales
    return text

# Función para buscar coincidencias en los productos
def buscar_coincidencias(nombre, base_df):
    # Limpiar el nombre ingresado
    nombre_limpio = clean_text(nombre)
    palabras = nombre_limpio.split()  # Dividir el nombre en palabras
    
    coincidencias = []

    # Iterar sobre los productos en la base de datos
    for _, row in base_df.iterrows():
        base_name = clean_text(row['nomart'])

        # Comprobar que todas las palabras estén en el nombre de la base
        if all(palabra in base_name for palabra in palabras):
            coincidencias.append({
                "Nombre_ingresado": nombre,
                "Nombre_encontrado": row["nomart"],
                "Codigo": row["codart"]
            })
    
    return coincidencias

# Simulación de entrada de productos
productos_df = pd.DataFrame({
    'nombre': ["ACETAMINOFEN + METOCARBAMOL 325MG/400MG TABLETAS RECUBIERTAS"]  # Cambia esto con los productos que tienes
})

# Cargar la base de datos desde el archivo
base_df = load_base()

# Lista para almacenar los resultados
resultados = []

# Buscar coincidencias para cada producto ingresado
for nombre in productos_df['nombre']:
    coincidencias = buscar_coincidencias(nombre, base_df)
    if coincidencias:
        resultados.extend(coincidencias)
    else:
        resultados.append({
            "Nombre_ingresado": nombre,
            "Nombre_encontrado": "No encontrado",
            "Codigo": "No disponible"
        })

# Mostrar los resultados
resultados_df = pd.DataFrame(resultados)
print(resultados_df)

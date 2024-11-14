import pandas as pd

# URL de tu archivo de Google Sheets (modificado para exportar como xlsx)
base_url = "https://docs.google.com/spreadsheets/d/1WV4la88gTl6OUgqQ5UM0IztNBn_k4VrC/export?format=xlsx"

# Cargar la base de datos
base_df = pd.read_excel(base_url)

# Verificar las columnas para encontrar el nombre correcto
print("Columnas disponibles:")
print(base_df.columns)

# Función para buscar el producto ingresado en la base de datos
def buscar_producto(producto_ingresado, base_df):
    # Dividir el nombre del producto ingresado en palabras clave
    palabras = producto_ingresado.split()  # Divide por espacios

    # Filtrar filas que contienen todas las palabras del producto ingresado
    productos_encontrados = []

    for index, row in base_df.iterrows():
        # Cambiar 'Producto' por el nombre correcto de la columna
        nombre_producto_base = str(row['Producto'])  # Ajustar esta parte

        if all(palabra.lower() in nombre_producto_base.lower() for palabra in palabras):
            productos_encontrados.append(nombre_producto_base)
    
    return productos_encontrados

# Ejemplo de búsqueda
producto_ingresado = "ACETAMINOFEN + METOCARBAMOL 325MG/400MG TABLETAS RECUBIERTAS"
productos_encontrados = buscar_producto(producto_ingresado, base_df)

# Mostrar los productos encontrados
print("Productos encontrados:")
print(productos_encontrados)

import pandas as pd
import re

# Función para cargar el archivo desde Google Drive
def load_base():
    # URL de Google Drive para descargar el archivo
    base_url = "https://docs.google.com/spreadsheets/d/1WV4la88gTl6OUgqQ5UM0IztNBn_k4VrC/export?format=xlsx"
    
    try:
        # Intentamos cargar el archivo Excel desde la URL proporcionada
        base_df = pd.read_excel(base_url)
        # Imprimir las columnas disponibles para inspección
        print(base_df.columns)  # Esto mostrará las columnas del archivo
        return base_df
    except Exception as e:
        print(f"Error al cargar el archivo: {e}")
        return None

# Función para buscar las palabras clave en el nombre del producto
def buscar_producto(producto_ingresado, base_df):
    # Separar las palabras clave del nombre ingresado
    palabras_ingresadas = producto_ingresado.split()

    # Resultado de coincidencias
    resultados = []

    # Iteramos sobre los productos en la base de datos
    for index, row in base_df.iterrows():
        # Ajusta el nombre de la columna aquí si es necesario
        nombre_producto_base = row['Producto']  # Cambiar 'Producto' según la columna correcta
        coincidencias = 0

        # Comprobar cada palabra ingresada en el nombre del producto de la base de datos
        for palabra in palabras_ingresadas:
            if re.search(r'\b' + re.escape(palabra) + r'\b', nombre_producto_base, re.IGNORECASE):
                coincidencias += 1

        # Si encontramos todas las palabras en el nombre, lo añadimos a los resultados
        if coincidencias == len(palabras_ingresadas):
            resultados.append(row)

    return resultados

# Función principal
def main():
    # Cargar la base de datos
    base_df = load_base()

    if base_df is not None:
        # Solicitar al usuario el nombre del producto a buscar
        producto_ingresado = "ACETAMINOFEN + METOCARBAMOL 325MG/400MG TABLETAS RECUBIERTAS"  # Aquí va el nombre que quieres buscar

        # Buscar el producto
        productos_encontrados = buscar_producto(producto_ingresado, base_df)

        # Imprimir resultados
        if productos_encontrados:
            print("Productos encontrados:")
            for producto in productos_encontrados:
                print(producto)
        else:
            print("No se encontraron productos que coincidan.")
    else:
        print("No se pudo cargar el archivo de la base de datos.")

# Ejecutar el código
if __name__ == "__main__":
    main()

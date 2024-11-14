import pandas as pd
import gspread
from fuzzywuzzy import fuzz, process
from oauth2client.service_account import ServiceAccountCredentials

# Configurar el acceso a Google Sheets
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive.file", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name('ruta_a_tu_credencial.json', scope)
client = gspread.authorize(creds)

# Cargar la base de datos de Google Sheets
sheet = client.open_by_url("https://docs.google.com/spreadsheets/d/1Y9SgliayP_J5Vi2SdtZmGxKWwf1iY7ma/edit?usp=sharing")
worksheet = sheet.get_worksheet(0)  # Selecciona la primera hoja
data_base = pd.DataFrame(worksheet.get_all_records())

# Subir el archivo con productos a buscar
archivo_usuario = pd.read_csv('archivo_usuario.csv')  # Asegúrate de que tiene columnas 'nombre' y 'Embalaje'

# Función para buscar coincidencias de nombres con tolerancia a diferencias en palabras y orden
def buscar_producto(nombre_producto, data_base):
    mejores_coincidencias = []
    for _, row in data_base.iterrows():
        base_producto = row['nombre_producto_base']
        score = fuzz.token_set_ratio(nombre_producto, base_producto)
        if score > 70:  # Ajusta el umbral de coincidencia si es necesario
            mejores_coincidencias.append((row['codigo'], base_producto, score))
    mejores_coincidencias = sorted(mejores_coincidencias, key=lambda x: x[2], reverse=True)
    return mejores_coincidencias[0] if mejores_coincidencias else (None, None, None)

# Buscar coincidencias para cada producto en el archivo del usuario
resultados = []
for _, row in archivo_usuario.iterrows():
    nombre = row['nombre']
    embalaje = row['Embalaje']
    codigo, nombre_base, score = buscar_producto(nombre, data_base)
    resultados.append({'nombre': nombre, 'Embalaje': embalaje, 'codigo_encontrado': codigo, 'nombre_base': nombre_base, 'similaridad': score})

# Crear un DataFrame con los resultados
df_resultados = pd.DataFrame(resultados)

# Guardar los resultados
df_resultados.to_csv('resultados_busqueda.csv', index=False)
print("Búsqueda completada. Los resultados se guardaron en 'resultados_busqueda.csv'.")

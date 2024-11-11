import sqlite3
import pandas as pd
import io
from pdfcreate import generar_reporte_pdf  # Importar la función para generar el PDF desde un módulo externo
import re
from io import BytesIO

def estructurar_datos(df):
    # Hacer una copia explícita del DataFrame original para evitar SettingWithCopyWarning
    df = df.copy()
    
    # Generar la columna "No." con asterisco si la columna "PATRON" es 1
    df.insert(0, "No.", range(1, len(df) + 1))  # Insertar la columna "No." al inicio
    df['No.'] = df['No.'].astype(str)  # Convertir "No." a str
    df.loc[:, 'No.'] = df.apply(lambda x: f"{x['No.']}*" if x['PATRON'] == 1 else x['No.'], axis=1)

    # Formatear la fecha al formato DD/MM/YYYY
    df.loc[:, 'Fecha'] = pd.to_datetime(df['Fecha'], format='%d-%m-%y', errors='coerce').dt.strftime('%d/%m/%Y')

    # Crear la columna "Fallas" con los nombres de columnas concatenados que tengan "Si"
    columnas_fallas = ["WNPH", "ASN", "IntCor", "ExtCor", "AB", "NC", "IP", "EP", "AP", "FD", "DG", "Otro"]
    df.loc[:, 'Fallas'] = df[columnas_fallas].apply(lambda x: ' '.join(x.index[x == "Si"]), axis=1)

    # Función para agregar saltos de línea en el espacio más cercano cada 20 caracteres
    def agregar_saltos_linea(texto, max_length=20):
        if len(texto) > max_length:
            # Dividir el texto en bloques de hasta `max_length` caracteres usando expresiones regulares
            return '\n'.join(re.findall(r'.{1,' + str(max_length) + r'}(?:\s|$)', texto))
        else:
            return texto

    # Aplicar la función para dividir el texto en la columna "Fallas"
    df.loc[:, 'Fallas'] = df['Fallas'].apply(lambda x: agregar_saltos_linea(x))

    # Seleccionar y reordenar las columnas en el orden adecuado para el reporte
    columnas_finales = [
        "No.", "Fecha", "Codigo", "Prueba", "Operador", "Tiempo", "SN", "GasSVC", "Fabricante",
        "FechaFab", "Cliente", "Dimension", "PObjetivo", "PPico", "PPromedio", "TiempoEspera",
        "Disposicion", "Fallas"
    ]
    df = df[columnas_finales]

    return df

def export_filtered_historial_to_pdf(db_file, start_date, end_date, cancel_flag=None):
    try:
        # Conectar a la base de datos SQLite
        conn = sqlite3.connect(db_file)
        
        # Verificar si la tabla "Historial" existe en la base de datos
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='Historial';")
        table_exists = cursor.fetchone()
        
        if not table_exists:
            print("La tabla 'Historial' no existe en la base de datos.")
            conn.close()
            return 1  # Código de retorno para indicar que la tabla no existe

        # Comprobar si se ha solicitado la cancelación
        if cancel_flag and cancel_flag():
            conn.close()
            print("Proceso cancelado por el usuario.")
            return 5  # Código de retorno para indicar cancelación por el usuario

        # Leer la tabla "Historial" en un DataFrame de Pandas
        query = """
        SELECT Fecha, Codigo, Prueba, Operador, Tiempo, SN, GasSVC, Fabricante, FechaFab,
               Cliente, Dimension, PObjetivo, PPico, PPromedio, TiempoEspera, Disposicion, WNPH,	
               ASN,	IntCor,	ExtCor,	AB,	NC,	IP,	EP,	AP,	FD,	DG,	Otro, PATRON
        FROM 'Historial' WHERE Fecha != '';
        """
        df = pd.read_sql_query(query, conn)
        
        # Comprobar de nuevo la cancelación
        if cancel_flag and cancel_flag():
            conn.close()
            print("Proceso cancelado por el usuario.")
            return 5  # Código de retorno para indicar cancelación por el usuario

        # Cerrar la conexión a la base de datos
        conn.close()

        # Verificar si el DataFrame está vacío
        if df.empty:
            print("No existe información en el archivo de la base de datos.")
            return 2  # Código de retorno para indicar que no hay información

        # Convertir las fechas al formato YYYYMMDD 
        df['Fecha_convertida'] = pd.to_datetime(df['Fecha'], format='%d-%m-%y', errors='coerce').dt.strftime('%Y%m%d')

        # Verificar si la conversión de fechas ha fallado
        if df['Fecha_convertida'].isnull().all():
            print("La conversión de fechas falló.")
            return 3  # Código de retorno para indicar error en la conversión de fechas

        # Filtrar el DataFrame según el rango de fechas
        filtered_df = df[(df['Fecha_convertida'] >= start_date) & (df['Fecha_convertida'] <= end_date)]

        # Verificar la cancelación antes de continuar
        if cancel_flag and cancel_flag():
            print("Proceso cancelado por el usuario.")
            return 5  # Código de retorno para indicar cancelación por el usuario

        # Verificar si el DataFrame filtrado está vacío
        if filtered_df.empty:
            print("No se encontraron registros en el rango de fechas y condiciones proporcionadas.")
            return 4  # Código de retorno para indicar que no hay registros en el rango

        # Estructurar los datos para el formato de salida
        structured_data = estructurar_datos(filtered_df)

        # Comprobar la cancelación antes de generar el PDF
        if cancel_flag and cancel_flag():
            print("Proceso cancelado por el usuario antes de generar el PDF.")
            return 5  # Código de retorno para indicar cancelación por el usuario

        # Convertir el DataFrame estructurado a una lista de listas
        data = structured_data.values.tolist()
        # Generar el PDF usando la función `generar_reporte_pdf`
        pdf_content = generar_reporte_pdf(data, start_date, end_date)

        return pdf_content  # Retornar el contenido del PDF

    except Exception as e:
        # Manejar cualquier error inesperado
        print(f"Error al exportar la tabla 'Historial': {e}")
        return 6  # Código de retorno para indicar un error inesperado

# Bloque principal de ejecución
if __name__ == '__main__':
    db_file = 'dbproof/Historial.db'  # Ruta al archivo de base de datos SQLite
    start_date = input("Ingresa la fecha de inicio (YYYYMMDD): ")  # Solicitar al usuario la fecha de inicio
    end_date = input("Ingresa la fecha de fin (YYYYMMDD): ")  # Solicitar al usuario la fecha de fin

    # Llamar a la función para exportar los datos filtrados y generar el PDF
    pdf_content = export_filtered_historial_to_pdf(db_file, start_date, end_date)

    # Verificar si el contenido del PDF es de tipo `bytes` y convertirlo a `BytesIO` si es necesario
    if isinstance(pdf_content, bytes):
        pdf_content = io.BytesIO(pdf_content)
    # Verificar el resultado y mostrar el mensaje adecuado al usuario
    if isinstance(pdf_content, io.BytesIO):
        # Guardar el PDF en un archivo local
        with open('reporte_generado.pdf', 'wb') as f:
            f.write(pdf_content.getvalue())
        print("PDF generado en memoria y guardado como 'reporte_generado.pdf'.")
    elif pdf_content == 1:
        print("La tabla 'Historial' no existe en la base de datos.")
    elif pdf_content == 2:
        print("No existe información en el archivo de la base de datos.")
    elif pdf_content == 3:
        print("La conversión de fechas falló.")
    elif pdf_content == 4:
        print("No se encontraron registros en el rango de fechas y condiciones proporcionadas.")
    elif pdf_content == 5:
        print("Proceso cancelado por el usuario.")
    elif pdf_content == 6:
        print("Hubo un error inesperado al generar el PDF.")

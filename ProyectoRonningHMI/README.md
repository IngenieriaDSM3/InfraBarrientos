
# Conversor de Datos de Pruebas de Presión

Este proyecto es un software diseñado para Infra de México, cuyo objetivo es convertir los datos extraídos de un HMI (Human-Machine Interface) de un equipo de pruebas de presión. El sistema permite cargar un archivo de base de datos SQLite, filtrar datos por rango de fechas y exportar los resultados en un archivo PDF con formato estructurado.

## Descripción del Proyecto

El software incluye las siguientes funcionalidades:
- Interfaz gráfica de usuario (GUI) desarrollada con PyQt5.
- Carga de archivos de base de datos SQLite para la lectura de datos históricos.
- Filtrado de registros basados en fechas específicas.
- Exportación de los resultados a un archivo PDF con un diseño personalizado.
- Soporte para la cancelación del proceso durante la generación del PDF.
- Verificación y validación de los datos de entrada, incluyendo el nombre del archivo de salida.

## Dependencias

Las dependencias necesarias para ejecutar este proyecto se encuentran en el archivo `requirements.txt` y se pueden instalar con:

```bash
pip install -r requirements.txt
```

## Instrucciones de Uso

1. Ejecute el archivo principal del programa para iniciar la interfaz gráfica.
2. Seleccione el archivo de base de datos .db a procesar.
3. Elija un rango de fechas para filtrar los registros.
4. Asigne un nombre al archivo de salida.
5. Haga clic en el botón `Exportar` para generar el archivo PDF.
6. Si es necesario, puede cancelar el proceso durante la generación del PDF.

## Contacto

Para más información o soporte, por favor contacte al desarrollador o al equipo de soporte de Infra de México.

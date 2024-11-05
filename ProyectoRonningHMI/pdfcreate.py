from reportlab.lib.pagesizes import letter, landscape
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, PageBreak, Spacer, Image
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase import pdfmetrics
from reportlab.lib.enums import TA_JUSTIFY
from datetime import datetime
from io import BytesIO

# Registrar la fuente Calibri para su uso en el PDF
pdfmetrics.registerFont(TTFont('Calibri', 'font/calibri.ttf'))  # Reemplaza con la ruta a tu archivo .ttf

def generar_reporte_pdf(data, fecha_inicio, fecha_fin):
    # Crear un buffer de memoria para el contenido del PDF
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=landscape(letter))  # Configurar el documento en formato horizontal (landscape)

    # Crear estilos personalizados de texto con la fuente Calibri
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(name='CustomTitle', fontName='Calibri', fontSize=16, alignment=1, spaceAfter=12))
    styles.add(ParagraphStyle(name='SubTitle', fontName='Calibri', fontSize=12, alignment=1, spaceAfter=10))
    styles.add(ParagraphStyle(name='JustifiedSubTitle', fontName='Calibri', fontSize=12, alignment=TA_JUSTIFY, spaceAfter=10))

    # Función para formatear la fecha de "YYYYMMDD" a "dd-mm-yyyy"
    def formatear_fecha(fecha_str):
        fecha = datetime.strptime(fecha_str, "%Y%m%d")
        return fecha.strftime("%d-%m-%Y")

    # Convertir las fechas de inicio y fin al formato deseado
    fecha_inicio_formateada = formatear_fecha(fecha_inicio)
    fecha_fin_formateada = formatear_fecha(fecha_fin)

    # Definir el encabezado de la tabla
    encabezado = [
        ['No.', 'Fecha', 'Código', 'Prueba', 'Operador', 'Tiempo', 'Número de \nserie', 'Gas',
         'Fabricante', 'Fecha de \nfabricación', 'Cliente', 'Dimensión', 'Presión \nObjetivo \n(psi)',
         'Presión \nPico \n(psi)', 'Presión \nPromedio \n(psi)', 'Tiempo de \nespera', 'Disposición', 'Fallas']
    ]

    # Combinar el encabezado con los datos proporcionados
    data_completa = encabezado + data

    # Contar el número de pruebas en los datos
    numero_pruebas = len(data)  # Contar solo las filas de datos, no el encabezado

    # Crear un subtítulo con las fechas de inicio y fin, y el número de pruebas
    subtitulo = (f"Este reporte detalla las pruebas realizadas recientes del "
                 f"{fecha_inicio_formateada} al {fecha_fin_formateada}."
                 f"<br/>El número de pruebas realizadas fue de {numero_pruebas}.")

    # Función para agregar encabezado y pie de página con un logo y número de página
    def agregar_encabezado_pie_pagina(canvas, doc):
        canvas.saveState()
        
        # Ruta de la imagen del logo
        ruta_icono = 'figure/logo-infra.png'  # Reemplaza con la ruta a tu archivo de imagen
        
        # Obtener dimensiones originales de la imagen para escalarla proporcionalmente
        imagen = Image(ruta_icono)
        imagen_width, imagen_height = imagen.wrap(0, 0)
        
        # Escalar la imagen para que mantenga la proporción
        max_width = 100  # Ancho máximo permitido
        scale_ratio = max_width / imagen_width
        scaled_width = imagen_width * scale_ratio
        scaled_height = imagen_height * scale_ratio
        
        # Dibujar la imagen en la parte superior derecha del documento
        canvas.drawImage(ruta_icono, x=doc.pagesize[0] - scaled_width - 30, y=doc.pagesize[1] - scaled_height - 20,
                        width=scaled_width, height=scaled_height, preserveAspectRatio=True, mask='auto')
        
        # Agregar texto al encabezado
        canvas.setFont('Calibri', 12)
        canvas.drawString(90, doc.pagesize[1] - 50, "Reporte de pruebas de presión")
        
        # Agregar número de página
        pagina = f"Página {doc.page}"
        canvas.setFont('Calibri', 10)
        canvas.drawString(750, 20, pagina)  # Posición ajustada para una página en orientación horizontal
        
        canvas.restoreState()

   # Definir el estilo de la tabla con estilos específicos para el encabezado
    estilo_tabla = TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),  # Color de fondo para el encabezado
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),  # Color del texto en el encabezado
        ('ALIGN', (0, 0), (-1, 0), 'CENTER'),  # Alineación centrada en el encabezado
        ('VALIGN', (0, 0), (-1, 0), 'MIDDLE'),  # Alineación vertical centrada en el encabezado
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),  # Fuente negrita para el encabezado
        ('FONTSIZE', (0, 0), (-1, 0), 6),  # Tamaño de fuente para el encabezado
        ('BOTTOMPADDING', (0, 0), (-1, 0), 4),  # Espaciado inferior en el encabezado
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),  # Color de fondo para las celdas de datos
        ('FONTNAME', (0, 1), (-1, -1), 'Calibri'),  # Fuente Calibri para las celdas de datos
        ('FONTSIZE', (0, 1), (-1, -1), 6),  # Tamaño de fuente para las celdas de datos
        ('ALIGN', (0, 1), (-1, -1), 'CENTER'),  # Alineación centrada en las celdas de datos
        ('VALIGN', (0, 1), (-1, -1), 'MIDDLE'),  # Alineación vertical centrada en las celdas de datos
        ('GRID', (0, 0), (-1, -1), 0.5, colors.black),  # Líneas de la tabla
        ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),  # Color de texto en las celdas de datos
        ('WORDWRAP', (0, 0), (-1, -1)),  # Ajuste de texto para todas las celdas
    ])

    # Definir anchos de columna en puntos (1 cm = 28.35 puntos)
    column_widths = [
        1 * 28.35,  # No.
        1.3 * 28.35,  # Fecha
        1.1 * 28.35,  # Código
        1.2 * 28.35,  # Prueba
        1.9 * 28.35,  # Operador
        1.27 * 28.35,  # Tiempo
        1.4 * 28.35,  # Número de serie
        1.15 * 28.35,  # Gas
        1.88 * 28.35,  # Fabricante
        1.4 * 28.35,  # Fecha de fabricación
        1.23 * 28.35,  # Cliente
        1.25 * 28.35,  # Dimensión
        1.25 * 28.35,  # Presión Objetivo (psi)
        1.25 * 28.35,  # Presión Pico (psi)
        1.4 * 28.35,  # Presión Promedio (psi)
        1.5 * 28.35,  # Tiempo de espera
        1.3 * 28.35,  # Disposición
        3 * 28.35,  # Fallas
    ]

    # Definir alturas de filas para encabezado y celdas de datos
    altura_encabezado = 1.5 * 28.35
    altura_filas = 1.8 * 28.35

    # Lista para agregar los elementos del PDF
    elementos = []
    elementos.append(Paragraph("Reporte de Pruebas en equipo Rönning", styles['CustomTitle']))
    elementos.append(Paragraph(subtitulo, styles['JustifiedSubTitle']))
    elementos.append(Spacer(1, 12))  # Espacio entre el título y la tabla

    current_data = []  # Lista temporal para las filas actuales

    # Número de filas por página
    filas_por_primera_pagina = 7
    filas_por_pagina = 9
    pagina_actual = 1  # Contador de la página actual

    for i, fila in enumerate(data_completa):
        current_data.append(fila)

        # Verificar si se debe agregar una tabla a la lista de elementos
        if (pagina_actual == 1 and len(current_data) == filas_por_primera_pagina) or \
        (pagina_actual > 1 and len(current_data) % filas_por_pagina == 0) or \
        (i == len(data_completa) - 1):  # Última fila de los datos

            # Crear la tabla con las alturas de filas especificadas
            row_heights = [altura_encabezado] + [altura_filas] * (len(current_data) - 1)
            sub_tabla = Table(current_data, colWidths=column_widths, rowHeights=row_heights)
            sub_tabla.setStyle(estilo_tabla)
            
            # Aplicar estilo condicional para resaltar filas con asterisco en la columna "No."
            for row_index, fila in enumerate(current_data):
                if '*' in str(fila[0]):  # Verificar si hay un asterisco en la celda
                    sub_tabla.setStyle(TableStyle([('BACKGROUND', (0, row_index), (-1, row_index), colors.orange)]))

            sub_tabla.hAlign = 'CENTER'
            
            # Agregar la tabla y un salto de página
            elementos.append(sub_tabla)
            elementos.append(PageBreak())
            
            # Reiniciar `current_data` con el encabezado para la siguiente página si hay más filas
            if i != len(data_completa) - 1:
                current_data = encabezado.copy()
                pagina_actual += 1  # Incrementar el contador de la página

    # Construir el documento PDF con la función de encabezado/pie de página
    doc.build(elementos, onFirstPage=agregar_encabezado_pie_pagina, onLaterPages=agregar_encabezado_pie_pagina)

    # Retornar el contenido del PDF desde el buffer
    buffer.seek(0)
    return buffer.getvalue()

if __name__ == "__main__":
    # Datos de ejemplo con y sin asterisco
    data = [
        ['1*', '2024-01-01', 'ABC123', 'Prueba 1', 'Operador 1', '10:00', '123456', 'Gas X',
         'Fabricante Y', '2023-12-01', 'Cliente Z', '10x10', '150', '155', '152', '5 min', 'OK', 'Ninguna'],
        ['2', '2024-01-02', 'DEF456', 'Prueba 2', 'Operador 2', '11:00', '654321', 'Gas Y',
         'Fabricante X', '2023-11-15', 'Cliente A', '15x15', '160', '165', '162', '6 min', 'OK', 'Ninguna'],
        # ... más filas de ejemplo ...
    ]

    fecha_inicio = "20240101"
    fecha_fin = "20241231"

    pdf_content = generar_reporte_pdf(data, fecha_inicio, fecha_fin)

    # Guardar el PDF en un archivo
    with open("reporte_generado.pdf", "wb") as f:
        f.write(pdf_content)

import os
import sys
from reportlab.lib.pagesizes import letter, landscape
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, PageBreak, Spacer, Image
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase import pdfmetrics
from reportlab.lib.enums import TA_JUSTIFY
from datetime import datetime
from io import BytesIO

# Obtener el directorio base
if getattr(sys, 'frozen', False):
    base_path = sys._MEIPASS
else:
    base_path = os.path.dirname(__file__)

# Actualizar las rutas a los archivos con base_path
font_path = os.path.join(base_path, 'font', 'calibri.ttf')
logo_path = os.path.join(base_path, 'figure', 'logo-infra.png')

print(f"Ruta al archivo de fuente: {font_path}")
print(f"Ruta al logo: {logo_path}")

# Verifica si el archivo de fuente existe
if os.path.exists(font_path):
    print("El archivo de fuente se encontró correctamente.")
else:
    print("El archivo de fuente NO se encontró.")

# Registrar la fuente
pdfmetrics.registerFont(TTFont('Calibri', font_path))

def generar_reporte_pdf(data, fecha_inicio, fecha_fin):
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=landscape(letter))

    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(name='CustomTitle', fontName='Calibri', fontSize=16, alignment=1, spaceAfter=12))
    styles.add(ParagraphStyle(name='SubTitle', fontName='Calibri', fontSize=12, alignment=1, spaceAfter=10))
    styles.add(ParagraphStyle(name='JustifiedSubTitle', fontName='Calibri', fontSize=12, alignment=TA_JUSTIFY, spaceAfter=10))

    def formatear_fecha(fecha_str):
        fecha = datetime.strptime(fecha_str, "%Y%m%d")
        return fecha.strftime("%d-%m-%Y")

    fecha_inicio_formateada = formatear_fecha(fecha_inicio)
    fecha_fin_formateada = formatear_fecha(fecha_fin)

    encabezado = [
        ['No.', 'Fecha', 'Código', 'Prueba', 'Operador', 'Tiempo', 'Número de \nserie', 'Gas',
         'Fabricante', 'Fecha de \nfabricación', 'Cliente', 'Dimensión', 'Presión \nObjetivo \n(psi)',
         'Presión \nPico \n(psi)', 'Presión \nPromedio \n(psi)', 'Tiempo de \nespera', 'Disposición', 'Fallas']
    ]

    data_completa = encabezado + data
    numero_pruebas = len(data)
    
    subtitulo = (f"Este reporte detalla las pruebas realizadas del "
                 f"<u>{fecha_inicio_formateada}</u> al <u>{fecha_fin_formateada}</u>."
                 f"<br/><br/>Número de pruebas realizadas: <u>{numero_pruebas}</u>.")


    def agregar_encabezado_pie_pagina(canvas, doc):
        canvas.saveState()
        
        if os.path.exists(logo_path):
            imagen = Image(logo_path)
            imagen_width, imagen_height = imagen.wrap(0, 0)
            max_width = 100
            scale_ratio = max_width / imagen_width
            scaled_width = imagen_width * scale_ratio
            scaled_height = imagen_height * scale_ratio
            canvas.drawImage(logo_path, x=doc.pagesize[0] - scaled_width - 30, y=doc.pagesize[1] - scaled_height - 20,
                            width=scaled_width, height=scaled_height, preserveAspectRatio=True, mask='auto')
        
        # Agregar texto al encabezado
        canvas.setFont('Calibri', 12)
        canvas.drawString(90, doc.pagesize[1] - 50, "Reporte de pruebas de presión")
        
        # Agregar número de página
        pagina = f"Página {doc.page}"
        canvas.setFont('Calibri', 10)
        canvas.drawString(750, 20, pagina)

        # Agregar pie de página en la parte inferior derecha
        #canvas.setFont('Calibri', 10)
        #canvas.drawString(30, 20, "* Prueba de calibración")

        canvas.restoreState()


    estilo_tabla = TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
        ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
        ('VALIGN', (0, 0), (-1, 0), 'MIDDLE'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 6),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 4),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('FONTNAME', (0, 1), (-1, -1), 'Calibri'),
        ('FONTSIZE', (0, 1), (-1, -1), 6),
        ('ALIGN', (0, 1), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 1), (-1, -1), 'MIDDLE'),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
        ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
        ('WORDWRAP', (0, 0), (-1, -1)),
    ])

    column_widths = [
        0.8 * 28.35, 1.3 * 28.35, 1.1 * 28.35, 1.4 * 28.35, 2.1 * 28.35,
        1.27 * 28.35, 1.6 * 28.35, 1.15 * 28.35, 2.1 * 28.35, 1.3 * 28.35,
        1.35 * 28.35, 1.25 * 28.35, 1.25 * 28.35, 1.25 * 28.35, 1.4 * 28.35,
        1.9 * 28.35, 1.3 * 28.35, 2.7 * 28.35,
    ]

    altura_encabezado = 1.5 * 28.35
    altura_filas = 1.8 * 28.35

    elementos = []
    elementos.append(Paragraph("Reporte de pruebas en equipo Rönning", styles['CustomTitle']))
    elementos.append(Paragraph(subtitulo, styles['JustifiedSubTitle']))
    elementos.append(Spacer(1, 12))

    current_data = []
    filas_por_primera_pagina = 7
    filas_por_pagina = 9
    pagina_actual = 1

    for i, fila in enumerate(data_completa):
        current_data.append(fila)
        if (pagina_actual == 1 and len(current_data) == filas_por_primera_pagina) or \
           (pagina_actual > 1 and len(current_data) % filas_por_pagina == 0) or \
           (i == len(data_completa) - 1):
            row_heights = [altura_encabezado] + [altura_filas] * (len(current_data) - 1)
            sub_tabla = Table(current_data, colWidths=column_widths, rowHeights=row_heights)
            sub_tabla.setStyle(estilo_tabla)

            for row_index, fila in enumerate(current_data):
                if '*' in str(fila[0]):
                    sub_tabla.setStyle(TableStyle([('BACKGROUND', (0, row_index), (-1, row_index), colors.orange)]))

            sub_tabla.hAlign = 'CENTER'
            elementos.append(sub_tabla)
            elementos.append(PageBreak())

            if i != len(data_completa) - 1:
                current_data = encabezado.copy()
                pagina_actual += 1

    doc.build(elementos, onFirstPage=agregar_encabezado_pie_pagina, onLaterPages=agregar_encabezado_pie_pagina)
    buffer.seek(0)
    return buffer.getvalue()

if __name__ == "__main__":
    data = [
        ['1*', '2024-01-01', 'ABC123', 'Prueba 1', 'Operador 1', '10:00', '123456', 'Gas X',
         'Fabricante Y', '2023-12-01', 'Cliente Z', '10x10', '150', '155', '152', '5 min', 'OK', 'Ninguna'],
        ['2', '2024-01-02', 'DEF456', 'Prueba 2', 'Operador 2', '11:00', '654321', 'Gas Y',
         'Fabricante X', '2023-11-15', 'Cliente A', '15x15', '160', '165', '162', '6 min', 'OK', 'Ninguna'],
    ]

    fecha_inicio = "20240101"
    fecha_fin = "20241231"

    pdf_content = generar_reporte_pdf(data, fecha_inicio, fecha_fin)

    with open("reporte_generado.pdf", "wb") as f:
        f.write(pdf_content)

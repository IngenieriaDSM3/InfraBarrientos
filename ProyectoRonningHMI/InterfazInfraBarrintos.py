import sys
import os
import re
from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QLineEdit, QPushButton,
    QFileDialog, QDateEdit, QMessageBox, QProgressDialog
)
from PyQt5.QtGui import QFont, QPixmap, QIcon
from PyQt5.QtCore import Qt, QDate, QTimer, QThread, pyqtSlot, pyqtSignal
from conversor import export_filtered_historial_to_pdf  # Actualiza con el nombre de tu módulo
import io

class ConversionThread(QThread):
    # Señal para emitir el resultado al final de la conversión
    resultado_signal = pyqtSignal(object)

    def __init__(self, archivo, start_date, end_date, cancel_flag):
        super().__init__()
        self.archivo = archivo
        self.start_date = start_date
        self.end_date = end_date
        self.cancel_flag = cancel_flag  # Guardar la referencia a la función de cancelación
        self.cancelado = False  # Indicar si el proceso ha sido cancelado

    def run(self):
        if not self.cancelado:
            # Llamar a la función de exportación y pasar la función de cancelación
            resultado = io.BytesIO(export_filtered_historial_to_pdf(self.archivo, self.start_date, self.end_date, cancel_flag=self.cancel_flag))
            self.resultado_signal.emit(resultado)  # Emitir el resultado al finalizar

    def cancelar(self):
        # Marcar el proceso como cancelado
        self.cancelado = True

class SplashScreen(QWidget):
    def __init__(self):
        super().__init__()
        self.setFixedSize(850, 480)
        self.setWindowFlags(Qt.FramelessWindowHint)  # Eliminar los bordes de la ventana

        # Configuración de la imagen de fondo para el splash screen
        pixmap = QPixmap("figure/Open.jpg")  # Reemplazar con la ruta a la imagen de splash
        label = QLabel(self)
        label.setPixmap(pixmap)
        label.setScaledContents(True)  # Ajustar la imagen al tamaño del QLabel
        label.setGeometry(0, 0, 850, 480)

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Registro de datos de pruebas en cilindro")
        self.setFixedSize(850, 480)  # Establecer tamaño fijo de la ventana
        self.setWindowIcon(QIcon("figure/app-icon.png"))  # Establecer ícono de la ventana

        self.thread_conversion = None  # Inicializar el hilo de conversión

        # Panel superior con título e imagen de fondo
        panel_superior = QLabel(self)
        panel_superior.setGeometry(0, 9, 850, 60)
        panel_superior.setStyleSheet("background-color: #364E6C;")  # Color de fondo

        # Etiqueta de título en el panel superior
        label_titulo = QLabel("Registro de datos de pruebas en cilindro", self)
        label_titulo.setFont(QFont("Calibri", 24, QFont.Bold))
        label_titulo.setStyleSheet("color: white;")
        label_titulo.setGeometry(126, 9, 600, 60)
        label_titulo.setAlignment(Qt.AlignCenter)

        # Imagen del logo en el panel superior
        imagen_logo_infra = QLabel(self)
        pixmap_logo = QPixmap("figure/logo-infra.png")  # Ruta a la imagen del logo
        imagen_logo_infra.setPixmap(pixmap_logo)
        imagen_logo_infra.setGeometry(7, 17, 100, 45)
        imagen_logo_infra.setScaledContents(True)

        # Sección de selección de archivo
        label_archivo = QLabel("Seleccione archivo fuente", self)
        font = QFont("Calibri", 14)
        font.setBold(True)
        font.setItalic(True)
        label_archivo.setFont(font)
        label_archivo.setStyleSheet("color: #FF8300;")
        label_archivo.setGeometry(32, 92, 300, 30)

        self.line_edit_archivo = QLineEdit(self)
        self.line_edit_archivo.setGeometry(107, 122, 600, 30)
        self.line_edit_archivo.setPlaceholderText("Ruta del archivo")
        self.line_edit_archivo.setStyleSheet("border: 1px solid #000000;")
        self.line_edit_archivo.setReadOnly(True)  # Campo de solo lectura

        btn_archivo = QPushButton(self)
        btn_archivo.setGeometry(712, 122, 30, 30)
        btn_archivo.setIcon(QIcon("figure/ICONFILES.png"))
        btn_archivo.clicked.connect(self.abrir_archivo)

        # Sección de selección de fechas
        label_fechas = QLabel("Seleccione fechas de prueba", self)
        label_fechas.setFont(font)
        label_fechas.setStyleSheet("color: #FF8300;")
        label_fechas.setGeometry(32, 199, 300, 30)

        label_inicio = QLabel("Inicio", self)
        font.setItalic(True)
        label_inicio.setFont(font)
        label_inicio.setGeometry(151, 229, 120, 30)

        self.date_edit_inicio = QDateEdit(self)
        self.date_edit_inicio.setGeometry(271, 229, 120, 30)
        self.date_edit_inicio.setCalendarPopup(True)  # Mostrar calendario emergente
        self.date_edit_inicio.setDate(QDate.currentDate())
        self.date_edit_inicio.setStyleSheet("border: 1px solid #000000; color: #000000;")
        self.date_edit_inicio.dateChanged.connect(self.actualizar_fecha_min_fin)  # Conectar al método de actualización

        label_fin = QLabel("Fin", self)
        label_fin.setFont(font)
        label_fin.setGeometry(459, 229, 120, 30)

        self.date_edit_fin = QDateEdit(self)
        self.date_edit_fin.setGeometry(579, 229, 120, 30)
        self.date_edit_fin.setCalendarPopup(True)
        self.date_edit_fin.setDate(QDate.currentDate())
        self.date_edit_fin.setStyleSheet("border: 1px solid #000000; color: #000000;")
        self.date_edit_fin.setMinimumDate(self.date_edit_inicio.date())  # Fecha mínima igual a la de inicio

        # Sección para asignar nombre al archivo exportado
        label_nombre = QLabel("Asigne un nombre al archivo", self)
        font.setBold(True)
        font.setItalic(True)
        label_nombre.setFont(font)
        label_nombre.setStyleSheet("color: #FF8300;")
        label_nombre.setGeometry(32, 306, 300, 30)

        self.line_edit_nombre = QLineEdit(self)
        self.line_edit_nombre.setStyleSheet("border: 1px solid #000000;")
        self.line_edit_nombre.setPlaceholderText("nombre")
        self.line_edit_nombre.setGeometry(107, 336, 600, 30)

        # Botón para exportar
        btn_exportar = QPushButton("Exportar", self)
        font.setBold(True)
        btn_exportar.setFont(font)
        btn_exportar.setGeometry(350, 415, 150, 30)
        btn_exportar.setStyleSheet("""
            background-color: #D9D9D9;
            color: #000000;
            border: 1px solid #000000;
            border-radius: 10px;
        """)
        btn_exportar.clicked.connect(self.validar_datos)  # Conectar al método de validación

        # Imagen del logo en el panel inferior
        imagen_logo_caae = QLabel(self)
        pixmap_logo = QPixmap("figure/LOGODSM3.jpeg")  # Ruta al logo
        imagen_logo_caae.setPixmap(pixmap_logo)
        imagen_logo_caae.setGeometry(790, 402, 60, 78)
        imagen_logo_caae.setScaledContents(True)

    def abrir_archivo(self):
        # Método para seleccionar un archivo de base de datos
        archivo, _ = QFileDialog.getOpenFileName(self, "Seleccionar archivo", filter="Database Files (*.db)")
        if archivo:
            if archivo.endswith('.db'):
                self.line_edit_archivo.setText(archivo)
            else:
                self.line_edit_archivo.setText("Archivo no válido. Seleccione un archivo .db")

    def actualizar_fecha_min_fin(self):
        # Actualiza la fecha mínima del campo "Fin" al seleccionar una fecha de inicio
        self.date_edit_fin.setMinimumDate(self.date_edit_inicio.date())

    def validar_datos(self):
        # Verifica los datos antes de iniciar la conversión
        self.proceso_cancelado = False  # Restablecer el flag de cancelación

        # Convertir las fechas a formato numérico
        start_date = self.date_edit_inicio.date().toString("yyyyMMdd")
        end_date = self.date_edit_fin.date().toString("yyyyMMdd")

        # Imprimir las fechas seleccionadas para depuración
        print(f"Fecha de inicio seleccionada (numérica): {start_date}")
        print(f"Fecha de fin seleccionada (numérica): {end_date}")

        # Verificar si el archivo seleccionado existe
        archivo = self.line_edit_archivo.text()
        if not os.path.exists(archivo):
            QMessageBox.critical(self, "Error", "El archivo seleccionado no existe.")
            return

        # Verificar que el nombre del archivo sea válido
        nombre_archivo = self.line_edit_nombre.text()
        if not re.match(r"^[A-Za-z][A-Za-z0-9_ -]*$", nombre_archivo):
            QMessageBox.critical(self, "Error", "El nombre asignado no debe contener caracteres especiales, símbolos ni comenzar con un número.")
            return

        # Mostrar barra de progreso y permitir la cancelación
        self.progress_dialog = QProgressDialog("Convirtiendo archivo a PDF, por favor espere...", "Cancelar", 0, 0, self)
        self.progress_dialog.setWindowModality(Qt.WindowModal)
        self.progress_dialog.setWindowTitle("Proceso en curso")
        self.progress_dialog.canceled.connect(self.cancelar_proceso)  # Conectar al método de cancelación
        self.progress_dialog.setMinimumDuration(0)
        self.progress_dialog.setRange(0, 0)
        self.progress_dialog.show()

        # Función de cancelación
        def cancel_flag():
            return self.proceso_cancelado

        # Crear un nuevo hilo de conversión
        self.thread_conversion = ConversionThread(archivo, start_date, end_date, cancel_flag=cancel_flag)
        self.thread_conversion.resultado_signal.connect(self.proceso_completado)
        self.thread_conversion.start()

    def cancelar_proceso(self):
        # Indicar que el proceso fue cancelado por el usuario
        self.proceso_cancelado = True
        if self.thread_conversion:
            self.thread_conversion.cancelar()
        self.progress_dialog.cancel()
        QMessageBox.information(self, "Proceso cancelado", "La conversión ha sido cancelada por el usuario.")

    @pyqtSlot(object)
    def proceso_completado(self, resultado):
        # Manejar la finalización del proceso de conversión
        self.progress_dialog.canceled.disconnect(self.cancelar_proceso)
        self.progress_dialog.close()

        if self.proceso_cancelado:
            # Si el proceso fue cancelado, no hacer nada más
            self.proceso_cancelado = False  # Restablecer el estado
            return

        if isinstance(resultado, int):
            # Manejar los diferentes códigos de error
            if resultado == 2:
                QMessageBox.warning(self, "Advertencia", "No existe información en la tabla 'Historial' o no hay registros con fechas.")
            elif resultado == 3:
                QMessageBox.critical(self, "Error", "La conversión de fechas falló. Verifique que las fechas en la columna 'Fecha' estén en el formato correcto.")
            elif resultado == 4:
                QMessageBox.warning(self, "Advertencia", "No se encontraron registros en el rango de fechas especificado.")
            elif resultado == 5:
                QMessageBox.information(self, "Proceso cancelado", "El proceso fue cancelado por el usuario.")
            elif resultado == 6:
                QMessageBox.critical(self, "Error", "Hubo un error inesperado durante la conversión.")
            else:
                QMessageBox.critical(self, "Error", "Se produjo un error desconocido.")
        elif resultado:
            # Guardar el archivo PDF si el resultado es válido
            output_path, _ = QFileDialog.getSaveFileName(self, "Guardar archivo como", f"{self.line_edit_nombre.text().strip()}.pdf", "PDF Files (*.pdf)")
            if output_path:
                with open(output_path, 'wb') as f:
                    f.write(resultado.getvalue())
                QMessageBox.information(self, "Éxito", f"El archivo PDF se ha guardado correctamente en {output_path}.")
            else:
                QMessageBox.warning(self, "Advertencia", "No se seleccionó una ubicación para guardar el archivo.")
        else:
            QMessageBox.critical(self, "Error", "Se produjo un error inesperado durante la conversión.")

if __name__ == "__main__":
    app = QApplication(sys.argv)

    # Crear y mostrar el splash screen
    splash = SplashScreen()
    splash.show()

    # Crear una instancia de MainWindow
    main_window = MainWindow()

    # Mostrar MainWindow después de cerrar el splash screen
    QTimer.singleShot(3000, splash.close)
    QTimer.singleShot(3000, main_window.show)

    sys.exit(app.exec_())

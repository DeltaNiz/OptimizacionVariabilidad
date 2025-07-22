from PyQt5.QtWidgets import (
    QMainWindow, QApplication, QWidget, QLabel, QPushButton,
    QLineEdit, QComboBox, QFormLayout, QVBoxLayout, QHBoxLayout,
    QFileDialog, QProgressBar, QMessageBox
)
from PyQt5.QtCore import Qt, QTimer, QThread, pyqtSignal
from PyQt5.QtGui import QCursor
import DatosNF
import time

class CargaDatosWorker(QThread):
    """Worker thread para simular carga de datos sin bloquear la UI"""
    finished = pyqtSignal()  # Señal simple que indica que terminó
    error = pyqtSignal(str)  # Señal para errores
    
    def __init__(self):
        super().__init__()
    
    def run(self):
        try:
            # Simular tiempo mínimo de carga (para mostrar el loader brevemente)
            self.msleep(500)  # Reducido a 0.5 segundos
            
            # Emitir señal de finalización
            self.finished.emit()
            
        except Exception as e:
            # Emitir señal de error
            self.error.emit(str(e))

class SubirArchivos(QMainWindow):
    def __init__(self, ventana_main=None):
        super().__init__()
        self.ventana_main = ventana_main  # Referencia a la ventana Main
        self.init_ui()

    def init_ui(self):
        self.resize(500, 250)  # Aumentar altura para la nueva fila
        self.setWindowTitle("Subir Archivo")

        # Formulario principal
        form_layout = QFormLayout()
        form_layout.setRowWrapPolicy(QFormLayout.DontWrapRows)
        form_layout.setFieldGrowthPolicy(QFormLayout.FieldsStayAtSizeHint)
        form_layout.setFormAlignment(Qt.AlignHCenter | Qt.AlignVCenter)  # Centrar horizontal y verticalmente
        form_layout.setLabelAlignment(Qt.AlignRight)  # Alinear etiquetas a la derecha
        form_layout.setVerticalSpacing(10)  # Espaciado entre filas
        form_layout.setHorizontalSpacing(15)  # Espaciado entre etiquetas y campos

        # Fila 1: Magnitudes I
        labelI_inserte = QLabel("<b>Filtro <i>I</i> :</b>")
        comboI = QComboBox()
        comboI.setFixedWidth(200)  # Controlar ancho del combo
        comboI.addItem("Seleccione una carpeta...")

        # Botón para examinar carpeta
        botonI_examinar = QPushButton("Examinar")
        botonI_examinar.setFixedWidth(80)
        botonI_examinar.setCursor(QCursor(Qt.PointingHandCursor))
        botonI_examinar.setStyleSheet("""
            QPushButton {
                font-size: 12px;
                color: white;
                background-color: #a7c942;
                border: none;
                padding: 5px 10px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #98b83b;
            }
        """)
        
        # Conectar el botón con la función de selección de carpeta
        botonI_examinar.clicked.connect(lambda: self.seleccionar_carpeta('I'))

        # Crear un widget contenedor para combo y botón
        folderI_row = QWidget()
        folderI_row.setFixedWidth(290)  # Controlar ancho total del contenedor
        folderI_row_layout = QHBoxLayout()
        folderI_row_layout.addWidget(comboI)
        folderI_row_layout.addWidget(botonI_examinar)
        folderI_row_layout.setContentsMargins(0,0,0,0)
        folderI_row_layout.setAlignment(Qt.AlignCenter)  # Centrar contenido del HBox
        folderI_row.setLayout(folderI_row_layout)

        form_layout.addRow(labelI_inserte, folderI_row)

        # Guardar referencia al combo para usarlo en la función
        self.combo_I = comboI

        # Fila 2: Magnitudes V
        labelV_inserte = QLabel("<b>Filtro <i>V</i> :</b>")
        comboV = QComboBox()
        comboV.setFixedWidth(200)  # Controlar ancho del combo
        comboV.addItem("Seleccione una carpeta...")

        # Botón para examinar carpeta
        botonV_examinar = QPushButton("Examinar")
        botonV_examinar.setFixedWidth(80)
        botonV_examinar.setCursor(QCursor(Qt.PointingHandCursor))
        botonV_examinar.setStyleSheet("""
            QPushButton {
                font-size: 12px;
                color: white;
                background-color: #a7c942;
                border: none;
                padding: 5px 10px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #98b83b;
            }
        """)
        
        # Conectar el botón con la función de selección de carpeta
        botonV_examinar.clicked.connect(lambda: self.seleccionar_carpeta('V'))

        # Crear un widget contenedor para combo y botón
        folderV_row = QWidget()
        folderV_row.setFixedWidth(290)  # Controlar ancho total del contenedor
        folderV_row_layout = QHBoxLayout()
        folderV_row_layout.addWidget(comboV)
        folderV_row_layout.addWidget(botonV_examinar)
        folderV_row_layout.setContentsMargins(0,0,0,0)
        folderV_row_layout.setAlignment(Qt.AlignCenter)  # Centrar contenido del HBox
        folderV_row.setLayout(folderV_row_layout)

        form_layout.addRow(labelV_inserte, folderV_row)

        # Guardar referencia al combo para usarlo en la función
        self.combo_V = comboV

        # Fila 3: Subir archivo CSV
        label_csv = QLabel("<b>Archivo Mag. (.csv):</b>")
        combo_csv = QComboBox()
        combo_csv.setFixedWidth(200)  # Controlar ancho del combo
        combo_csv.addItem("Seleccione un archivo CSV...")
        
        # Botón para examinar archivo CSV
        boton_csv = QPushButton("Examinar")
        boton_csv.setFixedWidth(80)
        boton_csv.setCursor(QCursor(Qt.PointingHandCursor))
        boton_csv.setStyleSheet("""
            QPushButton {
                font-size: 12px;
                color: white;
                background-color: #a7c942;
                border: none;
                padding: 5px 10px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #98b83b;
            }
        """)
        
        # Conectar el botón con la función de selección de archivo CSV
        boton_csv.clicked.connect(self.seleccionar_archivo_csv)
        
        # Crear un widget contenedor para combo CSV y botón
        csv_row = QWidget()
        csv_row.setFixedWidth(290)  # Controlar ancho total del contenedor
        csv_row_layout = QHBoxLayout()
        csv_row_layout.addWidget(combo_csv)
        csv_row_layout.addWidget(boton_csv)
        csv_row_layout.setContentsMargins(0,0,0,0)
        csv_row_layout.setAlignment(Qt.AlignCenter)  # Centrar contenido del HBox
        csv_row.setLayout(csv_row_layout)
        
        form_layout.addRow(label_csv, csv_row)
        
        # Guardar referencia al combo CSV para usarlo en la función
        self.combo_csv = combo_csv

        # Fila 4: Periodo Máx
        label_periodo_max = QLabel("<b>Periodo Máx:</b>")
        input_max = QLineEdit("3")
        input_max.setFixedWidth(120)  # Controlar ancho del input
        dias_label1 = QLabel("Días")
        max_row = QWidget()
        max_row.setFixedWidth(170)  # Controlar ancho total del contenedor
        max_row_layout = QHBoxLayout()
        max_row_layout.addWidget(input_max)
        max_row_layout.addWidget(dias_label1)
        max_row_layout.setContentsMargins(0,0,0,0)
        max_row_layout.setAlignment(Qt.AlignCenter)  # Centrar contenido del HBox
        max_row.setLayout(max_row_layout)
        form_layout.addRow(label_periodo_max, max_row)
        
        # Guardar referencia al input para usarlo en la función
        self.input_periodo_max = input_max

        # Fila 5: Periodo Min
        label_periodo_min = QLabel("<b>Periodo Min:</b>")
        input_min = QLineEdit("2")
        input_min.setFixedWidth(120)  # Controlar ancho del input
        dias_label2 = QLabel("Días")
        min_row = QWidget()
        min_row.setFixedWidth(170)  # Controlar ancho total del contenedor
        min_row_layout = QHBoxLayout()
        min_row_layout.addWidget(input_min)
        min_row_layout.addWidget(dias_label2)
        min_row_layout.setContentsMargins(0,0,0,0)
        min_row_layout.setAlignment(Qt.AlignCenter)  # Centrar contenido del HBox
        min_row.setLayout(min_row_layout)
        form_layout.addRow(label_periodo_min, min_row)
        
        # Guardar referencia al input para usarlo en la función
        self.input_periodo_min = input_min

        # Fila 6: Step (Saltos)
        label_step = QLabel("<b>Step (Saltos):</b>")
        input_step = QLineEdit("0.1")
        input_step.setFixedWidth(120)  # Controlar ancho del input
        dias_label3 = QLabel("Días")
        step_row = QWidget()
        step_row.setFixedWidth(170)  # Controlar ancho total del contenedor
        step_row_layout = QHBoxLayout()
        step_row_layout.addWidget(input_step)
        step_row_layout.addWidget(dias_label3)
        step_row_layout.setContentsMargins(0,0,0,0)
        step_row_layout.setAlignment(Qt.AlignCenter)  # Centrar contenido del HBox
        step_row.setLayout(step_row_layout)
        form_layout.addRow(label_step, step_row)
        
        # Guardar referencia al input para usarlo en la función
        self.input_step = input_step

        # Agregar separación vertical entre fila 6 y 7
        separador = QLabel("")  # Etiqueta vacía como separador
        separador.setFixedHeight(5)  # Altura del espaciado
        form_layout.addRow(separador)

        # Fila 7: Botón de análisis
        boton = QPushButton("Cargar Datos")

        # al click del botón, se abre la ventana de DatosNF
        boton.clicked.connect(self.abrir_datos_nf)  # Conectar el botón a la función
        boton.setCursor(QCursor(Qt.PointingHandCursor))
        boton.setStyleSheet("""
            QPushButton {
                font-size: 15px;
                color: white;
                font-weight: bold;
                background-color: #a7c942;
                border: none;
                padding: 10px 20px;
                border-radius: 8px;
            }
            QPushButton:hover {
                background-color: #98b83b;
            }
            QPushButton:pressed {
                background-color: #7a9530;
            }
        """)
        
        # Agregar el botón usando addRow con alineación
        form_layout.addRow(boton)
        
        # Obtener el widget del botón y centrarlo
        boton_item = form_layout.itemAt(form_layout.rowCount()-1, QFormLayout.SpanningRole)
        if boton_item:
            boton_item.setAlignment(Qt.AlignCenter)

        # Layout general
        container = QWidget()
        main_layout = QVBoxLayout()
        
        # Crear un widget contenedor para el formulario
        form_container = QWidget()
        form_container.setLayout(form_layout)
        form_container.setFixedWidth(450)  # Ancho fijo para el formulario
        
        main_layout.addWidget(form_container, alignment=Qt.AlignCenter)  # Centrar horizontal y verticalmente
        main_layout.setContentsMargins(20, 20, 20, 20)  # Márgenes alrededor del contenido

        container.setLayout(main_layout)
        self.setCentralWidget(container)
        
        # Crear loader (inicialmente oculto)
        self.crear_loader()

    def crear_loader(self):
        """Crea el widget de loader"""
        # Widget overlay para el loader
        self.loader_widget = QWidget(self)
        self.loader_widget.setStyleSheet("""
            QWidget {
                background-color: rgba(0, 0, 0, 0.7);
            }
        """)
        self.loader_widget.hide()  # Oculto inicialmente
        
        # Layout para centrar el contenido del loader
        loader_layout = QVBoxLayout(self.loader_widget)
        loader_layout.setAlignment(Qt.AlignCenter)
        
        # Etiqueta de texto
        self.loader_label = QLabel("Cargando datos...")
        self.loader_label.setStyleSheet("""
            QLabel {
                color: white;
                font-size: 16px;
                font-weight: bold;
                margin-bottom: 10px;
            }
        """)
        self.loader_label.setAlignment(Qt.AlignCenter)
        
        # Barra de progreso
        self.progress_bar = QProgressBar()
        self.progress_bar.setFixedWidth(300)
        self.progress_bar.setFixedHeight(20)
        self.progress_bar.setRange(0, 0)  # Modo indeterminado
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                border: 2px solid #a7c942;
                border-radius: 10px;
                background-color: white;
                text-align: center;
            }
            QProgressBar::chunk {
                background-color: #a7c942;
                border-radius: 8px;
            }
        """)
        
        loader_layout.addWidget(self.loader_label)
        loader_layout.addWidget(self.progress_bar)
        
        # Posicionar el loader para que cubra toda la ventana
        self.loader_widget.setGeometry(0, 0, self.width(), self.height())

    def resizeEvent(self, event):
        """Redimensionar el loader cuando cambie el tamaño de la ventana"""
        super().resizeEvent(event)
        if hasattr(self, 'loader_widget'):
            self.loader_widget.setGeometry(0, 0, self.width(), self.height())

    def mostrar_loader(self):
        """Muestra el loader"""
        self.loader_widget.show()
        self.loader_widget.raise_()  # Asegurarse de que esté en la parte superior

    def ocultar_loader(self):
        """Oculta el loader"""
        self.loader_widget.hide()

    def seleccionar_carpeta(self, filtro_tipo):
        """Función para abrir el diálogo de selección de carpeta"""
        carpeta_seleccionada = QFileDialog.getExistingDirectory(
            self, 
            f"Seleccionar Carpeta para Filtro {filtro_tipo}", 
            "",  # Directorio inicial (vacío para usar el último usado)
            QFileDialog.ShowDirsOnly
        )
        
        if carpeta_seleccionada:
            # Determinar qué combo actualizar según el tipo de filtro
            if filtro_tipo == 'I':
                combo_target = self.combo_I
            elif filtro_tipo == 'V':
                combo_target = self.combo_V
            else:
                return  # Tipo no reconocido
            
            # Actualizar el combo correspondiente
            combo_target.clear()
            combo_target.addItem(carpeta_seleccionada)
            # Mostrar solo el nombre de la carpeta en el tooltip
            combo_target.setToolTip(carpeta_seleccionada)

    def seleccionar_archivo_csv(self):
        """Función para abrir el diálogo de selección de archivo CSV"""
        archivo_seleccionado = QFileDialog.getOpenFileName(
            self,
            "Seleccionar Archivo CSV",
            "",  # Directorio inicial (vacío para usar el último usado)
            "Archivos CSV (*.csv);;Todos los archivos (*.*)"
        )
        
        if archivo_seleccionado[0]:  # Si se seleccionó un archivo
            # Actualizar el combo con el archivo seleccionado
            self.combo_csv.clear()
            # Mostrar solo el nombre del archivo, no la ruta completa
            nombre_archivo = archivo_seleccionado[0].split('/')[-1]  # Para Unix
            if '\\' in archivo_seleccionado[0]:  # Para Windows
                nombre_archivo = archivo_seleccionado[0].split('\\')[-1]
            
            self.combo_csv.addItem(nombre_archivo)
            # Mostrar la ruta completa en el tooltip
            self.combo_csv.setToolTip(archivo_seleccionado[0])

    def obtener_datos_formulario(self):
        """Recopila todos los datos del formulario en un diccionario"""
        datos = {}
        
        # Obtener carpetas seleccionadas
        if self.combo_I.currentText() != "Seleccione una carpeta...":
            datos['carpeta_filtro_I'] = self.combo_I.currentText()
        
        if self.combo_V.currentText() != "Seleccione una carpeta...":
            datos['carpeta_filtro_V'] = self.combo_V.currentText()
        
        # Obtener archivo CSV seleccionado
        if self.combo_csv.currentText() != "Seleccione un archivo CSV...":
            datos['archivo_csv'] = self.combo_csv.currentText()
            # También incluir la ruta completa si está disponible
            if self.combo_csv.toolTip():
                datos['ruta_completa_csv'] = self.combo_csv.toolTip()
        
        # Obtener valores numéricos
        datos['periodo_max'] = self.input_periodo_max.text()
        datos['periodo_min'] = self.input_periodo_min.text()
        datos['step'] = self.input_step.text()
        
        return datos

    def abrir_datos_nf(self):
        """Función para abrir la ventana de DatosNF con loader"""
        # Recopilar datos del formulario
        self.datos_formulario = self.obtener_datos_formulario()
        
        # Mostrar loader
        self.mostrar_loader()
        
        # Crear y configurar el worker thread
        self.worker = CargaDatosWorker()
        
        # Conectar señales
        self.worker.finished.connect(self.on_carga_completada)
        self.worker.error.connect(self.on_error_carga)
        
        # Iniciar el worker
        self.worker.start()

    def on_carga_completada(self):
        """Se ejecuta cuando la carga de datos se completa exitosamente"""
        try:
            # Actualizar el texto del loader para indicar que se está creando la ventana
            self.loader_label.setText("Procesando datos del CSV...")
            QApplication.processEvents()  # Forzar actualización de UI
            
            # Usar QTimer para permitir que la UI se actualice
            QTimer.singleShot(200, self.crear_ventana_datos)  # Aumentado a 200ms
            
        except Exception as e:
            # Si hay error al crear la ventana, tratarlo como error
            self.on_error_carga(str(e))

    def crear_ventana_datos(self):
        """Crea la ventana DatosNF después de un pequeño delay"""
        try:
            # Actualizar mensaje
            self.loader_label.setText("Creando tabla de datos...")
            QApplication.processEvents()
            
            # Crear un timer que mantenga la animación activa durante la creación
            self.animation_timer = QTimer()
            self.animation_timer.timeout.connect(lambda: QApplication.processEvents())
            self.animation_timer.start(50)  # Procesar eventos cada 50ms
            
            # Crear ventana DatosNF en el hilo principal
            # IMPORTANTE: Esta línea puede tardar mucho con archivos grandes
            self.datos_nf_window = DatosNF.DatosNF(
                datos_formulario=self.datos_formulario,
                ventana_subir=self,
                ventana_main=self.ventana_main
            )
            
            # Detener el timer de animación
            self.animation_timer.stop()
            
            # Mostrar datos en consola para debugging
            self.datos_nf_window.mostrar_datos_formulario()
            
            # Actualizar texto del loader una vez más
            self.loader_label.setText("Preparando interfaz...")
            QApplication.processEvents()
            
            # Usar otro QTimer para mostrar la ventana después de que esté completamente lista
            QTimer.singleShot(300, self.mostrar_ventana_final)  # Aumentado a 300ms
            
        except Exception as e:
            # Asegurarse de detener el timer en caso de error
            if hasattr(self, 'animation_timer'):
                self.animation_timer.stop()
            # Si hay error al crear la ventana, tratarlo como error
            self.on_error_carga(str(e))

    def mostrar_ventana_final(self):
        """Muestra la ventana DatosNF y oculta el loader"""
        try:
            # Actualizar mensaje del loader
            self.loader_label.setText("Mostrando ventana...")
            QApplication.processEvents()
            
            # Mostrar la ventana como modal
            self.datos_nf_window.setWindowModality(Qt.ApplicationModal)
            self.datos_nf_window.show()
            
            # Forzar que la ventana se renderice completamente
            self.datos_nf_window.raise_()
            self.datos_nf_window.activateWindow()
            QApplication.processEvents()
            
            # Ocultar el loader después de mostrar la ventana
            QTimer.singleShot(500, self.ocultar_loader_final)  # Ocultar después de 0.5 segundos
            
        except Exception as e:
            self.on_error_carga(str(e))

    def ocultar_loader_final(self):
        """Oculta el loader y restaura el texto original"""
        self.ocultar_loader()
        self.loader_label.setText("Cargando datos...")  # Restaurar texto original

    def on_error_carga(self, error_msg):
        """Se ejecuta cuando hay un error durante la carga"""
        # Detener timer de animación si existe
        if hasattr(self, 'animation_timer'):
            self.animation_timer.stop()
            
        # Ocultar loader
        self.ocultar_loader()
        
        # Mostrar mensaje de error en consola
        print(f"Error al cargar datos: {error_msg}")
        
        # Mostrar un diálogo de error
        QMessageBox.critical(self, "Error", f"Error al cargar datos:\n{error_msg}")

if __name__ == "__main__":
    app = QApplication([])
    window = SubirArchivos()
    window.show()
    app.exec_()

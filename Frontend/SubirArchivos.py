from PyQt5.QtWidgets import (
    QMainWindow, QApplication, QWidget, QLabel, QPushButton,
    QLineEdit, QComboBox, QFormLayout, QVBoxLayout, QHBoxLayout,
    QFileDialog, QProgressBar, QMessageBox
)
from PyQt5.QtCore import Qt, QTimer, QThread, pyqtSignal
from PyQt5.QtGui import QCursor, QIcon
import DatosNF
import time
import os
import sys

class AppConstants:
    """Constantes centralizadas para la aplicación SubirArchivos"""
    
    # Dimensiones de la ventana
    WINDOW_WIDTH = 480
    WINDOW_HEIGHT = 210
    
    # Anchos de componentes
    COMBO_WIDTH = 200
    BUTTON_WIDTH = 80
    INPUT_WIDTH = 120
    ROW_CONTAINER_WIDTH_LARGE = 290
    ROW_CONTAINER_WIDTH_SMALL = 170
    FORM_CONTAINER_WIDTH = 450
    PROGRESS_BAR_WIDTH = 300
    PROGRESS_BAR_HEIGHT = 20
    
    # Espaciados y márgenes
    VERTICAL_SPACING = 10
    HORIZONTAL_SPACING = 15
    SEPARATOR_HEIGHT = 5
    MAIN_MARGINS = 20
    
    # Colores del tema
    COLOR_VERDE_PRINCIPAL = "#a7c942"
    COLOR_VERDE_HOVER = "#98b83b"
    COLOR_VERDE_PRESSED = "#7a9530"
    
    # Textos de combo por defecto
    COMBO_DEFAULT_FOLDER = "Seleccione una carpeta..."
    COMBO_DEFAULT_CSV = "Seleccione un archivo CSV..."
    
    # Textos de etiquetas
    LABEL_DIAS = "Días"
    LABEL_CARGAR_DATOS = "Cargar Datos"
    LABEL_EXAMINAR = "Examinar"
    
    # Mensajes del loader
    LOADER_CARGANDO = "Cargando datos..."
    LOADER_PROCESANDO = "Procesando datos del CSV..."
    LOADER_CREANDO = "Creando tabla de datos..."
    LOADER_PREPARANDO = "Preparando interfaz..."
    LOADER_MOSTRANDO = "Mostrando ventana..."

class StyleSheets:
    """Estilos CSS centralizados para la aplicación"""
    
    BUTTON_EXAMINAR = f"""
        QPushButton {{
            font-size: 12px;
            color: white;
            background-color: {AppConstants.COLOR_VERDE_PRINCIPAL};
            border: none;
            padding: 5px 10px;
            border-radius: 4px;
        }}
        QPushButton:hover {{
            background-color: {AppConstants.COLOR_VERDE_HOVER};
        }}
    """
    
    BUTTON_CARGAR_DATOS = f"""
        QPushButton {{
            font-size: 15px;
            color: white;
            font-weight: bold;
            background-color: {AppConstants.COLOR_VERDE_PRINCIPAL};
            border: none;
            padding: 10px 20px;
            border-radius: 8px;
        }}
        QPushButton:hover {{
            background-color: {AppConstants.COLOR_VERDE_HOVER};
        }}
        QPushButton:pressed {{
            background-color: {AppConstants.COLOR_VERDE_PRESSED};
        }}
    """
    
    LOADER_OVERLAY = """
        QWidget {
            background-color: rgba(0, 0, 0, 0.7);
        }
    """
    
    LOADER_LABEL = """
        QLabel {
            color: white;
            font-size: 16px;
            font-weight: bold;
            margin-bottom: 10px;
        }
    """
    
    PROGRESS_BAR = f"""
        QProgressBar {{
            border: 2px solid {AppConstants.COLOR_VERDE_PRINCIPAL};
            border-radius: 10px;
            background-color: white;
            text-align: center;
        }}
        QProgressBar::chunk {{
            background-color: {AppConstants.COLOR_VERDE_PRINCIPAL};
            border-radius: 8px;
        }}
    """

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
        """Inicializa la interfaz de usuario de manera modular"""
        self.resize(AppConstants.WINDOW_WIDTH, AppConstants.WINDOW_HEIGHT)
        self.setWindowTitle("Subir Archivo")
        
        # Configurar el icono de la ventana
        if hasattr(sys, '_MEIPASS'):
            icon_path = os.path.join(sys._MEIPASS, 'media', 'icono.ico')
        else:
            icon_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'media', 'icono.ico')
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))

        # Configurar formulario principal
        form_layout = self._setup_form_layout()
        
        # Crear todas las filas del formulario
        self._create_all_form_rows(form_layout)
        
        # Configurar contenedor principal
        self._setup_main_container(form_layout)
        
        # Crear loader (inicialmente oculto)
        self.crear_loader()

    def _setup_form_layout(self):
        """Configura el layout del formulario con espaciados y alineaciones"""
        form_layout = QFormLayout()
        form_layout.setRowWrapPolicy(QFormLayout.DontWrapRows)
        form_layout.setFieldGrowthPolicy(QFormLayout.FieldsStayAtSizeHint)
        form_layout.setFormAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
        form_layout.setLabelAlignment(Qt.AlignRight)
        form_layout.setVerticalSpacing(AppConstants.VERTICAL_SPACING)
        form_layout.setHorizontalSpacing(AppConstants.HORIZONTAL_SPACING)
        return form_layout

    def _create_all_form_rows(self, form_layout):
        """Crea todas las filas del formulario de manera organizada"""
        # Fila 1: Filtro I
        self._create_folder_row(form_layout, "I", "<b>Filtro <i>I</i> :</b>")
        
        # Fila 2: Filtro V  
        self._create_folder_row(form_layout, "V", "<b>Filtro <i>V</i> :</b>")
        
        # Fila 3: Archivo CSV
        self._create_csv_row(form_layout)
        
        # Separador
        self._add_separator(form_layout)
        
        # Fila 4: Botón cargar datos
        self._create_submit_button(form_layout)

    def _create_folder_row(self, form_layout, filtro_tipo, label_text):
        """Crea una fila para selección de carpeta (I o V)"""
        label = QLabel(label_text)
        
        # Crear combo y botón
        combo = self._create_combo(AppConstants.COMBO_DEFAULT_FOLDER)
        button = self._create_examine_button()
        
        # Conectar funcionalidad
        button.clicked.connect(lambda: self.seleccionar_carpeta(filtro_tipo))
        
        # Crear contenedor
        row_widget = self._create_row_container([combo, button], AppConstants.ROW_CONTAINER_WIDTH_LARGE)
        
        # Agregar al formulario
        form_layout.addRow(label, row_widget)
        
        # Guardar referencia
        if filtro_tipo == 'I':
            self.combo_I = combo
        else:
            self.combo_V = combo

    def _create_csv_row(self, form_layout):
        """Crea la fila para selección de archivo CSV"""
        label = QLabel("<b>Archivo Mag. (.csv):</b>")
        
        # Crear combo y botón
        combo = self._create_combo(AppConstants.COMBO_DEFAULT_CSV)
        button = self._create_examine_button()
        
        # Conectar funcionalidad
        button.clicked.connect(self.seleccionar_archivo_csv)
        
        # Crear contenedor
        row_widget = self._create_row_container([combo, button], AppConstants.ROW_CONTAINER_WIDTH_LARGE)
        
        # Agregar al formulario
        form_layout.addRow(label, row_widget)
        
        # Guardar referencia
        self.combo_csv = combo

    def _create_input_row(self, form_layout, field_name, label_text, placeholder):
        """Crea una fila para entrada de datos numéricos"""
        label = QLabel(label_text)
        
        # Crear input y etiqueta de días
        input_field = QLineEdit("")
        input_field.setPlaceholderText(placeholder)
        input_field.setFixedWidth(AppConstants.INPUT_WIDTH)
        
        dias_label = QLabel(AppConstants.LABEL_DIAS)
        
        # Crear contenedor
        row_widget = self._create_row_container([input_field, dias_label], AppConstants.ROW_CONTAINER_WIDTH_SMALL)
        
        # Agregar al formulario
        form_layout.addRow(label, row_widget)
        
        # Guardar referencia
        setattr(self, f"input_{field_name}", input_field)

    def _create_combo(self, default_text):
        """Crea un combobox con configuración estándar"""
        combo = QComboBox()
        combo.setFixedWidth(AppConstants.COMBO_WIDTH)
        combo.addItem(default_text)
        return combo

    def _create_examine_button(self):
        """Crea un botón de examinar con estilo estándar"""
        button = QPushButton(AppConstants.LABEL_EXAMINAR)
        button.setFixedWidth(AppConstants.BUTTON_WIDTH)
        button.setCursor(QCursor(Qt.PointingHandCursor))
        button.setStyleSheet(StyleSheets.BUTTON_EXAMINAR)
        return button

    def _create_row_container(self, widgets, width):
        """Crea un contenedor horizontal para widgets con ancho específico"""
        container = QWidget()
        container.setFixedWidth(width)
        
        layout = QHBoxLayout()
        for widget in widgets:
            layout.addWidget(widget)
        
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setAlignment(Qt.AlignCenter)
        container.setLayout(layout)
        
        return container

    def _add_separator(self, form_layout):
        """Agrega un separador vertical al formulario"""
        separator = QLabel("")
        separator.setFixedHeight(AppConstants.SEPARATOR_HEIGHT)
        form_layout.addRow(separator)

    def _create_submit_button(self, form_layout):
        """Crea el botón principal de carga de datos"""
        button = QPushButton(AppConstants.LABEL_CARGAR_DATOS)
        button.clicked.connect(self.abrir_datos_nf)
        button.setCursor(QCursor(Qt.PointingHandCursor))
        button.setStyleSheet(StyleSheets.BUTTON_CARGAR_DATOS)
        
        # Agregar el botón al formulario
        form_layout.addRow(button)
        
        # Centrar el botón
        button_item = form_layout.itemAt(form_layout.rowCount()-1, QFormLayout.SpanningRole)
        if button_item:
            button_item.setAlignment(Qt.AlignCenter)

    def _setup_main_container(self, form_layout):
        """Configura el contenedor principal de la ventana"""
        container = QWidget()
        main_layout = QVBoxLayout()
        
        # Crear contenedor del formulario
        form_container = QWidget()
        form_container.setLayout(form_layout)
        form_container.setFixedWidth(AppConstants.FORM_CONTAINER_WIDTH)
        
        main_layout.addWidget(form_container, alignment=Qt.AlignCenter)
        main_layout.setContentsMargins(AppConstants.MAIN_MARGINS, AppConstants.MAIN_MARGINS, 
                                     AppConstants.MAIN_MARGINS, AppConstants.MAIN_MARGINS)

        container.setLayout(main_layout)
        self.setCentralWidget(container)

    def crear_loader(self):
        """Crea el widget de loader con estilos centralizados"""
        # Widget overlay para el loader
        self.loader_widget = QWidget(self)
        self.loader_widget.setStyleSheet(StyleSheets.LOADER_OVERLAY)
        self.loader_widget.hide()  # Oculto inicialmente
        
        # Layout para centrar el contenido del loader
        loader_layout = QVBoxLayout(self.loader_widget)
        loader_layout.setAlignment(Qt.AlignCenter)
        
        # Etiqueta de texto
        self.loader_label = QLabel(AppConstants.LOADER_CARGANDO)
        self.loader_label.setStyleSheet(StyleSheets.LOADER_LABEL)
        self.loader_label.setAlignment(Qt.AlignCenter)
        
        # Barra de progreso
        self.progress_bar = QProgressBar()
        self.progress_bar.setFixedWidth(AppConstants.PROGRESS_BAR_WIDTH)
        self.progress_bar.setFixedHeight(AppConstants.PROGRESS_BAR_HEIGHT)
        self.progress_bar.setRange(0, 0)  # Modo indeterminado
        self.progress_bar.setStyleSheet(StyleSheets.PROGRESS_BAR)
        
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
        
        return datos

    def abrir_datos_nf(self):
        """Función para abrir la ventana de DatosNF con loader"""
        # Validar que todos los campos estén completos
        if not self.validar_formulario():
            return  # No continuar si la validación falla
        
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

    def validar_formulario(self):
        """Valida que todos los campos del formulario estén completos"""
        errores = []
        
        # Validar Filtro I
        if self.combo_I.currentText() == "Seleccione una carpeta...":
            errores.append("• Debe seleccionar una carpeta para el Filtro I")
        
        # Validar Filtro V
        if self.combo_V.currentText() == "Seleccione una carpeta...":
            errores.append("• Debe seleccionar una carpeta para el Filtro V")
        
        # Validar archivo CSV
        if self.combo_csv.currentText() == "Seleccione un archivo CSV...":
            errores.append("• Debe seleccionar un archivo CSV de magnitudes")
        
        # Si hay errores, mostrar mensaje y retornar False
        if errores:
            mensaje_error = "Faltan campos obligatorios:\n\n" + "\n".join(errores)
            QMessageBox.warning(self, "Campos Incompletos", mensaje_error)
            return False
        
        return True

    def on_carga_completada(self):
        """Se ejecuta cuando la carga de datos se completa exitosamente"""
        try:
            # Actualizar el texto del loader usando constantes
            self.loader_label.setText(AppConstants.LOADER_PROCESANDO)
            QApplication.processEvents()  # Forzar actualización de UI
            
            # Usar QTimer para permitir que la UI se actualice
            QTimer.singleShot(200, self.crear_ventana_datos)
            
        except Exception as e:
            # Si hay error al crear la ventana, tratarlo como error
            self.on_error_carga(str(e))

    def crear_ventana_datos(self):
        """Crea la ventana DatosNF después de un pequeño delay"""
        try:
            # Actualizar mensaje usando constantes
            self.loader_label.setText(AppConstants.LOADER_CREANDO)
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
            
            # Actualizar texto del loader usando constantes
            self.loader_label.setText(AppConstants.LOADER_PREPARANDO)
            QApplication.processEvents()
            
            # Usar otro QTimer para mostrar la ventana después de que esté completamente lista
            QTimer.singleShot(300, self.mostrar_ventana_final)
            
        except Exception as e:
            # Asegurarse de detener el timer en caso de error
            if hasattr(self, 'animation_timer'):
                self.animation_timer.stop()
            # Si hay error al crear la ventana, tratarlo como error
            self.on_error_carga(str(e))

    def mostrar_ventana_final(self):
        """Muestra la ventana DatosNF y oculta el loader"""
        try:
            # Actualizar mensaje del loader usando constantes
            self.loader_label.setText(AppConstants.LOADER_MOSTRANDO)
            QApplication.processEvents()
            
            # Mostrar la ventana como modal
            self.datos_nf_window.setWindowModality(Qt.ApplicationModal)
            self.datos_nf_window.show()
            
            # Forzar que la ventana se renderice completamente
            self.datos_nf_window.raise_()
            self.datos_nf_window.activateWindow()
            QApplication.processEvents()
            
            # Ocultar el loader después de mostrar la ventana
            QTimer.singleShot(500, self.ocultar_loader_final)
            
        except Exception as e:
            self.on_error_carga(str(e))

    def ocultar_loader_final(self):
        """Oculta el loader y restaura el texto original"""
        self.ocultar_loader()
        self.loader_label.setText(AppConstants.LOADER_CARGANDO)  # Restaurar texto original usando constante

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

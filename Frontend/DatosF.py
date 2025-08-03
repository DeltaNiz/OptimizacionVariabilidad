from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QTableWidget, QTableWidgetItem, QPushButton, QLabel,
    QFrame, QScrollArea, QMessageBox, QFileDialog
)
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QCursor, QPixmap
import sys
import pandas as pd
import os

# Constantes de la aplicación
class AppConstants:
    # Dimensiones de imágenes
    IMAGEN_ANCHO_FIJO = 725
    IMAGEN_ALTO_MAXIMO = 600
    
    # Dimensiones de celdas
    ANCHO_CELDA_DEFAULT = 119
    ANCHO_CELDA_PRIMERA = 48
    ANCHO_CELDA_SCREEN_1920 = 117
    ANCHO_CELDA_PRIMERA_1920 = 49
    
    # Breakpoints de pantalla
    SCREEN_SMALL = 1366
    SCREEN_MEDIUM = 1920
    
    # Tamaños de ventana
    WINDOW_MEDIUM = (1350, 800)
    WINDOW_LARGE = (1600, 1000)
    
    # Headers de tabla
    TABLE_HEADERS = ["Archivo", "ID", "RA", "DEC", "Magnitud", "Período", "Amplitud", "Tipo", "Significancia"]
    
    # Extensiones de archivos
    IMAGEN_EXTENSIONES = ['.png', '.jpg', '.jpeg', '.gif', '.bmp']
    CSV_EXTENSIONS = ['.csv']
    
    # Patrones de archivos
    PATRON_DATOS_FILTRADOS = 'datos_filtrados_*.csv'
    PATRON_CARPETAS_ESTRELLA = 'star*'
    
    # Mensajes
    MSG_SIN_IMAGENES = ("No se encontraron imágenes en las carpetas de estrellas\n\n"
                       "Las imágenes se generan durante el procesamiento.\n"
                       "Usa 'Refrescar Datos' si el análisis continúa.")
    MSG_SIN_CARPETA = "No se encontró la carpeta de análisis"
    
    # Colores del tema
    COLOR_VERDE_PRINCIPAL = "#a7c942"
    COLOR_VERDE_HOVER = "#98b83b"
    COLOR_VERDE_PRESSED = "#7a9530"
    COLOR_VERDE_BORDER = "#98b83b"
    
    # Extensiones de archivos
    EXTENSIONES_IMAGEN = ['.png', '.jpg', '.jpeg', '.gif', '.bmp']
    EXTENSIONES_CSV = ['.csv']

# Estilos CSS centralizados
class StyleSheets:
    HEADER_TABLE = f"""
        QHeaderView::section {{ 
            background-color: {AppConstants.COLOR_VERDE_PRINCIPAL}; 
            color: white; 
            font-weight: bold;
            border: 1px solid {AppConstants.COLOR_VERDE_BORDER};
            padding: 5px;
            text-align: center;
            border-style: solid;
            border-top: none;
            border-left: none;
            border-right: 1px solid {AppConstants.COLOR_VERDE_BORDER};
            border-bottom: 1px solid {AppConstants.COLOR_VERDE_BORDER};
        }}
        QHeaderView::section:hover {{
            background-color: {AppConstants.COLOR_VERDE_PRINCIPAL};
        }}
        QHeaderView::section:pressed {{
            background-color: {AppConstants.COLOR_VERDE_PRINCIPAL};
        }}
    """
    
    TABLE_MAIN = f"""
        QTableWidget {{
            gridline-color: {AppConstants.COLOR_VERDE_PRINCIPAL};
            background-color: white;
            alternate-background-color: #f0f0f0;
            margin: 10px;
        }}
        QTableWidget::item {{
            border: 1px solid {AppConstants.COLOR_VERDE_PRINCIPAL};
        }}
        QTableWidget::item:selected {{
            background-color: {AppConstants.COLOR_VERDE_HOVER};
            color: white;
        }}
    """
    
    BUTTON_BASE = """
        QPushButton {{
            font-size: 11px;
            color: white;
            font-weight: bold;
            border: none;
            padding: 5px 10px;
            border-radius: 4px;
        }}
        QPushButton:disabled {{
            background-color: #cccccc;
            color: #666666;
        }}
    """
    
    BUTTON_NAVIGATION = BUTTON_BASE + """
        QPushButton {{
            background-color: #6c757d;
        }}
        QPushButton:hover {{
            background-color: #5a6268;
        }}
    """
    
    BUTTON_ACTION = """
        QPushButton {{
            font-size: 12px;
            color: white;
            font-weight: bold;
            border: none;
            padding: 5px 20px;
            border-radius: 8px;
        }}
    """
    
    BUTTON_REFRESCAR = BUTTON_ACTION + """
        QPushButton {{
            background-color: #f0ad4e;
        }}
        QPushButton:hover {{
            background-color: #ec971f;
        }}
        QPushButton:pressed {{
            background-color: #d58512;
        }}
    """
    
    BUTTON_EXPORTAR = BUTTON_ACTION + f"""
        QPushButton {{
            background-color: {AppConstants.COLOR_VERDE_PRINCIPAL};
        }}
        QPushButton:hover {{
            background-color: {AppConstants.COLOR_VERDE_HOVER};
        }}
        QPushButton:pressed {{
            background-color: {AppConstants.COLOR_VERDE_PRESSED};
        }}
    """
    
    BUTTON_NUEVO_ANALISIS = BUTTON_ACTION + """
        QPushButton {{
            background-color: #5bc0de;
        }}
        QPushButton:hover {{
            background-color: #46b8da;
        }}
        QPushButton:pressed {{
            background-color: #31b0d5;
        }}
    """
    
    IMAGE_LABEL = f"""
        QLabel {{
            border: 2px solid {AppConstants.COLOR_VERDE_PRINCIPAL};
            border-radius: 5px;
            background-color: #f9f9f9;
            padding: 10px;
        }}
    """
    
    SEPARATOR = f"QFrame {{ color: {AppConstants.COLOR_VERDE_PRINCIPAL}; background-color: {AppConstants.COLOR_VERDE_PRINCIPAL}; }}"

class DatosF(QMainWindow):
    def __init__(self, data_folder=None, datos_formulario=None, ventana_anterior=None, ruta_csv_filtrado=None):
        super().__init__()
        self.data_folder = data_folder or ""
        self.datos_formulario = datos_formulario or {}
        self.ventana_anterior = ventana_anterior
        self.ruta_csv_filtrado = ruta_csv_filtrado  # CSV generado con datos filtrados
        self.imagenes_estrellas = []  # Lista de imágenes encontradas
        self.imagen_actual_index = 0  # Índice de imagen actual mostrada
        
        # Configuración centralizada usando constantes
        self.imagen_ancho_fijo = AppConstants.IMAGEN_ANCHO_FIJO
        self.imagen_alto_maximo = AppConstants.IMAGEN_ALTO_MAXIMO
        self.ancho_celda = AppConstants.ANCHO_CELDA_DEFAULT
        self.ancho_celda_1 = AppConstants.ANCHO_CELDA_PRIMERA
        
        # Variable para controlar si la ventana debe mantenerse maximizada
        self.ventana_maximizada = False

        self.init_ui()
    
    def init_ui(self):
        self.setWindowTitle("Resultados del Análisis")
        screen_width = self.screen().size().width()
        
        # Configuración responsiva optimizada con constantes
        layout_margin = self._configure_screen_layout(screen_width)

        # Widget central
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Layout principal horizontal
        main_layout = QHBoxLayout()
        main_layout.setContentsMargins(layout_margin, layout_margin, layout_margin, layout_margin)
        main_layout.setSpacing(layout_margin + 5)

        # Configurar tabla principal
        self._setup_main_table()

        # Cargar datos del CSV filtrado si está disponible
        self.cargar_datos_csv_filtrado()

        # Configurar layout derecho
        right_layout = self._setup_right_layout()

        # Crear separador vertical
        separator = self._create_vertical_separator()
        
        # Agregar widgets al layout principal
        main_layout.addWidget(self.table_main, 9)
        main_layout.addWidget(separator, 0)
        main_layout.addLayout(right_layout, 13)

        central_widget.setLayout(main_layout)
        
        # Instalar filtro de eventos
        self.installEventFilter(self)
        
        # Maximizar la ventana al final si está marcado para pantallas pequeñas
        if self.ventana_maximizada:
            QTimer.singleShot(50, self.asegurar_maximizacion)

    def _configure_screen_layout(self, screen_width):
        """Configura el layout según el tamaño de pantalla"""
        if screen_width <= AppConstants.SCREEN_SMALL:
            # Para pantallas pequeñas, marcar para maximizar automáticamente
            self.ventana_maximizada = True
            layout_margin = 5
            print(f"Pantalla pequeña detectada ({screen_width}px) - Ventana será maximizada automáticamente")
        elif screen_width <= AppConstants.SCREEN_MEDIUM:
            self.ancho_celda = AppConstants.ANCHO_CELDA_SCREEN_1920
            self.ancho_celda_1 = AppConstants.ANCHO_CELDA_PRIMERA_1920
            self.resize(*AppConstants.WINDOW_MEDIUM)
            layout_margin = 5
        else:
            self.resize(*AppConstants.WINDOW_LARGE)
            layout_margin = 20
        return layout_margin

    def _setup_main_table(self):
        """Configura la tabla principal con estilos optimizados"""
        self.table_main = QTableWidget()
        self.table_main.setRowCount(0)
        self.table_main.setColumnCount(0)

        # Ocultar la numeración automática de filas
        self.table_main.verticalHeader().setVisible(False)
        
        # Instalar filtro de eventos para limpiar selección al hacer clic fuera de la tabla
        self.table_main.viewport().installEventFilter(self)
        
        # Aplicar estilos centralizados
        header = self.table_main.horizontalHeader()
        header.setStyleSheet(StyleSheets.HEADER_TABLE)
        self.table_main.setStyleSheet(StyleSheets.TABLE_MAIN)
        
        # Activar colores alternados en las filas
        self.table_main.setAlternatingRowColors(True)
        
        # Controlar altura de filas
        self.table_main.verticalHeader().setDefaultSectionSize(30)

    def _setup_right_layout(self):
        """Configura el layout del panel derecho"""
        right_layout = QVBoxLayout()
        right_layout.setContentsMargins(10, 10, 10, 10)
        right_layout.setSpacing(10)

        # Título
        self.label_title = QLabel("<b>Análisis Completado</b>")
        self.label_title.setAlignment(Qt.AlignCenter)
        self.label_title.setStyleSheet("QLabel { font-size: 16px; font-weight: bold; }")
        
        # Actualizar título con número de estrella
        self.actualizar_titulo()
        
        # Mostrar información de los datos del formulario si están disponibles
        if self.datos_formulario:
            info_formulario = self.crear_info_formulario()
            # Mantener el número de estrella pero agregar información del formulario
            texto_actual = self.label_title.text()
            if info_formulario:
                self.label_title.setText(f"{texto_actual}<br><small>{info_formulario}</small>")
        
        # Determinar el subtítulo basado en la presencia de datos
        if self.data_folder and os.path.exists(self.data_folder):
            label_subtitle = QLabel(f"Carpeta: {os.path.basename(self.data_folder)}")
        else:
            label_subtitle = QLabel("Resultados del procesamiento de estrellas")
        label_subtitle.setAlignment(Qt.AlignCenter)
        label_subtitle.setStyleSheet("QLabel { font-size: 12px; color: #666; }")

        # Agregar elementos al layout
        right_layout.addWidget(self.label_title)
        right_layout.addWidget(label_subtitle)
        right_layout.addSpacing(8)
        right_layout.addWidget(self._create_horizontal_separator())
        right_layout.addSpacing(10)

        # Configurar área de imágenes
        self._setup_image_area(right_layout)

        # Cargar imágenes de las estrellas si están disponibles
        self.cargar_imagenes_estrellas()

        right_layout.addSpacing(10)
        right_layout.addWidget(self._create_horizontal_separator())
        right_layout.addSpacing(10)

        # Configurar botones de acción
        self._setup_action_buttons(right_layout)
        
        return right_layout

    def _setup_image_area(self, layout):
        """Configura el área de visualización de imágenes"""
        # Área para mostrar las imágenes de las estrellas
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setMinimumHeight(300)
        
        self.image_label = QLabel()
        self.image_label.setAlignment(Qt.AlignCenter)
        self.image_label.setText("Cargando imágenes...")
        self.image_label.setStyleSheet(StyleSheets.IMAGE_LABEL)
        
        self.scroll_area.setWidget(self.image_label)
        
        # Controles para navegar entre imágenes
        navegacion_layout = self._create_navigation_controls()
        
        layout.addWidget(self.scroll_area)
        layout.addLayout(navegacion_layout)

    def _create_navigation_controls(self):
        """Crea los controles de navegación entre imágenes"""
        navegacion_layout = QHBoxLayout()
        
        self.btn_anterior = self._create_navigation_button("← Anterior", self.imagen_anterior)
        self.label_imagen_info = QLabel("Sin imágenes")
        self.label_imagen_info.setAlignment(Qt.AlignCenter)
        self.label_imagen_info.setStyleSheet("font-size: 11px; color: #666;")
        self.btn_siguiente = self._create_navigation_button("Siguiente →", self.imagen_siguiente)
        
        navegacion_layout.addWidget(self.btn_anterior)
        navegacion_layout.addStretch()
        navegacion_layout.addWidget(self.label_imagen_info)
        navegacion_layout.addStretch()
        navegacion_layout.addWidget(self.btn_siguiente)
        
        return navegacion_layout

    def _create_navigation_button(self, text, callback):
        """Crea un botón de navegación con estilo consistente"""
        button = QPushButton(text)
        button.setEnabled(False)
        button.setMaximumWidth(100)
        button.setCursor(QCursor(Qt.PointingHandCursor))
        button.setStyleSheet(StyleSheets.BUTTON_NAVIGATION)
        button.clicked.connect(callback)
        return button

    def _setup_action_buttons(self, layout):
        """Configura los botones de acción principales"""
        btn_refrescar = self._create_action_button(
            "Refrescar Datos", 
            StyleSheets.BUTTON_REFRESCAR, 
            self.refrescar_datos
        )
        
        btn_exportar = self._create_action_button(
            "Exportar Resultados", 
            StyleSheets.BUTTON_EXPORTAR, 
            self.exportar_resultados
        )
        
        btn_nuevo_analisis = self._create_action_button(
            "Nuevo Análisis", 
            StyleSheets.BUTTON_NUEVO_ANALISIS, 
            self.nuevo_analisis
        )

        # Layout para botones
        buttons_layout = QHBoxLayout()
        buttons_layout.addStretch()
        buttons_layout.addWidget(btn_refrescar)
        buttons_layout.addSpacing(10)
        buttons_layout.addWidget(btn_exportar)
        buttons_layout.addSpacing(10)
        buttons_layout.addWidget(btn_nuevo_analisis)
        buttons_layout.addStretch()
        
        layout.addLayout(buttons_layout)
        layout.addSpacing(10)

    def _create_action_button(self, text, style, callback):
        """Crea un botón de acción con estilo y configuración consistente"""
        button = QPushButton(text)
        button.setCursor(QCursor(Qt.PointingHandCursor))
        button.setMaximumWidth(200)
        button.setStyleSheet(style)
        button.clicked.connect(callback)
        return button

    def _create_horizontal_separator(self):
        """Crea un separador horizontal personalizado"""
        separator = QFrame()
        separator.setFrameShape(QFrame.HLine)
        separator.setFrameShadow(QFrame.Sunken)
        separator.setStyleSheet(StyleSheets.SEPARATOR)
        return separator

    def _create_vertical_separator(self):
        """Crea un separador vertical personalizado"""
        separator = QFrame()
        separator.setFrameShape(QFrame.VLine)
        separator.setFrameShadow(QFrame.Sunken)
        separator.setStyleSheet(StyleSheets.SEPARATOR)
        separator.setMaximumWidth(2)
        return separator

    def eventFilter(self, source, event):
        """Filtro de eventos para limpiar selecciones al hacer clic fuera de las tablas"""
        from PyQt5.QtCore import QEvent
        
        if event.type() == QEvent.MouseButtonPress:
            if hasattr(self, 'table_main') and source not in [self.table_main, self.table_main.viewport()]:
                self.table_main.clearSelection()
        
        return super().eventFilter(source, event)
    
    def asegurar_maximizacion(self):
        """Asegura que la ventana esté maximizada para pantallas pequeñas"""
        if self.ventana_maximizada and not self.isMaximized():
            self.showMaximized()
            print("Ventana forzada a maximizar para pantalla pequeña")
    
    def resizeEvent(self, event):
        """Sobrescribe el evento de redimensionamiento para mantener maximización"""
        super().resizeEvent(event)
        # Si la ventana debe estar maximizada pero no lo está, restaurar maximización
        if self.ventana_maximizada and not self.isMaximized():
            QTimer.singleShot(10, self.showMaximized)

    def actualizar_titulo(self):
        """Actualiza el título con el número de estrella actual"""
        numero_estrella = self.obtener_numero_estrella_actual()
        if numero_estrella:
            self.label_title.setText(f"<b>Estrella {numero_estrella}</b>")
        else:
            self.label_title.setText("<b>Análisis Completado</b>")
    
    def obtener_numero_estrella_actual(self):
        """Obtiene el número de la estrella actual desde diferentes fuentes"""
        # 1. Intentar desde la imagen actual mostrada
        if hasattr(self, 'imagenes_estrellas') and self.imagenes_estrellas and hasattr(self, 'imagen_actual_index'):
            if 0 <= self.imagen_actual_index < len(self.imagenes_estrellas):
                return self.imagenes_estrellas[self.imagen_actual_index]['estrella']
        
        # 2. Intentar desde el nombre de la carpeta de datos
        if self.data_folder and os.path.exists(self.data_folder):
            nombre_carpeta = os.path.basename(self.data_folder)
            # Buscar patrones como analisis_YYYYMMDD_HHMMSS con carpetas star1, star2, etc.
            try:
                for item in os.listdir(self.data_folder):
                    item_path = os.path.join(self.data_folder, item)
                    if os.path.isdir(item_path) and item.startswith('star'):
                        # Si solo hay una carpeta star, usar ese número
                        numero = item.replace('star', '')
                        if numero.isdigit():
                            return numero
                        break
            except:
                pass
        
        # 3. Fallback: verificar si hay imágenes cargadas y usar la primera
        if hasattr(self, 'imagenes_estrellas') and self.imagenes_estrellas:
            return self.imagenes_estrellas[0]['estrella']
        
        return None

    def crear_info_formulario(self):
        """Crea texto informativo basado en los datos del formulario"""
        info_parts = []
        
        if 'periodo_max' in self.datos_formulario and self.datos_formulario['periodo_max']:
            info_parts.append(f"Período máx: {self.datos_formulario['periodo_max']} días")
        
        if 'periodo_min' in self.datos_formulario and self.datos_formulario['periodo_min']:
            info_parts.append(f"Período mín: {self.datos_formulario['periodo_min']} días")
        
        if 'step' in self.datos_formulario and self.datos_formulario['step']:
            info_parts.append(f"Step: {self.datos_formulario['step']} días")
        
        return " | ".join(info_parts) if info_parts else "Parámetros de análisis"

    def cargar_datos_resultados(self):
        """Carga los datos de los archivos CSV generados por procesofull.py"""

        """if not self.data_folder or not os.path.exists(self.data_folder):
            self.mostrar_datos_ejemplo()
            return"""
        
        # Buscar archivos CSV de resultados (empezar con el primero disponible)
        archivos_csv = ['pglsv.csv', 'pglsi.csv', 'ppdmv.csv', 'ppdmi.csv']
        
        for archivo in archivos_csv:
            ruta_csv = os.path.join(self.data_folder, archivo)
            if os.path.exists(ruta_csv):
                try:
                    self.cargar_csv(ruta_csv)
                    print(f"Datos cargados desde: {archivo}")
                    return
                except Exception as e:
                    print(f"Error al cargar {archivo}: {e}")
                    continue
        
        # Si no se encuentran CSVs de resultados, buscar información de las carpetas de estrellas
        self.cargar_datos_carpetas_estrellas()

    def cargar_datos_carpetas_estrellas(self):
        """Carga datos basándose en las carpetas de estrellas encontradas"""
        try:
            # Listar carpetas de estrellas
            carpetas_estrella = []
            if os.path.exists(self.data_folder):
                for item in os.listdir(self.data_folder):
                    item_path = os.path.join(self.data_folder, item)
                    if os.path.isdir(item_path) and item.startswith('star'):
                        carpetas_estrella.append(item)
            
            if carpetas_estrella:
                # Ordenar las carpetas numéricamente
                carpetas_estrella.sort(key=lambda x: int(x.replace('star', '')))
                
                # Configurar tabla con información de las carpetas encontradas
                self.table_main.setRowCount(len(carpetas_estrella))
                self.table_main.setColumnCount(3)
                self.table_main.setHorizontalHeaderLabels(["Estrella", "Carpeta", "Estado"])
                
                for row, carpeta in enumerate(carpetas_estrella):
                    # Número de estrella
                    numero_estrella = carpeta.replace('star', '')
                    item_numero = QTableWidgetItem(numero_estrella)
                    item_numero.setTextAlignment(Qt.AlignCenter)
                    self.table_main.setItem(row, 0, item_numero)
                    
                    # Nombre de carpeta
                    item_carpeta = QTableWidgetItem(carpeta)
                    item_carpeta.setTextAlignment(Qt.AlignCenter)
                    self.table_main.setItem(row, 1, item_carpeta)
                    
                    # Verificar estado (si hay archivos dentro)
                    carpeta_path = os.path.join(self.data_folder, carpeta)
                    archivos_en_carpeta = len([f for f in os.listdir(carpeta_path) if os.path.isfile(os.path.join(carpeta_path, f))])
                    
                    estado = "Procesada" if archivos_en_carpeta > 0 else "Vacía"
                    item_estado = QTableWidgetItem(estado)
                    item_estado.setTextAlignment(Qt.AlignCenter)
                    self.table_main.setItem(row, 2, item_estado)
                
                # Ajustar ancho de columnas
                self.table_main.setColumnWidth(0, 80)
                self.table_main.setColumnWidth(1, 120)
                self.table_main.setColumnWidth(2, 100)
                
                print(f"Datos cargados desde {len(carpetas_estrella)} carpetas de estrellas")
            else:
                print("No se encontraron carpetas de estrellas, mostrando datos de ejemplo")
                # self.mostrar_datos_ejemplo()
                
        except Exception as e:
            print(f"Error al cargar datos de carpetas: {e}")
            # self.mostrar_datos_ejemplo()

    def cargar_csv(self, ruta_csv):
        """Carga datos desde un archivo CSV específico"""
        try:
            df = pd.read_csv(ruta_csv)
            
            # Configurar tabla
            self.table_main.setRowCount(len(df))
            self.table_main.setColumnCount(len(df.columns))
            self.table_main.setHorizontalHeaderLabels(df.columns.tolist())
            
            # Llenar tabla con datos
            for row in range(len(df)):
                for col in range(len(df.columns)):
                    valor = df.iloc[row, col]
                    
                    # Mostrar valores sin redondear (usar el valor completo)
                    if isinstance(valor, (int, float)):
                        texto = str(valor)  # Usar el valor completo sin formatear
                    else:
                        texto = str(valor)
                    
                    item = QTableWidgetItem(texto)
                    item.setTextAlignment(Qt.AlignCenter)
                    self.table_main.setItem(row, col, item)
            
            # Ajustar ancho de columnas automáticamente
            self.table_main.resizeColumnsToContents()
            
            # Asegurar que las columnas no sean demasiado estrechas
            for col in range(self.table_main.columnCount()):
                if self.table_main.columnWidth(col) < 80:
                    self.table_main.setColumnWidth(col, 80)
            
        except Exception as e:
            print(f"Error al cargar CSV: {e}")
            # self.mostrar_datos_ejemplo()

    # def mostrar_datos_ejemplo(self):
    #     """Muestra datos de ejemplo si no se pueden cargar los resultados"""
    #     # Configurar tabla con datos de ejemplo
    #     self.table_main.setRowCount(5)
    #     self.table_main.setColumnCount(5)
    #     self.table_main.setHorizontalHeaderLabels(["N°", "V", "I", "MV", "MI"])
    #     
    #     datos_ejemplo = [
    #         ["1","0552.491_0637.323V","0551.708_0637.363i", "15.0034280824373", "13.9925005227811"],
    #         ["2","0455.988_0351.249V","0455.231_0350.973i", "15.000864265233", "13.8664936400888"]
    #     ]
    #     
    #     for row, fila_datos in enumerate(datos_ejemplo):
    #         for col, valor in enumerate(fila_datos):
    #             item = QTableWidgetItem(valor)
    #             item.setTextAlignment(Qt.AlignCenter)
    #             self.table_main.setItem(row, col, item)
    #     
    #     # Ajustar ancho de columnas
    #     self.table_main.setColumnWidth(0, self.ancho_celda_1)   # N° - 48px
    #     self.table_main.setColumnWidth(1, self.ancho_celda) # Columnas restantes - 130px
    #     self.table_main.setColumnWidth(2, self.ancho_celda)
    #     self.table_main.setColumnWidth(3, self.ancho_celda)
    #     self.table_main.setColumnWidth(4, self.ancho_celda)
    #     
    #     # Limpiar selección cuando se muestran datos de ejemplo
    #     self.table_main.clearSelection()
    #     
    #     # Crear imágenes de ejemplo simuladas para las dos estrellas
    #     self.crear_imagenes_ejemplo()
    #     
    #     # Mostrar imagen de ejemplo después de que la UI esté completamente inicializada
    #     from PyQt5.QtCore import QTimer
    #     QTimer.singleShot(100, self.mostrar_imagen_ejemplo)

    # def crear_imagenes_ejemplo(self):
    #     """Crea un conjunto de imágenes de ejemplo para simular la navegación"""
    #     # Lista de rutas de imágenes de ejemplo
    #     rutas_ejemplo = [
    #         r"C:\Users\tomas\OneDrive\Escritorio\xd\U\2025-1\Formulacion de Proyecto de Titulacion\data\analisis_20250729_170749\star1\GLSPDM.png",
    #         r"C:\Users\tomas\OneDrive\Escritorio\xd\U\2025-1\Formulacion de Proyecto de Titulacion\data\analisis_20250729_170749\star2\GLSPDM.png"
    #     ]
    #     
    #     # Limpiar la lista de imágenes existente
    #     self.imagenes_estrellas = []
    #     
    #     # Agregar imágenes de ejemplo si existen
    #     for i, ruta in enumerate(rutas_ejemplo, 1):
    #         if os.path.exists(ruta):
    #             self.imagenes_estrellas.append({
    #                 'ruta': ruta,
    #                 'estrella': str(i),
    #                 'nombre': f'GLSPDM_ejemplo_estrella_{i}.png',
    #                 'carpeta': f'star{i}_ejemplo'
    #             })
    #             print(f"Imagen de ejemplo agregada: Estrella {i}")
    #         else:
    #             # Si no existe la imagen real, crear una entrada para imagen generada
    #             self.imagenes_estrellas.append({
    #                 'ruta': 'generada',  # Marcador para imagen generada
    #                 'estrella': str(i),
    #                 'nombre': f'ejemplo_generado_estrella_{i}.png',
    #                 'carpeta': f'star{i}_ejemplo'
    #             })
    #             print(f"Imagen generada programáticamente para: Estrella {i}")
    #     
    #     # Configurar el índice inicial
    #     self.imagen_actual_index = 0
    #     
    #     # Actualizar controles de navegación para habilitar los botones
    #     # Usar QTimer para llamarlo después de que la UI esté completamente inicializada
    #     from PyQt5.QtCore import QTimer
    #     QTimer.singleShot(200, self.actualizar_controles_navegacion)

    # def mostrar_imagen_ejemplo(self):
    #     """Muestra una imagen de ejemplo cuando no hay datos reales disponibles"""
    #     # Verificar si image_label existe (puede no existir durante la inicialización)
    #     if not hasattr(self, 'image_label') or self.image_label is None:
    #         print("image_label no disponible, imagen de ejemplo será mostrada después")
    #         return
    #     
    #     # Verificar si hay imágenes de ejemplo disponibles
    #     if not hasattr(self, 'imagenes_estrellas') or not self.imagenes_estrellas:
    #         self.mostrar_imagen_ejemplo_fallback()
    #         return
    #     
    #     # Obtener la imagen actual del índice
    #     if self.imagen_actual_index >= len(self.imagenes_estrellas):
    #         self.imagen_actual_index = 0
    #     
    #     imagen_info = self.imagenes_estrellas[self.imagen_actual_index]
    #     
    #     try:
    #         if imagen_info['ruta'] != 'generada' and os.path.exists(imagen_info['ruta']):
    #             # Cargar imagen real si existe
    #             from PyQt5.QtGui import QPixmap
    #             from PyQt5.QtCore import Qt
    #             
    #             pixmap = QPixmap(imagen_info['ruta'])
    #             if not pixmap.isNull():
    #                 # Escalar imagen para que quepa bien en el área
    #                 scaled_pixmap = pixmap.scaled(
    #                     self.imagen_ancho_fijo,  # Usar configuración centralizada
    #                     self.imagen_alto_maximo,  # Usar configuración centralizada
    #                     Qt.KeepAspectRatio, 
    #                     Qt.SmoothTransformation
    #                 )
    #                 self.image_label.setPixmap(scaled_pixmap)
    #                 self.image_label.setText("")
    #                 print(f"Imagen de ejemplo cargada desde: {imagen_info['ruta']}")
    #             else:
    #                 # Si no se puede cargar, crear imagen programática
    #                 self.crear_imagen_ejemplo_programatica(imagen_info['estrella'])
    #         else:
    #             # Crear imagen programática para esta estrella
    #             self.crear_imagen_ejemplo_programatica(imagen_info['estrella'])
    #             
    #     except Exception as e:
    #         print(f"Error al cargar imagen de ejemplo: {e}")
    #         # Fallback a imagen programática
    #         self.crear_imagen_ejemplo_programatica(imagen_info['estrella'])
    #     
    #     # Actualizar título y selección de fila
    #     self.actualizar_titulo()
    #     self.seleccionar_fila_estrella_actual()

    # def mostrar_imagen_ejemplo_fallback(self):
    #     """Muestra imagen de ejemplo cuando no hay sistema de navegación configurado"""
    #     try:
    #         # Ruta de la imagen de ejemplo principal
    #         ruta_imagen_ejemplo = r"C:\Users\tomas\OneDrive\Escritorio\xd\U\2025-1\Formulacion de Proyecto de Titulacion\data\analisis_20250729_170749\star1\GLSPDM.png"
    #         
    #         # Verificar si la imagen de ejemplo existe
    #         if os.path.exists(ruta_imagen_ejemplo):
    #             # Cargar la imagen de ejemplo
    #             from PyQt5.QtGui import QPixmap
    #             from PyQt5.QtCore import Qt
    #             
    #             pixmap = QPixmap(ruta_imagen_ejemplo)
    #             if not pixmap.isNull():
    #                 # Escalar imagen para que quepa bien en el área
    #                 scaled_pixmap = pixmap.scaled(
    #                     self.imagen_ancho_fijo,  # Usar configuración centralizada
    #                     self.imagen_alto_maximo,  # Usar configuración centralizada
    #                     Qt.KeepAspectRatio, 
    #                     Qt.SmoothTransformation
    #                 )
    #                 self.image_label.setPixmap(scaled_pixmap)
    #                 self.image_label.setText("")
    #                 print(f"Imagen de ejemplo fallback cargada desde: {ruta_imagen_ejemplo}")
    #             else:
    #                 raise Exception("No se pudo cargar la imagen de ejemplo")
    #         else:
    #             raise Exception(f"Imagen de ejemplo no encontrada en: {ruta_imagen_ejemplo}")
    #         
    #     except Exception as e:
    #         print(f"Error al cargar imagen de ejemplo fallback: {e}")
    #         # Crear imagen programática como último recurso
    #         self.crear_imagen_ejemplo_programatica("1")

    # def crear_imagen_ejemplo_programatica(self, numero_estrella):
    #     """Crea una imagen de ejemplo programáticamente para una estrella específica"""
    #     try:
    #         # Crear una imagen de ejemplo usando texto
    #         from PyQt5.QtGui import QPixmap, QPainter, QFont, QFontMetrics
    #         from PyQt5.QtCore import Qt
    #         
    #         # Crear un pixmap para la imagen de ejemplo
    #         width, height = 400, 300
    #         pixmap = QPixmap(width, height)
    #         pixmap.fill(QColor(240, 240, 240))  # Fondo gris claro
    #         
    #         painter = QPainter(pixmap)
    #         painter.setRenderHint(QPainter.Antialiasing)
    #         
    #         # Configurar fuente
    #         font = QFont("Arial", 12, QFont.Bold)
    #         painter.setFont(font)
    #         painter.setPen(QColor(70, 70, 70))
    #         
    #         # Texto de ejemplo específico para la estrella
    #         texto_ejemplo = [
    #             f"EJEMPLO DE ANÁLISIS",
    #             "",
    #             f"Estrella Variable #{numero_estrella}",
    #             "",
    #             f"• Período: {2.45 + float(numero_estrella) * 0.3:.2f} días",
    #             f"• Amplitud: {0.3 + float(numero_estrella) * 0.1:.2f} mag",
    #             "• Tipo: RR Lyrae",
    #             "",
    #             "Este es un ejemplo de los",
    #             "resultados que se mostrarán",
    #             "una vez completado el análisis"
    #         ]
    #         
    #         # Calcular posición inicial
    #         font_metrics = QFontMetrics(font)
    #         line_height = font_metrics.height()
    #         y_start = (height - len(texto_ejemplo) * line_height) // 2
    #         
    #         # Dibujar texto línea por línea
    #         for i, linea in enumerate(texto_ejemplo):
    #             if linea:  # Solo dibujar si la línea no está vacía
    #                 text_width = font_metrics.width(linea)
    #                 x = (width - text_width) // 2  # Centrar texto
    #                 y = y_start + i * line_height
    #                 painter.drawText(x, y, linea)
    #         
    #         # Dibujar un marco decorativo
    #         painter.setPen(QColor(167, 201, 66))  # Color verde del tema
    #         painter.drawRect(10, 10, width-20, height-20)
    #         
    #         painter.end()
    #         
    #         # Mostrar la imagen
    #         self.image_label.setPixmap(pixmap)
    #         self.image_label.setText("")
    #         print(f"Imagen de ejemplo generada programáticamente para Estrella {numero_estrella}")
    #         
    #     except Exception as e2:
    #         # Si hay error creando la imagen, mostrar texto de ejemplo
    #         texto_ejemplo = (f"DATOS DE EJEMPLO - ESTRELLA {numero_estrella}\n\n"
    #                        "Esta es una vista previa de cómo\n"
    #                        "se mostrarán los resultados una vez\n"
    #                        "que se complete el análisis.\n\n"
    #                        "• Tabla con datos filtrados\n"
    #                        "• Gráficos de curvas de luz\n"
    #                        "• Imágenes de cada estrella\n\n"
    #                        "Usa 'Nuevo Análisis' para\n"
    #                        "procesar datos reales")
    #         
    #         self.image_label.setText(texto_ejemplo)
    #         print(f"Error al crear imagen de respaldo, mostrando texto para Estrella {numero_estrella}: {e2}")

    def _buscar_archivos_por_patron(self, directorio, patrones, extensiones=None):
        """
        Busca archivos que coincidan con patrones específicos de manera optimizada
        
        Args:
            directorio (str): Directorio donde buscar
            patrones (list): Lista de patrones de nombres de archivo
            extensiones (list): Lista de extensiones permitidas
            
        Returns:
            list: Lista de rutas de archivos encontrados
        """
        archivos_encontrados = []
        extensiones = extensiones or AppConstants.EXTENSIONES_IMAGEN
        
        if not os.path.exists(directorio):
            return archivos_encontrados
            
        try:
            # Búsqueda optimizada usando os.scandir (más rápido que os.listdir)
            with os.scandir(directorio) as entries:
                for entry in entries:
                    if entry.is_file():
                        nombre_archivo = entry.name.lower()
                        # Verificar extensión
                        if any(nombre_archivo.endswith(ext) for ext in extensiones):
                            # Verificar patrones
                            if any(patron.lower() in nombre_archivo for patron in patrones):
                                archivos_encontrados.append(entry.path)
                    elif entry.is_dir():
                        # Búsqueda recursiva en subdirectorios
                        sub_archivos = self._buscar_archivos_por_patron(
                            entry.path, patrones, extensiones
                        )
                        archivos_encontrados.extend(sub_archivos)
        except PermissionError:
            print(f"Sin permisos para acceder a: {directorio}")
        except Exception as e:
            print(f"Error al buscar archivos en {directorio}: {e}")
            
        return archivos_encontrados

    def _cargar_imagen_optimizada(self, ruta_imagen):
        """Carga una imagen de manera optimizada con manejo de errores"""
        try:
            pixmap = QPixmap(ruta_imagen)
            if not pixmap.isNull():
                # Escalar imagen usando configuración centralizada
                scaled_pixmap = pixmap.scaled(
                    self.imagen_ancho_fijo,
                    self.imagen_alto_maximo,
                    Qt.KeepAspectRatio, 
                    Qt.SmoothTransformation
                )
                self.image_label.setPixmap(scaled_pixmap)
                self.image_label.setText("")
                return True
            else:
                self.image_label.setText("Error al cargar la imagen")
                return False
        except Exception as e:
            self.image_label.setText(f"Error al cargar imagen: {str(e)}")
            print(f"Error al cargar imagen: {e}")
            return False

    def cargar_imagen_resultado(self):
        """Carga la imagen generada por procesofull.py de manera optimizada"""
        if not self.data_folder or not os.path.exists(self.data_folder):
            self.image_label.setText("No se encontró la carpeta de resultados")
            return
        
        # Buscar imágenes usando la función optimizada
        imagenes_encontradas = self._buscar_archivos_por_patron(
            self.data_folder, 
            ['GLSPDM', 'glspdm'], 
            AppConstants.EXTENSIONES_IMAGEN
        )
        
        if imagenes_encontradas:
            # Cargar la primera imagen encontrada
            if self._cargar_imagen_optimizada(imagenes_encontradas[0]):
                print(f"Imagen cargada desde: {imagenes_encontradas[0]}")
                return
        
        # Si no se encuentra la imagen, mostrar información útil
        self._mostrar_info_archivos_disponibles()

    def _mostrar_info_archivos_disponibles(self):
        """Muestra información sobre archivos disponibles cuando no se encuentra la imagen"""
        info_texto = "Imagen de resultados no encontrada\n\n"
        info_texto += "Análisis en progreso o incompleto.\n"
        
        # Mostrar qué archivos sí existen (limitado para mejor rendimiento)
        try:
            archivos_existentes = []
            with os.scandir(self.data_folder) as entries:
                for entry in entries:
                    if entry.is_file():
                        archivos_existentes.append(entry.name)
                    elif entry.is_dir():
                        archivos_existentes.append(f"{entry.name}/")
            
            if archivos_existentes:
                info_texto += f"\nArchivos encontrados:\n"
                # Mostrar máximo 10 archivos para mejor rendimiento
                for archivo in sorted(archivos_existentes)[:10]:
                    info_texto += f"• {archivo}\n"
                if len(archivos_existentes) > 10:
                    info_texto += f"... y {len(archivos_existentes) - 10} más"
            else:
                info_texto += "\nCarpeta vacía"
        except Exception as e:
            info_texto += f"\nError al listar archivos: {e}"
        
        self.image_label.setText(info_texto)

    def refrescar_datos(self):
        """Refresca los datos y las imágenes"""
        print("Refrescando datos...")
        self.cargar_datos_csv_filtrado()
        self.cargar_imagenes_estrellas()
        
        QMessageBox.information(
            self,
            "Datos Refrescados",
            "Los datos han sido actualizados con cualquier nuevo resultado disponible."
        )

    def exportar_resultados(self):
        """Exporta los resultados a un archivo de manera optimizada"""
        try:
            # Abrir diálogo para seleccionar ubicación
            ruta_exportacion, _ = QFileDialog.getSaveFileName(
                self,
                "Exportar Resultados",
                "resultados_analisis.csv",
                "CSV files (*.csv);;All files (*.*)"
            )
            
            if ruta_exportacion:
                # Crear DataFrame optimizado directamente desde la tabla
                datos = self._extraer_datos_tabla()
                headers = self._extraer_headers_tabla()
                
                # Crear y guardar DataFrame
                df = pd.DataFrame(datos, columns=headers)
                df.to_csv(ruta_exportacion, index=False)
                
                QMessageBox.information(
                    self,
                    "Exportación Completada",
                    f"Los resultados se han exportado exitosamente a:\n{ruta_exportacion}"
                )
                
        except Exception as e:
            QMessageBox.critical(
                self,
                "Error de Exportación",
                f"Error al exportar los resultados:\n{str(e)}"
            )

    def _extraer_datos_tabla(self):
        """Extrae datos de la tabla de manera optimizada"""
        datos = []
        for row in range(self.table_main.rowCount()):
            fila = []
            for col in range(self.table_main.columnCount()):
                item = self.table_main.item(row, col)
                fila.append(item.text() if item else "")
            datos.append(fila)
        return datos

    def _extraer_headers_tabla(self):
        """Extrae headers de la tabla"""
        headers = []
        for col in range(self.table_main.columnCount()):
            header_item = self.table_main.horizontalHeaderItem(col)
            headers.append(header_item.text() if header_item else f"Col_{col+1}")
        return headers

    def cargar_datos_csv_filtrado(self):
        """Carga los datos del CSV filtrado generado en la carpeta de análisis de manera optimizada"""
        # Primera prioridad: ruta específica del CSV filtrado
        if self.ruta_csv_filtrado and os.path.exists(self.ruta_csv_filtrado):
            if self._cargar_csv_seguro(self.ruta_csv_filtrado):
                return
        
        # Segunda prioridad: buscar en carpeta de análisis específica
        if self.data_folder:
            csv_encontrado = self._buscar_csv_filtrado_en_carpeta(self.data_folder)
            if csv_encontrado and self._cargar_csv_seguro(csv_encontrado):
                return
        
        # Tercera prioridad: buscar en directorio raíz del proyecto
        csv_encontrado = self._buscar_csv_filtrado_en_raiz()
        if csv_encontrado and self._cargar_csv_seguro(csv_encontrado):
            return
        
        # Si no se encuentra nada
        print("No se encontró CSV de datos filtrados")

    def _cargar_csv_seguro(self, ruta_csv):
        """Carga un CSV de manera segura con manejo de errores optimizado"""
        try:
            self.cargar_csv_datos_filtrados(ruta_csv)
            print(f"Datos cargados desde: {os.path.basename(ruta_csv)}")
            return True
        except Exception as e:
            print(f"Error al cargar CSV {ruta_csv}: {e}")
            return False

    def _buscar_csv_filtrado_en_carpeta(self, carpeta):
        """Busca archivos CSV filtrados en una carpeta específica"""
        try:
            csvs_filtrados = [
                os.path.join(carpeta, archivo)
                for archivo in os.listdir(carpeta)
                if archivo.startswith('datos_filtrados_') and archivo.endswith('.csv')
            ]
            return max(csvs_filtrados, key=os.path.getmtime) if csvs_filtrados else None
        except Exception as e:
            print(f"Error al buscar CSVs filtrados en {carpeta}: {e}")
            return None

    def _buscar_csv_filtrado_en_raiz(self):
        """Busca archivos CSV filtrados en el directorio raíz del proyecto"""
        script_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        return self._buscar_csv_filtrado_en_carpeta(script_dir)
    
    def cargar_csv_datos_filtrados(self, ruta_csv):
        """Carga datos desde el CSV de datos filtrados (sin headers)"""
        try:
            # Leer CSV sin headers (como se genera en el análisis)
            df = pd.read_csv(ruta_csv, header=None)
            
            # Asignar nombres de columnas según el formato generado
            if len(df.columns) == 4:
                df.columns = ['V', 'I', 'MV', 'MI']
            else:
                # Si tiene diferente número de columnas, usar nombres genéricos
                df.columns = [f'Col_{i+1}' for i in range(len(df.columns))]
            
            # Agregar columna de número de estrella (índice + 1)
            df.insert(0, 'N°', range(1, len(df) + 1))
            
            # Configurar tabla
            self.table_main.setRowCount(len(df))
            self.table_main.setColumnCount(len(df.columns))
            self.table_main.setHorizontalHeaderLabels(df.columns.tolist())
            
            # Llenar tabla con datos
            for row in range(len(df)):
                for col in range(len(df.columns)):
                    valor = df.iloc[row, col]
                    
                    # Mostrar valores sin redondear (usar el valor completo)
                    if isinstance(valor, (int, float)):
                        texto = str(valor)  # Usar el valor completo sin formatear
                    else:
                        texto = str(valor)
                    
                    item = QTableWidgetItem(texto)
                    item.setTextAlignment(Qt.AlignCenter)
                    self.table_main.setItem(row, col, item)
            
            # Ajustar ancho de columnas
            self.table_main.setColumnWidth(0, self.ancho_celda_1)   # N° - 48px
            for col in range(1, self.table_main.columnCount()):
                self.table_main.setColumnWidth(col, self.ancho_celda)  # Columnas restantes - 130px
            
        except Exception as e:
            print(f"Error al cargar CSV de datos filtrados: {e}")
            # self.mostrar_datos_ejemplo()

    def cargar_imagenes_estrellas(self):
        """Carga las imágenes generadas por procesofull.py desde las carpetas de estrellas de manera optimizada"""
        self.imagenes_estrellas = []
        
        if not self._validar_carpeta_analisis():
            return
        
        # Buscar imágenes de manera eficiente
        try:
            self.imagenes_estrellas = self._buscar_imagenes_en_carpetas_estrellas()
            
            if self.imagenes_estrellas:
                self._configurar_visualizacion_imagenes()
            else:
                self._mostrar_mensaje_sin_imagenes()
                
        except Exception as e:
            self._manejar_error_carga_imagenes(e)

    def _validar_carpeta_analisis(self):
        """Valida que la carpeta de análisis exista"""
        if not self.data_folder or not os.path.exists(self.data_folder):
            self.image_label.setText("No se encontró la carpeta de análisis")
            self.actualizar_controles_navegacion()
            self.table_main.clearSelection()
            return False
        return True

    def _buscar_imagenes_en_carpetas_estrellas(self):
        """Busca imágenes en carpetas de estrellas de manera optimizada"""
        imagenes = []
        
        # Usar os.scandir para mejor rendimiento
        with os.scandir(self.data_folder) as entries:
            carpetas_estrella = [
                entry for entry in entries 
                if entry.is_dir() and entry.name.startswith('star')
            ]
        
        # Procesar cada carpeta de estrella
        for carpeta_entry in carpetas_estrella:
            imagenes_carpeta = self._buscar_imagenes_en_carpeta(carpeta_entry)
            imagenes.extend(imagenes_carpeta)
        
        # Ordenar por número de estrella
        return sorted(imagenes, key=lambda x: int(x['estrella']) if x['estrella'].isdigit() else 0)

    def _buscar_imagenes_en_carpeta(self, carpeta_entry):
        """Busca imágenes en una carpeta específica de estrella"""
        imagenes = []
        numero_estrella = carpeta_entry.name.replace('star', '')
        
        try:
            with os.scandir(carpeta_entry.path) as archivos:
                for archivo in archivos:
                    if archivo.is_file() and self._es_archivo_imagen(archivo.name):
                        imagenes.append({
                            'ruta': archivo.path,
                            'estrella': numero_estrella,
                            'nombre': archivo.name,
                            'carpeta': carpeta_entry.name
                        })
        except Exception as e:
            print(f"Error al buscar imágenes en {carpeta_entry.name}: {e}")
            
        return imagenes

    def _es_archivo_imagen(self, nombre_archivo):
        """Verifica si un archivo es una imagen usando extensiones predefinidas"""
        return any(nombre_archivo.lower().endswith(ext) for ext in AppConstants.IMAGEN_EXTENSIONES)

    def _configurar_visualizacion_imagenes(self):
        """Configura la visualización cuando hay imágenes disponibles"""
        print(f"Encontradas {len(self.imagenes_estrellas)} imágenes de estrellas")
        self.imagen_actual_index = 0
        self.mostrar_imagen_actual()
        self.actualizar_controles_navegacion()

    def _mostrar_mensaje_sin_imagenes(self):
        """Muestra mensaje cuando no hay imágenes disponibles"""
        mensaje = ("No se encontraron imágenes en las carpetas de estrellas\n\n"
                  "Las imágenes se generan durante el procesamiento.\n"
                  "Usa 'Refrescar Datos' si el análisis continúa.")
        self.image_label.setText(mensaje)
        print("No se encontraron imágenes en las carpetas de estrellas")
        self.actualizar_titulo()
        self.table_main.clearSelection()
        self.actualizar_controles_navegacion()

    def _manejar_error_carga_imagenes(self, error):
        """Maneja errores durante la carga de imágenes"""
        mensaje_error = f"Error al buscar imágenes: {str(error)}"
        self.image_label.setText(mensaje_error)
        print(f"Error al cargar imágenes de estrellas: {error}")
        self.actualizar_controles_navegacion()
        self.actualizar_titulo()
        self.table_main.clearSelection()

    def mostrar_imagen_actual(self):
        """Muestra la imagen actual según el índice"""
        if not self.imagenes_estrellas or self.imagen_actual_index >= len(self.imagenes_estrellas):
            return
        
        imagen_info = self.imagenes_estrellas[self.imagen_actual_index]
        
        try:
            pixmap = QPixmap(imagen_info['ruta'])
            if not pixmap.isNull():
                # Escalar imagen para que quepa bien en el área
                scaled_pixmap = pixmap.scaled(
                    self.imagen_ancho_fijo,  # Usar configuración centralizada
                    self.imagen_alto_maximo,  # Usar configuración centralizada
                    Qt.KeepAspectRatio, 
                    Qt.SmoothTransformation
                )
                self.image_label.setPixmap(scaled_pixmap)
                self.image_label.setText("")
                print(f"Mostrando imagen de estrella {imagen_info['estrella']}: {imagen_info['nombre']}")
            else:
                self.image_label.setText(f"Error al cargar imagen de estrella {imagen_info['estrella']}")
        except Exception as e:
            self.image_label.setText(f"Error al mostrar imagen: {str(e)}")
            print(f"Error al mostrar imagen: {e}")
        
        self.actualizar_controles_navegacion()
        
        # Actualizar título con el número de estrella actual
        self.actualizar_titulo()
        
        # Seleccionar la fila correspondiente en la tabla
        self.seleccionar_fila_estrella_actual()

    def seleccionar_fila_estrella_actual(self):
        """Selecciona la fila en la tabla que corresponde a la estrella actual"""
        if not self.imagenes_estrellas or self.imagen_actual_index >= len(self.imagenes_estrellas):
            return
        
        imagen_info = self.imagenes_estrellas[self.imagen_actual_index]
        numero_estrella = imagen_info['estrella']
        
        # Buscar la fila que corresponde a esta estrella
        for row in range(self.table_main.rowCount()):
            # Verificar la primera columna (N°) para encontrar la estrella correspondiente
            item = self.table_main.item(row, 0)
            if item and item.text() == numero_estrella:
                # Limpiar selección anterior
                self.table_main.clearSelection()
                
                # Seleccionar toda la fila
                self.table_main.selectRow(row)
                
                # Hacer scroll para que la fila sea visible
                self.table_main.scrollToItem(item)
                
                print(f"Fila seleccionada: {row + 1} (Estrella {numero_estrella})")
                break

    def actualizar_controles_navegacion(self):
        """Actualiza los controles de navegación entre imágenes"""
        # Verificar que los controles de navegación existan antes de actualizarlos
        if not hasattr(self, 'btn_anterior') or not hasattr(self, 'btn_siguiente') or not hasattr(self, 'label_imagen_info'):
            print("Controles de navegación no disponibles aún durante la inicialización")
            return
            
        total_imagenes = len(self.imagenes_estrellas)
        
        if total_imagenes == 0:
            self.btn_anterior.setEnabled(False)
            self.btn_siguiente.setEnabled(False)
            self.label_imagen_info.setText("Sin imágenes")
        else:
            self.btn_anterior.setEnabled(self.imagen_actual_index > 0)
            self.btn_siguiente.setEnabled(self.imagen_actual_index < total_imagenes - 1)
            
            imagen_info = self.imagenes_estrellas[self.imagen_actual_index]
            self.label_imagen_info.setText(f"Estrella {imagen_info['estrella']} ({self.imagen_actual_index + 1}/{total_imagenes})")

    def imagen_anterior(self):
        """Muestra la imagen anterior"""
        if self.imagen_actual_index > 0:
            self.imagen_actual_index -= 1
            # Verificar si estamos en modo ejemplo o modo real
            if hasattr(self, 'data_folder') and self.data_folder and os.path.exists(self.data_folder):
                self.mostrar_imagen_actual()
            else:
                # Modo ejemplo
                # self.mostrar_imagen_ejemplo()
                pass

    def imagen_siguiente(self):
        """Muestra la imagen siguiente"""
        if self.imagen_actual_index < len(self.imagenes_estrellas) - 1:
            self.imagen_actual_index += 1
            # Verificar si estamos en modo ejemplo o modo real
            if hasattr(self, 'data_folder') and self.data_folder and os.path.exists(self.data_folder):
                self.mostrar_imagen_actual()
            else:
                # Modo ejemplo
                # self.mostrar_imagen_ejemplo()
                pass

    def nuevo_analisis(self):
        """Vuelve a la ventana anterior para realizar un nuevo análisis"""
        if self.ventana_anterior:
            self.ventana_anterior.show()
        self.close()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = DatosF()
    window.show()
    sys.exit(app.exec_())


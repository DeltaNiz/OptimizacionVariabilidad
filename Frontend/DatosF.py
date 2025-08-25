from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QTableWidget, QTableWidgetItem, QPushButton, QLabel,
    QFrame, QScrollArea, QMessageBox, QFileDialog
)
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QCursor, QPixmap
import os
import sys
import pandas as pd

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
    WINDOW_MEDIUM = (1350, 950)
    WINDOW_LARGE = (1600, 1000)
    
    # Headers de tabla
    TABLE_HEADERS = ["Archivo", "ID", "RA", "DEC", "Magnitud", "Período", "Amplitud", "Tipo", "Significancia"]
    
    # Extensiones de archivos
    EXTENSIONES_IMAGEN = ['.png', '.jpg', '.jpeg', '.gif', '.bmp']
    CSV_EXTENSIONS = ['.csv']
    
    # Patrones de archivos
    PATRON_DATOS_FILTRADOS = 'datos_filtrados_*.csv'
    PATRON_CARPETAS_ESTRELLA = 'star*'
    
    # Mensajes
    MSG_SIN_IMAGENES = ("No se encontraron imágenes en las carpetas de estrellas\n\n"
                       "Las imágenes se generan durante el procesamiento.\n"
                       "Verifica que el análisis haya finalizado correctamente.")
    MSG_SIN_CARPETA = "No se encontró la carpeta de análisis"
    
    # Colores del tema
    COLOR_VERDE_PRINCIPAL = "#a7c942"
    COLOR_VERDE_HOVER = "#98b83b"
    COLOR_VERDE_PRESSED = "#7a9530"
    COLOR_VERDE_BORDER = "#98b83b"

# Estilos CSS centralizados
class StyleSheets:
    HEADER_TABLE = """
        QHeaderView::section { 
            background-color: #a7c942; 
            color: white; 
            font-weight: bold;
            border: 1px solid #98b83b;
            padding: 5px;
            text-align: center;
            border-style: solid;
            border-top: none;
            border-left: none;
            border-right: 1px solid #98b83b;
            border-bottom: 1px solid #98b83b;
        }
        QHeaderView::section:hover {
            background-color: #a7c942;
        }
        QHeaderView::section:pressed {
            background-color: #a7c942;
        }
    """
    
    TABLE_MAIN = """
        QTableWidget {
            gridline-color: #a7c942;
            background-color: white;
            alternate-background-color: #f0f0f0;
            margin: 10px;
        }
        QTableWidget::item {
            border: 1px solid #a7c942;
        }
        QTableWidget::item:selected {
            background-color: #98b83b;
            color: white;
        }
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
    
    BUTTON_NAVIGATION = """
        QPushButton {
            font-size: 11px;
            color: white;
            font-weight: bold;
            border: none;
            padding: 5px 10px;
            border-radius: 4px;
            background-color: #6c757d;
        }
        QPushButton:hover {
            background-color: #5a6268;
        }
        QPushButton:disabled {
            background-color: #cccccc;
            color: #666666;
        }
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
    
    BUTTON_EXPORTAR = """
        QPushButton {
            font-size: 12px;
            color: white;
            font-weight: bold;
            border: none;
            padding: 5px 20px;
            border-radius: 8px;
            background-color: #a7c942;
        }
        QPushButton:hover {
            background-color: #98b83b;
        }
        QPushButton:pressed {
            background-color: #7a9530;
        }
    """
    
    BUTTON_NUEVO_ANALISIS = """
        QPushButton {
            font-size: 12px;
            color: white;
            font-weight: bold;
            border: none;
            padding: 5px 20px;
            border-radius: 8px;
            background-color: #5bc0de;
        }
        QPushButton:hover {
            background-color: #46b8da;
        }
        QPushButton:pressed {
            background-color: #31b0d5;
        }
    """
    
    IMAGE_LABEL = """
        QLabel {
            border: 2px solid #a7c942;
            border-radius: 5px;
            background-color: #f9f9f9;
            padding: 10px;
        }
    """
    
    SEPARATOR = "QFrame { color: #a7c942; background-color: #a7c942; }"

class DatosF(QMainWindow):
    def __init__(self, data_folder=None, datos_formulario=None, ventana_anterior=None, ruta_csv_filtrado=None, ventana_subir=None):
        super().__init__()
        self.data_folder = data_folder or ""
        self.datos_formulario = datos_formulario or {}
        self.ventana_anterior = ventana_anterior
        self.ventana_subir = ventana_subir
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
        else:
            # Para pantallas medianas y grandes: centrar y hacer no redimensionable
            QTimer.singleShot(50, self.centrar_ventana)
            # Hacer la ventana no redimensionable después de configurar el layout
            # (solo para pantallas medianas y grandes, pantallas pequeñas mantienen redimensionamiento)
            if hasattr(self, 'window_size') and self.window_size:
                self.setFixedSize(*self.window_size)
    
    def centrar_ventana(self):
        """Centra la ventana en la pantalla con un pequeño offset en altura"""
        try:
            from PyQt5.QtWidgets import QApplication
            desktop = QApplication.desktop()
            screen_geometry = desktop.screenGeometry()
            
            # Calcular posición central con offset en altura
            x = (screen_geometry.width() - self.width()) // 2
            y = (screen_geometry.height() - self.height()) // 2 - 50  # Offset de 50px hacia arriba
            
            # Posicionar la ventana en el centro
            self.move(max(0, x), max(0, y))
            print(f"Ventana DatosF centrada en posición ({x}, {y}) con offset")
        except Exception as e:
            print(f"Error al centrar ventana: {e}")

    def _configure_screen_layout(self, screen_width):
        """Configura el layout según el tamaño de pantalla"""
        if screen_width <= AppConstants.SCREEN_SMALL:
            # Para pantallas pequeñas, marcar para maximizar automáticamente
            self.ventana_maximizada = True
            self.window_size = None  # No hay tamaño fijo para pantallas pequeñas
            layout_margin = 5
            print(f"Pantalla pequeña detectada ({screen_width}px) - Ventana será maximizada automáticamente")
        elif screen_width <= AppConstants.SCREEN_MEDIUM:
            self.ancho_celda = AppConstants.ANCHO_CELDA_SCREEN_1920
            self.ancho_celda_1 = AppConstants.ANCHO_CELDA_PRIMERA_1920
            self.window_size = AppConstants.WINDOW_MEDIUM
            layout_margin = 5
        else:
            self.window_size = AppConstants.WINDOW_LARGE
            layout_margin = 20
        return layout_margin

    def _setup_main_table(self):
        """Configura la tabla principal con estilos optimizados"""
        self.table_main = QTableWidget()
        self.table_main.setRowCount(0)
        self.table_main.setColumnCount(0)

        # Ocultar la numeración automática de filas
        self.table_main.verticalHeader().setVisible(False)
        
        # Hacer la tabla no editable
        self.table_main.setEditTriggers(QTableWidget.NoEditTriggers)
        
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
        # Eliminar el efecto 3D del marco del scroll area
        self.scroll_area.setFrameShape(QFrame.NoFrame)
        self.scroll_area.setFrameShadow(QFrame.Plain)
        
        self.image_label = QLabel()
        self.image_label.setAlignment(Qt.AlignCenter)
        self.image_label.setText("Cargando imágenes...")
        self.image_label.setStyleSheet(StyleSheets.IMAGE_LABEL)
        
        self.scroll_area.setWidget(self.image_label)
        
        # Controles para navegar entre imágenes
        navegacion_layout = self._create_navigation_controls()
        
        # Área de logs para mostrar datos de análisis
        self.logs_area = self._create_logs_area()
        
        layout.addWidget(self.scroll_area)
        layout.addLayout(navegacion_layout)
        layout.addWidget(self.logs_area)

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

    def _create_logs_area(self):
        """Crea el área de logs para mostrar datos de análisis"""
        logs_frame = QFrame()
        logs_frame.setFrameStyle(QFrame.StyledPanel)
        logs_frame.setMaximumHeight(130)

        logs_frame.setStyleSheet("""
            QFrame {
                border: 2px solid #a7c942;
                border-radius: 5px;
                background-color: #f9f9f9;
                padding: 2px;
            }
        """)
        
        logs_layout = QVBoxLayout()
        # Reducir márgenes para maximizar el espacio utilizable
        logs_layout.setContentsMargins(5, 5, 5, 5)
        logs_layout.setSpacing(2)
        
        # Área de texto para mostrar los logs
        self.logs_text = QLabel()
        self.logs_text.setAlignment(Qt.AlignTop | Qt.AlignLeft)
        self.logs_text.setStyleSheet("""
            QLabel {
                font-family: 'Courier New', monospace;
                font-size: 12px;
                color: #444;
                background-color: #fff;
                padding: 6px;
                border: none;
                selection-background-color: #3390ff;
            }
        """)
        self.logs_text.setText("Selecciona una estrella para ver sus datos de análisis...")
        self.logs_text.setWordWrap(True)
        self.logs_text.setTextInteractionFlags(Qt.TextSelectableByMouse)
        
        # Scroll area para el contenido de logs
        logs_scroll = QScrollArea()
        logs_scroll.setWidgetResizable(True)
        logs_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        logs_scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        logs_scroll.setWidget(self.logs_text)
        # Eliminar borde del scroll area para evitar bordes múltiples
        logs_scroll.setFrameStyle(QFrame.NoFrame)
        logs_scroll.setStyleSheet("""
            QScrollArea {
                border: none;
                background-color: transparent;
            }
        """)
        # Remover limitación de altura máxima para que use todo el espacio disponible
        
        logs_layout.addWidget(logs_scroll)
        
        logs_frame.setLayout(logs_layout)
        return logs_frame

    def cargar_datos_reporte_analisis(self):
        """Carga los datos del reporte Best_Peak_GLS_Min_PDM.csv"""
        self.datos_reporte = {}
        
        if not self.data_folder:
            return
        
        # Buscar el archivo de reporte en la carpeta de análisis
        ruta_reporte = os.path.join(self.data_folder, 'Best_Peak_GLS_Min_PDM.csv')
        
        if os.path.exists(ruta_reporte):
            try:
                import pandas as pd
                df_reporte = pd.read_csv(ruta_reporte)
                
                print(f"Cargando reporte desde: {ruta_reporte}")
                print(f"Columnas encontradas: {list(df_reporte.columns)}")
                print(f"Número de filas: {len(df_reporte)}")
                
                # Convertir a diccionario indexado por número de estrella
                for _, row in df_reporte.iterrows():
                    if 'star' in row:
                        star_name = str(row['star'])  # "star1", "star2", etc.
                        
                        # Extraer solo el número de la estrella
                        if star_name.startswith('star'):
                            star_number = star_name.replace('star', '')
                        else:
                            star_number = star_name
                        
                        self.datos_reporte[star_number] = {
                            'status': row.get('status', 'N/A'),
                            'time': row.get('time', 0),
                            'Best Peak GLS V': row.get('Best Peak GLS V', 'N/A'),
                            'Best Peak GLS I': row.get('Best Peak GLS I', 'N/A'),
                            'Best Minima PDM V': row.get('Best Minima PDM V', 'N/A'),
                            'Best Minima PDM I': row.get('Best Minima PDM I', 'N/A')
                        }
                
                print(f"Datos de reporte cargados: {len(self.datos_reporte)} estrellas")
                print(f"Claves en datos_reporte: {list(self.datos_reporte.keys())}")
                
            except Exception as e:
                print(f"Error al cargar reporte de análisis: {e}")
                import traceback
                traceback.print_exc()
                self.datos_reporte = {}
        else:
            print(f"No se encontró el archivo de reporte en: {ruta_reporte}")
            print(f"Contenido de la carpeta: {os.listdir(self.data_folder) if os.path.exists(self.data_folder) else 'Carpeta no existe'}")

    def mostrar_datos_estrella_actual(self):
        """Muestra los datos de análisis de la estrella actual en el área de logs"""
        if not hasattr(self, 'logs_text'):
            print("logs_text no existe todavía")
            return
            
        numero_estrella = self.obtener_numero_estrella_actual()

        if not numero_estrella:
            self.logs_text.setText("No se pudo determinar el número de estrella actual.")
            return
            
        if not hasattr(self, 'datos_reporte') or not self.datos_reporte:
            self.logs_text.setText("No se han cargado los datos del reporte de análisis.")
            return
            
        if numero_estrella not in self.datos_reporte:
            self.logs_text.setText(f"No hay datos de análisis disponibles para la estrella {numero_estrella}.\nDatos disponibles para: {', '.join(self.datos_reporte.keys())}")
            return
        
        datos = self.datos_reporte[numero_estrella]
        
        # Formatear los datos para mostrar
        texto_logs = f"<b>ESTRELLA {numero_estrella}</b><br><br>"
        
        # Estado del procesamiento
        status = datos.get('status', 'N/A')
        tiempo = datos.get('time', 0)
        
        if status == 'success':
            texto_logs += f"<span style='color: green;'>Procesamiento exitoso</span><br>"
        elif status == 'error':
            texto_logs += f"<span style='color: red;'>Error en procesamiento</span><br>"
        else:
            texto_logs += f"<span style='color: orange;'>Estado: {status}</span><br>"
        
        texto_logs += f"<span style='color: #666;'>Tiempo de procesamiento: {tiempo:.2f}s</span><br><br>"
        
        # Datos de análisis
        if status == 'success':
            texto_logs += "<b>PERÍODOS DETECTADOS:</b><br><br>"
            
            # GLS (Generalized Lomb-Scargle)
            gls_v = datos.get('Best Peak GLS V', 'N/A')
            gls_i = datos.get('Best Peak GLS I', 'N/A')
            
            texto_logs += "<u>Análisis GLS:</u><br>"
            texto_logs += f"• Filtro V: <b>{gls_v}</b> días<br>"
            texto_logs += f"• Filtro I: <b>{gls_i}</b> días<br><br>"
            
            # PDM (Phase Dispersion Minimization)
            pdm_v = datos.get('Best Minima PDM V', 'N/A')
            pdm_i = datos.get('Best Minima PDM I', 'N/A')
            
            texto_logs += "<u>Análisis PDM:</u><br>"
            texto_logs += f"• Filtro V: <b>{pdm_v}</b> días<br>"
            texto_logs += f"• Filtro I: <b>{pdm_i}</b> días<br><br>"
            
        else:
            # Mostrar información de error si está disponible
            mensaje = datos.get('message', 'No hay información adicional disponible')
            texto_logs += f"<b>DETALLES DEL ERROR:</b><br>"
            texto_logs += f"<span style='color: red;'>{mensaje}</span><br>"
        
        self.logs_text.setText(texto_logs)

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
        separator.setFrameShadow(QFrame.Plain)
        separator.setStyleSheet(StyleSheets.SEPARATOR)
        return separator

    def _create_vertical_separator(self):
        """Crea un separador vertical personalizado"""
        separator = QFrame()
        separator.setFrameShape(QFrame.VLine)
        separator.setFrameShadow(QFrame.Plain)
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
        """Sobrescribe el evento de redimensionamiento"""
        super().resizeEvent(event)
        # No forzar maximización en resizeEvent para permitir redimensionamiento libre
        # en pantallas pequeñas. La maximización inicial se maneja en asegurar_maximizacion()

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
        
        # Cargar datos del reporte de análisis
        self.cargar_datos_reporte_analisis()
        
        # Buscar imágenes de manera eficiente
        try:
            self.imagenes_estrellas = self._buscar_imagenes_en_carpetas_estrellas()
            self._configurar_visualizacion_imagenes()
        except Exception as e:
            print(f"Error al cargar imágenes de estrellas: {e}")
            self._mostrar_mensaje_sin_imagenes()

    def _validar_carpeta_analisis(self):
        """Valida que la carpeta de análisis exista"""
        if not self.data_folder or not os.path.exists(self.data_folder):
            self._mostrar_mensaje_sin_imagenes()
            return False
        return True

    def _buscar_imagenes_en_carpetas_estrellas(self):
        """Busca imágenes en carpetas de estrellas de manera optimizada"""
        imagenes = []
        try:
            with os.scandir(self.data_folder) as entries:
                for entry in entries:
                    if entry.is_dir() and entry.name.startswith('star'):
                        imagenes_carpeta = self._buscar_imagenes_en_carpeta(entry)
                        imagenes.extend(imagenes_carpeta)
        except Exception as e:
            print(f"Error al buscar imágenes en carpetas: {e}")
        return imagenes

    def _buscar_imagenes_en_carpeta(self, carpeta_entry):
        """Busca imágenes en una carpeta específica de estrella"""
        imagenes = []
        try:
            with os.scandir(carpeta_entry.path) as archivos:
                for archivo in archivos:
                    if archivo.is_file() and self._es_archivo_imagen(archivo.name):
                        # Extraer número de estrella del nombre de la carpeta
                        numero_estrella = carpeta_entry.name.replace('star', '')
                        
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
        """Verifica si un archivo es una imagen válida"""
        return any(nombre_archivo.lower().endswith(ext) for ext in AppConstants.EXTENSIONES_IMAGEN)

    def _configurar_visualizacion_imagenes(self):
        """Configura la visualización inicial de imágenes"""
        if self.imagenes_estrellas:
            # Ordenar imágenes por número de estrella
            self.imagenes_estrellas.sort(key=lambda x: int(x['estrella']))
            print(f"Encontradas {len(self.imagenes_estrellas)} imágenes de estrellas")
            self.imagen_actual_index = 0
            self.mostrar_imagen_actual()
            self.actualizar_controles_navegacion()
        else:
            print("No se encontraron imágenes")
            self._mostrar_mensaje_sin_imagenes()

    def _mostrar_mensaje_sin_imagenes(self):
        """Muestra mensaje cuando no hay imágenes disponibles"""
        mensaje = ("No se encontraron imágenes en las carpetas de estrellas\n\n"
                  "Las imágenes se generan durante el procesamiento.\n"
                  "Verifica que el análisis haya finalizado correctamente.")
        self.image_label.setText(mensaje)
        print("No se encontraron imágenes en las carpetas de estrellas")
        self.actualizar_titulo()
        self.table_main.clearSelection()
        self.actualizar_controles_navegacion()
        
        # Mostrar mensaje por defecto en los logs cuando no hay imágenes
        if hasattr(self, 'logs_text'):
            self.logs_text.setText("No se encontraron imágenes de análisis.\n\nLos datos de análisis se mostrarán aquí cuando las imágenes estén disponibles.")

    def mostrar_imagen_actual(self):
        """Muestra la imagen actual basada en el índice"""
        if not self.imagenes_estrellas or self.imagen_actual_index >= len(self.imagenes_estrellas):
            self._mostrar_mensaje_sin_imagenes()
            return
        
        imagen_info = self.imagenes_estrellas[self.imagen_actual_index]
        
        try:
            if self._cargar_imagen_optimizada(imagen_info['ruta']):
                self.actualizar_titulo()
                self.seleccionar_fila_estrella_actual()
                self.mostrar_datos_estrella_actual()
                # Actualizar controles de navegación después de mostrar la imagen
                self.actualizar_controles_navegacion()
            else:
                self._mostrar_mensaje_sin_imagenes()
        except Exception as e:
            print(f"Error al mostrar imagen actual: {e}")
            self._mostrar_mensaje_sin_imagenes()

    def seleccionar_fila_estrella_actual(self):
        """Selecciona la fila correspondiente a la estrella actual en la tabla"""
        if not self.imagenes_estrellas or self.imagen_actual_index >= len(self.imagenes_estrellas):
            return
        
        try:
            numero_estrella = self.imagenes_estrellas[self.imagen_actual_index]['estrella']
            
            # Buscar la fila que corresponde a esta estrella
            for row in range(self.table_main.rowCount()):
                item_primera_columna = self.table_main.item(row, 0)
                if item_primera_columna and item_primera_columna.text() == numero_estrella:
                    self.table_main.selectRow(row)
                    break
        except Exception as e:
            print(f"Error al seleccionar fila de estrella: {e}")

    def actualizar_controles_navegacion(self):
        """Actualiza el estado de los controles de navegación"""
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
        """Vuelve a la ventana 'Subir Archivos' para realizar un nuevo análisis"""
        if self.ventana_subir:
            self.ventana_subir.show()
            self.ventana_subir.raise_()
            self.ventana_subir.activateWindow()
        self.close()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = DatosF()
    window.show()
    sys.exit(app.exec_())


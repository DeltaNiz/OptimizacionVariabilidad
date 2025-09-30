from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QTableWidget, QTableWidgetItem, QPushButton, QLabel,
    QLineEdit, QFrame, QCheckBox, QMessageBox
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QCursor, QColor
import sys
import pandas as pd
import os
# Importar funciones de análisis
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from Analisis import realizar_analisis_completo

class AppConstants:
    """Constantes centralizadas para la aplicación DatosNF"""
    
    # Configuraciones de pantalla
    SCREEN_SMALL = 1366
    SCREEN_MEDIUM = 1920
    
    # Dimensiones de ventana por tipo de pantalla
    WINDOW_SMALL = (1175, 666)
    WINDOW_MEDIUM = (1159, 800)
    WINDOW_LARGE = (1600, 1000)
    
    # Headers de tablas
    TABLE_MAIN_HEADERS = ["N°", "V", "I", "MV", "MI", "Desc."]
    TABLE_DESCARTADAS_HEADERS = ["N°", "V", "I", "MV", "MI"]
    
    # Configuraciones de columnas - Tabla Principal
    COL_WIDTH_MAIN = {
        0: 48,   # N°
        1: 130,  # V
        2: 130,  # I
        3: 130,  # MV
        4: 130,  # MI
        5: 62    # Desc.
    }
    
    # Configuraciones de columnas - Tabla Descartadas
    COL_WIDTH_DESC = {
        0: 50,   # N°
        1: 87,   # V
        2: 87,   # I
        3: 87,   # MV
        4: 87    # MI
    }
    
    # Alturas de filas
    ROW_HEIGHT_MAIN = 30
    ROW_HEIGHT_DESC = 28
    
    # Colores del tema
    COLOR_VERDE_PRINCIPAL = "#a7c942"
    COLOR_VERDE_HOVER = "#98b83b"
    COLOR_VERDE_PRESSED = "#7a9530"
    COLOR_VERDE_BORDER = "#98b83b"
    COLOR_ROJO_PRINCIPAL = "#d9534f"
    COLOR_ROJO_HOVER = "#c9302c"
    COLOR_ROJO_PRESSED = "#ac2925"
    COLOR_AMARILLO_MARCA = "#ffff96"  # Color para marcar filas
    
    # Textos de información
    PREFIJO_ARCHIVO = "Archivo"
    LABEL_TOTAL_ESTRELLAS = "Total estrellas"
    LABEL_DESCARTADAS = "Descartadas"
    TEXTO_SIN_ARCHIVO = "Sin archivo cargado"
    LABEL_ESTRELLAS_DISPONIBLES = "Estrellas disponibles"
    LABEL_ESTRELLAS_SELECCIONADAS = "Estrellas seleccionadas"
    
    # Estilos de fuente
    FUENTE_INFORMACION = "font-size: 11px; color: #333333;"
    FUENTE_TITULO = "QLabel { font-size: 16px; font-weight: bold; }"
    FUENTE_SUBTITULO = "QLabel { font-size: 12px; }"

class StyleSheets:
    """Estilos CSS centralizados para la aplicación"""
    
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
    
    INPUT_FIELD = f"""
        QLineEdit {{
            padding: 5px 8px;
            border: 1px solid {AppConstants.COLOR_VERDE_PRINCIPAL};
            border-radius: 4px;
            background-color: white;
            font-size: 12px;
        }}
        QLineEdit:focus {{
            border: 2px solid {AppConstants.COLOR_VERDE_HOVER};
        }}
        QLineEdit::placeholder {{
            color: #888;
            font-style: italic;
        }}
    """
    
    BUTTON_PRIMARY = f"""
        QPushButton {{
            font-size: 12px;
            color: white;
            font-weight: bold;
            background-color: {AppConstants.COLOR_VERDE_PRINCIPAL};
            border: none;
            padding: 5px 20px;
            border-radius: 8px;
        }}
        QPushButton:hover {{
            background-color: {AppConstants.COLOR_VERDE_HOVER};
        }}
        QPushButton:pressed {{
            background-color: {AppConstants.COLOR_VERDE_PRESSED};
        }}
    """
    
    BUTTON_DANGER = f"""
        QPushButton {{
            font-size: 12px;
            color: white;
            font-weight: bold;
            background-color: red;
            border: none;
            padding: 5px 20px;
            border-radius: 8px;
        }}
        QPushButton:hover {{
            background-color: #8a0000;
        }}
        QPushButton:pressed {{
            background-color: {AppConstants.COLOR_VERDE_PRESSED};
        }}
    """
    
    BUTTON_SECONDARY = f"""
        QPushButton {{
            font-size: 11px;
            color: white;
            font-weight: bold;
            background-color: {AppConstants.COLOR_ROJO_PRINCIPAL};
            border: none;
            padding: 5px 10px;
            border-radius: 4px;
        }}
        QPushButton:hover {{
            background-color: {AppConstants.COLOR_ROJO_HOVER};
        }}
        QPushButton:pressed {{
            background-color: {AppConstants.COLOR_ROJO_PRESSED};
        }}
    """
    
    BUTTON_SMALL = f"""
        QPushButton {{
            font-size: 11px;
            color: white;
            font-weight: bold;
            background-color: {AppConstants.COLOR_VERDE_PRINCIPAL};
            border: none;
            padding: 5px 10px;
            border-radius: 4px;
        }}
        QPushButton:hover {{
            background-color: {AppConstants.COLOR_VERDE_HOVER};
        }}
        QPushButton:pressed {{
            background-color: {AppConstants.COLOR_VERDE_PRESSED};
        }}
    """
    
    CHECKBOX = f"""
        QCheckBox::indicator {{
            width: 18px;
            height: 18px;
        }}
        QCheckBox::indicator:unchecked {{
            border: 2px solid {AppConstants.COLOR_VERDE_PRINCIPAL};
            background-color: white;
            border-radius: 3px;
        }}
        QCheckBox::indicator:checked {{
            border: 2px solid {AppConstants.COLOR_VERDE_PRINCIPAL};
            background-color: {AppConstants.COLOR_VERDE_PRINCIPAL};
            border-radius: 3px;
        }}
    """
    
    SEPARATOR = f"QFrame {{ color: {AppConstants.COLOR_VERDE_PRINCIPAL}; }}"

class DatosNF(QMainWindow):
    def __init__(self, datos_formulario=None, ventana_subir=None, ventana_main=None):
        super().__init__()
        self.datos_formulario = datos_formulario or {}
        # Usar referencias simples, no débiles - más estable
        self.ventana_subir = ventana_subir
        self.ventana_main = ventana_main
        self.filas_descartadas = []  # Lista para mantener track de las filas descartadas
        
        # Variables para configuración de período (sin valores por defecto)
        self.periodo_max = None
        self.periodo_min = None
        
        self.init_ui()
    
    def init_ui(self):
        """Inicializa la interfaz de usuario de manera modular"""
        self.setWindowTitle("Optim. Estrellas")
        
        # Configuración responsiva de pantalla
        layout_margin = self._configure_screen_layout()
        
        # Widget central y layout principal
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout()
        main_layout.setContentsMargins(layout_margin, layout_margin, layout_margin, layout_margin)
        main_layout.setSpacing(layout_margin + 5)
        
        # Configurar tabla principal
        self._setup_main_table()
        
        # Cargar datos
        self.cargar_datos_tabla()
        
        # Configurar panel derecho
        right_layout = self._setup_right_panel()
        
        # Crear separador vertical
        separator = self._create_vertical_separator()
        
        # Ensamblar layout principal
        main_layout.addWidget(self.table_main, 19)
        main_layout.addWidget(separator, 0)
        main_layout.addLayout(right_layout, 13)
        
        central_widget.setLayout(main_layout)
        
        # Instalar filtros de eventos
        self.installEventFilter(self)
        
        # Actualizar información final
        self.actualizar_info_estrellas()
        
        # Hacer la ventana no redimensionable después de configurar el layout
        self.setFixedSize(*self.window_size)
        
        # Centrar la ventana en la pantalla con un pequeño offset vertical
        self.centrar_ventana()

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

        except Exception as e:
            print(f"Error al centrar ventana: {e}")

    def _configure_screen_layout(self):
        """Configura el layout según el tamaño de pantalla"""
        screen_width = self.screen().size().width()
        
        if screen_width <= AppConstants.SCREEN_SMALL:
            self.window_size = AppConstants.WINDOW_SMALL
            self.setWindowTitle("SODEV-CG")
            layout_margin = 9
        elif screen_width <= AppConstants.SCREEN_MEDIUM:
            self.window_size = AppConstants.WINDOW_MEDIUM
            self.setWindowTitle("SODEV-CG")
            layout_margin = 5
        else:
            self.window_size = AppConstants.WINDOW_LARGE
            self.setWindowTitle("SODEV-CG")
            layout_margin = 20
        
        return layout_margin

    def _setup_main_table(self):
        """Configura la tabla principal con estilos optimizados"""
        self.table_main = QTableWidget()
        self.table_main.setRowCount(0)
        self.table_main.setColumnCount(len(AppConstants.TABLE_MAIN_HEADERS))
        self.table_main.setHorizontalHeaderLabels(AppConstants.TABLE_MAIN_HEADERS)
        
        # Ocultar numeración automática de filas
        self.table_main.verticalHeader().setVisible(False)
        
        # Hacer la tabla no editable
        self.table_main.setEditTriggers(QTableWidget.NoEditTriggers)
        
        # Instalar filtros de eventos
        self.table_main.viewport().installEventFilter(self)
        self.table_main.itemClicked.connect(self.on_table_main_item_clicked)
        
        # Aplicar estilos centralizados
        header = self.table_main.horizontalHeader()
        header.setStyleSheet(StyleSheets.HEADER_TABLE)
        self.table_main.setStyleSheet(StyleSheets.TABLE_MAIN)
        
        # Configurar colores alternados y dimensiones
        self.table_main.setAlternatingRowColors(True)
        self.table_main.verticalHeader().setDefaultSectionSize(AppConstants.ROW_HEIGHT_MAIN)
        
        # Configurar anchos de columnas
        for col, width in AppConstants.COL_WIDTH_MAIN.items():
            self.table_main.setColumnWidth(col, width)

    def _setup_right_panel(self):
        """Configura el panel derecho completo"""
        right_layout = QVBoxLayout()
        right_layout.setContentsMargins(10, 10, 10, 10)
        right_layout.setSpacing(10)
        
        # Título y subtítulo
        self._setup_header_labels(right_layout)
        
        # Separador
        right_layout.addSpacing(8)
        right_layout.addWidget(self._create_horizontal_separator())
        right_layout.addSpacing(10)
        
        # Tabla de descartadas
        self._setup_descartadas_table(right_layout)
        
        # Botón limpiar
        self._setup_clear_button(right_layout)
        
        # Separador
        right_layout.addWidget(self._create_horizontal_separator())
        right_layout.addSpacing(10)
        
        # Controles de rango
        self._setup_range_controls(right_layout)
        
        # Separador
        right_layout.addSpacing(10)
        right_layout.addWidget(self._create_horizontal_separator())
        right_layout.addSpacing(10)
        
        # Controles de período
        self._setup_periodo_controls(right_layout)
        
        # Separador
        right_layout.addSpacing(10)
        right_layout.addWidget(self._create_horizontal_separator())
        right_layout.addSpacing(10)
        
        # Botones de acción
        self._setup_action_buttons(right_layout)
        right_layout.addSpacing(10)
        
        return right_layout

    def _setup_header_labels(self, layout):
        """Configura las etiquetas de encabezado"""
        label_title = QLabel("<b>Datos Cargados Correctamente</b>")
        label_title.setAlignment(Qt.AlignCenter)
        label_title.setStyleSheet(AppConstants.FUENTE_TITULO)
        
        label_subtitle = QLabel("Seleccione una estrella de la lista para descartarla")
        label_subtitle.setAlignment(Qt.AlignCenter)
        label_subtitle.setStyleSheet(AppConstants.FUENTE_SUBTITULO)
        
        # Etiqueta dinámica para información de estrellas
        self.label_descartadas = QLabel("<b>Estrellas descartadas: 0</b>")
        self.label_descartadas.setAlignment(Qt.AlignCenter)
        
        layout.addWidget(label_title)
        layout.addWidget(label_subtitle)

    def _setup_descartadas_table(self, layout):
        """Configura la tabla de estrellas descartadas"""
        layout.addWidget(self.label_descartadas)
        
        self.table_descartadas = QTableWidget()
        self.table_descartadas.setRowCount(0)
        self.table_descartadas.setColumnCount(len(AppConstants.TABLE_DESCARTADAS_HEADERS))
        self.table_descartadas.setHorizontalHeaderLabels(AppConstants.TABLE_DESCARTADAS_HEADERS)
        
        # Configurar eventos y estilos
        self.table_descartadas.verticalHeader().setVisible(False)
        
        # Hacer que el scroll vertical aparezca siempre
        self.table_descartadas.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        
        # Hacer la tabla no editable
        self.table_descartadas.setEditTriggers(QTableWidget.NoEditTriggers)
        
        self.table_descartadas.viewport().installEventFilter(self)
        self.table_descartadas.itemClicked.connect(self.on_table_descartadas_item_clicked)
        
        # Aplicar estilos
        header_descartadas = self.table_descartadas.horizontalHeader()
        header_descartadas.setStyleSheet(StyleSheets.HEADER_TABLE)
        self.table_descartadas.setStyleSheet(StyleSheets.TABLE_MAIN)
        self.table_descartadas.setAlternatingRowColors(True)
        self.table_descartadas.verticalHeader().setDefaultSectionSize(AppConstants.ROW_HEIGHT_DESC)
        
        # Configurar anchos de columnas
        for col, width in AppConstants.COL_WIDTH_DESC.items():
            self.table_descartadas.setColumnWidth(col, width)
        
        layout.addWidget(self.table_descartadas)

    def _setup_clear_button(self, layout):
        """Configura el botón de limpiar selecciones"""
        btn_limpiar = self._create_button("Limpiar Selecciones", StyleSheets.BUTTON_SECONDARY, self.limpiar_selecciones)
        btn_limpiar.setMaximumWidth(150)
        
        # Layout para centrar el botón
        limpiar_layout = QHBoxLayout()
        limpiar_layout.addStretch()
        limpiar_layout.addWidget(btn_limpiar)
        limpiar_layout.addStretch()
        
        layout.addLayout(limpiar_layout)

    def _setup_range_controls(self, layout):
        """Configura los controles de rango"""
        # Etiqueta del rango
        label_rango = QLabel("<b>Rango de descarte:</b>")
        layout.addWidget(label_rango)
        
        # Layout horizontal para controles
        range_layout = QHBoxLayout()
        
        # Campo de texto para rangos
        self.input_rangos = QLineEdit()
        self.input_rangos.setPlaceholderText("Ej: 1-5, 8, 10-15, 20-25")
        self.input_rangos.setStyleSheet(StyleSheets.INPUT_FIELD)
        self.input_rangos.returnPressed.connect(self.aplicar_rangos)
        
        # Botón aplicar
        btn_aplicar_rangos = self._create_button("Aplicar", StyleSheets.BUTTON_SMALL, self.aplicar_rangos)
        btn_aplicar_rangos.setMaximumWidth(70)
        
        # Ensamblar layout
        range_layout.addWidget(label_rango)
        range_layout.addWidget(self.input_rangos, 1)
        range_layout.addWidget(btn_aplicar_rangos)
        
        layout.addLayout(range_layout)

    def _setup_periodo_controls(self, layout):
        """Configura los controles para período mínimo y máximo"""
        # Título de la sección (igual que rangos)
        titulo = QLabel("<b>Configuración de Período:</b>")
        layout.addWidget(titulo)
        
        # Layout para período máximo
        max_layout = QHBoxLayout()
        max_label = QLabel("Período Máx:")
        max_label.setFixedWidth(85)
        max_label.setStyleSheet("font-weight: bold; color: #34495e; font-size: 11px;")
        
        self.input_periodo_max = QLineEdit()
        self.input_periodo_max.setPlaceholderText("Ej: 3")
        self.input_periodo_max.setFixedWidth(70)
        self.input_periodo_max.setStyleSheet("border: 1px solid #a7c942; border-radius: 3px; padding: 2px;")  # Borde verde para indicar requerido

        dias_label1 = QLabel("días")
        dias_label1.setStyleSheet("color: #7f8c8d; font-size: 10px;")
        
        max_layout.addWidget(max_label)
        max_layout.addWidget(self.input_periodo_max)
        max_layout.addWidget(dias_label1)
        max_layout.addStretch()
        
        # Layout para período mínimo
        min_layout = QHBoxLayout()
        min_label = QLabel("Período Min:")
        min_label.setFixedWidth(85)
        min_label.setStyleSheet("font-weight: bold; color: #34495e; font-size: 11px;")
        
        self.input_periodo_min = QLineEdit()
        self.input_periodo_min.setPlaceholderText("Ej: 0.01")
        self.input_periodo_min.setFixedWidth(70)
        self.input_periodo_min.setStyleSheet("border: 1px solid #a7c942; border-radius: 3px; padding: 2px;")  # Borde verde para indicar requerido

        dias_label2 = QLabel("días")
        dias_label2.setStyleSheet("color: #7f8c8d; font-size: 10px;")
        
        min_layout.addWidget(min_label)
        min_layout.addWidget(self.input_periodo_min)
        min_layout.addWidget(dias_label2)
        min_layout.addStretch()
        
        # Crear contenedor centrado para ambos layouts
        contenedor_centrado = QHBoxLayout()
        contenedor_centrado.addStretch()  # Espacio izquierdo
        
        # Contenedor vertical para los inputs
        inputs_verticales = QVBoxLayout()
        inputs_verticales.addLayout(max_layout)
        inputs_verticales.addLayout(min_layout)
        
        contenedor_centrado.addLayout(inputs_verticales)
        contenedor_centrado.addStretch()  # Espacio derecho
        
        # Agregar el contenedor centrado al layout principal
        layout.addLayout(contenedor_centrado)

    def _setup_action_buttons(self, layout):
        """Configura los botones de acción principales"""
        btn_descartar = self._create_button("Descartar Datos", StyleSheets.BUTTON_DANGER, self.abrir_ventana_main)
        btn_descartar.setMaximumWidth(200)
        
        btn_analisis = self._create_button("Realizar Análisis", StyleSheets.BUTTON_PRIMARY, self.realizar_analisis)
        btn_analisis.setMaximumWidth(200)
        
        # Layout horizontal para botones
        buttons_layout = QHBoxLayout()
        buttons_layout.addStretch()
        buttons_layout.addWidget(btn_descartar)
        buttons_layout.addSpacing(10)
        buttons_layout.addWidget(btn_analisis)
        buttons_layout.addStretch()
        
        layout.addLayout(buttons_layout)

    def _create_button(self, text, style, callback):
        """Crea un botón con estilo y configuración consistente"""
        button = QPushButton(text)
        button.setCursor(QCursor(Qt.PointingHandCursor))
        button.setStyleSheet(style)
        button.clicked.connect(callback)
        return button

    def _create_horizontal_separator(self):
        """Crea un separador horizontal personalizado"""
        separator = QFrame()
        separator.setFrameShape(QFrame.HLine)
        separator.setLineWidth(1)
        separator.setStyleSheet(StyleSheets.SEPARATOR)
        return separator

    def _create_vertical_separator(self):
        """Crea un separador vertical personalizado"""
        separator = QFrame()
        separator.setFrameShape(QFrame.VLine)
        separator.setLineWidth(1)
        separator.setStyleSheet(StyleSheets.SEPARATOR)
        return separator

    def eventFilter(self, source, event):
        """Filtro de eventos para limpiar selecciones al hacer clic fuera de las tablas"""
        from PyQt5.QtCore import QEvent
        from PyQt5.QtGui import QMouseEvent
        
        if event.type() == QEvent.MouseButtonPress:
            if isinstance(event, QMouseEvent):
                # Si el clic fue en el viewport de alguna tabla pero no en una celda
                if source == self.table_main.viewport():
                    item = self.table_main.itemAt(event.pos())
                    if item is None:  # Clic en espacio vacío de la tabla
                        self.table_main.clearSelection()
                        return True
                elif source == self.table_descartadas.viewport():
                    item = self.table_descartadas.itemAt(event.pos())
                    if item is None:  # Clic en espacio vacío de la tabla
                        self.table_descartadas.clearSelection()
                        return True
                elif source == self:  # Clic en cualquier parte de la ventana principal
                    # Verificar si el clic fue fuera de ambas tablas
                    if not (self.table_main.underMouse() or self.table_descartadas.underMouse()):
                        self.table_main.clearSelection()
                        self.table_descartadas.clearSelection()
        
        return super().eventFilter(source, event)
    
    def on_table_main_item_clicked(self, item):
        """Maneja el clic en celdas de la tabla principal"""
        if item.column() == 0:  # Si se hizo clic en la primera columna (N°)
            # Seleccionar toda la fila
            self.table_main.selectRow(item.row())

    def on_table_descartadas_item_clicked(self, item):
        """Maneja el clic en celdas de la tabla de descartadas"""
        if item.column() == 0:  # Si se hizo clic en la primera columna (N°)
            # Seleccionar toda la fila
            self.table_descartadas.selectRow(item.row())

    def on_checkbox_descarte_changed(self, state, row):
        """Maneja el cambio de estado de los checkboxes de descarte"""
        if state == Qt.Checked:
            # Agregar fila a la tabla de descartadas
            self.agregar_fila_descartada(row)
        else:
            # Quitar fila de la tabla de descartadas
            self.quitar_fila_descartada(row)
        
        # Actualizar información de estrellas
        self.actualizar_info_estrellas()

    def agregar_fila_descartada(self, row):
        """Agrega una fila de la tabla principal a la tabla de descartadas"""
        # Verificar que la fila no esté ya en descartadas
        numero_estrella = self.table_main.item(row, 0).text()
        
        # Buscar si ya existe en la tabla de descartadas
        for desc_row in range(self.table_descartadas.rowCount()):
            if (self.table_descartadas.item(desc_row, 0) and 
                self.table_descartadas.item(desc_row, 0).text() == numero_estrella):
                return  # Ya existe, no agregar duplicado
        
        # Agregar nueva fila a la tabla de descartadas
        current_rows = self.table_descartadas.rowCount()
        self.table_descartadas.insertRow(current_rows)
        
        # Copiar datos de la tabla principal (solo las primeras 5 columnas)
        for col in range(5):  # N°, V, I, MV, MI
            source_item = self.table_main.item(row, col)
            if source_item:
                new_item = QTableWidgetItem(source_item.text())
                new_item.setTextAlignment(Qt.AlignCenter)
                self.table_descartadas.setItem(current_rows, col, new_item)
        
        # Agregar a la lista de filas descartadas
        if row not in self.filas_descartadas:
            self.filas_descartadas.append(row)

    def quitar_fila_descartada(self, row):
        """Quita una fila de la tabla de descartadas"""
        numero_estrella = self.table_main.item(row, 0).text()
        
        # Buscar y eliminar de la tabla de descartadas
        for desc_row in range(self.table_descartadas.rowCount()):
            if (self.table_descartadas.item(desc_row, 0) and 
                self.table_descartadas.item(desc_row, 0).text() == numero_estrella):
                self.table_descartadas.removeRow(desc_row)
                break
        
        # Quitar de la lista de filas descartadas
        if row in self.filas_descartadas:
            self.filas_descartadas.remove(row)

    def aplicar_rangos(self):
        """Aplica los rangos especificados por el usuario"""
        texto_rangos = self.input_rangos.text().strip()
        
        if not texto_rangos:
            print("No se especificó ningún rango")
            return
        
        try:
            rangos_validos = self.parsear_rangos(texto_rangos)
            if rangos_validos:
                # Marcar visualmente las filas
                self.marcar_filas_en_rangos(rangos_validos)
                # Activar checkboxes y agregar a tabla de descartadas
                self.aplicar_checkboxes_rangos(rangos_validos)
            else:
                print("No se encontraron rangos válidos")
        except Exception as e:
            print(f"Error al procesar rangos: {e}")

    def _validar_y_aplicar_periodo(self):
        """Valida y aplica los valores de período silenciosamente. Retorna True si es exitoso."""
        try:
            # Obtener valores de los inputs
            periodo_max_text = self.input_periodo_max.text().strip() if hasattr(self, 'input_periodo_max') else ""
            periodo_min_text = self.input_periodo_min.text().strip() if hasattr(self, 'input_periodo_min') else ""
            
            # Verificar que ambos campos tengan valores
            if not periodo_max_text or not periodo_min_text:
                QMessageBox.warning(self, "Valores Faltantes", 
                    "Debe ingresar valores para el período máximo y mínimo antes de realizar el análisis.")
                return False
            
            # Convertir a float
            periodo_max = float(periodo_max_text)
            periodo_min = float(periodo_min_text)
            
            # Validar que período mínimo sea menor que máximo
            if periodo_min >= periodo_max:
                QMessageBox.warning(self, "Error de Validación", 
                    "El período mínimo debe ser menor que el período máximo.")
                return False
            
            # Validar que los valores sean positivos
            if periodo_min <= 0 or periodo_max <= 0:
                QMessageBox.warning(self, "Error de Validación", 
                    "Los valores de período deben ser positivos.")
                return False
            
            # Guardar los nuevos valores
            self.periodo_min = periodo_min
            self.periodo_max = periodo_max
            
            print(f"Período aplicado: Máx={periodo_max}, Mín={periodo_min} días")
            return True
            
        except ValueError:
            QMessageBox.warning(self, "Error de Formato", 
                "Los valores de período deben ser números válidos.")
            return False
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error al aplicar período: {str(e)}")
            return False

    def aplicar_checkboxes_rangos(self, numeros):
        """Activa los checkboxes de las filas en los rangos especificados y las agrega a descartadas"""
        for numero in numeros:
            if 1 <= numero <= self.table_main.rowCount():
                row_index = numero - 1  # Convertir a índice de fila (base 0)
                
                # Obtener el widget checkbox de la columna 5
                checkbox_widget = self.table_main.cellWidget(row_index, 5)
                if checkbox_widget:
                    # Buscar el checkbox dentro del widget contenedor
                    checkbox = checkbox_widget.findChild(QCheckBox)
                    if checkbox and not checkbox.isChecked():
                        # Activar el checkbox (esto automáticamente triggereará on_checkbox_descarte_changed)
                        checkbox.setChecked(True)

    def limpiar_selecciones(self):
        """Limpia todas las selecciones: checkboxes, marcas visuales y tabla de descartadas"""
        # Limpiar marcas visuales usando método optimizado
        self._limpiar_marcas_visuales()
        
        # Desactivar todos los checkboxes
        self._desactivar_todos_checkboxes()
        
        # Limpiar el campo de texto de rangos
        self.input_rangos.clear()
        
        # Actualizar información
        self.actualizar_info_estrellas()
        
        print("Todas las selecciones han sido limpiadas")

    def _desactivar_todos_checkboxes(self):
        """Desactiva todos los checkboxes de la tabla principal"""
        for row in range(self.table_main.rowCount()):
            checkbox_widget = self.table_main.cellWidget(row, 5)
            if checkbox_widget:
                checkbox = checkbox_widget.findChild(QCheckBox)
                if checkbox and checkbox.isChecked():
                    checkbox.setChecked(False)  # Esto automáticamente quitará de la tabla de descartadas
    
    def parsear_rangos(self, texto):
        """
        Parsea el texto de rangos y devuelve una lista de números
        Ejemplos: "1-5, 8, 10-15" -> [1, 2, 3, 4, 5, 8, 10, 11, 12, 13, 14, 15]
        """
        numeros = set()
        
        # Dividir por comas
        partes = [parte.strip() for parte in texto.split(',')]
        
        for parte in partes:
            if '-' in parte:
                # Es un rango (ej: "1-5")
                try:
                    inicio, fin = map(int, parte.split('-'))
                    if inicio <= fin:
                        numeros.update(range(inicio, fin + 1))
                except ValueError:
                    print(f"Rango inválido: {parte}")
            else:
                # Es un número individual (ej: "8")
                try:
                    numero = int(parte)
                    numeros.add(numero)
                except ValueError:
                    print(f"Número inválido: {parte}")
        
        return sorted(list(numeros))
    
    def marcar_filas_en_rangos(self, numeros):
        """Marca visualmente las filas que están en los rangos especificados"""
        # Limpiar marcas previas
        self._limpiar_marcas_visuales()
        
        # Marcar filas en los rangos
        for numero in numeros:
            if 1 <= numero <= self.table_main.rowCount():
                row_index = numero - 1  # Convertir a índice de fila (base 0)
                self._marcar_fila_individual(row_index)

    def _limpiar_marcas_visuales(self):
        """Limpia todas las marcas visuales de la tabla principal"""
        for row in range(self.table_main.rowCount()):
            for col in range(self.table_main.columnCount()):
                item = self.table_main.item(row, col)
                if item:
                    item.setBackground(Qt.white)

    def _marcar_fila_individual(self, row_index):
        """Marca una fila individual con color de resaltado"""
        for col in range(self.table_main.columnCount()):
            item = self.table_main.item(row_index, col)
            if item:
                item.setBackground(QColor(AppConstants.COLOR_AMARILLO_MARCA))
    
    def obtener_rangos_seleccionados(self):
        """Obtiene los rangos seleccionados por el usuario"""
        texto_rangos = self.input_rangos.text().strip()
        if texto_rangos:
            return self.parsear_rangos(texto_rangos)
        return []
    
    def abrir_ventana_main(self):
        """Método para volver a las ventanas anteriores y cerrar DatosNF"""
        try:
            print("=== Iniciando regreso a ventanas anteriores ===")
            
            # Mostrar las ventanas anteriores primero
            self.mostrar_ventanas_anteriores()
            
            # Cerrar esta ventana
            print("Cerrando ventana DatosNF...")
            self.close()
            print("Ventana DatosNF cerrada exitosamente")
                
        except Exception as e:
            print(f"ERROR en abrir_ventana_main: {e}")
            import traceback
            traceback.print_exc()

    def realizar_analisis(self):
        """Método para realizar el análisis con los datos filtrados usando funciones de Analisis.py"""
        try:
            print("=== INICIANDO ANÁLISIS DESDE DATOSNF ===")
            
            # Aplicar automáticamente los valores de período antes del análisis
            print("Aplicando valores de período...")
            if not self._validar_y_aplicar_periodo():
                print("Error al aplicar período, análisis cancelado")
                return  # No continuar si hay error en los valores de período
            
            print(f"Período aplicado para análisis: Máx={self.periodo_max}, Mín={self.periodo_min} días")
            
            # Usar la función de Analisis.py con parámetros de período
            exito, mensaje = realizar_analisis_completo(
                self.table_main, 
                self.table_descartadas, 
                self.datos_formulario,
                periodo_max=self.periodo_max,
                periodo_min=self.periodo_min,
                ventana_subir=self.ventana_subir
            )
            
            print(f"=== ANÁLISIS COMPLETADO ===")
            print(f"Éxito: {exito}")
            print(f"Mensaje completo: {repr(mensaje)}")
            
            # Verificar si el mensaje indica que DatosF se abrió exitosamente
            datosf_abierto = ("✓ Ventana DatosF abierta exitosamente" in str(mensaje) or 
                            "data_folder_final:" in str(mensaje) or
                            "DatosF abierto" in str(mensaje))
            
            print(f"¿DatosF abierto detectado?: {datosf_abierto}")
            print(f"¿Análisis exitoso?: {exito}")
            
            # CERRAR DATOSNF SI EL ANÁLISIS FUE EXITOSO O DATOSF SE ABRIÓ
            debe_cerrar = exito or datosf_abierto
            print(f"¿Debe cerrar DatosNF?: {debe_cerrar}")
            
            if debe_cerrar:
                print("INICIANDO CIERRE FORZADO DE DATOSNF...")
                # Forzar cierre inmediato independientemente de otras condiciones
                self.hide()  # Ocultar inmediatamente
                print("DatosNF ocultado...")
                
                # Procesar eventos para asegurar que se oculte
                from PyQt5.QtWidgets import QApplication
                app = QApplication.instance()
                if app:
                    app.processEvents()
                    print("Eventos procesados después de hide()...")
                
                # Cerrar completamente
                self.close()
                print("DatosNF close() ejecutado...")
                
                # Procesar eventos nuevamente
                if app:
                    app.processEvents()
                    print("Eventos procesados después de close()...")
                
                print("✓ Ventana DatosNF CERRADA FORZADAMENTE")
                # No continuar con el resto del código si ya se cerró
                return
            
            # Solo mostrar mensaje de error si realmente falló y no se debe cerrar
            if not exito and not datosf_abierto:
                QMessageBox.warning(self, "Error en Análisis", mensaje)
                print("✗ Análisis falló completamente, no se abrirá DatosF")
                
        except Exception as e:
            error_msg = f"ERROR en realizar_analisis: {e}"
            print(error_msg)
            import traceback
            traceback.print_exc()
            QMessageBox.critical(self, "Error", error_msg)

    def mostrar_datos_formulario(self):
        """Muestra todos los datos recibidos del formulario en la consola para debugging"""
        if self.datos_formulario:
            print("=== Datos recibidos del formulario ===")
            for key, value in self.datos_formulario.items():
                print(f"{key}: {value}")
            print("======================================")
        else:
            print("No se recibieron datos del formulario")

    def cargar_datos_tabla(self):
        """Carga los datos del CSV en la tabla principal"""
        carga_exitosa = False
        
        # Verificar si hay un archivo CSV en los datos del formulario
        if (self.datos_formulario and 
            'ruta_completa_csv' in self.datos_formulario and 
            os.path.exists(self.datos_formulario['ruta_completa_csv'])):
            
            try:
                # Cargar datos del CSV
                self.cargar_csv(self.datos_formulario['ruta_completa_csv'])
                print(f"CSV cargado exitosamente: {self.datos_formulario['archivo_csv']}")
                carga_exitosa = True
            except Exception as e:
                print(f"Error al cargar CSV: {e}")
        else:
            # No hay CSV válido
            print("No se encontró CSV válido")
        
        # Actualizar la información después de cargar los datos
        if hasattr(self, 'label_descartadas'):
            self.actualizar_info_estrellas()
        
        # Si la carga fue exitosa y hay datos del formulario, ocultar ventanas anteriores
        if carga_exitosa and self.datos_formulario:
            print("Datos cargados exitosamente, ocultando ventanas anteriores")
            self.ocultar_ventanas_anteriores()
            # Cambiar la modalidad de la ventana para que sea independiente
            self.setWindowModality(Qt.NonModal)

    def cargar_csv(self, ruta_csv):
        """Carga los datos del archivo CSV en la tabla principal"""
        try:
            # Leer CSV y preparar tabla
            df = self._leer_archivo_csv(ruta_csv)
            num_filas = len(df)
            self._preparar_tabla_principal(num_filas)
            
            # Mapear columnas y llenar datos
            mapeo_columnas = self._mapear_columnas_csv(df)
            self._llenar_tabla_con_datos(df, mapeo_columnas, num_filas)
            
            # Configuración final
            self._configurar_tabla_final()
            self.actualizar_info_estrellas()
            
        except Exception as e:
            print(f"Error al cargar CSV: {e}")
            QMessageBox.critical(self, "Error", f"No se pudo cargar el archivo CSV:\n{str(e)}")

    def _leer_archivo_csv(self, ruta_csv):
        """Lee el archivo CSV sin usar encabezados"""
        df = pd.read_csv(ruta_csv, header=None)
        columnas_disponibles = df.columns.tolist()
        print(f"Columnas disponibles en CSV: {columnas_disponibles}")
        print(f"Total de filas en CSV: {len(df)}")
        return df

    def _preparar_tabla_principal(self, num_filas):
        """Prepara la tabla principal con el número correcto de filas"""
        self.table_main.setRowCount(num_filas)

    def _mapear_columnas_csv(self, df):
        """Mapea las columnas del CSV a las columnas de la tabla usando mapeo inteligente"""
        columnas_disponibles = df.columns.tolist()
        
        # Verificar si las columnas son numéricas (CSV sin encabezados) o tienen nombres
        if all(isinstance(col, int) for col in columnas_disponibles):
            # CSV sin encabezados - usar mapeo simple
            mapeo_columnas = self.mapear_columnas_csv_numericas(columnas_disponibles)
        else:
            # CSV con encabezados - usar mapeo inteligente
            mapeo_columnas = self.mapear_columnas_csv(columnas_disponibles)
        
        print(f"Mapeo de columnas: {mapeo_columnas}")
        return mapeo_columnas

    def _llenar_tabla_con_datos(self, df, mapeo_columnas, num_filas):
        """Llena la tabla con los datos del CSV"""
        for row in range(num_filas):
            self._llenar_fila_tabla(df, row, mapeo_columnas)

    def _llenar_fila_tabla(self, df, row, mapeo_columnas):
        """Llena una fila específica de la tabla con datos del CSV"""
        # Columna 0: Número de estrella
        self._agregar_numero_estrella(row)
        
        # Columnas 1-4: Datos del CSV
        self._agregar_datos_csv(df, row, mapeo_columnas)
        
        # Columna 5: Checkbox de descarte
        self._agregar_checkbox_descarte(row)

    def _agregar_numero_estrella(self, row):
        """Agrega el número de estrella en la primera columna"""
        item = QTableWidgetItem(str(row + 1))
        item.setTextAlignment(Qt.AlignCenter)
        self.table_main.setItem(row, 0, item)

    def _agregar_datos_csv(self, df, row, mapeo_columnas):
        """Agrega los datos del CSV en las columnas 1-4"""
        for col_tabla in range(1, 5):
            valor = self._obtener_valor_formateado(df, row, col_tabla, mapeo_columnas)
            item = QTableWidgetItem(valor)
            item.setTextAlignment(Qt.AlignCenter)
            self.table_main.setItem(row, col_tabla, item)

    def _obtener_valor_formateado(self, df, row, col_tabla, mapeo_columnas):
        """Obtiene y formatea un valor del CSV según el tipo de columna"""
        col_csv = mapeo_columnas.get(col_tabla)
        
        if col_csv is None or col_csv >= len(df.columns):
            return ""
        
        try:
            valor_raw = df.iloc[row, col_csv]
            if pd.notna(valor_raw):
                return self._formatear_valor_numerico(valor_raw, col_tabla)
            return ""
        except:
            return "N/A"

    def _formatear_valor_numerico(self, valor_raw, col_tabla):
        """Formatea valores numéricos según el tipo de columna"""
        if isinstance(valor_raw, (int, float)):
            # Para columnas MV (3) y MI (4), no redondear
            if col_tabla in [3, 4]:  # Columnas MV y MI
                return str(valor_raw)
            else:  # Columnas V (1) e I (2), redondear a 3 decimales
                return f"{valor_raw:.3f}"
        return str(valor_raw)

    def _agregar_checkbox_descarte(self, row):
        """Agrega el checkbox de descarte en la última columna"""
        checkbox_widget = QWidget()
        checkbox = QCheckBox()
        checkbox.setText("")
        checkbox.setStyleSheet(StyleSheets.CHECKBOX + """
            QCheckBox {
                spacing: 0px;       /* elimina espacio entre indicador y texto */
                padding-left: 0px;  /* elimina margen a la izquierda */
            }
        """)
        checkbox.stateChanged.connect(lambda state, r=row: self.on_checkbox_descarte_changed(state, r))
        
        # Crear widget contenedor centrado
        layout = QHBoxLayout(checkbox_widget)
        layout.addWidget(checkbox, alignment=Qt.AlignCenter)
        layout.setContentsMargins(0, 0, 0, 0)

        self.table_main.setCellWidget(row, 5, checkbox_widget)

    def _configurar_tabla_final(self):
        """Configuración final de la tabla después de cargar datos"""
        # Aplicar altura de filas
        for row in range(self.table_main.rowCount()):
            self.table_main.setRowHeight(row, AppConstants.ROW_HEIGHT_MAIN)

    def mapear_columnas_csv(self, columnas):
        """Mapea inteligentemente las columnas del CSV a las columnas de la tabla"""
        mapeo = {}
        columnas_lower = [col.lower() for col in columnas]
        
        # Buscar columnas para V (columna 1 de la tabla)
        for i, col in enumerate(columnas_lower):
            if any(keyword in col for keyword in ['v', 'mag_v', 'magnitude_v', 'vmag']) or col.endswith('v'):
                mapeo[1] = i
                break
        else:
            # Si no encuentra una columna específica para V, usar la primera columna numérica
            for i, col in enumerate(columnas):
                try:
                    # Verificar si la primera fila de la columna contiene datos numéricos
                    if i < len(columnas):
                        mapeo[1] = i
                        break
                except:
                    continue
        
        # Buscar columnas para I (columna 2 de la tabla)
        for i, col in enumerate(columnas_lower):
            if any(keyword in col for keyword in ['i', 'mag_i', 'magnitude_i', 'imag']) or col.endswith('i'):
                if i != mapeo.get(1):  # No usar la misma columna que V
                    mapeo[2] = i
                    break
        else:
            # Usar la siguiente columna numérica disponible
            for i, col in enumerate(columnas):
                if i != mapeo.get(1):  # No usar la misma columna que V
                    try:
                        mapeo[2] = i
                        break
                    except:
                        continue
        
        # Buscar columnas para MV (columna 3 de la tabla) - color o diferencia
        for i, col in enumerate(columnas_lower):
            if any(keyword in col for keyword in ['mv', 'mag_mv', 'v-i', 'color', 'diff']):
                mapeo[3] = i
                break
        else:
            # Usar la tercera columna numérica disponible
            for i, col in enumerate(columnas):
                if i not in [mapeo.get(1), mapeo.get(2)]:
                    try:
                        mapeo[3] = i
                        break
                    except:
                        continue
        
        # Buscar columnas para MI (columna 4 de la tabla) - diferencia I o magnitud I calculada
        for i, col in enumerate(columnas_lower):
            if any(keyword in col for keyword in ['mi', 'mag_mi', 'i-v', 'color_i']):
                mapeo[4] = i
                break
        else:
            # Usar la cuarta columna numérica disponible
            for i, col in enumerate(columnas):
                if i not in [mapeo.get(1), mapeo.get(2), mapeo.get(3)]:
                    try:
                        mapeo[4] = i
                        break
                    except:
                        continue
        
        # Si no se encontraron mapeos específicos, usar las primeras 4 columnas
        if not mapeo:
            for i in range(min(4, len(columnas))):
                mapeo[i + 1] = i
        
        return mapeo

    def mapear_columnas_csv_numericas(self, columnas):
        """Mapea columnas numéricas del CSV a las columnas de la tabla"""
        mapeo = {}
        
        # Para CSVs sin encabezados, simplemente mapear las primeras 4 columnas disponibles
        # columnas será [0, 1, 2, 3, ...] para un CSV con columnas numéricas
        for i in range(min(4, len(columnas))):
            mapeo[i + 1] = columnas[i]  # Mapear columna de tabla (1-4) a columna CSV (0-3)
        
        return mapeo

    def actualizar_info_estrellas(self):
        """Actualiza la información de estrellas cargadas y descartadas"""
        if not self._validar_widgets_informacion():
            return
        
        total_estrellas = self.table_main.rowCount()
        estrellas_descartadas = self.table_descartadas.rowCount()
        
        # Crear texto informativo usando constantes
        texto = self._crear_texto_informativo(total_estrellas, estrellas_descartadas)
        self.label_descartadas.setText(texto)

    def _validar_widgets_informacion(self):
        """Valida que los widgets necesarios para mostrar información existan"""
        widgets_requeridos = ['table_main', 'table_descartadas', 'label_descartadas']
        return all(hasattr(self, widget) for widget in widgets_requeridos)

    def _crear_texto_informativo(self, total_estrellas, estrellas_descartadas):
        """Crea el texto informativo con formato HTML usando constantes"""
        if self.datos_formulario and 'archivo_csv' in self.datos_formulario:
            archivo_info = f"{AppConstants.PREFIJO_ARCHIVO}: {self.datos_formulario['archivo_csv']}"
            return (f"<b>{archivo_info}</b><br>"
                   f"{AppConstants.LABEL_TOTAL_ESTRELLAS}: {total_estrellas} | "
                   f"{AppConstants.LABEL_DESCARTADAS}: {estrellas_descartadas}")
        else:
            return (f"<b>{AppConstants.TEXTO_SIN_ARCHIVO}</b><br>"
                   f"{AppConstants.LABEL_TOTAL_ESTRELLAS}: {total_estrellas} | "
                   f"{AppConstants.LABEL_DESCARTADAS}: {estrellas_descartadas}")

    def ocultar_ventanas_anteriores(self):
        """Oculta las ventanas anteriores cuando se abre DatosNF"""
        try:
            if self.ventana_subir:
                print("Ocultando ventana SubirArchivos...")
                self.ventana_subir.hide()
            
            if self.ventana_main:
                print("Ocultando ventana Main...")
                self.ventana_main.hide()
                
            print("Ventanas anteriores ocultadas exitosamente")
                
        except Exception as e:
            print(f"Error al ocultar ventanas anteriores: {e}")

    def mostrar_ventanas_anteriores(self):
        """Muestra las ventanas anteriores cuando se cierra DatosNF"""
        try:
            if self.ventana_main:
                print("Mostrando ventana Main...")
                self.ventana_main.show()
                self.ventana_main.raise_()
                self.ventana_main.activateWindow()
            
            if self.ventana_subir:
                print("Mostrando ventana SubirArchivos...")
                self.ventana_subir.show()
                self.ventana_subir.raise_()
                
            print("Ventanas anteriores mostradas exitosamente")
                
        except Exception as e:
            print(f"Error al mostrar ventanas anteriores: {e}")

    # def cerrar_ventanas_anteriores(self):
    #     """Método comentado - causaba cuelgues en la aplicación"""
    #     pass


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = DatosNF()
    window.show()
    sys.exit(app.exec_())

from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QTableWidget, QTableWidgetItem, QPushButton, QLabel,
    QLineEdit, QFrame, QCheckBox
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QCursor, QColor
import sys
import pandas as pd
import os
# Importar funciones de análisis
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from Analisis import realizar_analisis_completo

class DatosNF(QMainWindow):
    def __init__(self, datos_formulario=None, ventana_subir=None, ventana_main=None):
        super().__init__()
        self.datos_formulario = datos_formulario or {}
        # Usar referencias simples, no débiles - más estable
        self.ventana_subir = ventana_subir
        self.ventana_main = ventana_main
        self.filas_descartadas = []  # Lista para mantener track de las filas descartadas
        self.init_ui()
    
    def init_ui(self):
        self.setWindowTitle("Optim. Estrellas")
        screen_width = self.screen().size().width()
        # Lógica similar a media queries
        if screen_width <= 1366:  # Pantallas pequeñas/laptops
            self.resize(1133, 600)
            self.setWindowTitle("Nombre de Aplicación - Pantalla Pequeña")
            layout_margin = 10  # Márgenes pequeños para pantallas pequeñas
            print(f"Configuración aplicada: Pantalla pequeña - Ventana: {self.width()}x{self.height()}")
        elif screen_width <= 1920:  # Pantallas medianas/Full HD
            self.resize(1113, 800)
            self.setWindowTitle("Nombre de Aplicación - Pantalla Mediana")
            layout_margin = 5  # Márgenes medianos
            print(f"Configuración aplicada: Pantalla mediana - Ventana: {self.width()}x{self.height()}")
        else:  # Pantallas grandes/4K
            self.resize(1600, 1000)
            self.setWindowTitle("Nombre de Aplicación - Pantalla Grande")
            layout_margin = 20  # Márgenes grandes para pantallas grandes
            print(f"Configuración aplicada: Pantalla grande - Ventana: {self.width()}x{self.height()}")

        # Widget central
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Layout principal horizontal
        main_layout = QHBoxLayout()
        
        # Añadir márgenes internos al layout principal (dinámicos según tamaño de pantalla)
        main_layout.setContentsMargins(layout_margin, layout_margin, layout_margin, layout_margin)
        main_layout.setSpacing(layout_margin + 5)  # Espacio entre tabla y columna derecha

        # --- Tabla principal ---
        self.table_main = QTableWidget()
        self.table_main.setRowCount(0)  # Iniciar vacía
        self.table_main.setColumnCount(6)  # Ahora son 6 columnas
        self.table_main.setHorizontalHeaderLabels(["N°", "V", "I", "MV", "MI", "Desc."])

        # Ocultar la numeración automática de filas
        self.table_main.verticalHeader().setVisible(False)
        
        # Instalar filtro de eventos para limpiar selección al hacer clic fuera de la tabla
        self.table_main.viewport().installEventFilter(self)
        
        # Conectar evento para seleccionar fila completa al hacer clic en primera columna
        self.table_main.itemClicked.connect(self.on_table_main_item_clicked)
        
        # Set green background color for header cells
        header = self.table_main.horizontalHeader()
        header.setStyleSheet("""
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
                background-color: #a7c942;  /* Sin cambio en hover */
            }
            QHeaderView::section:pressed {
                background-color: #a7c942;  /* Sin cambio al presionar */
            }
        """)
        
        # Personalizar color de las líneas de la tabla y colores alternados
        self.table_main.setStyleSheet("""
            QTableWidget {
                gridline-color: #a7c942;  /* Color verde para las líneas */
                background-color: white;
                alternate-background-color: #f0f0f0;  /* Color verde claro alternado */
            }
            QTableWidget::item {
                border: 1px solid #a7c942;  /* Bordes verdes en cada celda */
            }
            QTableWidget::item:selected {
                background-color: #98b83b;  /* Color verde cuando se selecciona una celda */
                color: white;  /* Texto blanco en selección */
            }
        """)
        
        # Activar colores alternados en las filas
        self.table_main.setAlternatingRowColors(True)
        
        # Controlar ancho de columnas
        self.table_main.setColumnWidth(0, 48)   # Columna N° - 25px
        self.table_main.setColumnWidth(1, 130)   # Columna V - 130px
        self.table_main.setColumnWidth(2, 130)   # Columna I - 130px
        self.table_main.setColumnWidth(3, 130)   # Columna MV - 130px
        self.table_main.setColumnWidth(4, 130)   # Columna MI - 130px
        self.table_main.setColumnWidth(5, 62)   # Columna Desc. - 62px

        # Controlar altura de filas
        self.table_main.verticalHeader().setDefaultSectionSize(30)  # 30px de alto
        
        # Añadir márgenes específicos a la tabla principal usando CSS
        self.table_main.setStyleSheet(self.table_main.styleSheet() + """
            QTableWidget {
                margin: 10px;  /* Margen de 10px en todos los lados */
            }
        """)

        # Cargar datos del CSV si está disponible, sino usar datos de ejemplo
        self.cargar_datos_tabla()


        right_layout = QVBoxLayout()
        
        # Añadir márgenes internos al layout derecho
        right_layout.setContentsMargins(10, 10, 10, 10)  # Márgenes internos
        right_layout.setSpacing(10)  # Espacio entre elementos del layout derecho

        label_title = QLabel("<b>Datos Cargados Correctamente</b>")
        label_title.setAlignment(Qt.AlignCenter)
        label_title.setStyleSheet(""" QLabel { font-size: 16px;  /* Tamaño de texto dinámico */ font-weight: bold; }""")
        
        # Mostrar información de los datos del formulario si están disponibles
        if self.datos_formulario:
            info_formulario = self.crear_info_formulario()
            label_title.setText(f"<b>Datos Cargados Correctamente</b><br><small>{info_formulario}</small>")
        
        label_subtitle = QLabel("Seleccione una estrella de la lista para descartarla")
        label_subtitle.setAlignment(Qt.AlignCenter)
        label_subtitle.setStyleSheet(""" QLabel { font-size: 12px;  /* Tamaño de texto dinámico */}""")

        # Etiqueta dinámica para mostrar información de estrellas
        self.label_descartadas = QLabel("<b>Estrellas descartadas: 3</b>")
        # No llamar actualizar_info_estrellas() aquí todavía

        # --- Layout horizontal para rango de números (estilo Excel) ---
        range_layout = QHBoxLayout()
        
        # Etiqueta del rango
        label_rango = QLabel("<b>Rango de descarte:</b>")

        # Campo de texto para rangos múltiples
        self.input_rangos = QLineEdit()
        self.input_rangos.setPlaceholderText("Ej: 1-5, 8, 10-15, 20-25")
        self.input_rangos.setStyleSheet("""
            QLineEdit {
                padding: 5px 8px;
                border: 1px solid #a7c942;
                border-radius: 4px;
                background-color: white;
                font-size: 12px;
            }
            QLineEdit:focus {
                border: 2px solid #98b83b;
            }
            QLineEdit::placeholder {
                color: #888;
                font-style: italic;
            }
        """)
        
        # Botón para aplicar rangos
        btn_aplicar_rangos = QPushButton("Aplicar")
        btn_aplicar_rangos.setMaximumWidth(70)
        btn_aplicar_rangos.setCursor(QCursor(Qt.PointingHandCursor))
        btn_aplicar_rangos.setStyleSheet("""
            QPushButton {
                font-size: 11px;
                color: white;
                font-weight: bold;
                background-color: #a7c942;
                border: none;
                padding: 5px 10px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #98b83b;
            }
            QPushButton:pressed {
                background-color: #7a9530;
            }
        """)
        
        # Agregar widgets al layout horizontal
        range_layout.addWidget(label_rango)
        range_layout.addWidget(self.input_rangos, 1)  # El input ocupa el espacio disponible
        range_layout.addWidget(btn_aplicar_rangos)
        
        # Conectar evento del botón
        btn_aplicar_rangos.clicked.connect(self.aplicar_rangos)
        
        # También permitir aplicar con Enter
        self.input_rangos.returnPressed.connect(self.aplicar_rangos)

        self.table_descartadas = QTableWidget()
        self.table_descartadas.setRowCount(0)  # Iniciar vacía
        self.table_descartadas.setColumnCount(5)
        self.table_descartadas.setHorizontalHeaderLabels(["N°", "V", "I", "MV", "MI"])

        # Ocultar la numeración automática de filas
        self.table_descartadas.verticalHeader().setVisible(False)
        
        # Instalar filtro de eventos para limpiar selección al hacer clic fuera de la tabla
        self.table_descartadas.viewport().installEventFilter(self)
        
        # Conectar evento para seleccionar fila completa al hacer clic en primera columna
        self.table_descartadas.itemClicked.connect(self.on_table_descartadas_item_clicked)

        header_descartadas = self.table_descartadas.horizontalHeader()
        header_descartadas.setStyleSheet("""
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
                background-color: #a7c942;  /* Sin cambio en hover */
            }
            QHeaderView::section:pressed {
                background-color: #a7c942;  /* Sin cambio al presionar */
            }
        """)
        
        # Personalizar color de las líneas de la tabla descartadas y colores alternados
        self.table_descartadas.setStyleSheet("""
            QTableWidget {
                gridline-color: #a7c942;  /* Color verde para las líneas */
                background-color: white;
                alternate-background-color: #f0f0f0;  /* Color verde claro alternado */
            }
            QTableWidget::item {
                border: 1px solid #a7c942;  /* Bordes verdes en cada celda */
            }
            QTableWidget::item:selected {
                background-color: #98b83b;  /* Color verde cuando se selecciona una celda */
                color: white;  /* Texto blanco en selección */
            }
        """)
        
        # Activar colores alternados en las filas para tabla descartadas
        self.table_descartadas.setAlternatingRowColors(True)
        
        # Controlar ancho de columnas para tabla descartadas
        self.table_descartadas.setColumnWidth(0, 53)   # Columna N° - 53px
        self.table_descartadas.setColumnWidth(1, 84)   # Columna V - 84px
        self.table_descartadas.setColumnWidth(2, 84)   # Columna I - 84px
        self.table_descartadas.setColumnWidth(3, 84)   # Columna MV - 84px
        self.table_descartadas.setColumnWidth(4, 84)   # Columna MI - 84px

        # Controlar altura de filas para tabla descartadas
        self.table_descartadas.verticalHeader().setDefaultSectionSize(28)  # 28px de alto

        btn_descartar = QPushButton("Descartar Datos")
        btn_descartar.clicked.connect(self.abrir_ventana_main)  # Conectar al método personalizado
        btn_descartar.setCursor(QCursor(Qt.PointingHandCursor))
        # Controlar el tamaño del botón para que no ocupe todo el ancho
        btn_descartar.setSizePolicy(btn_descartar.sizePolicy().horizontalPolicy(), btn_descartar.sizePolicy().verticalPolicy())
        btn_descartar.setMaximumWidth(200)  # Ancho máximo de 200px
        btn_descartar.setStyleSheet("""
            QPushButton {
                font-size: 12px;
                color: white;
                font-weight: bold;
                background-color: red;  /* Rojo para el botón de descartar */
                border: none;
                padding: 5px 20px;
                border-radius: 8px;
            }
            QPushButton:hover {
                background-color: #8a0000;  /* Rojo más oscuro al pasar el mouse */
            }
            QPushButton:pressed {
                background-color: #7a9530;
            }
        """)

        btn_analisis = QPushButton("Realizar Análisis")
        btn_analisis.clicked.connect(self.realizar_analisis)  # Conectar al método de análisis
        btn_analisis.setCursor(QCursor(Qt.PointingHandCursor))
        # Controlar el tamaño del botón para que no ocupe todo el ancho
        btn_analisis.setMaximumWidth(200)  # Ancho máximo de 200px
        btn_analisis.setStyleSheet("""
            QPushButton {
                font-size: 12px;
                color: white;
                font-weight: bold;
                background-color: #a7c942;
                border: none;
                padding: 5px 20px;
                border-radius: 8px;
            }
            QPushButton:hover {
                background-color: #98b83b;
            }
            QPushButton:pressed {
                background-color: #7a9530;
            }
        """)

        # Agregar widgets a layout derecho
        right_layout.addWidget(label_title)
        right_layout.addWidget(label_subtitle)
        right_layout.addSpacing(8)  # Espacio entre subtítulo y separador
        
        # Crear separador horizontal
        right_layout.addWidget(self.separador_horizontal())

        right_layout.addSpacing(10)  # Espacio entre separador y "Estrellas descartadas"

        right_layout.addWidget(self.label_descartadas)
        right_layout.addWidget(self.table_descartadas)

        # Botón para limpiar selecciones (entre tabla y rangos)
        btn_limpiar = QPushButton("Limpiar Selecciones")
        btn_limpiar.setMaximumWidth(150)
        btn_limpiar.setCursor(QCursor(Qt.PointingHandCursor))
        btn_limpiar.setStyleSheet("""
            QPushButton {
                font-size: 11px;
                color: white;
                font-weight: bold;
                background-color: #d9534f;
                border: none;
                padding: 5px 10px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #c9302c;
            }
            QPushButton:pressed {
                background-color: #ac2925;
            }
        """)
        btn_limpiar.clicked.connect(self.limpiar_selecciones)
        
        # Crear layout para centrar el botón limpiar
        limpiar_layout = QHBoxLayout()
        limpiar_layout.addStretch()
        limpiar_layout.addWidget(btn_limpiar)
        limpiar_layout.addStretch()
        
        right_layout.addLayout(limpiar_layout)

        #separador horizontal debajo de la tabla descartadas
        right_layout.addWidget(self.separador_horizontal())

        # separacion entre tabla y rango
        right_layout.addSpacing(10)  # Espacio entre tabla y rango
        
        # Agregar etiqueta y layout de rango DEBAJO de la tabla
        right_layout.addWidget(label_rango)
        right_layout.addLayout(range_layout)

        #separacion entre rango y separador
        right_layout.addSpacing(10)  # Espacio entre rango y separador

        #separador horizontal debajo del rango
        right_layout.addWidget(self.separador_horizontal())

        # separacion entre rango y botones
        right_layout.addSpacing(10)  # Espacio entre rango y botones
        
        # Crear layout horizontal para ambos botones (lado a lado)
        buttons_layout = QHBoxLayout()
        buttons_layout.addStretch()  # Espacio flexible a la izquierda
        buttons_layout.addWidget(btn_descartar)
        buttons_layout.addSpacing(10)  # Espacio pequeño entre botones
        buttons_layout.addWidget(btn_analisis)
        buttons_layout.addStretch()  # Espacio flexible a la derecha
        
        right_layout.addLayout(buttons_layout)
        right_layout.addSpacing(10)  # Espacio entre botones y borde inferior
        
        # Crear separador vertical
        separator = self.separador_vertical()
        
        # para evitar que la tabla principal ocupe todo el ancho
        main_layout.addWidget(self.table_main, 13)      # Peso 7 (tabla principal)
        main_layout.addWidget(separator, 0)            # Peso 0 (separador)
        main_layout.addLayout(right_layout, 8)         # Peso 5 (layout derecho)

        central_widget.setLayout(main_layout)
        
        # Instalar filtro de eventos en la ventana principal para limpiar selecciones
        # al hacer clic fuera de las tablas
        self.installEventFilter(self)
        
        # Actualizar la información de estrellas ahora que todos los widgets están creados
        self.actualizar_info_estrellas()

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
    
    def separador_horizontal(self):
        """Crea un separador horizontal personalizado"""
        separator = QFrame()
        separator.setFrameShape(QFrame.HLine)
        separator.setLineWidth(1)
        separator.setStyleSheet("QFrame { color: #a7c942; }")  # Color verde
        return separator

    def separador_vertical(self):
        """Crea un separador vertical personalizado"""
        separator = QFrame()
        separator.setFrameShape(QFrame.VLine)
        separator.setLineWidth(1)
        separator.setStyleSheet("QFrame { color: #a7c942; }")
        return separator

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
        # Limpiar marcas visuales
        for row in range(self.table_main.rowCount()):
            for col in range(self.table_main.columnCount() - 1):  # Excluir la columna de checkboxes
                item = self.table_main.item(row, col)
                if item:
                    item.setBackground(Qt.white)  # Restablecer color de fondo
        
        # Desactivar todos los checkboxes
        for row in range(self.table_main.rowCount()):
            checkbox_widget = self.table_main.cellWidget(row, 5)
            if checkbox_widget:
                checkbox = checkbox_widget.findChild(QCheckBox)
                if checkbox and checkbox.isChecked():
                    checkbox.setChecked(False)  # Esto automáticamente quitará de la tabla de descartadas
        
        # Limpiar el campo de texto de rangos
        self.input_rangos.clear()
        
        # Actualizar información
        self.actualizar_info_estrellas()
        
        print("Todas las selecciones han sido limpiadas")
    
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
        for row in range(self.table_main.rowCount()):
            for col in range(self.table_main.columnCount()):
                item = self.table_main.item(row, col)
                if item:
                    item.setBackground(Qt.white)  # Restablecer color de fondo
        
        # Marcar filas en los rangos
        for numero in numeros:
            if 1 <= numero <= self.table_main.rowCount():
                row_index = numero - 1  # Convertir a índice de fila (base 0)
                for col in range(self.table_main.columnCount()):
                    item = self.table_main.item(row_index, col)
                    if item:
                        # Marcar con color amarillo claro
                        item.setBackground(QColor(255, 255, 150))  # Amarillo claro
    
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
            from PyQt5.QtWidgets import QMessageBox
            
            # Usar la función de Analisis.py
            exito, mensaje = realizar_analisis_completo(self.table_main, self.table_descartadas, self.datos_formulario)
            
            if exito:
                # Mostrar mensaje de confirmación
                QMessageBox.information(self, "CSV Generado", mensaje)
            else:
                # Mostrar mensaje de error
                QMessageBox.warning(self, "Error", mensaje)
                
        except Exception as e:
            error_msg = f"ERROR en realizar_analisis: {e}"
            print(error_msg)
            import traceback
            traceback.print_exc()
            from PyQt5.QtWidgets import QMessageBox
            QMessageBox.critical(self, "Error", error_msg)

    def crear_info_formulario(self):
        """Crea una cadena con información resumida del formulario"""
        info_parts = []
        
        if 'periodo_max' in self.datos_formulario:
            info_parts.append(f"P.Max: {self.datos_formulario['periodo_max']} días")
        if 'periodo_min' in self.datos_formulario:
            info_parts.append(f"P.Min: {self.datos_formulario['periodo_min']} días")
        if 'step' in self.datos_formulario:
            info_parts.append(f"Step: {self.datos_formulario['step']} días")
        
        return " | ".join(info_parts) if info_parts else "Parámetros cargados"

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
            # Leer el CSV sin usar la primera fila como encabezados
            # header=None hace que pandas trate todas las filas como datos
            df = pd.read_csv(ruta_csv, header=None)
            
            # Ajustar el número de filas según los datos del CSV
            num_filas = len(df)  # Sin límite, usar todas las filas del CSV
            self.table_main.setRowCount(num_filas)
            
            # Obtener las columnas disponibles (ahora serán números: 0, 1, 2, 3, etc.)
            columnas_disponibles = df.columns.tolist()
            print(f"Columnas disponibles en CSV: {columnas_disponibles}")
            print(f"Total de filas en CSV: {num_filas}")
            
            # Mapeo inteligente de columnas (ajustado para columnas numéricas)
            mapeo_columnas = self.mapear_columnas_csv_numericas(columnas_disponibles)
            print(f"Mapeo de columnas: {mapeo_columnas}")
            
            # Llenar la tabla con los datos del CSV
            for row in range(num_filas):
                # Columna 0: Número de estrella
                item = QTableWidgetItem(str(row+1))
                item.setTextAlignment(Qt.AlignCenter)
                self.table_main.setItem(row, 0, item)
                
                # Columnas 1-4: Usar el mapeo inteligente
                for col_tabla in range(1, 5):
                    valor = ""
                    col_csv = mapeo_columnas.get(col_tabla)
                    
                    if col_csv is not None and col_csv < len(columnas_disponibles):
                        try:
                            valor_raw = df.iloc[row, col_csv]
                            if pd.notna(valor_raw):
                                # Formatear según el tipo de columna
                                if isinstance(valor_raw, (int, float)):
                                    # Para columnas MV (3) y MI (4), no redondear
                                    if col_tabla in [3, 4]:  # Columnas MV y MI
                                        valor = str(valor_raw)
                                    else:  # Columnas V (1) e I (2), redondear a 3 decimales
                                        valor = f"{valor_raw:.3f}"
                                else:
                                    valor = str(valor_raw)
                        except:
                            valor = "N/A"
                    
                    item = QTableWidgetItem(valor)
                    item.setTextAlignment(Qt.AlignCenter)
                    self.table_main.setItem(row, col_tabla, item)
                
                # Columna 5: Descarte (checkbox)
                checkbox = QCheckBox()
                checkbox.setStyleSheet("""
                    QCheckBox::indicator {
                        width: 18px;
                        height: 18px;
                    }
                    QCheckBox::indicator:unchecked {
                        border: 2px solid #a7c942;
                        background-color: white;
                        border-radius: 3px;
                    }
                    QCheckBox::indicator:checked {
                        border: 2px solid #a7c942;
                        background-color: #a7c942;
                        border-radius: 3px;
                    }
                """)
                # Conectar el checkbox al método de manejo
                checkbox.stateChanged.connect(lambda state, r=row: self.on_checkbox_descarte_changed(state, r))
                
                # Crear un widget contenedor para centrar el checkbox
                checkbox_widget = QWidget()
                checkbox_layout = QHBoxLayout(checkbox_widget)
                checkbox_layout.addWidget(checkbox)
                checkbox_layout.setAlignment(Qt.AlignCenter)
                checkbox_layout.setContentsMargins(0, 0, 0, 0)
                
                self.table_main.setCellWidget(row, 5, checkbox_widget)
                
        except Exception as e:
            print(f"Error detallado al cargar CSV: {e}")
            # En caso de error, mantener tabla vacía
            self.table_main.setRowCount(0)

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
        # Verificar que los widgets necesarios existen
        if not hasattr(self, 'table_main') or not hasattr(self, 'table_descartadas') or not hasattr(self, 'label_descartadas'):
            return
        
        total_estrellas = self.table_main.rowCount()
        estrellas_descartadas = self.table_descartadas.rowCount()
        
        # Crear texto informativo
        if self.datos_formulario and 'archivo_csv' in self.datos_formulario:
            archivo_info = f"Archivo: {self.datos_formulario['archivo_csv']}"
            texto = f"<b>{archivo_info}</b><br>Total estrellas: {total_estrellas} | Descartadas: {estrellas_descartadas}"
        else:
            texto = f"<b>Sin archivo cargado</b><br>Total estrellas: {total_estrellas} | Descartadas: {estrellas_descartadas}"
        
        self.label_descartadas.setText(texto)
        self.label_descartadas.setAlignment(Qt.AlignCenter)

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

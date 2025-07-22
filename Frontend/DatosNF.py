from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QTableWidget, QTableWidgetItem, QPushButton, QLabel, QMenuBar, QAction,
    QLineEdit, QSpinBox, QFrame
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QCursor, QColor
import sys

class DatosNF(QMainWindow):  # Eliminado dataNF
    def __init__(self):
        super().__init__()
        self.init_ui()
    
    def init_ui(self):
        self.setWindowTitle("Optim. Estrellas")
        screen_width = self.screen().size().width()
        # Lógica similar a media queries
        if screen_width <= 1366:  # Pantallas pequeñas/laptops
            self.resize(793, 500)
            self.setWindowTitle("Nombre de Aplicación - Pantalla Pequeña")
            margin_size = "150px"  # Menos margen para pantallas pequeñas
            text_size = "24px"  # Tamaño de texto más pequeño
            vertical_offset = -75
            layout_margin = 10  # Márgenes pequeños para pantallas pequeñas
            print(f"Configuración aplicada: Pantalla pequeña - Ventana: {self.width()}x{self.height()}")
        elif screen_width <= 1920:  # Pantallas medianas/Full HD
            self.resize(773, 500)
            self.setWindowTitle("Nombre de Aplicación - Pantalla Mediana")
            margin_size = "100px"  # Margen muy pequeño para ventana mediana
            text_size = "36px"  # Tamaño de texto intermedio
            vertical_offset = -35
            layout_margin = 5  # Márgenes medianos
            print(f"Configuración aplicada: Pantalla mediana - Ventana: {self.width()}x{self.height()}")
        else:  # Pantallas grandes/4K
            self.resize(1600, 1000)
            self.setWindowTitle("Nombre de Aplicación - Pantalla Grande")
            margin_size = "300px"  # Margen grande para pantallas grandes
            text_size = "42px"  # Tamaño de texto grande
            vertical_offset = -20
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
        self.table_main.setRowCount(32)
        self.table_main.setColumnCount(5)
        self.table_main.setHorizontalHeaderLabels(["N°", "V", "M", "MV", "Desc."])
        
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
        self.table_main.setColumnWidth(0, 25)   # Columna N° - 50px
        self.table_main.setColumnWidth(1, 63)   # Columna V - 62px
        self.table_main.setColumnWidth(2, 63)   # Columna M - 63px
        self.table_main.setColumnWidth(3, 63)   # Columna MV - 63px
        self.table_main.setColumnWidth(4, 62)   # Columna Desc. - 62px

        # Controlar altura de filas
        self.table_main.verticalHeader().setDefaultSectionSize(30)  # 30px de alto
        
        # Añadir márgenes específicos a la tabla principal usando CSS
        self.table_main.setStyleSheet(self.table_main.styleSheet() + """
            QTableWidget {
                margin: 10px;  /* Margen de 10px en todos los lados */
            }
        """)

        # Llenar tabla con datos de ejemplo
        for row in range(32):
            for col in range(5):
                if col == 0:
                    item = QTableWidgetItem(str(row + 1))
                elif col == 4:
                    item = QTableWidgetItem("")
                else:
                    item = QTableWidgetItem("xxx")
                
                # Centrar el contenido de cada celda
                item.setTextAlignment(Qt.AlignCenter)
                self.table_main.setItem(row, col, item)


        right_layout = QVBoxLayout()
        
        # Añadir márgenes internos al layout derecho
        right_layout.setContentsMargins(10, 10, 10, 10)  # Márgenes internos
        right_layout.setSpacing(10)  # Espacio entre elementos del layout derecho

        label_title = QLabel("<b>Datos Cargados Correctamente</b>")
        label_title.setAlignment(Qt.AlignCenter)
        label_title.setStyleSheet(""" QLabel { font-size: 16px;  /* Tamaño de texto dinámico */ font-weight: bold; }""")
        label_subtitle = QLabel("Seleccione una estrella de la lista para descartarla")
        label_subtitle.setAlignment(Qt.AlignCenter)
        label_subtitle.setStyleSheet(""" QLabel { font-size: 12px;  /* Tamaño de texto dinámico */}""")

        label_descartadas = QLabel("<b>Estrellas descartadas: 3</b>")

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
        self.table_descartadas.setRowCount(3)
        self.table_descartadas.setColumnCount(5)
        self.table_descartadas.setHorizontalHeaderLabels(["N°", "I", "V", "M", "MV"])

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
        self.table_descartadas.setColumnWidth(0, 53)   # Columna N° - 51px
        self.table_descartadas.setColumnWidth(1, 84)   # Columna I - 84px
        self.table_descartadas.setColumnWidth(2, 84)   # Columna V - 84px
        self.table_descartadas.setColumnWidth(3, 84)   # Columna M - 84px
        self.table_descartadas.setColumnWidth(4, 84)   # Columna MV - 84px

        # Controlar altura de filas para tabla descartadas
        self.table_descartadas.verticalHeader().setDefaultSectionSize(28)  # 28px de alto

        for row in range(3):
            self.table_descartadas.setItem(row, 0, QTableWidgetItem(str(row * 10 + 6)))
            for col in range(1, 5):
                item = QTableWidgetItem("xxx")
                item.setTextAlignment(Qt.AlignCenter)  # Centrar contenido
                self.table_descartadas.setItem(row, col, item)
            
            # También centrar la primera columna (N°)
            item_num = self.table_descartadas.item(row, 0)
            if item_num:
                item_num.setTextAlignment(Qt.AlignCenter)

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
        separator_horizontal = QFrame()
        separator_horizontal.setFrameShape(QFrame.HLine)  # Línea horizontal
        separator_horizontal.setFrameShadow(QFrame.Sunken)  # Estilo hundido
        separator_horizontal.setLineWidth(1)
        separator_horizontal.setStyleSheet("QFrame { color: #a7c942; }")  # Color verde
        right_layout.addWidget(separator_horizontal)

        right_layout.addSpacing(10)  # Espacio entre separador y "Estrellas descartadas"

        right_layout.addWidget(label_descartadas)
        right_layout.addWidget(self.table_descartadas)

        #separador horizontal debajo de la tabla descartadas
        separator_horizontal_descartadas = QFrame()
        separator_horizontal_descartadas.setFrameShape(QFrame.HLine)  # Línea horizontal
        separator_horizontal_descartadas.setFrameShadow(QFrame.Sunken)  # Estilo hund
        separator_horizontal_descartadas.setLineWidth(1)
        separator_horizontal_descartadas.setStyleSheet("QFrame { color: #a7c942; }")  # Color verde
        right_layout.addWidget(separator_horizontal_descartadas)

        # separacion entre tabla y rango
        right_layout.addSpacing(10)  # Espacio entre tabla y rango
        
        # Agregar etiqueta y layout de rango DEBAJO de la tabla
        right_layout.addWidget(label_rango)
        right_layout.addLayout(range_layout)

        #separador horizontal debajo del rango
        separator_horizontal_rango = QFrame()
        separator_horizontal_rango.setFrameShape(QFrame.HLine)  # Línea horizontal
        separator_horizontal_rango.setFrameShadow(QFrame.Sunken)  # Estilo hundido
        separator_horizontal_rango.setLineWidth(1)
        separator_horizontal_rango.setStyleSheet("QFrame { color: #a7c942; }")  # Color verde

        #separacion entre rango y separador
        right_layout.addSpacing(10)  # Espacio entre rango y separador

        right_layout.addWidget(separator_horizontal_rango)

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
        separator = QFrame()
        separator.setFrameShape(QFrame.VLine)  # Línea vertical
        separator.setFrameShadow(QFrame.Sunken)  # Estilo hundido
        separator.setLineWidth(1)
        separator.setStyleSheet("QFrame { color: #a7c942; }")  # Color verde
        
        # para evitar que la tabla principal ocupe todo el ancho
        main_layout.addWidget(self.table_main, 4)      # Peso 4 (tabla principal)
        main_layout.addWidget(separator, 0)            # Peso 0 (separador)
        main_layout.addLayout(right_layout, 5)         # Peso 5 (layout derecho)

        central_widget.setLayout(main_layout)
        
        # Instalar filtro de eventos en la ventana principal para limpiar selecciones
        # al hacer clic fuera de las tablas
        self.installEventFilter(self)

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

    def aplicar_rangos(self):
        """Aplica los rangos especificados por el usuario"""
        texto_rangos = self.input_rangos.text().strip()
        
        if not texto_rangos:
            print("No se especificó ningún rango")
            return
        
        try:
            rangos_validos = self.parsear_rangos(texto_rangos)
            if rangos_validos:
                print(f"Rangos aplicados: {rangos_validos}")
                # Aquí puedes agregar la lógica para aplicar los rangos a la tabla
                self.marcar_filas_en_rangos(rangos_validos)
            else:
                print("No se encontraron rangos válidos")
        except Exception as e:
            print(f"Error al procesar rangos: {e}")
    
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
        """Abre la ventana principal (main) y cierra la actual"""
        try:
            # Importar la ventana main
            from main import Main
            
            # Crear y mostrar la ventana main
            self.main_window = Main()
            self.main_window.show()
            
            # Cerrar la ventana actual
            self.close()
            
        except ImportError:
            print("Error: No se pudo importar la ventana main")
        except Exception as e:
            print(f"Error al abrir ventana main: {e}")


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = DatosNF()
    window.show()
    sys.exit(app.exec_())

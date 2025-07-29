from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QTableWidget, QTableWidgetItem, QPushButton, QLabel,
    QLineEdit, QFrame, QCheckBox, QScrollArea
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QCursor, QColor, QPixmap
import sys
import pandas as pd
import os

class DatosF(QMainWindow):
    def __init__(self, data_folder=None, datos_formulario=None, ventana_anterior=None, ruta_csv_filtrado=None):
        super().__init__()
        self.data_folder = data_folder or ""
        self.datos_formulario = datos_formulario or {}
        self.ventana_anterior = ventana_anterior
        self.ruta_csv_filtrado = ruta_csv_filtrado  # CSV generado con datos filtrados
        self.imagenes_estrellas = []  # Lista de imágenes encontradas
        self.imagen_actual_index = 0  # Índice de imagen actual mostrada
        self.init_ui()
    
    def init_ui(self):
        self.setWindowTitle("Resultados del Análisis")
        screen_width = self.screen().size().width()
        
        # Lógica similar a media queries
        if screen_width <= 1366:
            self.resize(1133, 600)
            layout_margin = 10
        elif screen_width <= 1920:
            self.resize(1580, 800)
            layout_margin = 5
        else:
            self.resize(1600, 1000)
            layout_margin = 20

        # Widget central
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Layout principal horizontal
        main_layout = QHBoxLayout()
        main_layout.setContentsMargins(layout_margin, layout_margin, layout_margin, layout_margin)
        main_layout.setSpacing(layout_margin + 5)

        # --- Tabla principal ---
        self.table_main = QTableWidget()
        self.table_main.setRowCount(0)
        self.table_main.setColumnCount(0)  # Se establecerá dinámicamente según el CSV

        # Ocultar la numeración automática de filas
        self.table_main.verticalHeader().setVisible(False)
        
        # Instalar filtro de eventos para limpiar selección al hacer clic fuera de la tabla
        self.table_main.viewport().installEventFilter(self)
        
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
                background-color: #a7c942;
            }
            QHeaderView::section:pressed {
                background-color: #a7c942;
            }
        """)
        
        # Personalizar color de las líneas de la tabla y colores alternados
        self.table_main.setStyleSheet("""
            QTableWidget {
                gridline-color: #a7c942;
                background-color: white;
                alternate-background-color: #f0f0f0;
            }
            QTableWidget::item {
                border: 1px solid #a7c942;
            }
            QTableWidget::item:selected {
                background-color: #98b83b;
                color: white;
            }
        """)
        
        # Activar colores alternados en las filas
        self.table_main.setAlternatingRowColors(True)
        
        # Controlar altura de filas
        self.table_main.verticalHeader().setDefaultSectionSize(30)
        
        # Añadir márgenes específicos a la tabla principal usando CSS
        self.table_main.setStyleSheet(self.table_main.styleSheet() + """
            QTableWidget {
                margin: 10px;
            }
        """)

        # Cargar datos del CSV filtrado si está disponible
        self.cargar_datos_csv_filtrado()

        # --- Layout derecho ---
        right_layout = QVBoxLayout()
        right_layout.setContentsMargins(10, 10, 10, 10)
        right_layout.setSpacing(10)

        # Título
        label_title = QLabel("<b>Análisis Completado</b>")
        label_title.setAlignment(Qt.AlignCenter)
        label_title.setStyleSheet("QLabel { font-size: 16px; font-weight: bold; }")
        
        # Mostrar información de los datos del formulario si están disponibles
        if self.datos_formulario:
            info_formulario = self.crear_info_formulario()
            label_title.setText(f"<b>Resultados del Análisis</b><br><small>{info_formulario}</small>")
        
        # Determinar el subtítulo basado en la presencia de datos
        if self.data_folder and os.path.exists(self.data_folder):
            label_subtitle = QLabel(f"Carpeta: {os.path.basename(self.data_folder)}")
        else:
            label_subtitle = QLabel("Resultados del procesamiento de estrellas")
        label_subtitle.setAlignment(Qt.AlignCenter)
        label_subtitle.setStyleSheet("QLabel { font-size: 12px; color: #666; }")

        # Separador
        right_layout.addWidget(label_title)
        right_layout.addWidget(label_subtitle)
        right_layout.addSpacing(8)
        right_layout.addWidget(self.separador_horizontal())
        right_layout.addSpacing(10)

        # Área para mostrar las imágenes de las estrellas
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setMinimumHeight(300)
        
        self.image_label = QLabel()
        self.image_label.setAlignment(Qt.AlignCenter)
        self.image_label.setText("Cargando imágenes...")
        self.image_label.setStyleSheet("""
            QLabel {
                border: 2px solid #a7c942;
                border-radius: 5px;
                background-color: #f9f9f9;
                padding: 10px;
            }
        """)
        
        self.scroll_area.setWidget(self.image_label)
        
        # Controles para navegar entre imágenes
        navegacion_layout = QHBoxLayout()
        
        self.btn_anterior = QPushButton("← Anterior")
        self.btn_anterior.setEnabled(False)
        self.btn_anterior.setMaximumWidth(100)
        self.btn_anterior.setCursor(QCursor(Qt.PointingHandCursor))
        self.btn_anterior.setStyleSheet("""
            QPushButton {
                font-size: 11px;
                color: white;
                font-weight: bold;
                background-color: #6c757d;
                border: none;
                padding: 5px 10px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #5a6268;
            }
            QPushButton:disabled {
                background-color: #cccccc;
                color: #666666;
            }
        """)
        self.btn_anterior.clicked.connect(self.imagen_anterior)
        
        self.label_imagen_info = QLabel("Sin imágenes")
        self.label_imagen_info.setAlignment(Qt.AlignCenter)
        self.label_imagen_info.setStyleSheet("font-size: 11px; color: #666;")
        
        self.btn_siguiente = QPushButton("Siguiente →")
        self.btn_siguiente.setEnabled(False)
        self.btn_siguiente.setMaximumWidth(100)
        self.btn_siguiente.setCursor(QCursor(Qt.PointingHandCursor))
        self.btn_siguiente.setStyleSheet("""
            QPushButton {
                font-size: 11px;
                color: white;
                font-weight: bold;
                background-color: #6c757d;
                border: none;
                padding: 5px 10px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #5a6268;
            }
            QPushButton:disabled {
                background-color: #cccccc;
                color: #666666;
            }
        """)
        self.btn_siguiente.clicked.connect(self.imagen_siguiente)
        
        navegacion_layout.addWidget(self.btn_anterior)
        navegacion_layout.addStretch()
        navegacion_layout.addWidget(self.label_imagen_info)
        navegacion_layout.addStretch()
        navegacion_layout.addWidget(self.btn_siguiente)
        
        right_layout.addWidget(self.scroll_area)
        right_layout.addLayout(navegacion_layout)

        # Cargar imágenes de las estrellas si están disponibles
        self.cargar_imagenes_estrellas()

        right_layout.addSpacing(10)
        right_layout.addWidget(self.separador_horizontal())
        right_layout.addSpacing(10)

        # Botones
        btn_refrescar = QPushButton("Refrescar Datos")
        btn_refrescar.setCursor(QCursor(Qt.PointingHandCursor))
        btn_refrescar.setMaximumWidth(200)
        btn_refrescar.setStyleSheet("""
            QPushButton {
                font-size: 12px;
                color: white;
                font-weight: bold;
                background-color: #f0ad4e;
                border: none;
                padding: 5px 20px;
                border-radius: 8px;
            }
            QPushButton:hover {
                background-color: #ec971f;
            }
            QPushButton:pressed {
                background-color: #d58512;
            }
        """)
        btn_refrescar.clicked.connect(self.refrescar_datos)

        btn_exportar = QPushButton("Exportar Resultados")
        btn_exportar.setCursor(QCursor(Qt.PointingHandCursor))
        btn_exportar.setMaximumWidth(200)
        btn_exportar.setStyleSheet("""
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
        btn_exportar.clicked.connect(self.exportar_resultados)

        btn_nuevo_analisis = QPushButton("Nuevo Análisis")
        btn_nuevo_analisis.setCursor(QCursor(Qt.PointingHandCursor))
        btn_nuevo_analisis.setMaximumWidth(200)
        btn_nuevo_analisis.setStyleSheet("""
            QPushButton {
                font-size: 12px;
                color: white;
                font-weight: bold;
                background-color: #5bc0de;
                border: none;
                padding: 5px 20px;
                border-radius: 8px;
            }
            QPushButton:hover {
                background-color: #46b8da;
            }
            QPushButton:pressed {
                background-color: #31b0d5;
            }
        """)
        btn_nuevo_analisis.clicked.connect(self.nuevo_analisis)

        # Layout para botones
        buttons_layout = QHBoxLayout()
        buttons_layout.addStretch()
        buttons_layout.addWidget(btn_refrescar)
        buttons_layout.addSpacing(10)
        buttons_layout.addWidget(btn_exportar)
        buttons_layout.addSpacing(10)
        buttons_layout.addWidget(btn_nuevo_analisis)
        buttons_layout.addStretch()
        
        right_layout.addLayout(buttons_layout)
        right_layout.addSpacing(10)
        
        # Crear separador vertical
        separator = self.separador_vertical()
        
        # Agregar widgets al layout principal
        main_layout.addWidget(self.table_main, 8)
        main_layout.addWidget(separator, 0)
        main_layout.addLayout(right_layout, 13)

        central_widget.setLayout(main_layout)
        
        # Instalar filtro de eventos
        self.installEventFilter(self)

    def eventFilter(self, source, event):
        """Filtro de eventos para limpiar selecciones al hacer clic fuera de las tablas"""
        from PyQt5.QtCore import QEvent
        
        if event.type() == QEvent.MouseButtonPress:
            if hasattr(self, 'table_main') and source not in [self.table_main, self.table_main.viewport()]:
                self.table_main.clearSelection()
        
        return super().eventFilter(source, event)
    
    def separador_horizontal(self):
        """Crea un separador horizontal personalizado"""
        separator = QFrame()
        separator.setFrameShape(QFrame.HLine)
        separator.setFrameShadow(QFrame.Sunken)
        separator.setStyleSheet("QFrame { color: #a7c942; background-color: #a7c942; }")
        return separator

    def separador_vertical(self):
        """Crea un separador vertical personalizado"""
        separator = QFrame()
        separator.setFrameShape(QFrame.VLine)
        separator.setFrameShadow(QFrame.Sunken)
        separator.setStyleSheet("QFrame { color: #a7c942; background-color: #a7c942; }")
        separator.setMaximumWidth(2)
        return separator

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
        if not self.data_folder or not os.path.exists(self.data_folder):
            self.mostrar_datos_ejemplo()
            return
        
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
                self.mostrar_datos_ejemplo()
                
        except Exception as e:
            print(f"Error al cargar datos de carpetas: {e}")
            self.mostrar_datos_ejemplo()

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
            self.mostrar_datos_ejemplo()

    def mostrar_datos_ejemplo(self):
        """Muestra datos de ejemplo si no se pueden cargar los resultados"""
        # Configurar tabla con datos de ejemplo
        self.table_main.setRowCount(5)
        self.table_main.setColumnCount(5)
        self.table_main.setHorizontalHeaderLabels(["N°", "V", "I", "MV", "MI"])
        
        datos_ejemplo = [
            ["1","0552.491_0637.323V","0551.708_0637.363i", "15.0034280824373", "13.9925005227811"]
        ]
        
        for row, fila_datos in enumerate(datos_ejemplo):
            for col, valor in enumerate(fila_datos):
                item = QTableWidgetItem(valor)
                item.setTextAlignment(Qt.AlignCenter)
                self.table_main.setItem(row, col, item)
        
        # Ajustar ancho de columnas
        self.table_main.setColumnWidth(0, 48)   # N° - 48px
        self.table_main.setColumnWidth(1, 130) # Columnas restantes - 130px
        self.table_main.setColumnWidth(2, 130)
        self.table_main.setColumnWidth(3, 130)
        self.table_main.setColumnWidth(4, 130)

    def cargar_imagen_resultado(self):
        """Carga la imagen generada por procesofull.py"""
        if not self.data_folder or not os.path.exists(self.data_folder):
            self.image_label.setText("No se encontró la carpeta de resultados")
            return
        
        # Buscar la imagen GLSPDM.png en diferentes ubicaciones
        posibles_rutas = [
            os.path.join(self.data_folder, 'GLSPDM.png'),  # Directorio principal
            os.path.join(self.data_folder, 'results', 'GLSPDM.png'),  # Subdirectorio results
            os.path.join(self.data_folder, 'plots', 'GLSPDM.png'),   # Subdirectorio plots
        ]
        
        # También buscar en carpetas de estrellas individuales por si acaso
        try:
            for item in os.listdir(self.data_folder):
                item_path = os.path.join(self.data_folder, item)
                if os.path.isdir(item_path):
                    posibles_rutas.append(os.path.join(item_path, 'GLSPDM.png'))
        except:
            pass
        
        ruta_imagen_encontrada = None
        for ruta_imagen in posibles_rutas:
            if os.path.exists(ruta_imagen):
                ruta_imagen_encontrada = ruta_imagen
                break
        
        if ruta_imagen_encontrada:
            try:
                pixmap = QPixmap(ruta_imagen_encontrada)
                if not pixmap.isNull():
                    # Escalar imagen para que quepa bien en el área
                    scaled_pixmap = pixmap.scaled(
                        self.scroll_area.width() - 20, 
                        600, 
                        Qt.KeepAspectRatio, 
                        Qt.SmoothTransformation
                    )
                    self.image_label.setPixmap(scaled_pixmap)
                    self.image_label.setText("")
                    print(f"Imagen cargada desde: {ruta_imagen_encontrada}")
                else:
                    self.image_label.setText("Error al cargar la imagen")
            except Exception as e:
                self.image_label.setText(f"Error al cargar imagen: {str(e)}")
                print(f"Error al cargar imagen: {e}")
        else:
            # Si no se encuentra la imagen, mostrar información útil
            info_texto = "Imagen de resultados no encontrada\n\n"
            info_texto += "Análisis en progreso o incompleto.\n"
            
            # Mostrar qué archivos sí existen
            try:
                archivos_existentes = []
                for item in os.listdir(self.data_folder):
                    item_path = os.path.join(self.data_folder, item)
                    if os.path.isfile(item_path):
                        archivos_existentes.append(item)
                    elif os.path.isdir(item_path):
                        archivos_existentes.append(f"{item}/")
                
                if archivos_existentes:
                    info_texto += f"\nArchivos encontrados:\n"
                    for archivo in sorted(archivos_existentes)[:10]:  # Mostrar máximo 10
                        info_texto += f"• {archivo}\n"
                    if len(archivos_existentes) > 10:
                        info_texto += f"... y {len(archivos_existentes) - 10} más"
                else:
                    info_texto += "\nCarpeta vacía"
            except Exception as e:
                info_texto += f"\nError al listar archivos: {e}"
            
            self.image_label.setText(info_texto)
            print(f"Imagen no encontrada. Buscadas en: {posibles_rutas}")

    def refrescar_datos(self):
        """Refresca los datos y las imágenes"""
        print("Refrescando datos...")
        self.cargar_datos_csv_filtrado()
        self.cargar_imagenes_estrellas()
        
        from PyQt5.QtWidgets import QMessageBox
        QMessageBox.information(
            self,
            "Datos Refrescados",
            "Los datos han sido actualizados con cualquier nuevo resultado disponible."
        )

    def exportar_resultados(self):
        """Exporta los resultados a un archivo"""
        from PyQt5.QtWidgets import QFileDialog, QMessageBox
        
        try:
            # Abrir diálogo para seleccionar ubicación
            ruta_exportacion, _ = QFileDialog.getSaveFileName(
                self,
                "Exportar Resultados",
                "resultados_analisis.csv",
                "CSV files (*.csv);;All files (*.*)"
            )
            
            if ruta_exportacion:
                # Crear DataFrame con los datos de la tabla
                datos = []
                headers = []
                
                # Obtener headers
                for col in range(self.table_main.columnCount()):
                    headers.append(self.table_main.horizontalHeaderItem(col).text())
                
                # Obtener datos
                for row in range(self.table_main.rowCount()):
                    fila = []
                    for col in range(self.table_main.columnCount()):
                        item = self.table_main.item(row, col)
                        fila.append(item.text() if item else "")
                    datos.append(fila)
                
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

    def cargar_datos_csv_filtrado(self):
        """Carga los datos del CSV filtrado generado en la carpeta de análisis"""
        if self.ruta_csv_filtrado and os.path.exists(self.ruta_csv_filtrado):
            try:
                self.cargar_csv_datos_filtrados(self.ruta_csv_filtrado)
                print(f"Datos cargados desde CSV filtrado: {os.path.basename(self.ruta_csv_filtrado)}")
                return
            except Exception as e:
                print(f"Error al cargar CSV filtrado: {e}")
        
        # Si tenemos carpeta de análisis específica, buscar allí primero
        if self.data_folder:
            csvs_filtrados = []
            try:
                for archivo in os.listdir(self.data_folder):
                    if archivo.startswith('datos_filtrados_') and archivo.endswith('.csv'):
                        csvs_filtrados.append(os.path.join(self.data_folder, archivo))
            except Exception as e:
                print(f"Error al buscar CSVs filtrados en carpeta de análisis: {e}")
            
            if csvs_filtrados:
                # Usar el más reciente
                csv_mas_reciente = max(csvs_filtrados, key=os.path.getmtime)
                try:
                    self.cargar_csv_datos_filtrados(csv_mas_reciente)
                    print(f"Datos cargados desde CSV filtrado en carpeta de análisis: {os.path.basename(csv_mas_reciente)}")
                    return
                except Exception as e:
                    print(f"Error al cargar CSV filtrado de carpeta de análisis: {e}")
        
        # Fallback: buscar CSVs de datos filtrados en la raíz del proyecto (por compatibilidad)
        script_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # Subir dos niveles desde Frontend/
        
        # Buscar archivos que empiecen con "datos_filtrados_"
        csvs_filtrados = []
        try:
            for archivo in os.listdir(script_dir):
                if archivo.startswith('datos_filtrados_') and archivo.endswith('.csv'):
                    csvs_filtrados.append(os.path.join(script_dir, archivo))
        except Exception as e:
            print(f"Error al buscar CSVs filtrados en raíz: {e}")
        
        if csvs_filtrados:
            # Usar el más reciente
            csv_mas_reciente = max(csvs_filtrados, key=os.path.getmtime)
            try:
                self.cargar_csv_datos_filtrados(csv_mas_reciente)
                print(f"Datos cargados desde CSV filtrado encontrado en raíz: {os.path.basename(csv_mas_reciente)}")
                return
            except Exception as e:
                print(f"Error al cargar CSV filtrado encontrado: {e}")
        
        # Si no se encuentra nada, mostrar datos de ejemplo
        print("No se encontró CSV de datos filtrados, mostrando datos de ejemplo")
        self.mostrar_datos_ejemplo()
    
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
            self.table_main.setColumnWidth(0, 48)   # N° - 48px
            for col in range(1, self.table_main.columnCount()):
                self.table_main.setColumnWidth(col, 130)  # Columnas restantes - 130px
            
        except Exception as e:
            print(f"Error al cargar CSV de datos filtrados: {e}")
            self.mostrar_datos_ejemplo()

    def cargar_imagenes_estrellas(self):
        """Carga las imágenes generadas por procesofull.py desde las carpetas de estrellas"""
        self.imagenes_estrellas = []
        
        if not self.data_folder or not os.path.exists(self.data_folder):
            self.image_label.setText("No se encontró la carpeta de análisis")
            self.actualizar_controles_navegacion()
            return
        
        # Buscar imágenes en carpetas de estrellas
        try:
            # Extensiones de imagen a buscar
            extensiones_imagen = ['.png', '.jpg', '.jpeg', '.gif', '.bmp']
            
            for item in os.listdir(self.data_folder):
                item_path = os.path.join(self.data_folder, item)
                if os.path.isdir(item_path) and item.startswith('star'):
                    # Buscar imágenes en esta carpeta de estrella
                    try:
                        for archivo in os.listdir(item_path):
                            archivo_path = os.path.join(item_path, archivo)
                            if os.path.isfile(archivo_path):
                                nombre_lower = archivo.lower()
                                if any(ext in nombre_lower for ext in extensiones_imagen):
                                    numero_estrella = item.replace('star', '')
                                    self.imagenes_estrellas.append({
                                        'ruta': archivo_path,
                                        'estrella': numero_estrella,
                                        'nombre': archivo,
                                        'carpeta': item
                                    })
                    except Exception as e:
                        print(f"Error al buscar imágenes en {item}: {e}")
            
            # Ordenar por número de estrella
            self.imagenes_estrellas.sort(key=lambda x: int(x['estrella']) if x['estrella'].isdigit() else 0)
            
            if self.imagenes_estrellas:
                print(f"Encontradas {len(self.imagenes_estrellas)} imágenes de estrellas")
                self.imagen_actual_index = 0
                self.mostrar_imagen_actual()
            else:
                self.image_label.setText("No se encontraron imágenes en las carpetas de estrellas\n\nLas imágenes se generan durante el procesamiento.\nUsa 'Refrescar Datos' si el análisis continúa.")
                print("No se encontraron imágenes en las carpetas de estrellas")
            
            self.actualizar_controles_navegacion()
            
        except Exception as e:
            self.image_label.setText(f"Error al buscar imágenes: {str(e)}")
            print(f"Error al cargar imágenes de estrellas: {e}")
            self.actualizar_controles_navegacion()

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
                    self.scroll_area.width() - 20, 
                    400, 
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

    def actualizar_controles_navegacion(self):
        """Actualiza los controles de navegación entre imágenes"""
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
            self.mostrar_imagen_actual()

    def imagen_siguiente(self):
        """Muestra la imagen siguiente"""
        if self.imagen_actual_index < len(self.imagenes_estrellas) - 1:
            self.imagen_actual_index += 1
            self.mostrar_imagen_actual()

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


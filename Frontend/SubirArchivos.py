from PyQt5.QtWidgets import (
    QMainWindow, QApplication, QWidget, QLabel, QPushButton,
    QLineEdit, QComboBox, QFormLayout, QVBoxLayout, QHBoxLayout,
    QFileDialog
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QCursor

class SubirArchivos(QMainWindow):
    def __init__(self):
        super().__init__()
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

        # Agregar separación vertical entre fila 6 y 7
        separador = QLabel("")  # Etiqueta vacía como separador
        separador.setFixedHeight(5)  # Altura del espaciado
        form_layout.addRow(separador)

        # Fila 7: Botón de análisis
        boton = QPushButton("Cargar Datos")
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

if __name__ == "__main__":
    app = QApplication([])
    window = SubirArchivos()
    window.show()
    app.exec_()

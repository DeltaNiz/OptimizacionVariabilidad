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
        self.resize(500, 200)
        self.setWindowTitle("Subir Archivo")

        # Formulario principal
        form_layout = QFormLayout()
        form_layout.setRowWrapPolicy(QFormLayout.DontWrapRows)
        form_layout.setFieldGrowthPolicy(QFormLayout.FieldsStayAtSizeHint)
        form_layout.setFormAlignment(Qt.AlignHCenter | Qt.AlignVCenter)  # Centrar horizontal y verticalmente
        form_layout.setLabelAlignment(Qt.AlignRight)  # Alinear etiquetas a la derecha
        form_layout.setVerticalSpacing(10)  # Espaciado entre filas
        form_layout.setHorizontalSpacing(15)  # Espaciado entre etiquetas y campos

        # Fila 1: Dirección de la carpeta
        label_inserte = QLabel("<b>Dirección de la carpeta:</b>")
        combo = QComboBox()
        combo.setFixedWidth(200)  # Controlar ancho del combo
        combo.addItem("Seleccione una carpeta...")
        
        # Botón para examinar carpeta
        boton_examinar = QPushButton("Examinar")
        boton_examinar.setFixedWidth(80)
        boton_examinar.setCursor(QCursor(Qt.PointingHandCursor))
        boton_examinar.setStyleSheet("""
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
        boton_examinar.clicked.connect(self.seleccionar_carpeta)
        
        # Crear un widget contenedor para combo y botón
        folder_row = QWidget()
        folder_row.setFixedWidth(290)  # Controlar ancho total del contenedor
        folder_row_layout = QHBoxLayout()
        folder_row_layout.addWidget(combo)
        folder_row_layout.addWidget(boton_examinar)
        folder_row_layout.setContentsMargins(0,0,0,0)
        folder_row_layout.setAlignment(Qt.AlignCenter)  # Centrar contenido del HBox
        folder_row.setLayout(folder_row_layout)
        
        form_layout.addRow(label_inserte, folder_row)
        
        # Guardar referencia al combo para usarlo en la función
        self.combo_carpeta = combo

        # Fila 2: Periodo Máx
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

        # Fila 3: Periodo Min
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

        # Fila 4: Step (Saltos)
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

        # Agregar separación vertical entre fila 4 y 5
        separador = QLabel("")  # Etiqueta vacía como separador
        separador.setFixedHeight(15)  # Altura del espaciado
        form_layout.addRow(separador)

        # Fila 5: Botón de análisis
        boton = QPushButton("Comenzar Análisis")
        boton.setCursor(QCursor(Qt.PointingHandCursor))
        boton.setStyleSheet("""
            QPushButton {
                font-size: 16px;
                color: white;
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

    def seleccionar_carpeta(self):
        """Función para abrir el diálogo de selección de carpeta"""
        carpeta_seleccionada = QFileDialog.getExistingDirectory(
            self, 
            "Seleccionar Carpeta", 
            "",  # Directorio inicial (vacío para usar el último usado)
            QFileDialog.ShowDirsOnly
        )
        
        if carpeta_seleccionada:
            # Actualizar el combo con la carpeta seleccionada
            self.combo_carpeta.clear()
            self.combo_carpeta.addItem(carpeta_seleccionada)
            # Mostrar solo el nombre de la carpeta en el tooltip
            self.combo_carpeta.setToolTip(carpeta_seleccionada)

if __name__ == "__main__":
    app = QApplication([])
    window = SubirArchivos()
    window.show()
    app.exec_()

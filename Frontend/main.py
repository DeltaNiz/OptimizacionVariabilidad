from PyQt5.QtWidgets import QApplication, QWidget, QDesktopWidget, QMainWindow, QMenuBar, QLabel, QVBoxLayout, QMessageBox
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon
import SubirArchivos
import sys
import os
import multiprocessing as mp

# Configuración especial para PyInstaller y multiprocessing
if hasattr(sys, 'frozen') and hasattr(sys, '_MEIPASS'):
    # Estamos en un ejecutable empaquetado por PyInstaller
    try:
        mp.set_start_method('spawn', force=True)
    except RuntimeError:
        pass  # Ya configurado

class Main(QMainWindow):
    def __init__(self):
        super().__init__()
        self.init_ui()
        self._barra_menu()

    def _barra_menu(self):
        menuBar = self.menuBar()
        # Crear un menú "Subir Archivo"
        file_menu = menuBar.addMenu("Subir Archivo")
        # Agregar acciones al menú "Subir Archivo"
        new_action = file_menu.addAction("Nuevo")
        new_action.triggered.connect(self.abrir_ventana_subir_archivo)
        menuBar.addMenu(file_menu)

        # Crear un menú "Acerca de"
        about_menu = menuBar.addMenu("Acerca de")
        # Agregar acciones al menú "Acerca de"
        about_action = about_menu.addAction("Acerca de SODEV-CG")
        about_action.triggered.connect(self.mostrar_acerca_de)
        menuBar.addMenu(about_menu)
    
    def abrir_ventana_subir_archivo(self):
        """Abre una ventana emergente para subir archivos"""
        # Crear una instancia de la ventana SubirArchivos pasando referencia a esta ventana
        self.ventana_subir = SubirArchivos.SubirArchivos(ventana_main=self)
        # Mostrar la ventana como modal (bloquea la ventana principal)
        self.ventana_subir.setWindowModality(Qt.ApplicationModal)
        # Mostrar la ventana
        self.ventana_subir.show()
    
    def mostrar_acerca_de(self):
        """Muestra una ventana emergente con información sobre la aplicación"""
        msg = QMessageBox(self)
        msg.setWindowTitle("Acerca de SODEV-CG")
        msg.setIcon(QMessageBox.Information)
        
        # Configurar color de fondo
        msg.setStyleSheet("QMessageBox { background-color: #f0f0f0; }")
        
        # Texto principal
        texto = """<h2>SODEV-CG</h2>
        <p><b><i>Sistema para la Optimización en la Detección de Estrellas Variables en Cúmulos Globulares</i></b></p>
        <p><i>Versión 0.1.0</i></p>
        <p><b>Desarrollado por:</b> Tomás Valenzuela Vergara</p>
        <p><b>Email:</b> tvalenzuela20@alumnos.utalca.cl</p>
        <p><b>Colaboradores:</b> Tomás Cisternas - Caddy Cortés - Sandro Villanova - Ricardo Pérez - Carolina Salgado</p>
        <p><b>Institución:</b> Universidad de Talca, Facultad de Ingeniería - Departamento de Ciencias de la Computación, Curicó, Chile.</p>
        <p><b>Año:</b> 2025</p>
        """
        msg.setText(texto)
        msg.setStandardButtons(QMessageBox.Ok)
        msg.setFixedSize(250, 350)
        
        msg.exec_()

    def init_ui(self):
        # Configurar el icono de la ventana
        if hasattr(sys, '_MEIPASS'):
            # Ruta del icono cuando está empaquetado con PyInstaller
            icon_path = os.path.join(sys._MEIPASS, 'media', 'icono.ico')
        else:
            # Ruta del icono en desarrollo
            icon_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'media', 'icono.ico')
        
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))
        
        # Obtener información de la pantalla
        desktop = QDesktopWidget()
        screen_geometry = desktop.screenGeometry()
        screen_width = screen_geometry.width()
        screen_height = screen_geometry.height()
        vertical_offset = 0
        
        # Lógica similar a media queries
        if screen_width <= 1366:  # Pantallas pequeñas/laptops
            self.resize(480, 200)
            self.setWindowTitle("SODEV-CG")
            margin_y_size = "42px"  # Menos margen para pantallas pequeñas
            margin_x_size = "83px"  # Menos margen para pantallas pequeñas
            text_size = "28px"  # Tamaño de texto más pequeño
            vertical_offset = -95
            # Guardar dimensiones para fijar al final
            self.fixed_width, self.fixed_height = 490, 290

        elif screen_width <= 1920:  # Pantallas medianas/Full HD
            self.resize(600, 280)
            self.setWindowTitle("SODEV-CG")
            margin_y_size = "50px"  # Margen muy pequeño para ventana mediana
            margin_x_size = "100px"  # Margen muy pequeño para ventana mediana
            text_size = "36px"  # Tamaño de texto intermedio
            vertical_offset = -95
            # Guardar dimensiones para fijar al (las resoluciones son distintas al resize porque pyqt asi lo quiso xd)
            self.fixed_width, self.fixed_height = 600, 330

        else:  # Pantallas grandes/4K
            self.resize(1600, 1000)
            self.setWindowTitle("SODEV-CG")
            margin_size = "300px"  # Margen grande para pantallas grandes
            text_size = "42px"  # Tamaño de texto grande
            vertical_offset = -20
            # Guardar dimensiones para fijar al final
            self.fixed_width, self.fixed_height = 1600, 1000
        
        # Centrar la ventana en la pantalla con un offset vertical
        center_point = desktop.screen().rect().center() - self.rect().center()
        self.move(center_point.x(), center_point.y() + vertical_offset)

        # Crear un texto centrado en la ventana principal
        central_label = QLabel()

        # Usar HTML para diferentes tamaños de texto
        welcome_text = "SODEV-CG"
        subtitle_text = "Suba un archivo para realizar el análisis"
        
        # Definir el tamaño del subtítulo basado en el tamaño principal
        if text_size == "28px":
            subtitle_size = "13px"
        elif text_size == "36px":
            subtitle_size = "18px"
        else:
            subtitle_size = "16px"
        
        # Combinar ambos textos con HTML
        combined_text = f"""
            <div style="text-align: center;">
                <div style="font-size: {text_size}; font-weight: bold; font-style: italic; margin-bottom: 10px;">
                    {welcome_text}
                </div>
                <div style="font-size: {subtitle_size}; font-weight: normal; opacity: 0.9;">
                    {subtitle_text}
                </div>
            </div>
        """
        
        central_label.setText(combined_text)
        central_label.setAlignment(Qt.AlignCenter)  # Centrar el texto
        central_label.setStyleSheet(f"""
            QLabel {{
                background-color: #a7c942;  /* Verde como figura de fondo */
                font-size: {text_size};  /* Tamaño de texto dinámico */
                font-weight: bold;
                color: white;  /* Texto blanco para contraste */
                padding: 40px;
                border-radius: 20px;  /* Esquinas redondeadas */
                border: 3px solid #98b83b;  /* Borde verde más oscuro */
                margin-left: {margin_x_size};
                margin-right: {margin_x_size};
                margin-top: {margin_y_size};
                margin-bottom: {margin_y_size};
            }}
        """)
        
        # Crear pie de página
        footer_label = QLabel()
        footer_text = "¡Bienvenido! | Versión 0.1.0"
        footer_label.setText(footer_text)
        footer_label.setAlignment(Qt.AlignCenter)
        footer_label.setStyleSheet("""
            QLabel {
                color: #666666;
                font-size: 12px;
                font-style: italic;
                padding: 10px;
                background-color: #f5f5f5;
                border-top: 1px solid #ddd;
            }
        """)
        
        # Crear un widget contenedor para organizar el layout
        container_widget = QWidget()
        main_layout = QVBoxLayout()
        
        # Añadir el contenido principal y el pie de página
        main_layout.addWidget(central_label)
        main_layout.addWidget(footer_label)
        main_layout.setContentsMargins(0, 0, 0, 0)  # Sin márgenes en el layout
        
        container_widget.setLayout(main_layout)
        
        # Establecer el contenedor como widget central
        self.setCentralWidget(container_widget)
        
        # Hacer la ventana no redimensionable AL FINAL
        self.setFixedSize(self.fixed_width, self.fixed_height)

if __name__ == "__main__":
    # Protección para multiprocessing en PyInstaller
    mp.freeze_support()
    
    app = QApplication(sys.argv)
    window = Main()
    window.show()  # IMPORTANTE!!! LAS VENTANAS NO SE MUESTRAN HASTA QUE SE LLAME A show()
    
    # llamar a la app
    app.exec()
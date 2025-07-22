from PyQt5.QtWidgets import QApplication, QWidget, QDesktopWidget, QMainWindow, QMenuBar, QLabel, QVBoxLayout
from PyQt5.QtCore import Qt
import SubirArchivos
import sys

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
        #about_action = about_menu.addAction("Acerca de")
        menuBar.addMenu(about_menu)
    
    def abrir_ventana_subir_archivo(self):
        """Abre una ventana emergente para subir archivos"""
        # Crear una instancia de la ventana SubirArchivos pasando referencia a esta ventana
        self.ventana_subir = SubirArchivos.SubirArchivos(ventana_main=self)
        # Mostrar la ventana como modal (bloquea la ventana principal)
        self.ventana_subir.setWindowModality(Qt.ApplicationModal)
        # Mostrar la ventana
        self.ventana_subir.show()

    def init_ui(self):
        # Obtener información de la pantalla
        desktop = QDesktopWidget()
        screen_geometry = desktop.screenGeometry()
        screen_width = screen_geometry.width()
        screen_height = screen_geometry.height()
        vertical_offset = 0
        
        print(f"Resolución de pantalla: {screen_width}x{screen_height}")
        print(f"Tipo de pantalla detectado: {'Pequeña' if screen_width <= 1366 else 'Mediana' if screen_width <= 1920 else 'Grande'}")
        
        # Lógica similar a media queries
        if screen_width <= 1366:  # Pantallas pequeñas/laptops
            self.resize(600, 400)
            self.setWindowTitle("Nombre de Aplicación - Pantalla Pequeña")
            margin_size = "150px"  # Menos margen para pantallas pequeñas
            text_size = "24px"  # Tamaño de texto más pequeño
            vertical_offset = -75
            print(f"Configuración aplicada: Pantalla pequeña - Ventana: {self.width()}x{self.height()}")
        elif screen_width <= 1920:  # Pantallas medianas/Full HD
            self.resize(600, 400)
            self.setWindowTitle("Nombre de Aplicación - Pantalla Mediana")
            margin_size = "100px"  # Margen muy pequeño para ventana mediana
            text_size = "36px"  # Tamaño de texto intermedio
            vertical_offset = -35
            print(f"Configuración aplicada: Pantalla mediana - Ventana: {self.width()}x{self.height()}")
        else:  # Pantallas grandes/4K
            self.resize(1600, 1000)
            self.setWindowTitle("Nombre de Aplicación - Pantalla Grande")
            margin_size = "300px"  # Margen grande para pantallas grandes
            text_size = "42px"  # Tamaño de texto grande
            vertical_offset = -20
            print(f"Configuración aplicada: Pantalla grande - Ventana: {self.width()}x{self.height()}")
        
        # Centrar la ventana en la pantalla con un offset vertical
        center_point = desktop.screen().rect().center() - self.rect().center()
        self.move(center_point.x(), center_point.y() + vertical_offset)

        # Crear un texto centrado en la ventana principal
        central_label = QLabel()

        # Usar HTML para diferentes tamaños de texto
        welcome_text = "¡Bienvenido!"
        subtitle_text = "Suba un archivo para realizar el análisis"
        
        # Definir el tamaño del subtítulo basado en el tamaño principal
        if text_size == "24px":
            subtitle_size = "14px"
        elif text_size == "36px":
            subtitle_size = "18px"
        else:
            subtitle_size = "16px"
        
        # Combinar ambos textos con HTML
        combined_text = f"""
            <div style="text-align: center;">
                <div style="font-size: {text_size}; font-weight: bold; margin-bottom: 10px;">
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
                margin: {margin_size};
            }}
        """)
        
        # Crear pie de página
        footer_label = QLabel()
        footer_text = "Nombre de aplicación | Versión 0.0.1"
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
        

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = Main()
    window.show()  # IMPORTANTE!!! LAS VENTANAS NO SE MUESTRAN HASTA QUE SE LLAME A show()
    
    # llamar a la app
    app.exec()
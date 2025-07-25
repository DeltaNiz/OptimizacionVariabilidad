from PyQt5.QtWidgets import QMainWindow, QApplication, QMessageBox, QDialog, QVBoxLayout, QLabel, QProgressBar, QPushButton, QTextEdit
from PyQt5.QtCore import Qt, QThread, pyqtSignal
import pandas as pd
import sys
import argparse
import os
import subprocess
from datetime import datetime
import re

class VentanaProgreso(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Progreso del Análisis")
        self.setFixedSize(500, 400)
        self.setModal(True)
        self.worker_thread = None  # Referencia al worker thread
        
        # Layout principal
        layout = QVBoxLayout()
        
        # Etiqueta de estado
        self.label_estado = QLabel("Iniciando análisis...")
        self.label_estado.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.label_estado)
        
        # Etiqueta de progreso de estrellas (arriba de la barra)
        self.label_progreso_estrellas = QLabel("")
        self.label_progreso_estrellas.setAlignment(Qt.AlignCenter)
        self.label_progreso_estrellas.setStyleSheet("font-weight: bold; color: #333; margin: 5px;")
        layout.addWidget(self.label_progreso_estrellas)
        
        # Barra de progreso principal
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        layout.addWidget(self.progress_bar)
        
        # Etiqueta de progreso detallado
        self.label_detalle = QLabel("")
        self.label_detalle.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.label_detalle)
        
        # Área de texto para mostrar el log en tiempo real
        self.text_log = QTextEdit()
        self.text_log.setMaximumHeight(200)
        self.text_log.setReadOnly(True)
        layout.addWidget(self.text_log)
        
        # Layout para botones
        botones_layout = QVBoxLayout()
        
        # Botón para cancelar (habilitado durante el análisis)
        self.btn_cancelar = QPushButton("Cancelar Análisis")
        self.btn_cancelar.setEnabled(True)
        self.btn_cancelar.clicked.connect(self.cancelar_analisis)
        botones_layout.addWidget(self.btn_cancelar)
        
        # Botón para cerrar (inicialmente deshabilitado)
        self.btn_cerrar = QPushButton("Cerrar")
        self.btn_cerrar.setEnabled(False)
        self.btn_cerrar.clicked.connect(self.accept)
        botones_layout.addWidget(self.btn_cerrar)
        
        layout.addLayout(botones_layout)
        
        self.setLayout(layout)
        
        # Variable para controlar cancelación
        self.cancelado = False
        
    def cancelar_analisis(self):
        """Solicita cancelación del análisis"""
        respuesta = QMessageBox.question(
            self, 
            "Cancelar Análisis", 
            "¿Estás seguro de que deseas cancelar el análisis?\n\nSe perderá todo el progreso actual.",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if respuesta == QMessageBox.Yes:
            self.cancelado = True
            self.label_estado.setText("Cancelando análisis...")
            self.label_progreso_estrellas.setText("Cancelando...")
            self.btn_cancelar.setEnabled(False)
            self.agregar_log("--- CANCELACIÓN SOLICITADA POR EL USUARIO ---")
            self.agregar_log("Terminando procesos en curso...")
            
            # Cancelar inmediatamente el worker thread
            if self.worker_thread and self.worker_thread.isRunning():
                self.worker_thread.forzar_cancelacion()
                self.agregar_log("Terminando proceso inmediatamente...")
            
            QApplication.processEvents()
            
            # Forzar actualización inmediata de la interfaz
            self.repaint()
            QApplication.processEvents()
        
    def actualizar_estado(self, texto, progreso=None):
        """Actualiza el estado del análisis"""
        self.label_estado.setText(texto)
        if progreso is not None:
            self.progress_bar.setValue(progreso)
        QApplication.processEvents()
        
    def actualizar_detalle(self, texto):
        """Actualiza el detalle del progreso"""
        self.label_detalle.setText(texto)
        QApplication.processEvents()
        
    def actualizar_progreso_estrellas(self, actual, total):
        """Actualiza el progreso específico de estrellas"""
        if total > 0:
            # Progreso base: 25% (hasta el inicio del procesamiento de estrellas)
            # Progreso de estrellas: 75% restante (25% a 100%)
            progreso_base = 25
            progreso_estrellas = 75
            
            # Calcular porcentaje de estrellas completadas
            porcentaje_estrellas = (actual / total) * progreso_estrellas
            porcentaje_total = progreso_base + porcentaje_estrellas
            
            self.progress_bar.setValue(int(porcentaje_total))
            
            # Determinar el texto del estado basado en si es completado o en progreso
            if actual == 0:
                # Iniciando
                self.label_estado.setText(f"Procesando estrella 0/{total}")
            elif actual == total:
                # Todas completadas
                self.label_estado.setText(f"Completadas {actual}/{total} estrellas")
            else:
                # En progreso - mostrar la próxima a procesar
                self.label_estado.setText(f"Procesando estrella {actual + 1}/{total}")
            
            # Mantener el label de progreso de estrellas vacío
            self.label_progreso_estrellas.setText("")
        QApplication.processEvents()
        
    def actualizar_fase_analisis(self, fase, porcentaje_base=0):
        """Actualiza la fase del análisis con un porcentaje base"""
        # Actualizar el estado normalmente, ya que actualizar_progreso_estrellas sobreescribirá cuando sea necesario
        self.label_estado.setText(fase)
        if porcentaje_base > 0:
            self.progress_bar.setValue(porcentaje_base)
            # Limpiar el label de progreso de estrellas solo en fases iniciales
            if porcentaje_base < 25:  # Solo en las primeras fases
                self.label_progreso_estrellas.setText("")
        QApplication.processEvents()
        
    def agregar_log(self, texto):
        """Agrega texto al log"""
        self.text_log.append(texto)
        # Scroll automático al final
        scrollbar = self.text_log.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())
        QApplication.processEvents()
        
    def analisis_completado(self, exito=True, cancelado=False):
        """Marca el análisis como completado"""
        if cancelado:
            self.label_estado.setText("Análisis cancelado por el usuario")
            self.btn_cancelar.setEnabled(False)
        elif exito:
            self.label_estado.setText("¡Análisis completado exitosamente!")
            self.progress_bar.setValue(100)
            self.btn_cancelar.setEnabled(False)
        else:
            self.label_estado.setText("Error en el análisis")
            self.btn_cancelar.setEnabled(False)
        self.btn_cerrar.setEnabled(True)
        QApplication.processEvents()

class WorkerThread(QThread):
    # Señales para comunicarse con la interfaz
    estado_cambiado = pyqtSignal(str, int)
    detalle_cambiado = pyqtSignal(str)
    progreso_estrellas = pyqtSignal(int, int)  # actual, total
    fase_analisis = pyqtSignal(str, int)  # fase, porcentaje_base
    log_agregado = pyqtSignal(str)
    analisis_terminado = pyqtSignal(bool, str)
    
    def __init__(self, datos_filtrados, datos_formulario, ventana_progreso):
        super().__init__()
        self.datos_filtrados = datos_filtrados
        self.datos_formulario = datos_formulario
        self.ventana_progreso = ventana_progreso
        self.proceso_actual = None
        self.cancelacion_forzada = False
        
    def forzar_cancelacion(self):
        """Fuerza la cancelación inmediata"""
        self.cancelacion_forzada = True
        if self.proceso_actual and self.proceso_actual.poll() is None:
            try:
                self.proceso_actual.kill()  # Terminación inmediata
                self.log_agregado.emit("Proceso terminado inmediatamente")
            except:
                pass
        
    def cancelar(self):
        """Cancela el proceso actual"""
        if self.proceso_actual and self.proceso_actual.poll() is None:
            try:
                # Intentar terminación suave primero
                self.proceso_actual.terminate()
                self.log_agregado.emit("Terminando proceso...")
                
                # Esperar un poco para terminación suave
                import time
                time.sleep(1)
                
                # Si aún está ejecutándose, forzar terminación
                if self.proceso_actual.poll() is None:
                    self.proceso_actual.kill()
                    self.log_agregado.emit("Proceso terminado forzosamente")
                else:
                    self.log_agregado.emit("Proceso terminado correctamente")
            except Exception as e:
                self.log_agregado.emit(f"Error al terminar proceso: {e}")
                try:
                    self.proceso_actual.kill()
                    self.log_agregado.emit("Proceso forzosamente terminado")
                except:
                    pass
        
    def run(self):
        """Ejecuta el análisis en un hilo separado"""
        try:
            # Verificar cancelación antes de cada paso
            if self.ventana_progreso.cancelado:
                self.analisis_terminado.emit(False, "Análisis cancelado por el usuario")
                return
                
            self.fase_analisis.emit("Generando archivo CSV...", 5)
            self.log_agregado.emit("=== INICIANDO ANÁLISIS ===")
            
            # Generar CSV automáticamente
            ruta_csv = self.generar_csv_automatico()
            
            if not ruta_csv or self.ventana_progreso.cancelado:
                if self.ventana_progreso.cancelado:
                    self.analisis_terminado.emit(False, "Análisis cancelado por el usuario")
                else:
                    self.analisis_terminado.emit(False, "Error al generar el archivo CSV")
                return
                
            self.fase_analisis.emit("Ejecutando copiar.py...", 15)
            self.log_agregado.emit("Ejecutando copiar.py...")
            
            # Ejecutar copiar.py automáticamente
            exito_copia, nombre_subcarpeta = self.ejecutar_copiar_py(ruta_csv)
            
            if not exito_copia or self.ventana_progreso.cancelado:
                if self.ventana_progreso.cancelado:
                    self.analisis_terminado.emit(False, "Análisis cancelado por el usuario")
                else:
                    self.analisis_terminado.emit(False, "Error al copiar archivos")
                return
                
            self.fase_analisis.emit("Procesando estrellas...", 25)
            self.log_agregado.emit(f"Subcarpeta creada: data/{nombre_subcarpeta}")
            self.log_agregado.emit("Ejecutando procesofull.py...")
            
            # Construir ruta completa de la carpeta de datos
            ruta_base = 'C:/Users/tomas/OneDrive/Escritorio/xd/U/2025-1/Formulacion de Proyecto de Titulacion'
            data_folder = os.path.join(ruta_base, 'data', nombre_subcarpeta)
            
            # Ejecutar procesofull.py automáticamente
            exito_proceso = self.ejecutar_procesofull_py(data_folder)
            
            if self.ventana_progreso.cancelado:
                self.analisis_terminado.emit(False, "Análisis cancelado por el usuario")
                return
            
            if exito_proceso:
                # Mostrar progreso completo al final
                self.fase_analisis.emit("¡Análisis completado exitosamente!", 100)
                mensaje_exito = f"Análisis completado exitosamente\n\nCSV generado: {os.path.basename(ruta_csv)}\nEstrellas procesadas: {len(self.datos_filtrados)}\nSubcarpeta: data/{nombre_subcarpeta}"
                self.analisis_terminado.emit(True, mensaje_exito)
            else:
                mensaje_error = f"CSV generado correctamente, pero hubo errores en el procesamiento\n\nCSV: {os.path.basename(ruta_csv)}\nSubcarpeta: data/{nombre_subcarpeta}"
                self.analisis_terminado.emit(False, mensaje_error)
                
        except Exception as e:
            self.log_agregado.emit(f"ERROR: {str(e)}")
            self.analisis_terminado.emit(False, f"Error inesperado: {str(e)}")
    
    def generar_csv_automatico(self):
        """Genera automáticamente un archivo CSV con los datos filtrados"""
        try:
            # Crear DataFrame con los datos filtrados
            df = pd.DataFrame(self.datos_filtrados)
            
            # Seleccionar solo las columnas V, I, MV, MI (sin Numero)
            df = df[['V', 'I', 'MV', 'MI']]
            
            # Generar nombre del archivo con timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            nombre_archivo = f"datos_filtrados_{timestamp}.csv"
            
            # Obtener directorio donde está el script principal
            directorio_actual = os.path.dirname(os.path.abspath(__file__))
            ruta_archivo = os.path.join(directorio_actual, nombre_archivo)
            
            # Guardar CSV sin cabeceras (header=False) y sin índice
            df.to_csv(ruta_archivo, index=False, header=False)
            
            self.log_agregado.emit(f"CSV generado: {nombre_archivo}")
            self.log_agregado.emit(f"Registros exportados: {len(self.datos_filtrados)}")
            
            return ruta_archivo
            
        except Exception as e:
            self.log_agregado.emit(f"Error al generar CSV: {str(e)}")
            return None
    
    def ejecutar_copiar_py(self, ruta_csv):
        """Ejecuta copiar.py automáticamente con el CSV generado"""
        try:
            if self.ventana_progreso.cancelado:
                return False, ""
                
            script_dir = os.path.dirname(os.path.abspath(__file__))
            ruta_copiar = os.path.join(script_dir, 'copiar.py')
            
            if not os.path.exists(ruta_copiar):
                self.log_agregado.emit(f"ADVERTENCIA: No se encontró copiar.py")
                return False, ""
            
            # Generar nombre único para la subcarpeta del análisis
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            nombre_subcarpeta = f"analisis_{timestamp}"
            
            # Ejecutar copiar.py con parámetros
            self.proceso_actual = subprocess.run([
                sys.executable, ruta_copiar,
                '--csv', ruta_csv,
                '--subcarpeta', nombre_subcarpeta
            ], capture_output=True, text=True)
            
            if self.ventana_progreso.cancelado:
                return False, ""
            
            if self.proceso_actual.returncode == 0:
                self.log_agregado.emit("Archivos copiados correctamente")
                if self.proceso_actual.stdout:
                    self.log_agregado.emit(self.proceso_actual.stdout.strip())
                return True, nombre_subcarpeta
            else:
                self.log_agregado.emit("ERROR al ejecutar copiar.py")
                if self.proceso_actual.stderr:
                    self.log_agregado.emit(f"Error: {self.proceso_actual.stderr}")
                return False, ""
                
        except Exception as e:
            self.log_agregado.emit(f"ERROR al ejecutar copiar.py: {e}")
            return False, ""
    
    def ejecutar_procesofull_py(self, data_folder):
        """Ejecuta procesofull.py automáticamente con la carpeta de datos generada"""
        try:
            if self.ventana_progreso.cancelado:
                return False
                
            script_dir = os.path.dirname(os.path.abspath(__file__))
            ruta_procesofull = os.path.join(script_dir, 'procesofull.py')
            
            if not os.path.exists(ruta_procesofull):
                self.log_agregado.emit(f"ADVERTENCIA: No se encontró procesofull.py")
                return False
            
            # Ejecutar procesofull.py con parámetros y mostrar output en tiempo real
            self.proceso_actual = subprocess.Popen([
                sys.executable, '-u', ruta_procesofull,  # -u para unbuffered output
                '--data_folder', data_folder
            ], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, bufsize=0, universal_newlines=True)
            
            total_estrellas = 0
            estrellas_procesadas = 0
            analisis_iniciado = False
            
            # Leer y mostrar output línea por línea en tiempo real
            import platform
            
            while True:
                # Verificar cancelación periódicamente
                if self.ventana_progreso.cancelado or self.cancelacion_forzada:
                    self.log_agregado.emit("Cancelación detectada, terminando proceso...")
                    self.cancelar()
                    return False
                
                # Leer línea con verificación de cancelación frecuente
                try:
                    output = self.proceso_actual.stdout.readline()
                    if output == '' and self.proceso_actual.poll() is not None:
                        break
                except Exception as e:
                    self.log_agregado.emit(f"Error leyendo output: {str(e)}")
                    break
                    
                # Verificar cancelación después de cada línea leída
                if self.ventana_progreso.cancelado or self.cancelacion_forzada:
                    self.log_agregado.emit("Cancelación detectada durante lectura, terminando proceso...")
                    self.cancelar()
                    return False
                    
                if output:
                    linea = output.strip()
                    self.log_agregado.emit(linea)
                    
                    # Detectar total de estrellas al inicio
                    if "Total de estrellas a procesar:" in linea:
                        try:
                            match = re.search(r'Total de estrellas a procesar:\s*(\d+)', linea)
                            if match:
                                total_estrellas = int(match.group(1))
                                if not analisis_iniciado:
                                    # Inicializar progreso inmediatamente con el total detectado
                                    self.progreso_estrellas.emit(0, total_estrellas)
                                    analisis_iniciado = True
                        except:
                            pass
                    
                    # Detectar progreso con formato "Procesando estrella X/Y"
                    elif re.search(r'Procesando estrella (\d+)/(\d+)', linea):
                        try:
                            match = re.search(r'Procesando estrella (\d+)/(\d+)', linea)
                            if match:
                                actual = int(match.group(1))
                                total = int(match.group(2))
                                total_estrellas = total
                                
                                # Actualizar usando la señal específica para estrellas - mostrar que está procesando
                                # actual-1 porque representa estrellas completadas, no la que se está procesando
                                self.progreso_estrellas.emit(actual - 1, total)
                                analisis_iniciado = True
                        except:
                            pass
                    
                    # Detectar estrella individual siendo procesada
                    elif re.search(r'estrella[:\s]+(\d+)', linea, re.IGNORECASE):
                        try:
                            match = re.search(r'estrella[:\s]+(\d+)', linea, re.IGNORECASE)
                            if match:
                                numero_estrella = match.group(1)
                                if "procesando" in linea.lower() or "analizando" in linea.lower():
                                    self.detalle_cambiado.emit(f"Estrella actual: {numero_estrella}")
                                    
                                    # Si sabemos el total, actualizar progreso basado en el número de estrella
                                    if total_estrellas > 0:
                                        try:
                                            estrella_num = int(numero_estrella)
                                            # Calcular progreso basado en la estrella actual
                                            estrellas_procesadas = max(1, estrella_num)  # Al menos 1
                                            self.progreso_estrellas.emit(estrellas_procesadas, total_estrellas)
                                        except:
                                            pass
                                elif "leyendo" in linea.lower() or "archivo" in linea.lower():
                                    self.detalle_cambiado.emit(f"Leyendo datos estrella {numero_estrella}")
                        except:
                            pass
                    
                    # Detectar nombres de archivos siendo procesados
                    elif re.search(r'\b\d+\.(txt|dat)\b', linea):
                        try:
                            match = re.search(r'\b(\d+\.(txt|dat))\b', linea)
                            if match:
                                archivo = match.group(1)
                                numero = archivo.split('.')[0]
                                self.detalle_cambiado.emit(f"Procesando archivo estrella {numero}")
                        except:
                            pass
                    
                    # Detectar fases específicas del análisis
                    elif "GLS" in linea and ("ejecut" in linea.lower() or "anali" in linea.lower()):
                        self.detalle_cambiado.emit("Ejecutando análisis GLS...")
                    elif "PDM" in linea and ("ejecut" in linea.lower() or "anali" in linea.lower()):
                        self.detalle_cambiado.emit("Ejecutando análisis PDM...")
                    elif "gráfico" in linea.lower() or "plot" in linea.lower() or "visualiz" in linea.lower():
                        self.detalle_cambiado.emit("Generando visualizaciones...")
                    elif "guardando" in linea.lower() or "exportando" in linea.lower():
                        self.detalle_cambiado.emit("Guardando resultados...")
                    
                    elif "completada exitosamente" in linea or "completado exitosamente" in linea:
                        # Actualizar progreso cuando se completa una estrella
                        if total_estrellas > 0:
                            estrellas_procesadas += 1
                            # Usar la señal progreso_estrellas para actualizar correctamente
                            self.progreso_estrellas.emit(estrellas_procesadas, total_estrellas)
                            self.detalle_cambiado.emit(f"✓ Estrella completada ({estrellas_procesadas}/{total_estrellas})")
                    
                    elif "Procesamiento completado" in linea or "Análisis completado" in linea:
                        # Finalización completa - usar señal estado_cambiado
                        self.estado_cambiado.emit("¡Análisis completado exitosamente!", 100)
                    
                    # Detectar inicio de análisis de cualquier estrella para forzar actualización
                    elif ("iniciando" in linea.lower() or "comenzando" in linea.lower()) and "estrella" in linea.lower():
                        if total_estrellas > 0 and not analisis_iniciado:
                            self.progreso_estrellas.emit(0, total_estrellas)
                            analisis_iniciado = True
                    
                    # Si detectamos alguna línea que sugiere que ya hay al menos 1 estrella procesándose
                    elif total_estrellas == 0 and ("procesando estrella" in linea.lower() or "analizando estrella" in linea.lower()):
                        # Asumir al menos 1 estrella si no se detectó el total antes
                        total_estrellas = 1
                        self.progreso_estrellas.emit(1, 1)
                        analisis_iniciado = True
                    
                    # Detectar cualquier indicador de que el procesamiento de estrellas ya comenzó
                    elif any(keyword in linea.lower() for keyword in ["leyendo archivo", "archivo procesado", "gls", "pdm", "período"]) and total_estrellas > 0:
                        if not analisis_iniciado:
                            self.progreso_estrellas.emit(1, total_estrellas)
                            analisis_iniciado = True
                    
                    # Detectar si procesofull.py ya está ejecutándose con estrellas
                    elif "procesofull.py" in linea.lower() and total_estrellas == 0:
                        # Si no hemos detectado total pero procesofull está corriendo, asumir al menos 1
                        total_estrellas = 1
                        self.progreso_estrellas.emit(0, 1)
                        analisis_iniciado = True
            
            rc = self.proceso_actual.poll()
            
            if self.ventana_progreso.cancelado:
                return False
            
            if rc == 0:
                self.log_agregado.emit("ÉXITO: Procesamiento de estrellas completado")
                return True
            else:
                self.log_agregado.emit(f"ERROR: Código de retorno: {rc}")
                return False
                
        except Exception as e:
            self.log_agregado.emit(f"ERROR al ejecutar procesofull.py: {e}")
            return False

class Analisis(QMainWindow):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        # Obtener información de la pantalla
        screen_geometry = QApplication.desktop().screenGeometry()
        screen_width = screen_geometry.width()
        screen_height = screen_geometry.height()
        
        print(f"Resolución de pantalla: {screen_width}x{screen_height}")
        
        # Lógica similar a media queries
        if screen_width <= 1366:  # Pantallas pequeñas/laptops
            self.resize(600, 400)
            self.setWindowTitle("Análisis - Pantalla Pequeña")
            print(f"Configuración aplicada: Pantalla pequeña - Ventana: {self.width()}x{self.height()}")
        elif screen_width <= 1920:  # Pantallas medianas/Full HD
            self.resize(800, 600)
            self.setWindowTitle("Análisis - Pantalla Mediana")
            print(f"Configuración aplicada: Pantalla mediana - Ventana: {self.width()}x{self.height()}")
        else:  # Pantallas grandes
            self.resize(1000, 800)
            self.setWindowTitle("Análisis - Pantalla Grande")
            print(f"Configuración aplicada: Pantalla grande - Ventana: {self.width()}x{self.height()}")

def obtener_datos_filtrados(table_main, table_descartadas):
    """Obtiene los datos de la tabla principal excluyendo las filas descartadas"""
    datos_filtrados = []
    
    # Obtener números de estrellas descartadas
    numeros_descartados = set()
    for row in range(table_descartadas.rowCount()):
        item = table_descartadas.item(row, 0)
        if item:
            numeros_descartados.add(int(item.text()))
    
    # Recorrer la tabla principal y agregar solo las filas no descartadas
    for row in range(table_main.rowCount()):
        numero_item = table_main.item(row, 0)
        if numero_item:
            numero_estrella = int(numero_item.text())
            
            # Si la estrella no está descartada, incluirla
            if numero_estrella not in numeros_descartados:
                fila_datos = {}
                
                # Obtener datos de cada columna
                fila_datos['Numero'] = numero_estrella
                
                v_item = table_main.item(row, 1)
                fila_datos['V'] = v_item.text() if v_item else ""
                
                i_item = table_main.item(row, 2)
                fila_datos['I'] = i_item.text() if i_item else ""
                
                mv_item = table_main.item(row, 3)
                fila_datos['MV'] = mv_item.text() if mv_item else ""
                
                mi_item = table_main.item(row, 4)
                fila_datos['MI'] = mi_item.text() if mi_item else ""
                
                datos_filtrados.append(fila_datos)
    
    print(f"Datos filtrados: {len(datos_filtrados)} estrellas (de {table_main.rowCount()} originales)")
    return datos_filtrados

def realizar_analisis_completo(table_main, table_descartadas, datos_formulario):
    """Método principal para realizar el análisis completo con los datos filtrados"""
    try:
        print("=== INICIANDO ANÁLISIS ===")
        
        # Obtener datos filtrados (sin las filas descartadas)
        datos_filtrados = obtener_datos_filtrados(table_main, table_descartadas)
        
        if not datos_filtrados:
            print("No hay datos para analizar")
            return False, "No hay datos filtrados para generar el CSV."
        
        # Crear y mostrar ventana de progreso
        app = QApplication.instance()
        if app is None:
            app = QApplication([])
            
        ventana_progreso = VentanaProgreso()
        
        # Crear worker thread
        worker = WorkerThread(datos_filtrados, datos_formulario, ventana_progreso)
        
        # Asignar referencia del worker a la ventana
        ventana_progreso.worker_thread = worker
        
        # Conectar señales
        worker.estado_cambiado.connect(ventana_progreso.actualizar_estado)
        worker.detalle_cambiado.connect(ventana_progreso.actualizar_detalle)
        worker.progreso_estrellas.connect(ventana_progreso.actualizar_progreso_estrellas)
        worker.fase_analisis.connect(ventana_progreso.actualizar_fase_analisis)
        worker.log_agregado.connect(ventana_progreso.agregar_log)
        
        resultado_final = [False, ""]
        
        def on_analisis_terminado(exito, mensaje):
            if ventana_progreso.cancelado:
                ventana_progreso.analisis_completado(exito=False, cancelado=True)
            else:
                ventana_progreso.analisis_completado(exito)
            resultado_final[0] = exito
            resultado_final[1] = mensaje
        
        worker.analisis_terminado.connect(on_analisis_terminado)
        
        # Iniciar el worker
        worker.start()
        
        # Mostrar ventana de progreso
        ventana_progreso.exec_()
        
        # Esperar a que termine el worker
        worker.wait()
        
        return resultado_final[0], resultado_final[1]
        
    except Exception as e:
        error_msg = f"ERROR en realizar_analisis_completo: {e}"
        print(error_msg)
        import traceback
        traceback.print_exc()
        return False, error_msg

def procesar_csv_analisis(ruta_csv, parametros):
    """Procesa el CSV generado y muestra la información en consola"""
    try:
        
        # Verificar que el archivo existe
        if not os.path.exists(ruta_csv):
            print(f"ERROR: No se encontró el archivo CSV: {ruta_csv}")
            return
        
        # Leer el CSV sin cabeceras y asignar nombres de columnas
        df = pd.read_csv(ruta_csv, header=None)
        df.columns = ['V', 'I', 'MV', 'MI']
        
        if not df.empty:
            # Estadísticas básicas para columnas numéricas
            columnas_numericas = ['V', 'I', 'MV', 'MI']
            for col in columnas_numericas:
                if col in df.columns:
                    try:
                        # Convertir a numérico, manejando errores
                        df[col] = pd.to_numeric(df[col], errors='coerce')
                        valores_validos = df[col].dropna()
                
                    except:
                        print(f"No se pudieron calcular estadísticas para columna {col}")
            
            
            for idx, row in df.head(10).iterrows():
                print(f"{row['V']:<12} {row['I']:<12} {row['MV']:<12} {row['MI']:<12}")
            
            if len(df) > 10:
                print(f"... y {len(df) - 10} filas más")
            
        else:
            print("El CSV está vacío")
        
        print()
        print("=" * 80)
        print("ANÁLISIS COMPLETADO EXITOSAMENTE")
        print("=" * 80)
        
    except Exception as e:
        print(f"ERROR al procesar CSV: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    # Si se ejecuta desde línea de comandos con parámetros
    if len(sys.argv) > 1:
        parser = argparse.ArgumentParser(description='Análisis de datos filtrados')
        parser.add_argument('--ruta_csv', required=True, help='Ruta del archivo CSV a procesar')
        parser.add_argument('--periodo_max', help='Periodo máximo en días')
        parser.add_argument('--periodo_min', help='Periodo mínimo en días')
        parser.add_argument('--step', help='Step en días')
        parser.add_argument('--carpeta_filtro_I', help='Carpeta del filtro I')
        parser.add_argument('--carpeta_filtro_V', help='Carpeta del filtro V')
        parser.add_argument('--archivo_csv', help='Archivo CSV original')
        
        args = parser.parse_args()
        
        # Crear diccionario con los parámetros
        parametros = {
            'periodo_max': args.periodo_max,
            'periodo_min': args.periodo_min,
            'step': args.step,
            'carpeta_filtro_I': args.carpeta_filtro_I,
            'carpeta_filtro_V': args.carpeta_filtro_V,
            'archivo_csv': args.archivo_csv
        }
        
        # Procesar el CSV
        procesar_csv_analisis(args.ruta_csv, parametros)
    else:
        # Si se ejecuta normalmente, abrir la interfaz gráfica
        app = QApplication(sys.argv)
        window = Analisis()
        window.show()
        sys.exit(app.exec_())
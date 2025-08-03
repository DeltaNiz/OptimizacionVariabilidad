from PyQt5.QtWidgets import QMainWindow, QApplication, QMessageBox, QDialog, QVBoxLayout, QLabel, QProgressBar, QPushButton, QTextEdit
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QTimer
import pandas as pd
import sys
import argparse
import os
import subprocess
from datetime import datetime
import re
import time
import importlib.util
import traceback

class AppConstants:
    """Clase centralizada para todas las constantes del proyecto"""
    
    # Constantes del proyecto
    RUTA_BASE_PROYECTO = 'C:/Users/tomas/OneDrive/Escritorio/xd/U/2025-1/Formulacion de Proyecto de Titulacion'
    COLUMNAS_CSV = ['V', 'I', 'MV', 'MI']
    EXTENSIONES_ARCHIVOS = {
        'csv': '.csv',
        'txt': '.txt',
        'dat': '.dat'
    }
    
    # Constantes de progreso
    PROGRESO_BASE = 25  # Porcentaje base antes del procesamiento de estrellas
    PROGRESO_ESTRELLAS = 75  # Porcentaje asignado al procesamiento de estrellas
    
    # Palabras clave para detección de fases
    KEYWORDS_ARCHIVO = ["leyendo archivo", "archivo procesado", "gls", "pdm", "período"]
    KEYWORDS_PROCESAMIENTO = ["procesando estrella", "analizando estrella"]
    
    # Patrones regex precompilados para mejor rendimiento
    REGEX_PATTERNS = {
        'total_estrellas': re.compile(r'Total de estrellas a procesar:\s*(\d+)'),
        'procesando_estrella': re.compile(r'Procesando estrella (\d+)/(\d+)'),
        'numero_estrella': re.compile(r'estrella[:\s]+(\d+)', re.IGNORECASE),
        'archivo_estrella': re.compile(r'\b(\d+\.(txt|dat))\b'),
        'archivo_numero': re.compile(r'\b\d+\.(txt|dat)\b')
    }

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
            # Calcular porcentaje usando constantes
            porcentaje_estrellas = (actual / total) * AppConstants.PROGRESO_ESTRELLAS
            porcentaje_total = AppConstants.PROGRESO_BASE + porcentaje_estrellas
            
            self.progress_bar.setValue(int(porcentaje_total))
            
            # Determinar el texto del estado basado en si es completado o en progreso
            if actual == 0:
                self.label_estado.setText(f"Procesando estrella 0/{total}")
            elif actual == total:
                self.label_estado.setText(f"Completadas {actual}/{total} estrellas")
            else:
                self.label_estado.setText(f"Procesando estrella {actual + 1}/{total}")
            
            # Mantener el label de progreso de estrellas vacío
            self.label_progreso_estrellas.setText("")
        QApplication.processEvents()
        
    def actualizar_fase_analisis(self, fase, porcentaje_base=0):
        """Actualiza la fase del análisis con un porcentaje base"""
        self.label_estado.setText(fase)
        if porcentaje_base > 0:
            self.progress_bar.setValue(porcentaje_base)
            # Limpiar el label de progreso de estrellas solo en fases iniciales
            if porcentaje_base < AppConstants.PROGRESO_BASE:
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
        self.data_folder_final = None  # Para guardar la ruta final de los datos
        self.ruta_csv_generado = None  # Para guardar la ruta del CSV filtrado generado
        
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
                
                # Usar QTimer en lugar de time.sleep para no bloquear la UI
                QTimer.singleShot(1000, self._verificar_terminacion)
            except Exception as e:
                self.log_agregado.emit(f"Error al terminar proceso: {e}")
                self._forzar_terminacion()
    
    def _verificar_terminacion(self):
        """Verifica si el proceso terminó suavemente, sino lo fuerza"""
        if self.proceso_actual and self.proceso_actual.poll() is None:
            self._forzar_terminacion()
        else:
            self.log_agregado.emit("Proceso terminado correctamente")
    
    def _forzar_terminacion(self):
        """Fuerza la terminación del proceso"""
        try:
            if self.proceso_actual:
                self.proceso_actual.kill()
                self.log_agregado.emit("Proceso terminado forzosamente")
        except:
            pass
        
    def run(self):
        """Ejecuta el análisis en un hilo separado"""
        try:
            # Verificar cancelación antes de cada paso
            if self.ventana_progreso.cancelado:
                self.analisis_terminado.emit(False, "Análisis cancelado por el usuario")
                return
                
            self.fase_analisis.emit("Ejecutando copiar.py...", 15)
            self.log_agregado.emit("Ejecutando copiar.py...")
            
            # Primero generar CSV temporal para copiar.py
            ruta_csv_temporal = self.generar_csv_temporal()
            
            if not ruta_csv_temporal or self.ventana_progreso.cancelado:
                if self.ventana_progreso.cancelado:
                    self.analisis_terminado.emit(False, "Análisis cancelado por el usuario")
                else:
                    self.analisis_terminado.emit(False, "Error al generar el archivo CSV temporal")
                return
            
            # Ejecutar copiar.py automáticamente
            exito_copia, nombre_subcarpeta = self.ejecutar_copiar_py(ruta_csv_temporal)
            
            if not exito_copia or self.ventana_progreso.cancelado:
                if self.ventana_progreso.cancelado:
                    self.analisis_terminado.emit(False, "Análisis cancelado por el usuario")
                else:
                    self.analisis_terminado.emit(False, "Error al copiar archivos")
                return
                
            self.fase_analisis.emit("Preparando carpeta de análisis...", 20)
            self.log_agregado.emit(f"Subcarpeta creada: data/{nombre_subcarpeta}")
            
            # Construir ruta completa de la carpeta de datos
            data_folder = os.path.join(AppConstants.RUTA_BASE_PROYECTO, 'data', nombre_subcarpeta)
            
            # Guardar la ruta para usar después del análisis
            self.data_folder_final = data_folder
            
            self.fase_analisis.emit("Generando archivo CSV final...", 22)
            self.log_agregado.emit("Generando archivo CSV final en carpeta de análisis...")
            
            # Ahora generar el CSV final en la carpeta de análisis
            ruta_csv = self.generar_csv_automatico()
            self.ruta_csv_generado = ruta_csv  # Guardar la ruta para DatosF
            
            if not ruta_csv or self.ventana_progreso.cancelado:
                if self.ventana_progreso.cancelado:
                    self.analisis_terminado.emit(False, "Análisis cancelado por el usuario")
                else:
                    self.analisis_terminado.emit(False, "Error al generar el archivo CSV final")
                return
                
            self.fase_analisis.emit("Procesando estrellas...", 25)
            
            # Ejecutar procesofull.py automáticamente
            exito_proceso = self.ejecutar_procesofull_py(data_folder)
            
            if self.ventana_progreso.cancelado:
                self.analisis_terminado.emit(False, "Análisis cancelado por el usuario")
                return
            
            if exito_proceso:
                # Limpiar archivo CSV temporal
                try:
                    if os.path.exists(ruta_csv_temporal):
                        os.remove(ruta_csv_temporal)
                        self.log_agregado.emit("Archivo CSV temporal eliminado")
                except Exception as e:
                    self.log_agregado.emit(f"Nota: No se pudo eliminar archivo temporal: {e}")
                
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
    
    def _generar_csv_base(self, ruta_destino):
        """Función base para generar CSV con los datos filtrados"""
        try:
            # Crear DataFrame con los datos filtrados
            df = pd.DataFrame(self.datos_filtrados)
            
            # Seleccionar solo las columnas necesarias (sin Numero)
            df = df[AppConstants.COLUMNAS_CSV]
            
            # Guardar CSV sin cabeceras (header=False) y sin índice
            df.to_csv(ruta_destino, index=False, header=False)
            
            return ruta_destino
            
        except Exception as e:
            self.log_agregado.emit(f"Error al generar CSV: {str(e)}")
            return None

    def generar_csv_temporal(self):
        """Genera un archivo CSV temporal en la raíz del proyecto para copiar.py"""
        try:
            # Generar nombre del archivo con timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            nombre_archivo = f"datos_filtrados_{timestamp}{AppConstants.EXTENSIONES_ARCHIVOS['csv']}"
            
            # Guardar en la raíz del proyecto (para copiar.py)
            directorio_actual = os.path.dirname(os.path.abspath(__file__))
            ruta_archivo = os.path.join(directorio_actual, nombre_archivo)
            
            return self._generar_csv_base(ruta_archivo)
            
        except Exception as e:
            self.log_agregado.emit(f"Error al generar CSV temporal: {str(e)}")
            return None

    def generar_csv_automatico(self):
        """Genera automáticamente un archivo CSV con los datos filtrados"""
        try:
            # Verificar que data_folder_final esté disponible
            if not self.data_folder_final:
                self.log_agregado.emit("Error: Carpeta de análisis no disponible")
                return None
            
            # Generar nombre del archivo con timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            nombre_archivo = f"datos_filtrados_{timestamp}{AppConstants.EXTENSIONES_ARCHIVOS['csv']}"
            
            # Guardar el CSV en la carpeta de análisis
            ruta_archivo = os.path.join(self.data_folder_final, nombre_archivo)
            
            return self._generar_csv_base(ruta_archivo)
            
        except Exception as e:
            self.log_agregado.emit(f"Error al generar CSV automático: {str(e)}")
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
                    
                    # Detectar total de estrellas al inicio usando regex precompilada
                    if "Total de estrellas a procesar:" in linea:
                        try:
                            match = AppConstants.REGEX_PATTERNS['total_estrellas'].search(linea)
                            if match:
                                total_estrellas = int(match.group(1))
                                if not analisis_iniciado:
                                    self.progreso_estrellas.emit(0, total_estrellas)
                                    analisis_iniciado = True
                        except:
                            pass
                    
                    # Detectar progreso con formato "Procesando estrella X/Y"
                    elif AppConstants.REGEX_PATTERNS['procesando_estrella'].search(linea):
                        try:
                            match = AppConstants.REGEX_PATTERNS['procesando_estrella'].search(linea)
                            actual = int(match.group(1))
                            total = int(match.group(2))
                            total_estrellas = total
                            
                            # actual-1 porque representa estrellas completadas, no la que se está procesando
                            self.progreso_estrellas.emit(actual - 1, total)
                            analisis_iniciado = True
                        except:
                            pass
                    
                    # Detectar estrella individual siendo procesada
                    elif AppConstants.REGEX_PATTERNS['numero_estrella'].search(linea):
                        try:
                            match = AppConstants.REGEX_PATTERNS['numero_estrella'].search(linea)
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
                    elif any(keyword in linea.lower() for keyword in AppConstants.KEYWORDS_ARCHIVO) and total_estrellas > 0:
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
        callback_ejecutado = [False]  # Flag para saber si el callback terminó
        
        def on_analisis_terminado(exito, mensaje):
            print(f"=== ANÁLISIS TERMINADO ===")
            print(f"Éxito: {exito}")
            print(f"Mensaje: {mensaje}")
            print(f"Cancelado: {ventana_progreso.cancelado}")
            
            if ventana_progreso.cancelado:
                print("Análisis cancelado, no abriendo DatosF")
                ventana_progreso.analisis_completado(exito=False, cancelado=True)
            else:
                ventana_progreso.analisis_completado(exito)
                
                # Si el análisis fue exitoso, abrir ventana DatosF
                if exito and hasattr(worker, 'data_folder_final'):
                    print(f"Intentando abrir ventana DatosF...")
                    print(f"data_folder_final: {worker.data_folder_final}")
                    print(f"ruta_csv_generado: {getattr(worker, 'ruta_csv_generado', 'No disponible')}")
                    
                    try:
                        # Importar DatosF desde Frontend
                        script_dir = os.path.dirname(os.path.abspath(__file__))
                        frontend_path = os.path.join(script_dir, 'Frontend')
                        if frontend_path not in sys.path:
                            sys.path.append(frontend_path)
                        
                        import importlib.util
                        
                        print("Importando módulo DatosF...")
                        datosf_path = os.path.join(frontend_path, 'DatosF.py')
                        spec = importlib.util.spec_from_file_location("DatosF", datosf_path)
                        datosf_module = importlib.util.module_from_spec(spec)
                        spec.loader.exec_module(datosf_module)
                        
                        # Crear y mostrar ventana DatosF
                        print("Creando instancia de DatosF...")
                        ventana_resultados = datosf_module.DatosF(
                            data_folder=worker.data_folder_final,
                            datos_formulario=datos_formulario,
                            ventana_anterior=None,
                            ruta_csv_filtrado=worker.ruta_csv_generado if hasattr(worker, 'ruta_csv_generado') else None
                        )
                        
                        print("Mostrando ventana DatosF...")
                        # Configurar ventana con máxima prioridad y siempre encima
                        ventana_resultados.setWindowModality(Qt.NonModal)
                        ventana_resultados.setWindowFlags(ventana_resultados.windowFlags() | Qt.WindowStaysOnTopHint)
                        ventana_resultados.show()
                        ventana_resultados.raise_()
                        ventana_resultados.activateWindow()
                        
                        # Procesar eventos para asegurar que la ventana se muestre
                        app = QApplication.instance()
                        if app:
                            app.processEvents()
                        
                        # Forzar el foco múltiples veces con procesamiento de eventos
                        ventana_resultados.setWindowState(ventana_resultados.windowState() & ~Qt.WindowMinimized | Qt.WindowActive)
                        ventana_resultados.raise_()
                        ventana_resultados.activateWindow()
                        
                        if app:
                            app.processEvents()
                        
                        # Quitar la bandera "always on top" después de mostrarse para comportamiento normal
                        from PyQt5.QtCore import QTimer
                        def quitar_always_on_top():
                            ventana_resultados.setWindowFlags(ventana_resultados.windowFlags() & ~Qt.WindowStaysOnTopHint)
                            ventana_resultados.show()
                        
                        QTimer.singleShot(1000, quitar_always_on_top)  # Quitar después de 1 segundo
                        
                        print(f"✓ Ventana DatosF abierta exitosamente con datos de: {worker.data_folder_final}")
                        print(f"✓ CSV filtrado en: {worker.ruta_csv_generado if hasattr(worker, 'ruta_csv_generado') else 'No especificado'}")
                        
                        # Guardar referencia para evitar que se cierre automáticamente
                        if not hasattr(app, '_ventana_resultados'):
                            app._ventana_resultados = []
                        app._ventana_resultados.append(ventana_resultados)
                        
                        # Actualizar resultado final con mensaje de éxito de DatosF
                        resultado_final[0] = True
                        resultado_final[1] = f"✓ Ventana DatosF abierta exitosamente con datos de: {worker.data_folder_final}"
                        
                        # Cerrar automáticamente la ventana de progreso después de un breve retraso
                        from PyQt5.QtCore import QTimer
                        def cerrar_ventana_progreso():
                            print("Cerrando ventana de progreso automáticamente...")
                            ventana_progreso.close()
                        
                        QTimer.singleShot(1500, cerrar_ventana_progreso)  # 1.5 segundos de retraso
                        
                    except Exception as e:
                        print(f"ERROR al abrir ventana DatosF: {e}")
                        import traceback
                        traceback.print_exc()
                else:
                    print("No se pudo abrir DatosF:")
                    print(f"  - Éxito: {exito}")
                    print(f"  - Tiene data_folder_final: {hasattr(worker, 'data_folder_final')}")
                    if hasattr(worker, 'data_folder_final'):
                        print(f"  - Valor data_folder_final: {worker.data_folder_final}")
                        
            resultado_final[0] = exito
            resultado_final[1] = mensaje
            callback_ejecutado[0] = True  # Marcar que el callback terminó
        
        worker.analisis_terminado.connect(on_analisis_terminado)
        
        # Iniciar el worker
        worker.start()
        
        # Mostrar ventana de progreso y permitir que el análisis continúe
        ventana_progreso.show()
        
        # Procesar eventos mientras el worker ejecuta
        while worker.isRunning():
            app.processEvents()
            if ventana_progreso.cancelado:
                break
        
        # Asegurar que el worker termine limpiamente
        if worker.isRunning():
            worker.quit()
            worker.wait(5000)  # Esperar máximo 5 segundos
        
        # Esperar a que el callback se ejecute completamente
        timeout_counter = 0
        while not callback_ejecutado[0] and timeout_counter < 50:  # Máximo 5 segundos
            app.processEvents()
            timeout_counter += 1
            import time
            time.sleep(0.1)
        
        print(f"=== RETORNANDO RESULTADO ===")
        print(f"Callback ejecutado: {callback_ejecutado[0]}")
        print(f"resultado_final[0]: {resultado_final[0]}")
        print(f"resultado_final[1]: {resultado_final[1]}")
        
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
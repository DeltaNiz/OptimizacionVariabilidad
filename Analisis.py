from PyQt5.QtWidgets import QApplication, QMessageBox, QDialog, QVBoxLayout, QLabel, QProgressBar, QPushButton, QTextEdit
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QTimer
import pandas as pd
import sys
import argparse
import os
import subprocess
from datetime import datetime
import re

class AppConstants:
    """Clase centralizada para todas las constantes del proyecto"""
    
    # Configuración portable - rutas dinámicas según el usuario
    @staticmethod
    def get_base_project_path():
        """Obtiene la ruta base del proyecto de forma portable"""
        try:
            # Usar la carpeta Documents del usuario actual
            import os
            from pathlib import Path
            
            # Obtener carpeta Documents del usuario (acceso rápido de Windows)
            documents_path = Path.home() / "Documents"
            
            # Crear carpeta específica de la aplicación
            app_folder = documents_path / "OptimizacionVariabilidad"
            
            # Crear carpetas necesarias si no existen
            app_folder.mkdir(exist_ok=True)
            (app_folder / "data").mkdir(exist_ok=True)
            
            return str(app_folder)
            
        except Exception as e:
            # Fallback: usar directorio actual de la aplicación
            import os
            current_dir = os.path.dirname(os.path.abspath(__file__))
            return current_dir
    
    # Ruta base del proyecto (se calculará dinámicamente)
    RUTA_BASE_PROYECTO = get_base_project_path.__func__()
    
    # Modo debug (para desarrollo y diagnóstico)
    DEBUG_MODE = False
    
    @staticmethod
    def get_data_path():
        """Obtiene la ruta para guardar análisis de datos de forma portable"""
        from pathlib import Path
        return str(Path(AppConstants.RUTA_BASE_PROYECTO) / "data")
    
    @staticmethod
    def get_analysis_path(analysis_name=None):
        """Obtiene la ruta para un análisis específico dentro de la carpeta data con estructura completa"""
        from pathlib import Path
        from datetime import datetime
        
        if analysis_name is None:
            # Generar nombre basado en fecha y hora
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            analysis_name = f"Analisis_{timestamp}"
        
        # Los análisis se guardan dentro de la carpeta data
        analysis_folder = Path(AppConstants.get_data_path()) / analysis_name
        analysis_folder.mkdir(exist_ok=True)
        
        # Crear subcarpetas necesarias para el análisis
        AppConstants._create_analysis_subfolders(analysis_folder)
        
        return str(analysis_folder)
    
    @staticmethod
    def _create_analysis_subfolders(analysis_folder):
        """Crea la estructura real de análisis según el formato esperado"""
        from pathlib import Path
        
        analysis_path = Path(analysis_folder)
        
        # Solo crear la carpeta principal del análisis
        # Los archivos CSV se guardan directamente en la raíz del análisis
        # Las carpetas de estrellas las crea copiar.py
        
        """print(f"[FOLDER] Carpeta de analisis creada: {analysis_path}")
        print("   |-- Best_Peak_GLS_Min_PDM.csv (se creara por procesofull.py)")
        print("   |-- datos_filtrados_YYYYMMDD_HHMMSS.csv (se creara automaticamente)")
        print("   |-- star1/ (se crean por copiar.py)")
        print("   |-- star2/ (segun estrellas del CSV)")
        print("   +-- starN/ (una por cada estrella del CSV)")
        print("")"""
    
    @staticmethod
    def get_best_peak_file_path(analysis_path):
        """Obtiene la ruta del archivo Best_Peak_GLS_Min_PDM.csv"""
        from pathlib import Path
        return str(Path(analysis_path) / "Best_Peak_GLS_Min_PDM.csv")
     
    @staticmethod
    def create_analysis_timestamp():
        """Crea un timestamp para nombres de análisis y archivos"""
        from datetime import datetime
        return datetime.now().strftime("%Y%m%d_%H%M%S")
    
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
    KEYWORDS_PROCESAMIENTO = ["procesando estrella", "analizando estrella", "completada exitosamente"]
    
    # Patrones regex precompilados para mejor rendimiento
    REGEX_PATTERNS = {
        'total_estrellas': re.compile(r'Total de estrellas a procesar:\s*(\d+)'),
        'procesando_estrella': re.compile(r'Procesando estrella (\d+)/(\d+)'),
        'progreso_detallado': re.compile(r'Progreso:\s*(\d+)/(\d+)\s*\(([\d.]+)%\)\s*-\s*Exitosas:\s*(\d+),\s*Fallidas:\s*(\d+)'),
        'estrella_completada': re.compile(r'\[OK\] (\w+) completada exitosamente en ([\d.]+)s'),
        'estrella_error': re.compile(r'\[ERROR\] Error en estrella (\w+):'),
        'numero_estrella': re.compile(r'estrella[:\s]+(\d+)', re.IGNORECASE),
        'archivo_estrella': re.compile(r'\b(\d+\.(txt|dat))\b'),
        'archivo_numero': re.compile(r'\b\d+\.(txt|dat)\b'),
        'procesamiento_completado': re.compile(r'Procesamiento completado\.'),
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
        
        # Variable para almacenar datos de DatosF para abrir al cerrar
        self.datos_para_datosf = None
        
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
            self.label_estado.setText("[CANCEL] CANCELANDO ANALISIS...")
            self.label_progreso_estrellas.setText("Terminando procesos...")
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
            
            self.agregar_log("Cancelación en progreso, por favor espera...")
        
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
            
            # Asegurar que no exceda 100%
            porcentaje_total = min(100, int(porcentaje_total))
            self.progress_bar.setValue(porcentaje_total)
            
            # Texto más claro del estado
            if actual == 0:
                self.label_estado.setText(f"Iniciando procesamiento de {total} estrellas...")
            elif actual == total:
                self.label_estado.setText(f"[OK] Completadas todas las estrellas ({actual}/{total})")
                # Asegurar 100% cuando se completan todas
                self.progress_bar.setValue(100)
            else:
                self.label_estado.setText(f"Procesando estrellas: {actual}/{total} completadas")
            
            # Mostrar porcentaje en el label de progreso de estrellas
            porcentaje_estrellas_display = (actual / total) * 100
            self.label_progreso_estrellas.setText(f"{porcentaje_estrellas_display:.1f}% ({actual}/{total})")
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
    
    def accept(self):
        """Sobrescribir accept para abrir DatosF al cerrar si está disponible"""
        print("=== CERRANDO VENTANA DE PROGRESO ===")
        
        # Si hay datos para abrir DatosF, abrirlo antes de cerrar
        if self.datos_para_datosf:
            print("Abriendo ventana DatosF...")
            try:
                self._abrir_datosf(self.datos_para_datosf)
                print("Ventana DatosF abierta exitosamente")
            except Exception as e:
                print(f"ERROR al abrir ventana DatosF: {e}")
                import traceback
                traceback.print_exc()
        
        # Llamar al accept original para cerrar la ventana
        super().accept()
    
    def _abrir_datosf(self, datos):
        """Método para abrir la ventana DatosF"""
        import sys
        import os
        import importlib.util
        
        # Importar DatosF desde Frontend
        script_dir = os.path.dirname(os.path.abspath(__file__))
        frontend_path = os.path.join(script_dir, 'Frontend')
        if frontend_path not in sys.path:
            sys.path.append(frontend_path)
        
        print("Importando módulo DatosF...")
        datosf_path = os.path.join(frontend_path, 'DatosF.py')
        spec = importlib.util.spec_from_file_location("DatosF", datosf_path)
        datosf_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(datosf_module)
        
        # Crear y mostrar ventana DatosF
        print("Creando y mostrando ventana DatosF...")
        ventana_resultados = datosf_module.DatosF(
            data_folder=datos['data_folder'],
            datos_formulario=datos['datos_formulario'],
            ventana_anterior=None,
            ruta_csv_filtrado=datos.get('ruta_csv', None),
            ventana_subir=datos.get('ventana_subir', None)
        )
        
        ventana_resultados.show()
        ventana_resultados.raise_()
        ventana_resultados.activateWindow()
        
        # Guardar referencia para evitar que se cierre automáticamente
        app = QApplication.instance()
        if app:
            if not hasattr(app, '_ventana_resultados'):
                app._ventana_resultados = []
            app._ventana_resultados.append(ventana_resultados)

class WorkerThread(QThread):
    # Señales para comunicarse con la interfaz
    estado_cambiado = pyqtSignal(str, int)
    detalle_cambiado = pyqtSignal(str)
    progreso_estrellas = pyqtSignal(int, int)  # actual, total
    fase_analisis = pyqtSignal(str, int)  # fase, porcentaje_base
    log_agregado = pyqtSignal(str)
    analisis_terminado = pyqtSignal(bool, str)
    
    def __init__(self, datos_filtrados, datos_formulario, ventana_progreso, periodo_max=3, periodo_min=0.01):
        super().__init__()
        self.datos_filtrados = datos_filtrados
        self.datos_formulario = datos_formulario
        self.ventana_progreso = ventana_progreso
        self.periodo_max = periodo_max
        self.periodo_min = periodo_min
        self.proceso_actual = None
        self.cancelacion_forzada = False
        self.data_folder_final = None  # Para guardar la ruta final de los datos
        self.ruta_csv_generado = None  # Para guardar la ruta del CSV filtrado generado
        self.ruta_csv_temporal = None  # Para rastrear el CSV temporal y poder eliminarlo
        self.carpeta_analisis_creada = None  # Para rastrear la carpeta de análisis y poder eliminarla
        
    def forzar_cancelacion(self):
        """Fuerza la cancelación inmediata"""
        self.cancelacion_forzada = True
        self.log_agregado.emit("=== CANCELACIÓN FORZADA ===")
        
        # Limpiar archivos temporales inmediatamente
        self._limpiar_archivos_temporales()
        
        # Terminar cualquier proceso en ejecución
        if hasattr(self, 'proceso_actual') and self.proceso_actual and self.proceso_actual.poll() is None:
            try:
                self.proceso_actual.kill()  # Terminación inmediata
                self.log_agregado.emit("Proceso externo terminado inmediatamente")
            except Exception as e:
                self.log_agregado.emit(f"Error al terminar proceso: {e}")
        
        # Emitir señal de terminación inmediatamente
        self.log_agregado.emit("Terminando análisis...")
        self.analisis_terminado.emit(False, "Análisis cancelado por el usuario")
        
        # Terminar el hilo
        self.quit()
    
    def _forzar_terminacion(self):
        """
        Fuerza la terminación inmediata del proceso actual
        Utilizado durante cancelaciones para asegurar terminación rápida
        """
        try:
            if hasattr(self, 'proceso_actual') and self.proceso_actual:
                self.proceso_actual.kill()
                self.log_agregado.emit("Proceso terminado forzosamente")
        except Exception as e:
            self.log_agregado.emit(f"Error al terminar proceso: {e}")
    
    def _limpiar_archivos_temporales(self, incluir_carpeta_analisis=True):
        """
        Limpia archivos temporales creados durante el análisis
        
        Args:
            incluir_carpeta_analisis (bool): 
                - True: Limpia CSV temporal Y carpeta de análisis (para cancelaciones/errores)
                - False: Solo limpia CSV temporal (para análisis exitosos, conserva carpeta)
        """
        archivos_eliminados = 0
        
        # Limpiar CSV temporal (siempre)
        if self.ruta_csv_temporal and os.path.exists(self.ruta_csv_temporal):
            try:
                os.remove(self.ruta_csv_temporal)
                archivos_eliminados += 1
            except Exception as e:
                self.log_agregado.emit(f"No se pudo eliminar archivo temporal: {e}")
        
        # Limpiar carpeta de análisis solo si se solicita
        if incluir_carpeta_analisis and self.carpeta_analisis_creada and os.path.exists(self.carpeta_analisis_creada):
            try:
                import shutil
                shutil.rmtree(self.carpeta_analisis_creada)
                nombre_carpeta = os.path.basename(self.carpeta_analisis_creada)
                self.log_agregado.emit(f"Carpeta de análisis eliminada: {nombre_carpeta}")
                archivos_eliminados += 1
            except Exception as e:
                self.log_agregado.emit(f"No se pudo eliminar carpeta de análisis: {e}")
        
    def run(self):
        """Ejecuta el análisis en un hilo separado"""
        try:
            # Verificar cancelación antes de cada paso
            if self.ventana_progreso.cancelado or self.cancelacion_forzada:
                self.analisis_terminado.emit(False, "Análisis cancelado por el usuario")
                return
                
            self.fase_analisis.emit("Ejecutando copiar.py...", 15)
            self.log_agregado.emit("Ejecutando copiar.py...")
            
            # Primero generar CSV temporal para copiar.py
            ruta_csv_temporal = self.generar_csv_temporal()
            
            if not ruta_csv_temporal or self.ventana_progreso.cancelado:
                if self.ventana_progreso.cancelado:
                    self._limpiar_archivos_temporales()
                    self.analisis_terminado.emit(False, "Análisis cancelado por el usuario")
                else:
                    self.analisis_terminado.emit(False, "Error al generar el archivo CSV temporal")
                return
            
            # Ejecutar copiar.py automáticamente
            exito_copia, nombre_subcarpeta = self.ejecutar_copiar_py(ruta_csv_temporal)
            
            if not exito_copia or self.ventana_progreso.cancelado:
                if self.ventana_progreso.cancelado:
                    self._limpiar_archivos_temporales()
                    self.analisis_terminado.emit(False, "Análisis cancelado por el usuario")
                else:
                    self.analisis_terminado.emit(False, "Error al copiar archivos")
                return
                
            self.fase_analisis.emit("Preparando carpeta de análisis...", 20)
            
            # Construir ruta completa usando método portable
            data_folder = AppConstants.get_analysis_path(nombre_subcarpeta)
            
            # Guardar la ruta para usar después del análisis y para limpieza en caso de cancelación
            self.data_folder_final = data_folder
            self.carpeta_analisis_creada = data_folder  # Rastrear para limpieza si se cancela
            
            self.fase_analisis.emit("Generando archivo CSV final...", 22)
            self.log_agregado.emit("Generando archivo CSV final en carpeta de análisis...")
            
            # Ahora generar el CSV final en la carpeta de análisis
            ruta_csv = self.generar_csv_automatico()
            self.ruta_csv_generado = ruta_csv  # Guardar la ruta para DatosF
            
            if not ruta_csv or self.ventana_progreso.cancelado:
                if self.ventana_progreso.cancelado:
                    self._limpiar_archivos_temporales()
                    self.analisis_terminado.emit(False, "Análisis cancelado por el usuario")
                else:
                    self.analisis_terminado.emit(False, "Error al generar el archivo CSV final")
                return
                
            self.fase_analisis.emit("Procesando estrellas...", 25)
            
            # Ejecutar procesofull.py automáticamente
            exito_proceso = self.ejecutar_procesofull_py(data_folder)
            
            if self.ventana_progreso.cancelado:
                self._limpiar_archivos_temporales()  # Limpieza completa (CSV + carpeta) por cancelación
                self.analisis_terminado.emit(False, "Análisis cancelado por el usuario")
                return
            
            if exito_proceso:
                # Limpiar solo el archivo CSV temporal (conservar carpeta de análisis)
                self._limpiar_archivos_temporales(incluir_carpeta_analisis=False)
                
                # Mostrar progreso completo al final
                self.fase_analisis.emit("¡Análisis completado exitosamente!", 100)
                mensaje_exito = f"Análisis completado exitosamente\n\nCSV generado: {os.path.basename(ruta_csv)}\nEstrellas procesadas: {len(self.datos_filtrados)}\nSubcarpeta: data/{nombre_subcarpeta}"
                self.analisis_terminado.emit(True, mensaje_exito)
            else:
                # Limpiar archivo CSV temporal en caso de fallo (conservar carpeta para depuración)
                self._limpiar_archivos_temporales(incluir_carpeta_analisis=False)
                mensaje_error = f"CSV generado correctamente, pero hubo errores en el procesamiento\n\nCSV: {os.path.basename(ruta_csv)}\nSubcarpeta: data/{nombre_subcarpeta}"
                self.analisis_terminado.emit(False, mensaje_error)
                
        except Exception as e:
            self._limpiar_archivos_temporales()  # Limpieza completa (CSV + carpeta) por error inesperado
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
            
            # Guardar la ruta del CSV temporal para poder eliminarlo en caso de cancelación
            self.ruta_csv_temporal = ruta_archivo
            
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
            timestamp = AppConstants.create_analysis_timestamp()
            nombre_subcarpeta = f"analisis_{timestamp}"
            
            # Ejecutar copiar.py con parámetros portables
            cmd = [
                sys.executable, ruta_copiar,
                '--csv', ruta_csv,
                '--subcarpeta', nombre_subcarpeta
            ]
            
            # Obtener rutas de carpetas desde datos_formulario (seleccionadas por el usuario)
            lc_i_path = None
            lc_v_path = None
            
            if self.datos_formulario and 'carpeta_filtro_I' in self.datos_formulario:
                lc_i_path = self.datos_formulario['carpeta_filtro_I']
                
            if self.datos_formulario and 'carpeta_filtro_V' in self.datos_formulario:
                lc_v_path = self.datos_formulario['carpeta_filtro_V']
                
            # Agregar rutas de carpetas si están disponibles
            if lc_i_path and lc_v_path:
                cmd.extend(['--lc_i', lc_i_path, '--lc_v', lc_v_path])
            else:
                self.log_agregado.emit("[WARNING] No se encontraron rutas de carpetas I/V en datos del formulario")
                self.log_agregado.emit("[INFO] copiar.py buscará carpetas automáticamente")
            
            # Llamar directamente a copiar.py en lugar de usar subprocess
            try:
                import copiar
                from io import StringIO
                from contextlib import redirect_stdout, redirect_stderr
                
                # Simular sys.argv para copiar.py (solo los argumentos, no sys.executable ni ruta del script)
                original_argv = sys.argv.copy()
                # cmd = [sys.executable, ruta_copiar, '--csv', ruta_csv, '--subcarpeta', nombre_subcarpeta, ...]
                # Necesitamos: ['copiar.py', '--csv', ruta_csv, '--subcarpeta', nombre_subcarpeta, ...]
                sys.argv = ['copiar.py'] + cmd[2:]  # Saltar sys.executable y ruta_copiar
                
                # Capturar output
                stdout_capture = StringIO()
                stderr_capture = StringIO()
                
                with redirect_stdout(stdout_capture), redirect_stderr(stderr_capture):
                    try:
                        copiar.main()
                        resultado_exitoso = True
                    except SystemExit as e:
                        resultado_exitoso = (e.code == 0)
                    except Exception as e:
                        resultado_exitoso = False
                        stderr_capture.write(f"Error: {e}")
                
                # Restaurar sys.argv
                sys.argv = original_argv
                
                # Obtener output capturado
                output = stdout_capture.getvalue()
                error_output = stderr_capture.getvalue()
                
                if self.ventana_progreso.cancelado:
                    return False, ""
                
                if resultado_exitoso:
                    self.log_agregado.emit("Archivos copiados correctamente")
                    if output:
                        # Mostrar salida línea por línea para mejor legibilidad
                        for line in output.strip().split('\n'):
                            if line.strip():
                                self.log_agregado.emit(line.strip())
                    return True, nombre_subcarpeta
                else:
                    self.log_agregado.emit("ERROR al ejecutar copiar.py")
                    if error_output:
                        self.log_agregado.emit(f"Error: {error_output}")
                    if output:
                        self.log_agregado.emit(f"Output: {output}")
                    return False, ""
                    
            except ImportError:
                self.log_agregado.emit("ERROR: No se pudo importar copiar.py")
                return False, ""
                
        except Exception as e:
            self.log_agregado.emit(f"ERROR al ejecutar copiar.py: {e}")
            return False, ""
    
    def ejecutar_procesofull_py(self, data_folder):
        """Ejecuta procesofull.py automáticamente con la carpeta de datos generada y parámetros de período"""
        try:
            if self.ventana_progreso.cancelado:
                return False
                
            script_dir = os.path.dirname(os.path.abspath(__file__))
            ruta_procesofull = os.path.join(script_dir, 'procesofull.py')
            
            if not os.path.exists(ruta_procesofull):
                self.log_agregado.emit(f"ADVERTENCIA: No se encontró procesofull.py")
                return False

            self.log_agregado.emit(f"<b>Iniciando análisis con período: máx={self.periodo_max}, mín={self.periodo_min}</b>")

            # Ejecutar procesofull.py con parámetros portables
            # Extraer nombre del análisis desde data_folder para modo portable
            from pathlib import Path
            data_path = Path(data_folder)
            analysis_name = data_path.name  # ej: analisis_20250915_141459
            
            # Llamar directamente a procesofull.py en lugar de usar subprocess
            try:
                import procesofull
                from io import StringIO
                from contextlib import redirect_stdout, redirect_stderr
                
                # Simular sys.argv para procesofull.py
                original_argv = sys.argv.copy()
                sys.argv = [
                    'procesofull.py',
                    '--analisis', analysis_name,  # Usar modo portable
                    '--pend', str(self.periodo_max),
                    '--pbeg', str(self.periodo_min)
                ]
                
                # Capturar output
                stdout_capture = StringIO()
                stderr_capture = StringIO()
                
                with redirect_stdout(stdout_capture), redirect_stderr(stderr_capture):
                    try:
                        procesofull.main()
                        resultado_exitoso = True
                    except SystemExit as e:
                        resultado_exitoso = (e.code == 0)
                    except Exception as e:
                        resultado_exitoso = False
                        stderr_capture.write(f"Error: {e}")
                
                # Restaurar sys.argv
                sys.argv = original_argv
                
                # Obtener output capturado
                output = stdout_capture.getvalue()
                error_output = stderr_capture.getvalue()
            
                # Procesar output línea por línea
                total_estrellas = 0
                estrellas_procesadas = 0
                analisis_iniciado = False
                
                for line in output.strip().split('\n'):
                    linea = line.strip()
                    if linea:
                        self.log_agregado.emit(linea)
                        
                        # Verificar cancelación periódicamente
                        if self.ventana_progreso.cancelado or self.cancelacion_forzada:
                            self.log_agregado.emit("Cancelación detectada...")
                            return False
                    
                    # Detectar total de estrellas al inicio
                    if "Total de estrellas a procesar:" in linea:
                        try:
                            match = AppConstants.REGEX_PATTERNS['total_estrellas'].search(linea)
                            if match:
                                total_estrellas = int(match.group(1))
                                if not analisis_iniciado:
                                    self.progreso_estrellas.emit(0, total_estrellas)
                                    analisis_iniciado = True
                        except Exception as e:
                            self.log_agregado.emit(f"[ERROR] Error parseando total de estrellas: {e}")
                    
                    # PRIORIDAD 1: Detectar progreso detallado con estadísticas (más confiable para paralelo)
                    elif "Progreso:" in linea and "Exitosas:" in linea:
                        try:
                            match = AppConstants.REGEX_PATTERNS['progreso_detallado'].search(linea)
                            if match:
                                actual = int(match.group(1))
                                total = int(match.group(2))
                                
                                if total_estrellas == 0:
                                    total_estrellas = total
                                    analisis_iniciado = True
                                
                                # Actualizar progreso con el número REAL de estrellas completadas
                                self.progreso_estrellas.emit(actual, total)
                                
                        except Exception as e:
                            self.log_agregado.emit(f"[ERROR] Error parseando progreso detallado: {e}")
                    
                    # PRIORIDAD 2: Detectar estrella completada (incrementar contador local)
                    elif "[OK] Estrella" in linea and "completada exitosamente" in linea:
                        try:
                            match = AppConstants.REGEX_PATTERNS['estrella_completada'].search(linea)
                            if match:
                                estrella_nombre = match.group(1)
                                tiempo = match.group(2)
                                self.detalle_cambiado.emit(f"[OK] {estrella_nombre} completada en {tiempo}s")
                                
                                # Incrementar contador local de estrellas procesadas
                                estrellas_procesadas += 1
                                if total_estrellas > 0:
                                    self.progreso_estrellas.emit(estrellas_procesadas, total_estrellas)
                            else:
                                # Fallback sin regex - solo incrementar contador
                                estrellas_procesadas += 1
                                if total_estrellas > 0:
                                    self.progreso_estrellas.emit(estrellas_procesadas, total_estrellas)
                                self.detalle_cambiado.emit("[OK] Estrella completada exitosamente")
                                
                        except Exception as e:
                            self.log_agregado.emit(f"[ERROR] Error parseando estrella completada: {e}")
                    
                    # PRIORIDAD 3: Detectar progreso con formato "Procesando estrella X/Y" (solo para inicialización)
                    elif "Procesando estrella" in linea and not analisis_iniciado:
                        try:
                            match = AppConstants.REGEX_PATTERNS['procesando_estrella'].search(linea)
                            if match:
                                actual = int(match.group(1))
                                total = int(match.group(2))
                                
                                if total_estrellas == 0:
                                    total_estrellas = total
                                    analisis_iniciado = True
                                    # Solo inicializar, no actualizar progreso aquí
                                    self.progreso_estrellas.emit(0, total)
                                    self.detalle_cambiado.emit(f"Iniciando procesamiento de {total} estrellas...")
                                
                        except Exception as e:
                            self.log_agregado.emit(f"[ERROR] Error parseando progreso de estrella: {e}")
                    
                    # Detectar errores en estrellas (incrementar contador también)
                    elif "[ERROR] Error en estrella" in linea:
                        try:
                            match = AppConstants.REGEX_PATTERNS['estrella_error'].search(linea)
                            if match:
                                estrella_nombre = match.group(1)
                                self.detalle_cambiado.emit(f"[ERROR] Error en {estrella_nombre}")
                            else:
                                # Fallback sin regex
                                self.detalle_cambiado.emit("[ERROR] Error en procesamiento de estrella")
                            
                            # Incrementar contador local (estrella fallida también cuenta como procesada)
                            estrellas_procesadas += 1
                            if total_estrellas > 0:
                                self.progreso_estrellas.emit(estrellas_procesadas, total_estrellas)
                                
                        except Exception as e:
                            self.log_agregado.emit(f"[ERROR] Error parseando error de estrella: {e}")
                    
                    
                    # Detectar procesamiento completado
                    elif "Procesamiento completado." in linea:
                        if total_estrellas > 0:
                            self.progreso_estrellas.emit(total_estrellas, total_estrellas)
                        self.estado_cambiado.emit("¡Análisis completado exitosamente!", 100)
                        self.detalle_cambiado.emit("Procesamiento completado")
                    
                    # Detectar fases específicas del análisis
                    elif "Ejecutando análisis GLS" in linea:
                        self.detalle_cambiado.emit("Ejecutando análisis GLS...")
                    elif "Ejecutando análisis PDM" in linea:
                        self.detalle_cambiado.emit("Ejecutando análisis PDM...")
                    elif "Generando visualizaciones" in linea:
                        self.detalle_cambiado.emit("Generando gráficos...")
                    elif "Guardando resultados" in linea:
                        self.detalle_cambiado.emit("Guardando resultados...")
                    elif "Reporte detallado guardado" in linea:
                        self.detalle_cambiado.emit("Guardando reporte detallado...")
                    
                    # Detectar inicio de procesamiento si no se detectó el total antes
                    elif "procesamiento" in linea.lower() and total_estrellas == 0:
                        self.detalle_cambiado.emit("Iniciando procesamiento...")
                        if not analisis_iniciado:
                            # Asumir al menos 1 estrella para mostrar progreso
                            total_estrellas = 1
                            self.progreso_estrellas.emit(0, 1)
                            analisis_iniciado = True
                    
                    # Fallback: si vemos cualquier mención de estrellas pero no hemos iniciado análisis
                    elif not analisis_iniciado and ("estrella" in linea.lower() or "star" in linea.lower()):
                        if AppConstants.DEBUG_MODE:
                            self.log_agregado.emit(f"[DEBUG] Fallback - detectando mención de estrella: '{linea}'")
                        if total_estrellas == 0:
                            total_estrellas = 1  # Asumir al menos una estrella
                            self.progreso_estrellas.emit(0, 1)
                            analisis_iniciado = True
                            self.detalle_cambiado.emit("Iniciando análisis de estrellas...")
            
                if self.ventana_progreso.cancelado:
                    return False
                
                if resultado_exitoso:
                    self.log_agregado.emit("<b>Procesamiento completado</b>")
                    return True
                else:
                    self.log_agregado.emit(f"<b>ERROR al ejecutar procesofull.py</b>")
                    if error_output:
                        self.log_agregado.emit(f"Error: {error_output}")
                    return False
                    
            except ImportError:
                self.log_agregado.emit("ERROR: No se pudo importar procesofull.py")
                return False
                
        except Exception as e:
            self.log_agregado.emit(f"<b>ERROR al ejecutar procesofull.py: {e}</b>")
            return False

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

def realizar_analisis_completo(table_main, table_descartadas, datos_formulario, periodo_max=3, periodo_min=0.01, ventana_subir=None):
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
        worker = WorkerThread(datos_filtrados, datos_formulario, ventana_progreso, periodo_max, periodo_min)
        
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
                print("Análisis cancelado")
                ventana_progreso.analisis_completado(exito=False, cancelado=True)
            else:
                print("Análisis completado. Puedes cerrar la ventana para continuar.")
                ventana_progreso.analisis_completado(exito)
                
            # Guardar información del análisis para abrir DatosF después del cierre
            if exito and hasattr(worker, 'data_folder_final'):
                ventana_progreso.datos_para_datosf = {
                    'data_folder': worker.data_folder_final,
                    'datos_formulario': datos_formulario,
                    'ruta_csv': getattr(worker, 'ruta_csv_generado', None),
                    'ventana_subir': ventana_subir
                }
                print("Información guardada para abrir DatosF al cerrar la ventana.")
            else:
                ventana_progreso.datos_para_datosf = None
                        
            resultado_final[0] = exito
            resultado_final[1] = mensaje
            callback_ejecutado[0] = True  # Marcar que el callback terminó
        
        worker.analisis_terminado.connect(on_analisis_terminado)
        
        # Iniciar el worker
        worker.start()
        
        # Mostrar ventana de progreso para el bucle de procesamiento
        ventana_progreso.show()
        
        # Procesar eventos mientras el worker ejecuta
        while worker.isRunning():
            app.processEvents()
            if ventana_progreso.cancelado:
                print("=== CANCELACIÓN DETECTADA ===")
                worker.forzar_cancelacion()  # Forzar cancelación del worker
                break
        
        # Asegurar que el worker termine limpiamente
        if worker.isRunning():
            print("Terminando worker thread...")
            worker.quit()
            worker.wait(5000)  # Esperar máximo 5 segundos
            if worker.isRunning():
                print("Worker no terminó, terminando forzadamente...")
                worker.terminate()
                worker.wait(2000)
        
        # Si fue cancelado, retornar inmediatamente sin mostrar la ventana modal
        if ventana_progreso.cancelado:
            print("=== ANÁLISIS CANCELADO - RETORNANDO INMEDIATAMENTE ===")
            ventana_progreso.hide()  # Ocultar la ventana
            return False, "Análisis cancelado por el usuario"
        
        # Esperar a que el callback se ejecute completamente
        timeout_counter = 0
        while not callback_ejecutado[0] and timeout_counter < 50:  # Máximo 5 segundos
            app.processEvents()
            timeout_counter += 1
            import time
            time.sleep(0.1)
        
        # Usar exec_() para hacer la ventana modal y esperar hasta que se cierre manualmente
        result = ventana_progreso.exec_()  # Esto bloquea hasta que el usuario cierre la ventana
        
        print(f"=== RETORNANDO RESULTADO ===")
        print(f"Ventana cerrada por el usuario con resultado: {result}")
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
        # Si se ejecuta directamente, mostrar información portable
        print("[INFO] Analisis.py ya no tiene interfaz gráfica propia.")
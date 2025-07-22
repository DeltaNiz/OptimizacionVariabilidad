from PyQt5.QtWidgets import QMainWindow, QApplication, QMessageBox
from PyQt5.QtCore import Qt
import pandas as pd
import sys
import argparse
import os
import subprocess
from datetime import datetime

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

def generar_csv_automatico(datos_filtrados, datos_formulario=None):
    """Genera automáticamente un archivo CSV con los datos filtrados"""
    try:
        # Crear DataFrame con los datos filtrados
        df = pd.DataFrame(datos_filtrados)
        
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
        
        # Mostrar información en consola
        print(f"=== CSV GENERADO AUTOMÁTICAMENTE ===")
        print(f"Archivo: {nombre_archivo}")
        print(f"Ruta: {ruta_archivo}")
        print(f"Registros exportados: {len(datos_filtrados)} (solo columnas V, I, MV, MI)")
        print(f"Formato: Sin cabeceras, sin columna de numeración")
        print(f"Fecha/Hora: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        if datos_formulario:
            print(f"Parámetros utilizados:")
            for key, value in datos_formulario.items():
                print(f"  {key}: {value}")
        
        print("=" * 50)
        
        return ruta_archivo
        
    except Exception as e:
        error_msg = f"Error al generar CSV automáticamente: {str(e)}"
        print(error_msg)
        return None

def ejecutar_analisis_con_csv(ruta_csv, datos_formulario):
    """Ejecuta el análisis con el CSV generado"""
    try:
        # Preparar parámetros para pasar al script
        parametros = {
            'ruta_csv': ruta_csv,
            'periodo_max': datos_formulario.get('periodo_max', ''),
            'periodo_min': datos_formulario.get('periodo_min', ''),
            'step': datos_formulario.get('step', ''),
            'carpeta_filtro_I': datos_formulario.get('carpeta_filtro_I', ''),
            'carpeta_filtro_V': datos_formulario.get('carpeta_filtro_V', ''),
            'archivo_csv': datos_formulario.get('archivo_csv', '')
        }
        
        print(f"=== EJECUTANDO ANÁLISIS ===")
        print(f"CSV a procesar: {ruta_csv}")
        
        # Ejecutar análisis directamente
        procesar_csv_analisis(ruta_csv, parametros)
        
    except Exception as e:
        print(f"ERROR al ejecutar análisis: {e}")
        import traceback
        traceback.print_exc()

def ejecutar_copiar_py(ruta_csv):
    """Ejecuta copiar.py automáticamente con el CSV generado"""
    try:
        script_dir = os.path.dirname(os.path.abspath(__file__))
        ruta_copiar = os.path.join(script_dir, 'copiar.py')
        
        if not os.path.exists(ruta_copiar):
            print(f"ADVERTENCIA: No se encontró copiar.py en: {ruta_copiar}")
            return False, ""
        
        # Generar nombre único para la subcarpeta del análisis
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        nombre_subcarpeta = f"analisis_{timestamp}"
        
        print(f"=== EJECUTANDO COPIAR.PY ===")
        print(f"CSV: {os.path.basename(ruta_csv)}")
        print(f"Subcarpeta de destino: data/{nombre_subcarpeta}")
        print("-" * 40)
        
        # Ejecutar copiar.py con parámetros
        resultado = subprocess.run([
            sys.executable, ruta_copiar,
            '--csv', ruta_csv,
            '--subcarpeta', nombre_subcarpeta
        ], capture_output=True, text=True)
        
        if resultado.returncode == 0:
            print("ÉXITO: Archivos copiados correctamente")
            if resultado.stdout:
                print(resultado.stdout)
            return True, nombre_subcarpeta
        else:
            print("ERROR al ejecutar copiar.py")
            if resultado.stderr:
                print(f"Error: {resultado.stderr}")
            return False, ""
            
    except Exception as e:
        print(f"ERROR al ejecutar copiar.py: {e}")
        return False, ""

def realizar_analisis_completo(table_main, table_descartadas, datos_formulario):
    """Método principal para realizar el análisis completo con los datos filtrados"""
    try:
        print("=== INICIANDO ANÁLISIS ===")
        
        # Obtener datos filtrados (sin las filas descartadas)
        datos_filtrados = obtener_datos_filtrados(table_main, table_descartadas)
        
        if not datos_filtrados:
            print("No hay datos para analizar")
            return False, "No hay datos filtrados para generar el CSV."
        
        # Generar CSV automáticamente
        ruta_csv = generar_csv_automatico(datos_filtrados, datos_formulario)
        
        if ruta_csv:
            # Ejecutar análisis con el CSV generado
            ejecutar_analisis_con_csv(ruta_csv, datos_formulario)
            
            # Ejecutar copiar.py automáticamente
            exito_copia, nombre_subcarpeta = ejecutar_copiar_py(ruta_csv)
            
            print("Análisis completado exitosamente")
            
            if exito_copia and nombre_subcarpeta:
                return True, f"El archivo CSV ha sido generado automáticamente:\n\n{os.path.basename(ruta_csv)}\n\nEstrellas exportadas: {len(datos_filtrados)}\nUbicación: {os.path.dirname(ruta_csv)}\n\n✅ Archivos copiados con copiar.py\n📁 Subcarpeta creada: data/{nombre_subcarpeta}"
            else:
                return True, f"El archivo CSV ha sido generado automáticamente:\n\n{os.path.basename(ruta_csv)}\n\nEstrellas exportadas: {len(datos_filtrados)}\nUbicación: {os.path.dirname(ruta_csv)}\n\n⚠️ Error al copiar archivos"
        else:
            return False, "Error al generar el archivo CSV"
            
    except Exception as e:
        error_msg = f"ERROR en realizar_analisis_completo: {e}"
        print(error_msg)
        import traceback
        traceback.print_exc()
        return False, error_msg

def procesar_csv_analisis(ruta_csv, parametros):
    """Procesa el CSV generado y muestra la información en consola"""
    try:
        print("\n" + "=" * 80)
        print("🔬 ANÁLISIS DE DATOS FILTRADOS")
        print("=" * 80)
        
        # Verificar que el archivo existe
        if not os.path.exists(ruta_csv):
            print(f"❌ ERROR: No se encontró el archivo CSV: {ruta_csv}")
            return
        
        # Leer el CSV sin cabeceras y asignar nombres de columnas
        df = pd.read_csv(ruta_csv, header=None)
        df.columns = ['V', 'I', 'MV', 'MI']
        
        # Mostrar información del archivo
        print(f"📁 Archivo CSV procesado: {os.path.basename(ruta_csv)}")
        print(f"📂 Ubicación: {os.path.dirname(ruta_csv)}")
        print(f"📊 Total de filas filtradas: {len(df)}")
        print(f"📋 Formato: Sin cabeceras, columnas V, I, MV, MI")
        print()
        
        # Mostrar parámetros del análisis
        print("🔧 PARÁMETROS DEL ANÁLISIS:")
        print("-" * 40)
        if parametros.get('periodo_max'):
            print(f"⏰ Periodo Máximo: {parametros['periodo_max']} días")
        if parametros.get('periodo_min'):
            print(f"⏰ Periodo Mínimo: {parametros['periodo_min']} días")
        if parametros.get('step'):
            print(f"📏 Step (Saltos): {parametros['step']} días")
        if parametros.get('carpeta_filtro_I'):
            print(f"📁 Filtro I: {parametros['carpeta_filtro_I']}")
        if parametros.get('carpeta_filtro_V'):
            print(f"📁 Filtro V: {parametros['carpeta_filtro_V']}")
        if parametros.get('archivo_csv'):
            print(f"📄 Archivo CSV original: {parametros['archivo_csv']}")
        print()
        
        # Mostrar estadísticas de los datos
        print("📈 ESTADÍSTICAS DE LOS DATOS:")
        print("-" * 40)
        
        if not df.empty:
            # Estadísticas básicas para columnas numéricas
            columnas_numericas = ['V', 'I', 'MV', 'MI']
            for col in columnas_numericas:
                if col in df.columns:
                    try:
                        # Convertir a numérico, manejando errores
                        df[col] = pd.to_numeric(df[col], errors='coerce')
                        valores_validos = df[col].dropna()
                        
                        if len(valores_validos) > 0:
                            print(f"🔢 Columna {col}:")
                            print(f"   📊 Promedio: {valores_validos.mean():.3f}")
                            print(f"   📈 Máximo: {valores_validos.max():.3f}")
                            print(f"   📉 Mínimo: {valores_validos.min():.3f}")
                            print(f"   📋 Desv. Estándar: {valores_validos.std():.3f}")
                            print()
                    except:
                        print(f"⚠️  No se pudieron calcular estadísticas para columna {col}")
            
            # Mostrar primeras filas como muestra
            print("🔍 MUESTRA DE DATOS (Primeras 10 filas):")
            print("-" * 50)
            print(f"{'V':<12} {'I':<12} {'MV':<12} {'MI':<12}")
            print("-" * 50)
            
            for idx, row in df.head(10).iterrows():
                print(f"{row['V']:<12} {row['I']:<12} {row['MV']:<12} {row['MI']:<12}")
            
            if len(df) > 10:
                print(f"... y {len(df) - 10} filas más")
            
            print()
            
            # Información adicional sobre datos faltantes
            print("🔍 ANÁLISIS DE CALIDAD DE DATOS:")
            print("-" * 40)
            for col in df.columns:
                valores_faltantes = df[col].isna().sum()
                if valores_faltantes > 0:
                    print(f"⚠️  Columna {col}: {valores_faltantes} valores faltantes")
                else:
                    print(f"✅ Columna {col}: Sin valores faltantes")
        else:
            print("⚠️  El CSV está vacío")
        
        print()
        print("=" * 80)
        print("✅ ANÁLISIS COMPLETADO EXITOSAMENTE")
        print("=" * 80)
        
    except Exception as e:
        print(f"❌ ERROR al procesar CSV: {e}")
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
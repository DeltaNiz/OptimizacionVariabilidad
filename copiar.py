import os
import pandas as pd
import shutil
import sys
import argparse
from datetime import datetime
from pathlib import Path

# Importar la configuración portable
try:
    from Analisis import AppConstants
    PORTABLE_MODE = True
except ImportError:
    PORTABLE_MODE = False

def main():
    # Configurar argumentos de línea de comandos
    parser = argparse.ArgumentParser(description='Copiar archivos de estrellas a carpetas organizadas')
    parser.add_argument('--csv', help='Ruta del archivo CSV a procesar')
    parser.add_argument('--subcarpeta', help='Nombre de la subcarpeta dentro de data')
    parser.add_argument('--lc_i', help='Ruta específica de la carpeta con archivos I')
    parser.add_argument('--lc_v', help='Ruta específica de la carpeta con archivos V')
    
    args = parser.parse_args()
    
    # Configurar rutas de manera portable
    if PORTABLE_MODE:
        # Usar configuración portable
        print("[INFO] Usando configuracion portable")
        
        # Usar carpetas especificadas o buscar automáticamente
        if args.lc_i and args.lc_v:
            # Usar rutas especificadas por el usuario
            carpeta1 = Path(args.lc_i)
            carpeta2 = Path(args.lc_v)
        else:
            # Buscar carpetas de origen en múltiples ubicaciones
            script_dir = Path(__file__).parent
            possible_locations = [
                script_dir,  # Mismo directorio del script
                Path.cwd(),  # Directorio de trabajo actual
                script_dir.parent,  # Directorio padre del script
                Path.home() / "Documents" / "OptimizacionVariabilidad",  # Documents del usuario
            ]
            
            # Buscar carpeta lc_i
            carpeta1 = None
            for location in possible_locations:
                candidate = location / 'lc_i'
                if candidate.exists():
                    carpeta1 = candidate
                    break
                    
            # Buscar carpeta lc_v
            carpeta2 = None
            for location in possible_locations:
                candidate = location / 'lc_v'
                if candidate.exists():
                    carpeta2 = candidate
                    break
                    
            # Si no se encuentran, usar las rutas por defecto (para mostrar error claro)
            if carpeta1 is None:
                carpeta1 = script_dir / 'lc_i'
            if carpeta2 is None:
                carpeta2 = script_dir / 'lc_v'
            
        # Determinar carpeta de destino usando AppConstants
        if args.subcarpeta:
            # Si se especifica subcarpeta, es el nombre del análisis
            analysis_path = AppConstants.get_analysis_path(args.subcarpeta)
            data = analysis_path
        else:
            # Crear nuevo análisis con timestamp
            timestamp = AppConstants.create_analysis_timestamp()
            analysis_name = f"analisis_{timestamp}"
            analysis_path = AppConstants.get_analysis_path(analysis_name)
            data = analysis_path
            
    else:
        # Modo legado (rutas hardcoded)
        print("[LEGACY] Usando rutas hardcoded (modo legado)")
        ruta_base = 'C:/Users/tomas/OneDrive/Escritorio/xd/U/2025-1/Formulacion de Proyecto de Titulacion'
        carpeta1 = os.path.join(ruta_base, 'lc_i')
        carpeta2 = os.path.join(ruta_base, 'lc_v')
        
        if args.subcarpeta:
            data = os.path.join(ruta_base, 'data', args.subcarpeta)
        else:
            data = os.path.join(ruta_base, 'data')
    
    # Determinar archivo CSV a usar
    if args.csv:
        archivo_csv = args.csv
    else:
        # Buscar archivo CSV en el directorio actual o usar default
        script_dir = Path(__file__).parent
        default_csv = script_dir / 'magnitudCMD1516.csv'
        if default_csv.exists():
            archivo_csv = str(default_csv)
        else:
            archivo_csv = 'magnitudCMD1516.csv'
    
    print(f"CSV fuente: {archivo_csv}")
    print(f"<b>Destino: {data}</b>")

    # Leer el CSV
    try:
        df = pd.read_csv(archivo_csv, skiprows=0, header=None)
        print(f"Archivo CSV cargado: {len(df)} filas")
    except Exception as e:
        print(f"Error al leer CSV: {e}")
        return
    
    # Crear directorio base si no existe
    os.makedirs(data, exist_ok=True)
    
    archivos_copiados = 0
    archivos_no_encontrados = 0
    
    for i, row in df.iterrows():
        archivoV = row[0]
        archivoI = row[1]

        star_name = f'star{i+1}'
        
        # Crear carpeta de estrella (tanto en modo portable como legado)
        stars = os.path.join(data, star_name)
        os.makedirs(stars, exist_ok=True)

        # Copiar archivo I
        src1 = os.path.join(carpeta1, archivoI)
        dest1 = os.path.join(stars, archivoI)

        if os.path.exists(src1):
            shutil.copy(src1, dest1)
            archivos_copiados += 1
        else:
            print(f"Archivo no encontrado: {src1}")
            archivos_no_encontrados += 1

        # Copiar archivo V
        src2 = os.path.join(carpeta2, archivoV)
        dest2 = os.path.join(stars, archivoV)

        if os.path.exists(src2):
            shutil.copy(src2, dest2)
            archivos_copiados += 1
        else:
            print(f"Archivo no encontrado: {src2}")
            archivos_no_encontrados += 1
    
    print(f"Proceso completado")
    print(f"Carpetas creadas: {len(df)}")
    print(f"Archivos copiados: {archivos_copiados}")
    print(f"Archivos no encontrados: {archivos_no_encontrados}")

if __name__ == "__main__":
    main()
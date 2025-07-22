import os
import pandas as pd
import shutil
import sys
import argparse
from datetime import datetime

def main():
    # Configurar argumentos de línea de comandos
    parser = argparse.ArgumentParser(description='Copiar archivos de estrellas a carpetas organizadas')
    parser.add_argument('--csv', help='Ruta del archivo CSV a procesar')
    parser.add_argument('--subcarpeta', help='Nombre de la subcarpeta dentro de data')
    
    args = parser.parse_args()
    
    # Configurar rutas
    ruta_base = 'C:/Users/tomas/OneDrive/Escritorio/xd/U/2025-1/Formulacion de Proyecto de Titulacion'
    carpeta1 = os.path.join(ruta_base, 'lc_i')
    carpeta2 = os.path.join(ruta_base, 'lc_v')
    
    # Determinar archivo CSV a usar
    if args.csv:
        archivo_csv = args.csv
    else:
        archivo_csv = 'magnitudCMD1516.csv'
    
    # Determinar carpeta de destino
    if args.subcarpeta:
        data = os.path.join(ruta_base, 'data', args.subcarpeta)
    else:
        data = os.path.join(ruta_base, 'data')
    
    print(f"=== COPIAR ARCHIVOS ===")
    print(f"CSV fuente: {archivo_csv}")
    print(f"Destino: {data}")
    print("-" * 40)
    
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

        stars = os.path.join(data, f'star{i+1}')
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
    
    print("-" * 40)
    print(f" Proceso completado")
    print(f" Carpetas creadas: {len(df)}")
    print(f" Archivos copiados: {archivos_copiados}")
    print(f" Archivos no encontrados: {archivos_no_encontrados}")

if __name__ == "__main__":
    main()
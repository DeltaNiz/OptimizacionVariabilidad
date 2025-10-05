import os
import pandas as pd
import shutil
import sys
import argparse
from datetime import datetime
from pathlib import Path
import glob

# Importar la configuración portable
try:
    from Analisis import AppConstants
    PORTABLE_MODE = True
except ImportError:
    PORTABLE_MODE = False

# Importar verificador de descarteFAP
try:
    from descarteFAP import verificar_par_archivos
    FAP_FILTER_AVAILABLE = True
except ImportError:
    FAP_FILTER_AVAILABLE = False
    print("[ADVERTENCIA] No se pudo importar descarteFAP, se copiarán todas las estrellas sin filtro FAP")

def main():
    # Configurar argumentos de línea de comandos
    parser = argparse.ArgumentParser(description='Copiar archivos de estrellas a carpetas organizadas')
    parser.add_argument('--csv', help='Ruta del archivo CSV a procesar')
    parser.add_argument('--subcarpeta', help='Nombre de la subcarpeta dentro de data')
    parser.add_argument('--lc_i', help='Ruta específica de la carpeta con archivos I')
    parser.add_argument('--lc_v', help='Ruta específica de la carpeta con archivos V')
    parser.add_argument('--aplicar_fap', action='store_true', help='Aplicar filtro FAP antes de copiar')
    parser.add_argument('--pbeg', type=float, default=0.01, help='Período mínimo para análisis GLS (default: 0.01)')
    parser.add_argument('--pend', type=float, default=3.0, help='Período máximo para análisis GLS (default: 3.0)')
    
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
    estrellas_rechazadas_fap = 0
    estrellas_aprobadas = 0
    
    # Determinar si aplicar filtro FAP
    aplicar_filtro_fap = args.aplicar_fap and FAP_FILTER_AVAILABLE
    
    if aplicar_filtro_fap:
        print(f"[INFO] Filtro FAP activado (Pbeg={args.pbeg}, Pend={args.pend})")
        print(f"[INFO] Solo se copiarán estrellas que pasen los filtros FAP y amplitud")
    
    # CSV para guardar estrellas que pasan el filtro FAP
    estrellas_fap = []
    
    for i, row in df.iterrows():
        archivoV = row[0]
        archivoI = row[1]

        star_name = f'star{i+1}'
        
        # Verificar si los archivos existen antes de cualquier procesamiento
        src1 = os.path.join(carpeta1, archivoI)
        src2 = os.path.join(carpeta2, archivoV)
        
        if not os.path.exists(src1):
            print(f"Archivo no encontrado: {src1}")
            archivos_no_encontrados += 1
            continue
            
        if not os.path.exists(src2):
            print(f"Archivo no encontrado: {src2}")
            archivos_no_encontrados += 1
            continue
        
        # Aplicar filtro FAP si está activado
        if aplicar_filtro_fap:
            try:
                pasa_filtros, info = verificar_par_archivos(
                    src2, src1,  # V, I
                    Pbeg=args.pbeg, 
                    Pend=args.pend
                )
                
                if not pasa_filtros:
                    estrellas_rechazadas_fap += 1
                    if 'error' in info:
                        print(f"[FAP RECHAZADO] {star_name} - Error: {info['error']}")
                    else:
                        print(f"[FAP RECHAZADO] {star_name} - FAP:{info.get('pasa_FAP', False)}, Amp:{info.get('pasa_amplitud', False)}")
                    continue  # No crear carpeta ni copiar archivos
                else:
                    estrellas_aprobadas += 1
                    estrellas_fap.append([archivoV, archivoI])
                    print(f"[FAP APROBADO] {star_name}")
                    
            except Exception as e:
                print(f"[FAP ERROR] {star_name} - {e}")
                estrellas_rechazadas_fap += 1
                continue
        
        # Crear carpeta de estrella solo si pasa todos los filtros
        stars = os.path.join(data, star_name)
        os.makedirs(stars, exist_ok=True)

        # Copiar archivo I
        dest1 = os.path.join(stars, archivoI)
        shutil.copy(src1, dest1)
        archivos_copiados += 1

        # Copiar archivo V
        dest2 = os.path.join(stars, archivoV)
        shutil.copy(src2, dest2)
        archivos_copiados += 1
    
    # Guardar CSV de estrellas que pasaron FAP (incluso si está vacío)
    if aplicar_filtro_fap:
        csv_fap_path = os.path.join(data, 'FAPRevision.csv')
        pd.DataFrame(estrellas_fap, columns=['archivo_V', 'archivo_I']).to_csv(csv_fap_path, index=False, header=False)
        if estrellas_fap:
            print(f"[INFO] Archivo FAPRevision.csv guardado con {len(estrellas_fap)} estrellas")
            print(f"[INFO] La intersección con datos_filtrados se generará después del análisis")
        else:
            print(f"[WARNING] Archivo FAPRevision.csv generado VACÍO - Todas las estrellas fueron rechazadas")
    
    print(f"Proceso completado")
    
    if aplicar_filtro_fap:
        print(f"Estrellas procesadas: {len(df)}")
        print(f"Estrellas aprobadas FAP: {estrellas_aprobadas}")
        print(f"Estrellas rechazadas FAP: {estrellas_rechazadas_fap}")
        print(f"Carpetas creadas: {estrellas_aprobadas}")
    else:
        print(f"Carpetas creadas: {len(df)}")
    
    print(f"Archivos copiados: {archivos_copiados}")
    print(f"Archivos no encontrados: {archivos_no_encontrados}")

if __name__ == "__main__":
    main()
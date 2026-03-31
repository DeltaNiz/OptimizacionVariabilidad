import os
import pandas as pd
import shutil
import argparse
from pathlib import Path
import gc  # Para limpieza de memoria
import warnings  # Para suprimir warnings problemáticos
import multiprocessing  # Para procesamiento paralelo del filtro FAP

# Suprimir warnings globalmente para evitar problemas con PyAstronomy
warnings.filterwarnings('ignore', category=RuntimeWarning)
warnings.filterwarnings('ignore', category=UserWarning)
warnings.filterwarnings('ignore', category=FutureWarning)

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

# Importar función para calcular workers óptimos
try:
    from procesofull import get_optimal_workers
    OPTIMAL_WORKERS_AVAILABLE = True
except ImportError:
    OPTIMAL_WORKERS_AVAILABLE = False
    print("[ADVERTENCIA] No se pudo importar get_optimal_workers, usando cálculo simple")

def procesar_estrella_paralelo(args):
    """
    Worker function para procesamiento paralelo de estrellas (con o sin filtro FAP).

    Args:
        args: tuple con (i, archivoV, archivoI, carpeta1, carpeta2, aplicar_fap, pbeg, pend)

    Returns:
        tuple: (resultado_dict | None, mensaje_error | None)
    """
    i, archivoV, archivoI, carpeta1_str, carpeta2_str, aplicar_fap, pbeg, pend = args

    star_name = f'star{i+1}'
    src1 = os.path.join(carpeta1_str, archivoI)
    src2 = os.path.join(carpeta2_str, archivoV)

    # Verificar existencia de archivos
    if not os.path.exists(src1):
        return None, f"Archivo no encontrado: {src1}"

    if not os.path.exists(src2):
        return None, f"Archivo no encontrado: {src2}"

    # Si se debe aplicar filtro FAP, ejecutarlo
    if aplicar_fap:
        try:
            # Suprimir stdout/stderr de PyAstronomy
            import io
            import contextlib

            f = io.StringIO()
            with contextlib.redirect_stdout(f), contextlib.redirect_stderr(f):
                pasa_filtros, info = verificar_par_archivos(
                    src2, src1,  # V, I
                    Pbeg=pbeg,
                    Pend=pend
                )

            if pasa_filtros:
                # Estrella aprobada por FAP
                resultado = {
                    'index': i,
                    'archivoV': archivoV,
                    'archivoI': archivoI,
                    'src1': src1,
                    'src2': src2,
                    'star_name': star_name,
                    'pasa': True
                }
                return resultado, f"[FAP APROBADO] {star_name}"
            else:
                # Estrella rechazada por FAP
                razon = ""
                if 'error' in info:
                    razon = f" - Error: {info['error']}"
                elif 'early_exit' in info and info['early_exit']:
                    razon = f" - {info.get('razon', 'Filtro temprano')}"
                else:
                    razon = f" - FAP:{info.get('pasa_FAP', False)}, Amp:{info.get('pasa_amplitud', False)}"

                return None, f"[FAP RECHAZADO] {star_name}{razon}"

        except MemoryError as e:
            return None, f"[FAP ERROR MEMORIA] {star_name} - {e}"
        except Exception as e:
            return None, f"[FAP ERROR] {star_name} - {e}"
    else:
        # Sin filtro FAP: aprobar todas las estrellas que tengan archivos válidos
        resultado = {
            'index': i,
            'archivoV': archivoV,
            'archivoI': archivoI,
            'src1': src1,
            'src2': src2,
            'star_name': star_name,
            'pasa': True
        }
        return resultado, f"[COPIADO] {star_name}"

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
    parser.add_argument('--workers', type=int, help='Número de procesos paralelos (auto-detecta si no se especifica)')

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
                Path.home() / "Documents" / "SODEV-CG",  # Documents del usuario
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
        print("[INFO] Solo se copiarán estrellas que pasen los filtros FAP y amplitud")

    # CSV para guardar estrellas que pasan el filtro FAP
    estrellas_fap = []

    # Determinar número de workers
    if args.workers:
        num_workers = max(1, args.workers)
    else:
        if OPTIMAL_WORKERS_AVAILABLE:
            num_workers = get_optimal_workers()
        else:
            # Fallback: cálculo simple
            num_workers = max(1, multiprocessing.cpu_count() - 1)

    print(f"[INFO] Usando {num_workers} workers para procesamiento paralelo")

    # Preparar argumentos para procesamiento paralelo
    args_list = [
        (i, row[0], row[1], str(carpeta1), str(carpeta2), aplicar_filtro_fap, args.pbeg, args.pend)
        for i, row in df.iterrows()
    ]

    # Contadores
    archivos_copiados = 0
    archivos_no_encontrados = 0
    estrellas_rechazadas_fap = 0
    estrellas_aprobadas = 0

    # Procesar estrellas en paralelo
    with multiprocessing.Pool(num_workers) as pool:
        # Usar imap_unordered para procesar en tiempo real
        for resultado, mensaje in pool.imap_unordered(procesar_estrella_paralelo, args_list):
            if mensaje:
                print(mensaje)

            if resultado is None:
                # Estrella rechazada o error
                if "no encontrado" in mensaje:
                    archivos_no_encontrados += 1
                else:
                    estrellas_rechazadas_fap += 1
            else:
                # Estrella aprobada
                estrellas_aprobadas += 1

                if aplicar_filtro_fap:
                    estrellas_fap.append([resultado['archivoV'], resultado['archivoI']])

                # Crear carpeta de estrella
                stars = os.path.join(data, resultado['star_name'])
                os.makedirs(stars, exist_ok=True)

                # Copiar archivos
                dest1 = os.path.join(stars, resultado['archivoI'])
                shutil.copy(resultado['src1'], dest1)
                archivos_copiados += 1

                dest2 = os.path.join(stars, resultado['archivoV'])
                shutil.copy(resultado['src2'], dest2)
                archivos_copiados += 1

    # Guardar CSV de estrellas que pasaron FAP (incluso si está vacío)
    if aplicar_filtro_fap:
        csv_fap_path = os.path.join(data, 'FAPRevision.csv')
        pd.DataFrame(estrellas_fap, columns=['archivo_V', 'archivo_I']).to_csv(csv_fap_path, index=False, header=False)
    
    # Liberar memoria al final
    gc.collect()
    
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
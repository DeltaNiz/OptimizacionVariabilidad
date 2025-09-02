from __future__ import print_function, division
import numpy as np
from numba import njit, prange
import matplotlib.pylab as plt
from PyAstronomy.pyTiming import pyPeriod
from PyAstronomy.pyTiming import pyPDM
from pdmpy import pdm
import scipy.interpolate as sciinter
import scipy.optimize as sciopti
import os
import pandas as pd
import time as t
import sys
import argparse
import multiprocessing as mp
from concurrent.futures import ProcessPoolExecutor, as_completed
import Fase_monocolor
#import psutil
import traceback

def get_optimal_workers():
    """Detecta automáticamente el número óptimo de procesos paralelos"""
    try:
        # Detectar número de núcleos físicos
        physical_cores = mp.cpu_count() // 2 if mp.cpu_count() > 2 else mp.cpu_count()
        
        # Detectar RAM disponible (estimación sin psutil)
        import platform
        if platform.system() == "Windows":
            # Estimación conservadora para Windows
            estimated_ram_gb = 8  # Asumimos al menos 8GB
        else:
            estimated_ram_gb = 8
        
        # Calcular workers óptimos basado en memoria y CPU
        # Cada proceso usa ~2-3GB de RAM
        max_workers_by_memory = max(1, min(estimated_ram_gb // 3, 8))
        max_workers_by_cpu = max(1, min(physical_cores - 1, 12))
        
        optimal_workers = min(max_workers_by_memory, max_workers_by_cpu)
        
        return max(1, min(optimal_workers, 6))  # Máximo 6 para seguridad
    except:
        return 2  # Fallback seguro

def process_single_star(star_data, Pend=3, Pbeg=0.01):
    """Procesa una sola estrella de forma independiente"""
    data_folder, star_name = star_data
    
    try:
        route = os.path.join(data_folder, star_name)
        files = os.listdir(route)
        star_number = int(star_name[4:])
        
        fileV = next((f for f in files if f.endswith('V')), None)
        fileI = next((f for f in files if f.endswith('i')), None)
        
        if not (fileV and fileI):
            return {
                'star': star_name,
                'status': 'error',
                'message': f'Archivos faltantes: V={fileV}, I={fileI}',
                'time': 0
            }
        
        init_time = t.time()
        
        # Cargar datos
        dataV = np.loadtxt(os.path.join(route, fileV))
        dataI = np.loadtxt(os.path.join(route, fileI))
        
        # Preparar datos
        time_v = dataV[:, 0]
        flux_v = dataV[:, 1]
        time_i = dataI[:, 0]
        flux_i = dataI[:, 1]
        
        # Análisis GLS
        clp = pyPeriod.Gls((time_v, flux_v), norm="ZK", Pbeg=Pbeg, Pend=Pend)
        clpI = pyPeriod.Gls((time_i, flux_i), norm="ZK", Pbeg=Pbeg, Pend=Pend)
        
        # Análisis PDM
        f1, t1 = pdm_with_covers_pypdm_like(
            time_v, flux_v, 
            f_min=1./clp.Pend, f_max=1./clp.Pbeg, 
            delf=clp.fstep, nbin=7, ncovers=3
        )
        
        f2, t2 = pdm_with_covers_pypdm_like(
            time_i, flux_i,
            f_min=1./clpI.Pend, f_max=1./clpI.Pbeg,
            delf=clpI.fstep, nbin=7, ncovers=3
        )
        
        # Detectar picos
        from scipy.signal import find_peaks
        
        fapLevels = np.array([0.1, 0.05, 0.01, 0.001])
        plevels = clp.powerLevel(fapLevels)
        plevelsI = clpI.powerLevel(fapLevels)
        
        peaksglsv, _ = find_peaks(clp.power, height=plevels[3], prominence=0.3 * np.max(clp.power), distance=90)
        peaksglsi, _ = find_peaks(clpI.power, height=plevelsI[3], prominence=0.3 * np.max(clpI.power), distance=90)
        peakspdmv, _ = find_peaks(-t1, prominence=0.28*(np.max(t1)-np.min(t1)), distance=90)
        peakspdmi, _ = find_peaks(-t2, prominence=0.28*(np.max(t2)-np.min(t2)), distance=90)
        
        # Guardar resultados
        sortglsv = np.argsort(clp.power[peaksglsv])[::-1][:30]
        sortglsi = np.argsort(clpI.power[peaksglsi])[::-1][:30]
        sortpdmv = np.argsort(t1[peakspdmv])[:30]
        sortpdmi = np.argsort(t2[peakspdmi])[:30]
        
        freqsglsv = (clp.freq[peaksglsv])[sortglsv]
        freqsglsi = (clpI.freq[peaksglsi])[sortglsi]
        freqspdmv = (f1[peakspdmv])[sortpdmv]
        freqspdmi = (f2[peakspdmi])[sortpdmi]

        fase_monocolor = Fase_monocolor.FaseMonocolor()
        fase_monocolor.cargar_datos(star_data, 1./clp.freq[np.argmax(clp.power)]) # Generador de curvas de luz

        # Guardar CSVs
        pd.DataFrame({'freq': freqsglsv, 'period': 1./freqsglsv}).to_csv(
            os.path.join(route, 'pglsv.csv'), index=False)
        pd.DataFrame({'freq': freqsglsi, 'period': 1./freqsglsi}).to_csv(
            os.path.join(route, 'pglsi.csv'), index=False)
        pd.DataFrame({'freq': freqspdmv, 'period': 1./freqspdmv}).to_csv(
            os.path.join(route, 'ppdmv.csv'), index=False)
        pd.DataFrame({'freq': freqspdmi, 'period': 1./freqspdmi}).to_csv(
            os.path.join(route, 'ppdmi.csv'), index=False)
        
        # Generar gráficos
        generate_plots(clp, clpI, f1, t1, f2, t2, route)
        
        elapsed_time = t.time() - init_time
        
        return {
            'star': star_name,
            'status': 'success',
            'time': elapsed_time,
            'Best Peak GLS V': 1./clp.freq[np.argmax(clp.power)],
            'Best Peak GLS I': 1./clpI.freq[np.argmax(clpI.power)],
            'Best Minima PDM V': (1/f1)[np.argmin(t1)],
            'Best Minima PDM I': (1/f2)[np.argmin(t2)]
        }
        
    except Exception as e:
        return {
            'star': star_name,
            'status': 'error',
            'message': str(e),
            'traceback': traceback.format_exc(),
            'time': t.time() - init_time if 'init_time' in locals() else 0
        }

def generate_plots(clp, clpI, f1, t1, f2, t2, route):
    """Genera los gráficos para una estrella"""
    try:
        fapLevels = np.array([0.1, 0.05, 0.01, 0.001])
        plevels = clp.powerLevel(fapLevels)
        plevelsI = clpI.powerLevel(fapLevels)
        
        hpp = 1./clp.freq[np.argmax(clp.power)]
        hppI = 1./clpI.freq[np.argmax(clpI.power)]
        periodpdmV = (1/f1)[np.argmin(t1)]
        periodpdmI = (1/f2)[np.argmin(t2)]
        
        f, ax = plt.subplots(2, 2, figsize=(16, 12))
        
        # GLS V
        ax[0,0].plot((1./clp.freq), clp.power, 'b.-', lw=1.2)
        for i in range(len(fapLevels)):
            ax[0,0].plot([min(1./clp.freq), max(1./clp.freq)], [plevels[i]]*2, '--')
        ax[0,0].set_title("GLS and PDM $V$ filter")
        ax[0,0].axvline(hpp, color='darkmagenta', linestyle='--', label=f'Period = {hpp:.5f} days')
        ax[0,0].set_ylabel("Power")
        ax[0,0].set_xlim(clp.Pbeg, clp.Pend)
        ax[0,0].legend()
        ax[0,0].set_xticklabels([])
        
        # GLS I
        ax[0,1].plot((1./clpI.freq), clpI.power, 'b.-', lw=1.2)
        for i in range(len(fapLevels)):
            ax[0,1].plot([min(1./clpI.freq), max(1./clpI.freq)], [plevelsI[i]]*2, '--')
        ax[0,1].set_title("GLS and PDM $I$ filter")
        ax[0,1].axvline(hppI, color='darkmagenta', linestyle='--', label=f'Period = {hppI:.5f} days')
        ax[0,1].set_ylabel("Power")
        ax[0,1].set_xlim(clpI.Pbeg, clpI.Pend)
        ax[0,1].legend()
        ax[0,1].set_xticklabels([])
        
        # PDM V
        periodo1 = (1/f1)
        ax[1,0].plot(periodo1, t1, 'kp-', lw=1.2)
        ax[1,0].axvline(periodpdmV, color='darkmagenta', linestyle='--', label=f'Period = {periodpdmV:.5f} days')
        ax[1,0].set_xlabel("Period")
        ax[1,0].set_ylabel(r"$\Theta$")
        ax[1,0].set_xlim(clp.Pbeg, clp.Pend)
        ax[1,0].legend()
        
        # PDM I
        periodo2 = (1/f2)
        ax[1,1].plot(periodo2, t2, 'kp-', lw=1.2)
        ax[1,1].axvline(periodpdmI, color='darkmagenta', linestyle='--', label=f'Period = {periodpdmI:.5f} days')
        ax[1,1].set_xlabel("Period")
        ax[1,1].set_ylabel(r"$\Theta$")
        ax[1,1].set_xlim(clpI.Pbeg, clpI.Pend)
        ax[1,1].legend()
        
        plt.subplots_adjust(hspace=0)
        plt.savefig(os.path.join(route, 'GLSPDM.png'))
        plt.close()
        
    except Exception as e:
        # Si falla la generación de gráficos, no interrumpir el análisis
        pass

def print_timer(message, start_time):
    """Función auxiliar para imprimir tiempos transcurridos"""
    elapsed = t.time() - start_time
    print(f"[TIMER] {message}: {elapsed:.2f}s")
    sys.stdout.flush()
    return t.time()  # Retorna nuevo tiempo de inicio

@njit(parallel=True)
def compute_thetas_pypdm_style(time, flux, freqs, nbin, ncovers):
    nfreqs = len(freqs)
    thetas = np.zeros(nfreqs)

    for j in prange(nfreqs):
        f = freqs[j]
        period = 1.0 / f
        theta_covers = np.zeros(ncovers)

        for cover in range(ncovers):
            shift = cover / ncovers
            phases = ((time / period + shift) % 1.0)

            bins = np.linspace(0, 1, nbin + 1)
            bin_means = np.zeros(nbin)
            bin_counts = np.zeros(nbin)
            bin_vars = np.zeros(nbin)

            for i in range(len(phases)):
                for b in range(nbin):
                    if bins[b] <= phases[i] < bins[b+1]:
                        bin_means[b] += flux[i]
                        bin_counts[b] += 1
                        break

            for b in range(nbin):
                if bin_counts[b] > 0:
                    bin_means[b] /= bin_counts[b]

            # Segunda pasada: varianzas
            for i in range(len(phases)):
                for b in range(nbin):
                    if bins[b] <= phases[i] < bins[b+1]:
                        if bin_counts[b] > 0:
                            bin_vars[b] += (flux[i] - bin_means[b])**2
                        break

            sbin = np.sum(bin_vars)
            s2 = np.sum((flux - np.mean(flux))**2)
            theta_covers[cover] = sbin / s2 if s2 > 0 else 1.0

        thetas[j] = np.mean(theta_covers)

    return thetas


def pdm_with_covers_pypdm_like(time, flux, f_min, f_max, delf, nbin=10, ncovers=3):
    freqs = np.arange(f_min, f_max, delf)
    thetas = compute_thetas_pypdm_style(time, flux, freqs, nbin, ncovers)
    return freqs, thetas

def main():
    script_start = t.time()
    
    # Configurar argumentos de línea de comandos
    parser = argparse.ArgumentParser(description='Procesar análisis de estrellas en paralelo')
    parser.add_argument('--data_folder', help='Ruta de la carpeta con los datos de las estrellas')
    parser.add_argument('--workers', type=int, help='Número de procesos paralelos (auto-detecta si no se especifica)')
    parser.add_argument('--pend', type=float, default=3, help='Período máximo para análisis GLS (default: 3)')
    parser.add_argument('--pbeg', type=float, default=0.01, help='Período mínimo para análisis GLS (default: 0.01)')
    
    args = parser.parse_args()
    
    # Usar los parámetros de período desde argumentos
    periodo_max = args.pend
    periodo_min = args.pbeg
    
    # Determinar número de workers
    if args.workers:
        num_workers = max(1, min(args.workers, 12))  # Límite de seguridad
        print(f"Usando {num_workers} workers especificados por el usuario")
    else:
        num_workers = get_optimal_workers()
        print(f"Auto-detectados {num_workers} workers óptimos")
    
    # Determinar carpeta de datos
    if args.data_folder:
        data = args.data_folder
    else:
        data = 'C:/Users/tomas/OneDrive/Escritorio/xd/U/2025-1/Formulacion de Proyecto de Titulacion/data/analisis_20250722_180246'

    print(f"Carpeta de datos: {data}")
    
    if not os.path.exists(data):
        print(f"ERROR: No se encontró la carpeta de datos: {data}")
        return
    
    # Obtener lista de estrellas
    stars = [d for d in os.listdir(data) if os.path.isdir(os.path.join(data, d))]
    
    if not stars:
        print(f"ERROR: No se encontraron carpetas de estrellas en: {data}")
        return
    
    total_stars = len(stars)
    # Mensaje específico que la GUI puede detectar
    print(f"Total de estrellas a procesar: {total_stars}")
    print(f"Procesamiento paralelo con {num_workers} workers")
    
    # Preparar datos para procesamiento paralelo
    star_data_list = [(data, star) for star in stars]
    
    # Contadores de resultados
    successful_stars = 0
    failed_stars = 0
    results = []
    
    inicio_total = t.time()
    
    try:
        # Procesar estrellas en paralelo con progreso compatible para GUI
        with ProcessPoolExecutor(max_workers=num_workers) as executor:
            # Enviar todas las tareas
            future_to_star = {
                executor.submit(process_single_star, star_data, periodo_max, periodo_min): star_data[1] 
                for star_data in star_data_list
            }
            
            # Procesar resultados en orden de completación
            completed_count = 0
            for future in as_completed(future_to_star):
                star_name = future_to_star[future]
                completed_count += 1
                
                # Mensaje de progreso compatible con GUI - EXACTO formato esperado
                print(f"Procesando estrella {completed_count}/{total_stars}")
                sys.stdout.flush()
                
                try:
                    result = future.result()
                    results.append(result)
                    
                    if result['status'] == 'success':
                        successful_stars += 1
                        print(f"[OK] {star_name} completada exitosamente en {result['time']:.1f}s")
                        sys.stdout.flush()
                    else:
                        failed_stars += 1
                        print(f"[ERROR] Error en estrella {star_name}: {result.get('message', 'Error desconocido')}")
                        sys.stdout.flush()
                        
                except Exception as e:
                    failed_stars += 1
                    print(f"[ERROR] Error crítico procesando {star_name}: {str(e)}")
                    sys.stdout.flush()
                    results.append({
                        'star': star_name,
                        'status': 'critical_error',
                        'message': str(e),
                        'time': 0
                    })
                
                # Mostrar progreso detallado más frecuentemente para mejor UX
                # Para datasets pequeños (<=20): mostrar cada estrella completada
                # Para datasets medianos (21-100): mostrar cada 2-3 estrellas
                # Para datasets grandes (>100): mostrar cada 5% o mínimo cada 5 estrellas
                mostrar_progreso = False
                if total_stars <= 20:
                    mostrar_progreso = True  # Mostrar cada estrella para datasets pequeños
                elif total_stars <= 100:
                    mostrar_progreso = (completed_count % 2 == 0) or (completed_count == total_stars)
                else:
                    intervalo = max(5, total_stars // 20)  # Mínimo cada 5 estrellas, máximo cada 5%
                    mostrar_progreso = (completed_count % intervalo == 0) or (completed_count == total_stars)
                
                if mostrar_progreso:
                    porcentaje = (completed_count / total_stars) * 100
                    print(f"Progreso: {completed_count}/{total_stars} ({porcentaje:.1f}%) - Exitosas: {successful_stars}, Fallidas: {failed_stars}")
                    sys.stdout.flush()
    
    except KeyboardInterrupt:
        print("ADVERTENCIA: Procesamiento interrumpido por el usuario")
        return
    except Exception as e:
        print(f"ERROR: Error crítico en el procesamiento paralelo: {str(e)}")
        return
    
    # Calcular estadísticas finales
    fin_total = t.time()
    tiempo_total = (fin_total - inicio_total) / 60
    
    # Estadísticas de tiempo
    successful_results = [r for r in results if r['status'] == 'success']
    if successful_results:
        times = [r['time'] for r in successful_results]
        avg_time_per_star = np.mean(times)
        total_processing_time = np.sum(times)
        speedup = total_processing_time / tiempo_total if tiempo_total > 0 else 1
    else:
        avg_time_per_star = 0
        total_processing_time = 0
        speedup = 1
    
    # Imprimir resumen final compatible con GUI

    print(f"Total de estrellas: {total_stars}")
    print(f"Procesadas exitosamente: {successful_stars}")
    print(f"Fallidas: {failed_stars}")
    print(f"Tasa de éxito: {(successful_stars/total_stars)*100:.1f}%")
    print(f"<b>Tiempo total de ejecución: {tiempo_total:.2f} minutos</b>")
    print(f"<b>Tiempo promedio por estrella: {avg_time_per_star:.2f} segundos</b>")
    print(f"Speedup logrado: {speedup:.1f}x")
    
    # Guardar reporte detallado
    try:
        report_df = pd.DataFrame(results)
        report_path = os.path.join(data, 'Best_Peak_GLS_Min_PDM.csv')
        report_df.to_csv(report_path, index=False)
        print(f"Reporte detallado guardado en: {report_path}")
    except Exception as e:
        print(f"ADVERTENCIA: No se pudo guardar el reporte: {str(e)}")
    
    # Mostrar estrellas fallidas si las hay
    if failed_stars > 0:
        print(f"\nEstrellas fallidas ({failed_stars}):")
        failed_results = [r for r in results if r['status'] != 'success']
        for result in failed_results[:10]:  # Mostrar solo las primeras 10
            print(f"  - {result['star']}: {result.get('message', 'Error desconocido')}")
        if len(failed_results) > 10:
            print(f"  ... y {len(failed_results) - 10} más")

if __name__ == "__main__":
    main()
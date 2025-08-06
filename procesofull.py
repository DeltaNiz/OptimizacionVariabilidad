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
    print("[TIMER] Iniciando script procesofull.py")
    
    # Configurar argumentos de línea de comandos
    parser = argparse.ArgumentParser(description='Procesar análisis de estrellas')
    parser.add_argument('--data_folder', help='Ruta de la carpeta con los datos de las estrellas')
    
    args = parser.parse_args()
    
    print_timer("Configuración inicial", script_start)
    
    # Determinar carpeta de datos
    if args.data_folder:
        data = args.data_folder
    else:
        data = 'C:/Users/tomas/OneDrive/Escritorio/xd/U/2025-1/Formulacion de Proyecto de Titulacion/data/analisis_20250722_180246'

    print(f"Carpeta de datos: {data}")
    print("-" * 50)
    
    if not os.path.exists(data):
        print(f"ERROR: No se encontró la carpeta de datos: {data}")
        return
    
    stars = [d for d in os.listdir(data) if os.path.isdir(os.path.join(data, d))]
    
    if not stars:
        print(f"ERROR: No se encontraron carpetas de estrellas en: {data}")
        return
    
    print(f"Estrellas encontradas: {len(stars)}")
    print(f"Total de estrellas a procesar: {len(stars)}")
    print("-" * 50)
    sys.stdout.flush()  # Forzar salida inmediata
    
    inicio_total = t.time()
    
    for idx, star in enumerate(stars):
        print(f"\nProcesando estrella {idx + 1}/{len(stars)}: {star}")
        sys.stdout.flush()  # Forzar salida inmediata
        route = os.path.join(data, star)
        files = os.listdir(route)
        star_number = int(star[4:]) 

        fileV = next((f for f in files if f.endswith('V')), None)
        fileI = next((f for f in files if f.endswith('i')), None)

        if fileV and fileI:
            print(f"Archivos encontrados: {fileV}, {fileI}")
            sys.stdout.flush()
            init_time = t.time()
            
            try:
                load_start = t.time()
                print("Cargando datos...")
                sys.stdout.flush()
                
                dataV= np.loadtxt(os.path.join(route, fileV))
                dataI= np.loadtxt(os.path.join(route, fileI))
                load_time = print_timer("Carga de archivos", load_start)

                prep_start = t.time()
                dataredV=dataV[::2]
                dataredI=dataI[::2]

                time = dataV[:,0]
                flux = dataV[:,1]

                timeI = dataI[:,0]
                fluxI = dataI[:,1]
                
                prep_time = print_timer("Preparación de datos", prep_start)

                gls_start = t.time()
                print("Ejecutando análisis GLS...")
                sys.stdout.flush()
                #------------------------------GLS-----------------------------------
                Pend = 3
                gls_v_start = t.time()
                clp = pyPeriod.Gls((time, flux), norm="ZK", Pbeg=0.01, Pend=Pend)
                gls_v_time = print_timer("GLS filtro V", gls_v_start)
                
                fapLevels = np.array([0.1, 0.05, 0.01, 0.001])
                plevels = clp.powerLevel(fapLevels)

                ifmax = np.argmax(clp.power)

                pmax = clp.power[ifmax]
                fmax = clp.freq[ifmax]

                hpp = 1./fmax

                freqstep=clp.fstep
                periodos= (1./clp.freq)
                power=clp.power

                gls_i_start = t.time()
                clpI = pyPeriod.Gls((timeI, fluxI), norm="ZK", Pbeg=0.01, Pend=Pend)
                gls_i_time = print_timer("GLS filtro I", gls_i_start)

                fapLevelsI = np.array([0.1, 0.05, 0.01, 0.001])
                plevelsI = clpI.powerLevel(fapLevels)
                ifmaxI = np.argmax(clpI.power)

                pmaxI = clpI.power[ifmaxI]
                fmaxI = clpI.freq[ifmaxI]

                hppI = 1./fmaxI

                freqstepI=clpI.fstep
                periodosI= (1./clpI.freq)
                powerI=clpI.power

                gls_total_time = print_timer("GLS total", gls_start)

                pdm_start = t.time()
                print("Ejecutando análisis PDM...")
                sys.stdout.flush()
                
                #-----------------------------PDM--------------------------------------
                pdm_v_start = t.time()
                """S = pyPDM.Scanner(minVal=(1./clp.Pend), maxVal=(1./clp.Pbeg), dVal=freqstep, mode="frequency")
                P = pyPDM.PyPDM(time, flux)

                f1, t1 = P.pdmEquiBinCover(7, 3, S)
                """
                f1, t1 = pdm_with_covers_pypdm_like(time, flux, f_min=1./clp.Pend, f_max=1./clp.Pbeg, delf=freqstep, nbin=7, ncovers=3)
                thetmin1= np.min(t1)
                periodpdmV = (1/f1)[np.argmin(t1)]
                
                pdm_v_time = print_timer("PDM filtro V", pdm_v_start)

                equis= np.linspace(0, 10.0, 2)
                lequis=np.array([thetmin1 for i in range(len(equis))])

                periodo1 = (1/f1)

                pdm_i_start = t.time()
                """SI = pyPDM.Scanner(minVal=(1./clpI.Pend), maxVal=(1./clpI.Pbeg), dVal=freqstepI, mode="frequency")
                PI = pyPDM.PyPDM(timeI,  fluxI)

                f2, t2 = PI.pdmEquiBinCover(7, 3, SI)"""
                f2, t2 = pdm_with_covers_pypdm_like(timeI, fluxI, f_min=1./clpI.Pend, f_max=1./clpI.Pbeg, delf=freqstepI, nbin=7, ncovers=3)
                thetmin2=np.min(t2)
                periodpdmI = (1/f2)[np.argmin(t2)]
                
                pdm_i_time = print_timer("PDM filtro I", pdm_i_start)

                equisI= np.linspace(0, 10.0, 2)
                lequisI=np.array([thetmin2 for i in range(len(equisI))])

                periodo2 = (1/f2)

                pdm_total_time = print_timer("PDM total", pdm_start)

                peaks_start = t.time()
                print("Detectando picos de frecuencia...")
                sys.stdout.flush()
                #-----------------------------Frequency Peaks--------------------------------------
                from scipy.signal import find_peaks

                peaksglsv, _ = find_peaks(clp.power, height=plevels[3], prominence=0.3 * np.max(clp.power), distance=90)
                peaksglsi, _ = find_peaks(clpI.power, height=plevelsI[3], prominence=0.3 * np.max(clp.power), distance=90)

                peakspdmv, _ = find_peaks(-t1, prominence= 0.28*(np.max(t1)-np.min(t1)), distance=90)
                peakspdmi, _ = find_peaks(-t2, prominence= 0.28*(np.max(t2)-np.min(t2)), distance=90)
                
                peakperiodsv = 1./clp.freq[peaksglsv]
                peakperiodsi = 1./clpI.freq[peaksglsi]

                pdmperiodsv = 1./f1[peakspdmv]
                pdmperiodsi = 1./f2[peakspdmi]

                peaks_time = print_timer("Detección de picos", peaks_start)

                save_start = t.time()
                print("Organizando y guardando resultados...")
                sys.stdout.flush()
                #---sort---
                sortglsv = np.argsort(clp.power[peaksglsv])[::-1][:30]
                sortglsi = np.argsort(clpI.power[peaksglsi])[::-1][:30]
                sortpdmv = np.argsort(t1[peakspdmv])[:30]
                sortpdmi = np.argsort(t2[peakspdmi])[:30]

                freqsglsv = (clp.freq[peaksglsv])[sortglsv]
                freqsglsi = (clpI.freq[peaksglsi])[sortglsi]
                freqspdmv = (f1[peakspdmv])[sortpdmv]
                freqspdmi = (f2[peakspdmi])[sortpdmi]

                perglsv = 1./freqsglsv
                perglsi = 1./freqsglsi
                perpdmv = 1./freqspdmv
                perpdmi = 1./freqspdmi

                #guardar los peaks en cada caso
                df = pd.DataFrame({'freq': freqsglsv, 'period': perglsv})
                df.to_csv(os.path.join(route,'pglsv.csv'), index=False)

                df2 = pd.DataFrame({'freq': freqsglsi, 'period': perglsi})
                df2.to_csv(os.path.join(route,'pglsi.csv'), index=False)

                df3 = pd.DataFrame({'freq': freqspdmv, 'period': perpdmv})
                df3.to_csv(os.path.join(route,'ppdmv.csv'), index=False)

                df4 = pd.DataFrame({'freq': freqspdmi, 'period': perpdmi})
                df4.to_csv(os.path.join(route,'ppdmi.csv'), index=False)

                save_time = print_timer("Guardado de CSVs", save_start)

                peakspowerv = clp.power[peaksglsv]
                peakspoweri = clpI.power[peaksglsi]

                minimav = t1[peakspdmv]
                minimai = t2[peakspdmi]

                #Los Peaks del GLS son hpp y hppI
                print(f'Best Peak GLS V: {hpp}')
                print(f'Best Peak GLS I: {hppI}')
                print(f'Best Minima PDM V: {periodpdmV}')
                print(f'Best Minima PDM I: {periodpdmI}')

                plot_start = t.time()
                print("Generando gráficos...")
                sys.stdout.flush()
                #-----------------------------Plots---------------------------------------
                f, ax = plt.subplots(2, 2, figsize=(16, 12))

                ax[0,0].plot((1./clp.freq), clp.power, 'b.-', lw=1.2)
                #ax[0,0].plot(peakperiodsv, peakspowerv, 'rx', markersize=10, label='Detected Peaks')
                for i in range(len(fapLevels)):
                    ax[0,0].plot([min(1./clp.freq), max(1./clp.freq)], [plevels[i]]*2, '--')
                ax[0,0].set_title("GLS and PDM $V$ filter")
                ax[0,0].axvline(hpp, color='darkmagenta', linestyle='--', label=f'Period = {hpp:.5f} days')
                ax[0,0].set_ylabel("Power")
                ax[0,0].set_xlim(clp.Pbeg,clp.Pend)
                ax[0,0].legend()
                ax[0,0].set_xticklabels([])

                ax[0,1].plot((1./clpI.freq), clpI.power, 'b.-', lw=1.2)
                #ax[0,1].plot(peakperiodsi, peakspoweri, 'rx', markersize=10, label='Detected Peaks')
                for i in range(len(fapLevels)):
                    ax[0,1].plot([min(1./clpI.freq), max(1./clpI.freq)], [plevelsI[i]]*2, '--')
                ax[0,1].set_title("GLS and PDM $I$ filter")
                ax[0,1].axvline(hppI, color='darkmagenta', linestyle='--', label=f'Period = {hppI:.5f} days')
                ax[0,1].set_ylabel("Power")
                ax[0,1].set_xlim(clpI.Pbeg,clpI.Pend)
                ax[0,1].legend()
                ax[0,1].set_xticklabels([])

                ax[1,0].plot(periodo1, t1, 'kp-', lw=1.2)
                #ax[1,0].plot(pdmperiodsv, minimav, 'rx', markersize=10, label='Detected Minima')
                ax[1,0].plot(equis, lequis, color='black', linestyle='--')
                ax[1,0].axvline(periodpdmV, color='darkmagenta', linestyle='--', label=f'Period = {periodpdmV:.5f} days')
                ax[1,0].set_xlabel("Period")
                ax[1,0].set_ylabel(r"$\Theta$")
                ax[1,0].set_xlim(clp.Pbeg,clp.Pend) 
                ax[1,0].legend()

                ax[1,1].plot(periodo2, t2, 'kp-', lw=1.2)
                #ax[1,1].plot(pdmperiodsi, minimai, 'rx', markersize=10, label='Detected Minima')
                ax[1,1].plot(equisI, lequisI, color='black', linestyle='--')
                ax[1,1].axvline(periodpdmI, color='darkmagenta', linestyle='--', label=f'Period = {periodpdmI:.5f} days')
                ax[1,1].set_xlabel("Period")
                ax[1,1].set_ylabel(r"$\Theta$")
                ax[1,1].set_xlim(clpI.Pbeg,clpI.Pend)
                ax[1,1].legend()

                plt.subplots_adjust(hspace=0)
                figname1 = 'GLSPDM.png'
                figrute1 = os.path.join(route, figname1)
                #figname2 = 'GLSPDM.pdf'
                #figrute2 = os.path.join(route, figname2)
                plt.savefig(figrute1)
                #plt.savefig(figrute2)
                plt.close()
                
                plot_time = print_timer("Generación de gráficos", plot_start)
                
                end_time = t.time()  # End timing
                elapsed_time = (end_time - init_time) / 60  # Convert to minutes
                
                # Resumen de tiempos por estrella
                print(f"\n=== RESUMEN DE TIEMPOS ESTRELLA {star_number} ===")
                print(f"Tiempo total de análisis: {elapsed_time:.2f} minutos")
                star_total_seconds = end_time - init_time
                print(f"[TIMER] Carga datos: {((load_time - load_start) / star_total_seconds * 100):.1f}%")
                print(f"[TIMER] GLS: {((gls_total_time - gls_start) / star_total_seconds * 100):.1f}%")
                print(f"[TIMER] PDM: {((pdm_total_time - pdm_start) / star_total_seconds * 100):.1f}%")
                print(f"[TIMER] Picos: {((peaks_time - peaks_start) / star_total_seconds * 100):.1f}%")
                print(f"[TIMER] Gráficos: {((plot_time - plot_start) / star_total_seconds * 100):.1f}%")
                print(f"=====================================\n")
                
                print(f'Estrella {star_number} completada exitosamente')
                sys.stdout.flush()
                
            except Exception as e:
                end_time = t.time()
                elapsed_time = (end_time - init_time) / 60
                print(f'Error procesando estrella {star_number}: {str(e)}')
                print(f'Tiempo transcurrido antes del error: {elapsed_time:.2f} minutos')
                sys.stdout.flush()
        else:
            print(f'Archivos faltantes para estrella {star_number}: V={fileV}, I={fileI}')
            sys.stdout.flush()
    
    fin_total = t.time()
    tiempo_total = (fin_total - inicio_total) / 60
    print("-" * 50)
    print(f"Procesamiento completado para {len(stars)} estrellas")
    print(f"Tiempo total: {tiempo_total:.2f} minutos")
    print("-" * 50)
    sys.stdout.flush()

if __name__ == "__main__":
    main()
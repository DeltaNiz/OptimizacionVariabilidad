from __future__ import print_function, division
import numpy as np
from PyAstronomy.pyTiming import pyPeriod
import warnings
import gc

def verificar_par_archivos(ruta_archivo_V, ruta_archivo_I, Pbeg=0.01, Pend=3, fap_threshold=0.001):
    try:
        # Suprimir warnings de PyAstronomy que pueden causar problemas en el stream
        with warnings.catch_warnings():
            warnings.filterwarnings('ignore', category=RuntimeWarning)
            warnings.filterwarnings('ignore', category=UserWarning)
            
            # Cargar datos
            dataV = np.loadtxt(ruta_archivo_V)
            dataI = np.loadtxt(ruta_archivo_I)
            
            time = dataV[:, 0]
            flux = dataV[:, 1]
            timeI = dataI[:, 0]
            fluxI = dataI[:, 1]
            
            # Validar datos antes del análisis GLS
            if len(time) < 10 or len(timeI) < 10:
                raise ValueError("Datos insuficientes para análisis GLS (mínimo 10 puntos)")
            
            if np.any(np.isnan(flux)) or np.any(np.isnan(fluxI)):
                raise ValueError("Datos contienen NaN")
            
            if np.any(np.isinf(flux)) or np.any(np.isinf(fluxI)):
                raise ValueError("Datos contienen valores infinitos")
            
            # Análisis GLS para V
            clp = pyPeriod.Gls((time, flux), norm="ZK", Pbeg=Pbeg, Pend=Pend)
            
            # Análisis GLS para I
            clpI = pyPeriod.Gls((timeI, fluxI), norm="ZK", Pbeg=Pbeg, Pend=Pend)
            
            # Calcular niveles FAP
            fapLevels = np.array([0.1, 0.05, 0.01, 0.001])
            plevels = clp.powerLevel(fapLevels)
            plevelsI = clpI.powerLevel(fapLevels)
            
            # Obtener máximos
            ifmax = np.argmax(clp.power)
            pmax = clp.power[ifmax]
            
            ifmaxI = np.argmax(clpI.power)
            pmaxI = clpI.power[ifmaxI]
            
            # Verificar filtro FAP
            idx_fap = np.where(fapLevels == fap_threshold)[0][0]
            filtro_fap = (pmax > plevels[idx_fap]) and (pmaxI > plevelsI[idx_fap])
            
            # Verificar filtro de amplitud
            filtro_amplitud = (clp.hpstat["amp"] * 2 > clp.rms) and (clpI.hpstat["amp"] * 2 > clpI.rms)
            
            # Resultado final
            pasa_filtros = filtro_fap and filtro_amplitud
            
            # Información del análisis
            info = {
                'pasa_FAP': filtro_fap,
                'pasa_amplitud': filtro_amplitud,
                'pasa_todos': pasa_filtros,
                'rms_V': clp.rms,
                'amplitude_V': clp.hpstat["amp"],
                'rms_I': clpI.rms,
                'amplitude_I': clpI.hpstat["amp"],
                'power_max_V': pmax,
                'power_max_I': pmaxI,
                'fap_level_V': plevels[idx_fap],
                'fap_level_I': plevelsI[idx_fap]
            }
            
            # Liberar memoria de objetos GLS
            del clp, clpI, dataV, dataI
            gc.collect()
            
            return pasa_filtros, info
        
    except Exception as e:
        # En caso de error, devolver False y la información del error
        info = {
            'error': str(e),
            'pasa_todos': False
        }
        return False, info


if __name__ == "__main__":
    # Este script está diseñado para ser importado y usado como módulo.
    # La función principal es verificar_par_archivos()
    # 
    # Para uso standalone, ejecutar copiar.py con --aplicar_fap
    # o usar Analisis.py que orquesta todo el pipeline.
    print("=" * 80)
    print("descarteFAP.py - Módulo de verificación FAP")
    print("=" * 80)
    print()
    print("Este módulo proporciona la función verificar_par_archivos() para")
    print("filtrar curvas de luz basándose en FAP y amplitud.")
    print()
    print("Uso recomendado:")
    print("  - Desde copiar.py: python copiar.py --aplicar_fap ...")
    print("  - Desde Analisis.py: Usar la interfaz gráfica")
    print()
    print("Ejemplo de uso programático:")
    print("  from descarteFAP import verificar_par_archivos")
    print("  pasa, info = verificar_par_archivos('star1_V', 'star1_I')")
    print("  if pasa:")
    print("      print('Estrella aprobada')")
    print("=" * 80)

from __future__ import print_function, division
import numpy as np
import matplotlib.pylab as plt
from PyAstronomy.pyTiming import pyPeriod
from PyAstronomy.pyTiming import pyPDM
import scipy.interpolate as sciinter
import scipy.optimize as sciopti
import os
import pandas as pd
import time as t

data = 'C:/Users/tomas/OneDrive/Escritorio/xd/U/2025-1/Formulacion de Proyecto de Titulacion/data/analisis_20250722_180246'
stars = [d for d in os.listdir(data) if os.path.isdir(os.path.join(data, d))]

for star in stars:
    route = os.path.join(data, star)
    files = os.listdir(route)
    star_number = int(star[4:]) 

    fileV = next((f for f in files if f.endswith('V')), None)
    fileI = next((f for f in files if f.endswith('i')), None)

    

    if fileV and fileI:

        print(80*'-')
        print(f'processing star {star_number}: {fileV}, {fileI}')
        init_time = t.time()
        print(80*'-')

        dataV= np.loadtxt(os.path.join(route, fileV))
        dataI= np.loadtxt(os.path.join(route, fileI))

        dataredV=dataV[::2]
        dataredI=dataI[::2]

        time = dataV[:,0]
        flux = dataV[:,1]

        timeI = dataI[:,0]
        fluxI = dataI[:,1]

        #------------------------------GLS-----------------------------------
        Pend = 3
        clp = pyPeriod.Gls((time, flux), norm="ZK", Pbeg=0.01, Pend=Pend)
        #clp.info()

        fapLevels = np.array([0.1, 0.05, 0.01, 0.001])
        plevels = clp.powerLevel(fapLevels)

        ifmax = np.argmax(clp.power)

        pmax = clp.power[ifmax]
        fmax = clp.freq[ifmax]

        hpp = 1./fmax

        freqstep=clp.fstep
        periodos= (1./clp.freq)
        power=clp.power

        clpI = pyPeriod.Gls((timeI, fluxI), norm="ZK", Pbeg=0.01, Pend=Pend)


        fapLevelsI = np.array([0.1, 0.05, 0.01, 0.001])
        plevelsI = clpI.powerLevel(fapLevels)
        ifmaxI = np.argmax(clpI.power)

        pmaxI = clpI.power[ifmaxI]
        fmaxI = clpI.freq[ifmaxI]

        hppI = 1./fmaxI

        freqstepI=clpI.fstep
        periodosI= (1./clpI.freq)
        powerI=clpI.power

        #-----------------------------PDM--------------------------------------
        S = pyPDM.Scanner(minVal=(1./clp.Pend), maxVal=(1./clp.Pbeg), dVal=freqstep, mode="frequency")
        P = pyPDM.PyPDM(time, flux)

        f1, t1 = P.pdmEquiBinCover(7, 3, S)
        thetmin1=np.min(t1)
        periodpdmV = (1/f1)[np.argmin(t1)]

        equis= np.linspace(0, 10.0, 2)
        lequis=np.array([thetmin1 for i in range(len(equis))])

        periodo1 = (1/f1)


        SI = pyPDM.Scanner(minVal=(1./clpI.Pend), maxVal=(1./clpI.Pbeg), dVal=freqstepI, mode="frequency")
        PI = pyPDM.PyPDM(timeI,  fluxI)

        f2, t2 = PI.pdmEquiBinCover(7, 3, SI)
        thetmin2=np.min(t2)
        periodpdmI = (1/f2)[np.argmin(t2)]

        equisI= np.linspace(0, 10.0, 2)
        lequisI=np.array([thetmin2 for i in range(len(equisI))])

        periodo2 = (1/f2)

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

        peakspowerv = clp.power[peaksglsv]
        peakspoweri = clpI.power[peaksglsi]

        minimav = t1[peakspdmv]
        minimai = t2[peakspdmi]

        #Los Peaks del GLS son hpp y hppI
        print(f'Best Peak GLS V: {hpp}')
        print(f'Best Peak GLS I: {hppI}')
        print(f'Best Minima PDM V: {periodpdmV}')
        print(f'Best Minima PDM I: {periodpdmI}')

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
        end_time = t.time()  # End timing
        elapsed_time = (end_time - init_time) / 60  # Convert to minutes
        print(f'Tiempo de analisis de la estrella {star_number}: {elapsed_time:.2f} minutos')
from __future__ import print_function, division
import numpy as np
import matplotlib.pylab as plt
from PyAstronomy.pyTiming import pyPeriod
from PyAstronomy.pyTiming import pyPDM
import scipy.interpolate as sciinter
import scipy.optimize as sciopti
import os
import csv
import sys

sys.stdout = open('log.txt', 'w')

data = 'ngc6397/datarevision' #modificar donde se tengan los datos.
stars = [d for d in os.listdir(data) if os.path.isdir(os.path.join(data, d))]
filas = []

for star in stars:
    route = os.path.join(data, star)
    files = os.listdir(route)
    star_number = int(star[4:]) 

    fileV = next((f for f in files if f.endswith('V')), None)
    fileI = next((f for f in files if f.endswith('I')), None)

    if fileV and fileI:
        #if star_number != 600:
            #continue

        filtrofap = False
        filtroamp = False
        print(f'Estrella {star_number}: {fileV}, {fileI}')
        dataV= np.loadtxt(os.path.join(route, fileV))
        dataI= np.loadtxt(os.path.join(route, fileI))

        time = dataV[:,0]
        flux = dataV[:,1]

        timeI = dataI[:,0]
        fluxI = dataI[:,1]

        #------------------------------GLS-----------------------------------

        clp = pyPeriod.Gls((time, flux), norm="ZK", Pbeg=0.01, Pend=3)
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


        clpI = pyPeriod.Gls((timeI, fluxI), norm="ZK", Pbeg=0.01, Pend=3)
        #clpI.info()

        fapLevelsI = np.array([0.1, 0.05, 0.01, 0.001])
        plevelsI = clpI.powerLevel(fapLevels)
        ifmaxI = np.argmax(clpI.power)

        pmaxI = clpI.power[ifmaxI]
        fmaxI = clpI.freq[ifmaxI]

        hppI = 1./fmaxI

        #FAP

        if pmax > plevels[3] and pmaxI > plevelsI[3]:
            filtrofap = True
            print(f'Pasa FAP')
        else:
            print(f'No pasa FAP del {fapLevels[3]*100}%')
            filtrofap = False

        #-----------------------------Amplitude and RMS--------------------------------------

        if clp.hpstat["amp"]*2 > clp.rms and clpI.hpstat["amp"]*2 > clpI.rms:
            print('Pasa Filtro de Amplitud')
            filtroamp = True
        else:
            print('No pasa filtro de amplitud')
            filtroamp = False

        if filtroamp and filtrofap:
            filas.append([fileV, fileI])


        print(f'RMS V: {clp.rms:.6f}, 2*Amplitude V: {2*clp.hpstat["amp"]:.6f} || RMS I: {clpI.rms:.6f}, 2*Amplitude I: {2*clpI.hpstat["amp"]:.6f}')
        print('-'*80)

sys.stdout.close()
with open('FAPRevision.csv', mode='w', newline='') as csvfile:
    writer = csv.writer(csvfile)
    writer.writerows(filas)


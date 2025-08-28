import numpy as np
import matplotlib.pylab as plt

dataV= np.loadtxt('C:/Users/tomas/OneDrive/Escritorio/xd/U/2025-1/Formulacion de Proyecto de Titulacion/lc_v/0498.561_0358.881V')
dataI= np.loadtxt('C:/Users/tomas/OneDrive/Escritorio/xd/U/2025-1/Formulacion de Proyecto de Titulacion/lc_i/0497.646_0358.680I')

timeVfull = dataV[:,0]
fluxVfull = dataV[:,1]

timeIfull = dataI[:,0]
fluxIfull = dataI[:,1]

#---------------------------------------------------------------------
        
PerStar=0.0389613464230802

LentimeV= len(timeVfull)
FaseV=[]
FaseVmas=[]

for i in range(LentimeV):
    FaseoV = (abs( (timeVfull[i]/PerStar)-0.8) - abs( int ( (timeVfull[i]/PerStar)-0.8) ))
    FaseoVMas = FaseoV+1.0
    FaseV.append(FaseoV)
    FaseVmas.append(FaseoVMas)


LentimeI= len(timeIfull)
FaseI=[]
FaseImas=[]

for i in range(LentimeI):
    FaseoI = (abs( (timeIfull[i]/PerStar)-0.8) - abs( int ( (timeIfull[i]/PerStar)-0.8) ))
    FaseoIMas = FaseoI+1.0
    FaseI.append(FaseoI)
    FaseImas.append(FaseoIMas)


#---------------------------------------------------------------------
plt.subplot(2,1,1)

plt.plot(FaseV, fluxVfull, 'g.')
plt.plot(FaseVmas, fluxVfull, 'g.')
plt.xlim(-0.02,2.02)
plt.title('Star 8| $P=$%.6f' %PerStar)
plt.ylim(plt.ylim()[::-1])
plt.xticks(fontsize=2)
plt.ylabel('$V$',fontsize=12)

#---------------------------------------------------------------------
plt.subplot(2,1,2)

plt.plot(FaseI, fluxIfull, 'r.')
plt.plot(FaseImas, fluxIfull, 'r.')
plt.xlim(-0.02,2.02)
plt.ylim(plt.ylim()[::-1])
plt.ylabel('$I$', fontsize=12)
plt.xlabel('$\phi$', fontsize=12)

plt.subplots_adjust(hspace=0)
#plt.savefig('faseos/S8-V2.pdf')
plt.show()

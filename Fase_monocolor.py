import numpy as np
import matplotlib.pylab as plt

dataV= np.loadtxt('ngc6397/data4/star4/V18V')
dataI= np.loadtxt('ngc6397/data4/star4/V18I') #loadtxt

timeVfull = dataV[:,0]
fluxVfull = dataV[:,1]

timeIfull = dataI[:,0]
fluxIfull = dataI[:,1]

#---------------------------------------------------------------------
        
PerStar=0.252390807220625

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
plt.savefig('faseos/S8-V2.pdf')
plt.show()

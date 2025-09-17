import numpy as np
import matplotlib.pyplot as plt
import os

class FaseMonocolor:
    def __init__(self):
        self.timeVfull = []
        self.timeIfull = []
        self.fluxVfull = []
        self.fluxIfull = []
        self.FaseV = []
        self.FaseVmas = []
        self.FaseI = []
        self.FaseImas = []

    def cargar_datos(self, star_data, PerStar):
        data_folder, star_name = star_data

        # El directorio específico de la estrella está dentro del directorio principal
        route = os.path.join(data_folder, star_name)
        
        if not os.path.exists(route):
            return {
                'star': star_name,
                'status': 'error',
                'message': f'Directorio no encontrado: {route}',
                'time': 0
            }
        
        files = os.listdir(route)

        fileV = next((f for f in files if f.endswith('V')), None)
        fileI = next((f for f in files if f.endswith('i')), None)

        if not (fileV and fileI):
            return {
                'star': star_name,
                'status': 'error',
                'message': f'Archivos faltantes: V={fileV}, I={fileI}',
                'time': 0
            }
        
        dataV= np.loadtxt(os.path.join(route, fileV))
        dataI= np.loadtxt(os.path.join(route, fileI))

        self.timeVfull = dataV[:,0]
        self.fluxVfull = dataV[:,1]

        self.timeIfull = dataI[:,0]
        self.fluxIfull = dataI[:,1]

        #---------------------------------------------------------------------

        LentimeV= len(self.timeVfull)

        for i in range(LentimeV):
            FaseoV = (abs( (self.timeVfull[i]/PerStar)-0.8) - abs( int ( (self.timeVfull[i]/PerStar)-0.8) ))
            FaseoVMas = FaseoV+1.0
            self.FaseV.append(FaseoV)
            self.FaseVmas.append(FaseoVMas)

        LentimeI= len(self.timeIfull)

        for i in range(LentimeI):
            FaseoI = (abs( (self.timeIfull[i]/PerStar)-0.8) - abs( int ( (self.timeIfull[i]/PerStar)-0.8) ))
            FaseoIMas = FaseoI+1.0
            self.FaseI.append(FaseoI)
            self.FaseImas.append(FaseoIMas)

        self.generar_plot(route, star_name, PerStar)
        
        # Retornar éxito
        return {
            'star': star_name,
            'status': 'success',
            'message': 'Curva de luz generada exitosamente',
            'time': len(self.timeVfull) + len(self.timeIfull)
        }

    def generar_plot(self, route, star_name, PerStar):
        try:
            # Crear una nueva figura explícitamente
            fig = plt.figure(figsize=(12, 8))
            
            plt.subplot(2,1,1)
            plt.plot(self.FaseV, self.fluxVfull, 'g.')
            plt.plot(self.FaseVmas, self.fluxVfull, 'g.')
            plt.xlim(-0.02,2.02)
            plt.title(f'{star_name} | $P=$%.6f' % PerStar)
            plt.ylim(plt.ylim()[::-1])
            plt.xticks(fontsize=2)
            plt.ylabel('$V$',fontsize=12)

            #---------------------------------------------------------------------
            plt.subplot(2,1,2)
            plt.plot(self.FaseI, self.fluxIfull, 'r.')
            plt.plot(self.FaseImas, self.fluxIfull, 'r.')
            plt.xlim(-0.02,2.02)
            plt.ylim(plt.ylim()[::-1])
            plt.ylabel('$I$', fontsize=12)
            plt.xlabel(r'$\phi$', fontsize=12)
            plt.subplots_adjust(hspace=0)
            plot_path = os.path.join(route, f'light_curve_{star_name}.png')
            plt.savefig(plot_path, bbox_inches='tight')
            plt.close(fig)  # Cerrar la figura específica
            
        except Exception as e:
            print(f"ERROR en generar_plot: {e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    pass
import os
import pandas as pd
import shutil

ruta_base = 'C:/Users/tomas/OneDrive/Escritorio/xd/U/2025-1/Formulacion de Proyecto de Titulacion'
carpeta1 = os.path.join(ruta_base, 'lc_i')
carpeta2 = os.path.join(ruta_base, 'lc_v')
data = os.path.join(ruta_base, 'data')

df = pd.read_csv('magnitudCMD1516.csv', skiprows=0, header=None)
#print(df)


for i, row  in df.iterrows():
    archivoV = row[0]
    archivoI = row[1]

    stars = os.path.join(data, f'star{i+1}')
    os.makedirs(stars, exist_ok=True)

    src1 = os.path.join(carpeta1, archivoI)
    dest1 = os.path.join(stars, archivoI)

    if os.path.exists(src1):
        shutil.copy(src1, dest1)
    else:
        print(f"archivo no encontrado {src1}, carpeta: {carpeta1}, destino{dest1}, {stars}")

    src2 = os.path.join(carpeta2, archivoV)
    dest2 = os.path.join(stars, archivoV)

    if os.path.exists(src2):
        shutil.copy(src2, dest2)
    else:
        print(f"archivo no encontrado {src2}, carpeta: {carpeta2}, destino{dest1}, {stars}")
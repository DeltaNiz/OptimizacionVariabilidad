import os
import pandas as pd
import shutil

carpeta1 = 'ngc6397/lci'
carpeta2 = 'ngc6397/lcV'
data = 'ngc6397/data'

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
        shutil.move(src1, dest1)
    else:
        print(f"archivo no encontrado {src1}, carpeta: {carpeta1}, destino{dest1}, {stars}")

    src2 = os.path.join(carpeta2, archivoV)
    dest2 = os.path.join(stars, archivoV)

    if os.path.exists(src2):
        shutil.move(src2, dest2)
    else:
        print(f"archivo no encontrado {src2}, carpeta: {carpeta2}, destino{dest1}, {stars}")
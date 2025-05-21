import pandas as pd

df = pd.read_csv('magnitudCMD.csv', header=None)

masked = df[(df[2] >= 15) & (df[2] <= 16)]
print(masked)

masked.to_csv('magnitudCMD1516.csv', index=False)
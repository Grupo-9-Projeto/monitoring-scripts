import pandas as pd
import csv

df = pd.read_csv('dados_maquina.csv', sep=';')
df.columns = df.columns.str.strip()
df['Quando foi Coletado'] = pd.to_datetime(df['Quando foi Coletado'])
ultima = df['Quando foi Coletado'].max()
uma_hora =  df[df['Quando foi Coletado'] >= (ultima - pd.Timedelta(hours=1))]
um_dia =  df[df['Quando foi Coletado'] >= (ultima - pd.Timedelta(hours=24))]



media_ram_1h = uma_hora['ram(%)'].mean()
print(f"Média RAM última hora: {media_ram_1h:.2f}%")

media_cpu_1h = uma_hora['cpu total(%)'].mean()
print(f"Média CPU última hora: {media_cpu_1h:.2f}%")

pico_cpu_1h = uma_hora['cpu total(%)'].max()
print(f"Pico CPU última hora: {pico_cpu_1h:.2f}%")


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


max = 0
cpu_maior = ""
for i in df.columns:
    if i.lower().startswith('cpu') and 'total' not in i.lower():
        media_atual = uma_hora[i].mean()

        if media_atual > max:
            max = media_atual
            cpu_maior = i



print(f"CPU COM A MAIOR MÉDIA NA ULTIMA HORA: {cpu_maior} MÉDIA: {max}%")


download_hora = uma_hora['Rede recebida(Mbps)'].mean()
upload_hora = uma_hora['Rede enviada(Mbps)'].mean()
# perda_hora = uma_hora['perda pacotes'].mean()

print(f"Download médio (1h): {download_hora:.2f} Mbps")
print(f"Upload médio (1h): {upload_hora:.2f} Mbps")
# print(f"Perda média de pacotes (1h): {perda_hora:.2f}%")


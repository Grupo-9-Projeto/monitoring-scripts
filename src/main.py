import psutil
import csv
from datetime import datetime
import time;
from coleta import relatorio
import os

# envio para o csv +  loop 
if not os.path.exists('dados_maquina.csv'):
    with open('dados_maquina.csv', 'w', newline='') as csvfile:
        qtd = psutil.cpu_count(logical=True)
        cpus = [f"cpu{i+1}(%)" for i in range(qtd)]
        csv.writer(csvfile, delimiter=',').writerow(["Nome"] + ["cpu total(%)"] + cpus + [ "ram(%)", "disco(%)", "Quando foi Coletado", "Rede recebida(Mbps)", "Rede enviada(Mbps)", 'Frequencia de uso da CPU(MHz)', "Endereco MAC"])


print("iniciando")

try:
    while(True):
        coleta = relatorio()
        with open('dados_maquina.csv', 'a', newline='') as csvfile:

            csv.writer(csvfile, delimiter=',').writerow(["João"] + [coleta[0]] + coleta[1] + [coleta[2]] + [coleta[3]] + [coleta[4]] + [coleta[5]] + [coleta[6]] + [coleta[7]] + [coleta[8]])
            cpu_nucleos = coleta[1]
            cpus_individuais = " | ".join([f"cpu {i+1}: {cpu_nucleos[i]}%" for i in range(len(cpu_nucleos))])
            print(f"Nome: João | CPU TOTAL: {coleta[0]}% | {cpus_individuais} | RAM: {coleta[2]}% | Disco: {coleta[3]}% | Quando foi: {coleta[4]} | Rede recebida: {coleta[5]} Mbps | Rede enviada: {coleta[6]} Mbps | Frequencia: {coleta[7]} MHz | MAC: {coleta[8]}")

        time.sleep(5)
except  KeyboardInterrupt:
    print("encerrado")
   

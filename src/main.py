import psutil
import csv
from datetime import datetime
import time;
from coleta import relatorio

# envio para o csv +  loop 

with open('dados_maquina.csv', 'w', newline='') as csvfile:

    csv.writer(csvfile, delimiter=',').writerow(["cpu total","cpus_nucleos", "ram", "disco", "Quando foi Coletado", "Rede recebida", "Rede enviada", 'Frequencia de uso da CPU'])

print("iniciando")

while(True):
    coleta = relatorio()
    with open('dados_maquina.csv', 'a', newline='') as csvfile:

        csv.writer(csvfile, delimiter=',').writerow(relatorio())
        cpu_nucleos = coleta[1]
        cpus_individuais = " | ".join([f"cpu {i+1}: {cpu_nucleos[i]}%" for i in range(len(cpu_nucleos))])
        print(f"CPU TOTAL: {coleta[0]}% | {cpus_individuais} | RAM: {coleta[2]}% | Disco: {coleta[3]}% | Quando foi: {coleta[4]} | Rede recebida: {coleta[5]} | Rede enviada: {coleta[6]} | Frequencia: {coleta[7]}")

    time.sleep(5)
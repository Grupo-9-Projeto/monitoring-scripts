import psutil
import csv
from datetime import datetime
import time;
from coleta import relatorio

# envio para o csv +  loop 

with open('dados_maquina.csv', 'w', newline='') as csvfile:
    qtd = psutil.cpu_count(logical=True)
    cpus = [f"cpu{i+1}" for i in range(qtd)]
    csv.writer(csvfile, delimiter=',').writerow(["cpu total"] + cpus + [ "ram", "disco", "Quando foi Coletado", "Rede recebida", "Rede enviada", 'Frequencia de uso da CPU'])

print("iniciando")

try:
    while(True):
        coleta = relatorio()
        with open('dados_maquina.csv', 'a', newline='') as csvfile:

            csv.writer(csvfile, delimiter=',').writerow([coleta[0]] + coleta[1] + [coleta[2]] + [coleta[3]] + [coleta[4]] + [coleta[5]] + [coleta[6]] + [coleta[7]])
            cpu_nucleos = coleta[1]
            cpus_individuais = " | ".join([f"cpu {i+1}: {cpu_nucleos[i]}%" for i in range(len(cpu_nucleos))])
            print(f"CPU TOTAL: {coleta[0]}% | {cpus_individuais} | RAM: {coleta[2]}% | Disco: {coleta[3]}% | Quando foi: {coleta[4]} | Rede recebida: {coleta[5]} Mbps | Rede enviada: {coleta[6]} Mbps | Frequencia: {coleta[7]} MHz")

        time.sleep(5)
except  KeyboardInterrupt:
    print("encerrado")
   

import psutil
import csv
from datetime import datetime
import time;
from coleta import relatorio

# envio para o csv +  loop 

with open('dados_maquina.csv', 'w', newline='') as csvfile:

    csv.writer(csvfile, delimiter=',').writerow(["cpu", "ram", "disco", "Quando foi Coletado", "Rede recebida", "Rede enviada", 'Frequencia de uso da CPU'])

while(True):
    with open('dados_maquina.csv', 'a', newline='') as csvfile:

        csv.writer(csvfile, delimiter=',').writerow(relatorio())

    time.sleep(5)
import csv
from datetime import datetime
import os
import time
from coleta import relatorio
import psutil

# envio para o csv +  loop 
if not os.path.exists('dados_maquina.csv'):
    with open('dados_maquina.csv', 'w', newline='') as csvfile:
        qtd = psutil.cpu_count(logical=True)
        cpus = [f"cpu{i+1}(%)" for i in range(qtd)]
        csv.writer(csvfile, delimiter=';').writerow(["cpu total(%)"] + cpus + [ "ram(%)", "disco(%)", "Quando foi Coletado", "Rede recebida(Mbps)", "Rede enviada(Mbps)", 'Frequencia de uso da CPU(MHz)', "Endereco MAC", "Tempo Ligado", "Pacotes Descartados", "Pacotes descartados pelo sistema", "Tentativa flahas de envio", "pacotes que chegaram Corrompidos"])


print("iniciando")


inicio_programa = datetime.now()

try:
    while(True):
        coleta = relatorio()
        with open('dados_maquina.csv', 'a', newline='') as csvfile:

            csv.writer(csvfile, delimiter=';').writerow(
    [coleta[0]]
    + coleta[1]
    + [coleta[2]]
    + [coleta[3]]
    + [coleta[4]]
    + [coleta[5]]
    + [coleta[6]]
    + [coleta[7]]
    + [coleta[8]]
    + [coleta[10]]
    + [coleta[11]]
    + [coleta[12]]
    + [coleta[13]]
    + [coleta[14]]
)
            cpu_nucleos = coleta[1]

            cpus_individuais = " | ".join([f"cpu {i+1}: {cpu_nucleos[i]}%" for i in range(len(cpu_nucleos))])

            print(f"CPU TOTAL: {coleta[0]}% | {cpus_individuais} | RAM: {coleta[2]}% | Disco: {coleta[3]}% | Quando foi: {coleta[4]} | Rede recebida: {coleta[5]} Mbps | Rede enviada: {coleta[6]} Mbps | Frequencia: {coleta[7]} MHz | MAC: {coleta[8]}")

        time.sleep(3)
except KeyboardInterrupt:

    fim_programa = datetime.now()

    tempo_ligado = fim_programa - inicio_programa

    tempo_formatado = str(tempo_ligado).split('.')[0]

    qtd_cpus = psutil.cpu_count(logical=True)  

    
    total_colunas = 1 + qtd_cpus + 8

    
    linha_final = [""] + [""] * (total_colunas-2) + [tempo_formatado]

    with open('dados_maquina.csv', 'a', newline='') as csvfile:
        csv.writer(csvfile, delimiter=';').writerow(linha_final)

    print("encerrado")

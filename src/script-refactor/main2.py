import csv
from datetime import datetime
import os
import time
from coleta2 import relatorio
import psutil

# envio para o csv +  loop 
if not os.path.exists('dados_maquina.csv'):
    with open('dados_maquina.csv', 'w', newline='') as csvfile:
        qtd = psutil.cpu_count(logical=True)
        cpus = [f"cpu{i+1}(%)" for i in range(qtd)]
        csv.writer(csvfile, delimiter=';').writerow(["cpu total(%)", "cpu nucleos(%)", "ram(%)", "disco(%)", "Quando foi Coletado", "Rede recebida(Mbps)", "Rede enviada(Mbps)", "Endereco MAC",  "Pacotes Descartados entrada", "Pacotes descartados saida", "erros entrada", "erros saida", "perda pacotes"])


print("iniciando")


# inicio_programa = datetime.now()

try:
    while(True):
        coleta = relatorio()
        with open('dados_maquina.csv', 'a', newline='') as csvfile:

            csv.writer(csvfile, delimiter=';').writerow(
    # [coleta[0]]
    # , coleta[1]
    # , [coleta[2]]
    # , [coleta[3]]
    # , [coleta[4]]
    # , [coleta[5]]
    # , [coleta[6]]
    # , [coleta[7]]
    # , [coleta[8]]
    # , [coleta[9]]
    # , [coleta[10]]
    # , [coleta[11]]
    # + [coleta[12]]
    relatorio()
)
            cpu_nucleos = coleta[1]

            # cpus_individuais = " | ".join([f"cpu {i+1}: {cpu_nucleos[i]}%" for i in range(len(cpu_nucleos))])

            print(f"CPU TOTAL: {coleta[0]}% | {coleta[1]} | RAM: {coleta[2]}% | Disco: {coleta[3]}% | Quando foi: {coleta[4]} | Rede recebida: {coleta[5]} Mbps | Rede enviada: {coleta[6]} Mbps | MAC: {coleta[7]} | Descartados entrada: {coleta[8]} | Descartados saida: {coleta[9]} | Erros ent: {coleta[10]} | Erros sai: {coleta[11]} | Perda Ping: {coleta[12]}")

        time.sleep(3)
except KeyboardInterrupt:

    # fim_programa = datetime.now()

    # tempo_ligado = fim_programa - inicio_programa

    # tempo_formatado = str(tempo_ligado).split('.')[0]

    # qtd_cpus = psutil.cpu_count(logical=True)  

    
    # total_colunas = 1 + qtd_cpus + 13

    
    # linha_final = [""] * (total_colunas-1) + [tempo_formatado]

    # with open('dados_maquina.csv', 'a', newline='') as csvfile:
    #     csv.writer(csvfile, delimiter=';').writerow(relatorio())

    print("encerrado")

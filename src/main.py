import csv
from datetime import datetime
import os
import time
from coleta import relatorio
import psutil


PASTA_COLETAS = "coletas_hardware"
if not os.path.exists(PASTA_COLETAS):
    os.makedirs(PASTA_COLETAS)

print("Iniciando monitoramento...")

try:
    # Descomentar o while para rodar continuamente
    while(True):
        coleta = relatorio()
        timestamp = int(time.time())
        nome_arquivo = f"{PASTA_COLETAS}/dados_{timestamp}.csv"

        with open(nome_arquivo, 'w', newline='') as csvfile:
            writer = csv.writer(csvfile, delimiter=';')

            qtd_cpus = psutil.cpu_count(logical=True)
            headers_cpus = [f"cpu{i+1}(%)" for i in range(qtd_cpus)]

            headers = [
                "cpu total(%)", "ram(%)", "disco(%)", "Quando foi Coletado", 
                "Rede recebida(Mbps)", "Rede enviada(Mbps)", "Frequencia de uso da CPU(MHz)", 
                "Endereco MAC", "Pacotes Descartados entrada", "Pacotes descartados saida", 
                "erros entrada", "erros saida", "perda pacotes"
            ] + headers_cpus

            writer.writerow(headers)

            cpu_nucleos = coleta[1]

            dados_linha = [
                coleta[0],  # cpu total
                coleta[2],  # ram
                coleta[3],  # disco
                coleta[4],  # Quando foi coletado
                coleta[5],  # Rede recebida
                coleta[6],  # Rede enviada
                coleta[7],  # Frequencia
                coleta[8],  # MAC
                coleta[9],  # Descartes entrada
                coleta[10], # Descartes saida
                coleta[11], # Erros entrada
                coleta[12], # Erros saida
                coleta[13]  # Perda pacotes
            ] + cpu_nucleos

            writer.writerow(dados_linha)

        cpus_individuais = " | ".join([f"cpu {i+1}: {cpu_nucleos[i]}%" for i in range(len(cpu_nucleos))])
        print(f"[{coleta[4]}] Salvo: {nome_arquivo} | CPU TOTAL: {coleta[0]}% | RAM: {coleta[2]}% | MAC: {coleta[8]}")

        time.sleep(3)

except KeyboardInterrupt:
    print("Monitoramento encerrado.")
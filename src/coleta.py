
# Importações de Biblioteca
import psutil
import csv
from datetime import datetime
import time;

#Função que coleta os dados do hardware
def relatorio():

    # uso da cpu
    cpu = psutil.cpu_percent(interval=2);

    #uso memória ram
    ram = psutil.virtual_memory().percent;

    # Uso do disco
    disco = psutil.disk_usage('C:\\').percent;

    # primeiros dados da rede coletado
    rede_inicio = psutil.net_io_counters()

    # ultimo dado da rede a ser coletado
    rede_fim = psutil.net_io_counters()

    # data hora e segundos da coleta de dados
    data = datetime.now()

    # frquencia de uso cpu
    freq_uso_cpu= psutil.cpu_freq() 


    # converção de dados da rede
    bytes_enviados = rede_fim.bytes_sent - rede_inicio.bytes_sent
    bytes_recebidos = rede_fim.bytes_recv - rede_inicio.bytes_recv

    mbps_upload = round((bytes_enviados / 1024 * 1024),2)
    mbps_download = round((bytes_recebidos / 1024 * 1024), 2)

  

    return [cpu, ram, disco, data, mbps_download, mbps_upload, freq_uso_cpu]


# envio para o csv +  loop 

with open('dados_maquina.csv', 'w', newline='') as csvfile:

    csv.writer(csvfile, delimiter=',').writerow(["cpu", "ram", "disco", "Quando foi Coletado", "Rede recebida", "Rede enviada", 'Frequencia de uso da CPU'])

while(True):
    with open('dados_maquina.csv', 'a', newline='') as csvfile:

        csv.writer(csvfile, delimiter=',').writerow(relatorio())

    time.sleep(5)




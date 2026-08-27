
# Importações de Biblioteca
import psutil
from getmac import get_mac_address
import csv
from datetime import datetime
import time;
import subprocess
import re;

soma_cpu = 0;
qtd_coleta = 0;

def perda_pacotes():
    resultado = subprocess.run(
        ["ping", "-n", "4", "8.8.8.8"],
        capture_output=True,
        text=True
    )

    saida = resultado.stdout

    enviados = 4
    recebidos = len(re.findall(r"TTL=", saida, re.IGNORECASE))

    perda = ((enviados - recebidos) / enviados) * 100

    return round(perda, 2)


#Função que coleta os dados do hardware
def relatorio():

     # primeiros dados da rede coletado
    rede_inicio = psutil.net_io_counters()

    # uso da cpu
    cpu = psutil.cpu_percent(interval=2);

    cpu_nucleos = psutil.cpu_percent(interval=None, percpu=True)
#     cpu_nucleos = " ; ".join([f"{v}%" for v in cpu_nucleos])

    #uso memória ram
    ram = round(psutil.virtual_memory().percent, 2);

    # Uso do disco
    disco = psutil.disk_usage('/').percent;

    #endereço mac da máquina
    mac = get_mac_address()

    # ultimo dado da rede a ser coletado
    rede_fim = psutil.net_io_counters()

    # data hora e segundos da coleta de dados
    data = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # frquencia de uso cpu
    # freq_uso_cpu= round(psutil.cpu_freq().current, 2) 


    # converção de dados da rede
    bytes_enviados = rede_fim.bytes_sent - rede_inicio.bytes_sent
    bytes_recebidos = rede_fim.bytes_recv - rede_inicio.bytes_recv

    mbps_upload = round(((bytes_enviados * 8 / 2) / (1024 * 1024)),2)
    mbps_download = round(((bytes_recebidos * 8 / 2) / (1024 * 1024)), 2)

    #Perda de Pacotes 

    status_rede = psutil.net_io_counters();
    descartados_sistema = status_rede.dropin;
    tentativa_envio = status_rede.dropout;
    corrompidos = status_rede.errin
    dados_forcados = status_rede.errout;
    perda = perda_pacotes()





  

    return [cpu, cpu_nucleos, ram, disco, data, mbps_download, mbps_upload, mac, descartados_sistema, tentativa_envio, corrompidos, dados_forcados, perda];








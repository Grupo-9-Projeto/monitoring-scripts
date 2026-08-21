
# Importações de Biblioteca
import psutil
from getmac import get_mac_address
import csv
from datetime import datetime
import time;


#Função que coleta os dados do hardware
def relatorio():

     # primeiros dados da rede coletado
    rede_inicio = psutil.net_io_counters()

    # uso da cpu
    cpu = psutil.cpu_percent(interval=2);

    cpu_nucleos = psutil.cpu_percent(interval=None, percpu=True)

    #uso memória ram
    ram = psutil.virtual_memory().percent;

    # Uso do disco
    disco = psutil.disk_usage('C:\\').percent;

    #endereço mac da máquina
    mac = get_mac_address()

    # ultimo dado da rede a ser coletado
    rede_fim = psutil.net_io_counters()

    # data hora e segundos da coleta de dados
    data = datetime.now()

    # frquencia de uso cpu
    freq_uso_cpu= round(psutil.cpu_freq().current, 2) 


    # converção de dados da rede
    bytes_enviados = rede_fim.bytes_sent - rede_inicio.bytes_sent
    bytes_recebidos = rede_fim.bytes_recv - rede_inicio.bytes_recv

    mbps_upload = round(((bytes_enviados * 8 / 2) / (1024 * 1024)),2)
    mbps_download = round(((bytes_recebidos * 8 / 2) / (1024 * 1024)), 2)

  

    return [cpu, cpu_nucleos, ram, disco, data, mbps_download, mbps_upload, freq_uso_cpu, mac]







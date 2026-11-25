
# Importações de Biblioteca
import psutil
from getmac import get_mac_address
import csv
from datetime import datetime
import time;
import subprocess
import re;
import platform

soma_cpu = 0;
qtd_coleta = 0;

def perda_pacotes():
    parametro = "-n" if platform.system().lower() == "windows" else "-c"
    resultado = subprocess.run(
        ["ping", parametro, "4", "8.8.8.8"],
        capture_output=True,
        text=True
    )

    saida = resultado.stdout

    enviados = 4
    recebidos = len(re.findall(r"ttl=", saida, re.IGNORECASE))

    perda = ((enviados - recebidos) / enviados) * 100

    return round(perda, 2)


#Função que coleta os dados do hardware
def relatorio(timestamp):

    data = timestamp.strftime("%Y-%m-%d %H:%M:%S")

     # primeiros dados da rede coletado
    rede_inicio = psutil.net_io_counters()

    # uso da cpu
    cpu = psutil.cpu_percent(interval=1);

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
    freq_uso_cpu= round(psutil.cpu_freq().current, 2) 


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





  

    return [cpu, cpu_nucleos, ram, disco, data, mbps_download, mbps_upload, freq_uso_cpu, mac, descartados_sistema, tentativa_envio, corrompidos, dados_forcados, perda, data];


# ======================================================================
# DADO EXTERNO: temperatura do ambiente (API gratuita Open-Meteo, sem chave)
# Acrescentado para o entregável "consumir dados externos".
# Usa só a biblioteca padrão (urllib), então não precisa instalar nada.
# ======================================================================
import json
import os
import urllib.request

CLIMA_VALIDADE_SEGUNDOS = 600      # reaproveita a resposta por 10 min (o loop lê a cada 10 s)
CLIMA_REPETIR_SE_FALHAR = 60       # se a API falhar, só tenta de novo depois de 60 s
CLIMA_TIMEOUT_SEGUNDOS = 5         # nunca deixa a captura travada esperando a API
CLIMA_MANTER_ULTIMO_VALOR = 3600   # se a API cair, reaproveita o último valor por até 1 h

_clima_cache = {"valor": "", "obtido_em": None, "proxima_tentativa": 0.0}


def clima_externo():
    """Temperatura atual (°C) do local do equipamento, vinda da Open-Meteo.

    Devolve "" (vazio) quando não consegue obter, igual às métricas não
    monitoradas do CSV. Nunca levanta exceção: a captura não pode parar por
    causa de uma API externa.
    Local: variáveis CLIMA_LATITUDE / CLIMA_LONGITUDE do .env (padrão: São Paulo).
    """
    agora = time.monotonic()

    if agora < _clima_cache["proxima_tentativa"]:
        return _clima_cache["valor"]

    try:
        latitude = os.getenv("CLIMA_LATITUDE", "-23.55")
        longitude = os.getenv("CLIMA_LONGITUDE", "-46.63")
        url = (
            "https://api.open-meteo.com/v1/forecast"
            f"?latitude={latitude}&longitude={longitude}&current=temperature_2m"
        )

        with urllib.request.urlopen(url, timeout=CLIMA_TIMEOUT_SEGUNDOS) as resposta:
            dados = json.loads(resposta.read().decode("utf-8"))

        temperatura = round(float(dados["current"]["temperature_2m"]), 1)

        _clima_cache["valor"] = temperatura
        _clima_cache["obtido_em"] = agora
        _clima_cache["proxima_tentativa"] = agora + CLIMA_VALIDADE_SEGUNDOS

    except Exception as erro:
        print(f"Clima externo indisponível ({erro}). Coluna ficará vazia nesta leitura.")

        obtido_em = _clima_cache["obtido_em"]
        if obtido_em is None or agora - obtido_em > CLIMA_MANTER_ULTIMO_VALOR:
            _clima_cache["valor"] = ""

        _clima_cache["proxima_tentativa"] = agora + CLIMA_REPETIR_SE_FALHAR

    return _clima_cache["valor"]

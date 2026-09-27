#script de captura, usa os parametros do bd para registrar os csvs e enviar pro s3

import csv
from datetime import datetime
import os
import sys
import time
from coleta import relatorio
import psutil
from config import cursor
from getmac import get_mac_address
import pandas as pd


INTERVALO_COLETA = 10
INTERVALO_LOTE = 30


#primeira query apenas pra verificar o MAC no banco
def dispositivo_cadastrado(mac):
    query = """select e.nome_fantasia from dispositivo d
    join empresa_cliente e on d.empresa_id = e.id_empresa 
    where d.endereco_mac = (%s)"""

    cursor.execute(query, [mac])

    return cursor.fetchone() is not None


#Verifica quais são as métricas a serem monitoradas pelo dispositivo
def obter_metricas_monitoradas(mac):
    query = """select t.nome from tipo_componente t join
      componente c on c.tipo_id = t.id_tipo join 
      dispositivo d on d.id_dispositivo = c.dispositivo_id 
      where d.endereco_mac = (%s)"""

    cursor.execute(query, [mac])

    return cursor.fetchall()



#Organiza um registro em específico por linha de acordo com as métricas monitoradas
def capturar_leitura(mac, metricas_monitoradas):

    coleta = relatorio()

#Faz com que a comparação ignore o case 
    metricas = {
        item[0].lower()
        for item in metricas_monitoradas
    }

    dados = []

    # CPU
    if "cpu" in metricas:
        dados.append(coleta[0])

    # RAM
    if "ram" in metricas:
        dados.append(coleta[2])

    # DISCO
    if "disco" in metricas:
        dados.append(coleta[3])

    # Data/hora
    dados.append(coleta[4])

    # REDE
    if "rede" in metricas:
        dados.append(coleta[5])
        dados.append(coleta[6])

    # Frequência da CPU
    if "cpu" in metricas:
        dados.append(coleta[7])

    # MAC
    dados.append(coleta[8])

    # Dados adicionais de rede
    if "rede" in metricas:
        dados.append(coleta[9])
        dados.append(coleta[10])
        dados.append(coleta[11])
        dados.append(coleta[12])
        dados.append(coleta[13])

    return dados


#Cria o cabeçalho padrão do csv
def criar_cabecalho():

    cabecalho = [
        "cpu total(%)",
        "ram(%)",
        "disco(%)",
        "Quando foi Coletado",
        "Rede recebida(Mbps)",
        "Rede enviada(Mbps)",
        "Frequencia de uso da CPU(MHz)",
        "Endereco MAC",
        "Pacotes Descartados entrada",
        "Pacotes descartados saida",
        "erros entrada",
        "erros saida",
        "perda pacotes"
    ]

    return cabecalho


#Salva um grupo de registros (linhas) em um único csv, de forma estruturada para posterior envio ao s3
def salvar_lote(leituras, mac, inicio_lote):

    timestamp = inicio_lote.strftime("%Y%m%d_%H%M%S")

    nome_arquivo = f"dados_{mac.replace(':', '')}_{timestamp}.csv"

    with open(nome_arquivo, "w", newline="") as csvfile:

        writer = csv.writer(csvfile, delimiter=",")

        writer.writerow(criar_cabecalho())

        writer.writerows(leituras)

    print(f"Lote salvo: {nome_arquivo}")

    return nome_arquivo



#Método principal
def executar_captura():

    mac = get_mac_address()

    print(f"MAC identificado: {mac}")

    #Verifica o mac no banco
    if not dispositivo_cadastrado(mac):
        print("Seu MAC não está cadastrado no banco.")
        return

    print("Dispositivo encontrado no banco.")

    #obtém métricas de acordo com o mac adress
    metricas_monitoradas = obter_metricas_monitoradas(mac)

    print(
        "Métricas monitoradas:",
        [item[0] for item in metricas_monitoradas]
    )

    leituras = []

    inicio_lote = datetime.now()
    inicio_lote_monotonic = time.monotonic()

    print("Iniciando monitoramento...")

    while True:

        leitura = capturar_leitura(
            mac,
            metricas_monitoradas
        )

        #Guarda a leitura em memória, em uma lista de leituras
        leituras.append(leitura)

        print(
            f"[{leitura[3]}] "
            f"Leitura coletada."
        )

        
        tempo_decorrido = (
            time.monotonic() - inicio_lote_monotonic
        )

        #Verifica se passaram os 5 minutos para guardar todas as leituras em um csv
        if tempo_decorrido >= INTERVALO_LOTE:

            #Grava as leituras em memória em um mesmo .csv
            salvar_lote(
                leituras,
                mac,
                inicio_lote
            )

            #limpa a lista para o próximo grupo de leituras
            leituras = []

            inicio_lote = datetime.now()
            inicio_lote_monotonic = time.monotonic()

        #Faz com que as leituras ocorram de acordo com o tempo determinado
        time.sleep(INTERVALO_COLETA)


if __name__ == "__main__":
    executar_captura()
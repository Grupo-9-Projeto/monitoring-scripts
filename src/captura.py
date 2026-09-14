#esse script de captura, semelhante oq a main faz, só que usa os parametros do bd (sql)

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

mac = get_mac_address()




query = "select e.nome_fantasia from dispositivo d join empresa e on d.empresa_id = e.id_empresa where d.endereco_mac = (%s)"



cursor.execute(query, [mac])



# fetchone = pega exatamente a primeira linha 

if(cursor.fetchone()):
    print(f"seu mac está no banco")
    query2 = "select t.nome from tipo_componente t join componente c on c.tipo_id = t.id_tipo join dispositivo d on d.id_dispositivo = c.dispositivo_id where d.endereco_mac = (%s)"
    cursor.execute(query2, [mac])
    limiares = cursor.fetchall()

    if not os.path.exists('dados_maquina.csv'):
        with open('dados_maquina.csv', 'w', newline='') as csvfile:
            qtd = psutil.cpu_count(logical=True)
            cpus = [f"cpu{i+1}(%)" for i in range(qtd)]
            csv.writer(csvfile, delimiter=';').writerow(["cpu total(%)"] + cpus + [ "ram(%)", "disco(%)", "Quando foi Coletado", "Rede recebida(Mbps)", "Rede enviada(Mbps)", 'Frequencia de uso da CPU(MHz)', "Endereco MAC",  "Pacotes Descartados entrada", "Pacotes descartados saida", "erros entrada", "erros saida", "perda pacotes"])


    print("iniciando")

    coleta = relatorio()
    with open('dados_maquina.csv', 'a', newline='') as csvfile:
        csv.writer(csvfile, delimiter=';').writerow(
            #tratar como parametros
            #precisa usar any pois vem como tupla
            #limiares chega assim: [('CPU',), ('RAM',)]
            #se tiver a palavra no for, entao vai plotar
        ([coleta[0]] + coleta[1] if 'cpu' in (i[0].lower() for i in limiares) else [""]) +
        ([coleta[2]] if 'ram' in (i[0].lower() for i in limiares) else [""]) +
        ([coleta[3]] if 'disco' in (i[0].lower() for i in limiares) else [""]) +
        ([coleta[4]]) +
        ([coleta[5]] if 'rede' in (i[0].lower() for i in limiares) else [""]) +
        ([coleta[6]] if 'rede' in (i[0].lower() for i in limiares) else [""]) +
        ([coleta[7]] if 'cpu' in (i[0].lower() for i in limiares) else [""]) +
        ([coleta[8]]) +
        ([coleta[9]] if 'rede' in (i[0].lower() for i in limiares) else [""]) +
        ([coleta[10]] if 'rede' in (i[0].lower() for i in limiares) else [""]) +
        ([coleta[11]] if 'rede' in (i[0].lower() for i in limiares) else [""]) +
        ([coleta[12]] if 'rede' in (i[0].lower() for i in limiares) else [""]) +
        ([coleta[13]] if 'rede' in (i[0].lower() for i in limiares) else [""])
    )
        print(coleta)

else:
    print(f"seu mac nao esta cadastrado")
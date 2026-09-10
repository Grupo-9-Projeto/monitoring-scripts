import mysql.connector
from getmac import get_mac_address
import csv
import pandas as pd


mac = get_mac_address()

cnx = {'host': 'localhost',
            'user': 'argos_user',
            'password': 'sptech',
            'database': 'argos_db'}

conexao = mysql.connector.connect(**cnx)


query = "select e.nome_fantasia from dispositivo d join empresa e on d.empresa_id = e.id_empresa where d.endereco_mac = (%s)"

cursor = conexao.cursor()

cursor.execute(query, [mac])



# fetchone = pega exatamente a primeira linha 

if(cursor.fetchone()):
    print(f"seu mac está no banco")
    query2 = "select t.nome, c.limiar_aviso, c.limiar_critico from dispositivo d join componente c on c.dispositivo_id = d.id_dispositivo join tipo_componente t on t.id_tipo = c.tipo_id where d.endereco_mac = %s"
    cursor.execute(query2, [mac])
    limiares = cursor.fetchall()
    print(f"DEBUG - Limiares encontrados no banco: {limiares}")

    df = pd.read_csv('dados_maquina.csv', sep=';')
    ultima = df.iloc[-1]



# df.iterows = metodo do pandas pra percorrer dataframe, primeiro elemento é o numero da linha e o segundo é as colunas 
    for i, linha in df.iterrows():
        data = linha["Quando foi Coletado"]
        print(f"\ndata da leitura: {data} ------------------------\n")

        for i in limiares:
            tipo = i[0].lower()

            aviso = float(i[1])
            critico = float(i[2])

            if tipo == 'cpu':
                val = float(linha["cpu total(%)"])
            elif tipo == 'ram':
                val = float(linha["ram(%)"])
            elif tipo == 'disco':
                val = float(linha["disco(%)"])
            elif tipo == 'rede':
                val = float(linha["Rede recebida(Mbps)"])

            if critico and val >= critico:
                print(f"ALERTA CRITICO: {tipo} em {val}% (Limite: {critico}%)")
            elif aviso and val >= aviso:
                print(f"AVISO: {tipo} em {val}% (Limite: {aviso}%)")
            else:
                print(f"OK: {tipo} em {val}%")

else:
    print("seu mac NAO esta no banco")

cursor.close()
conexao.close()
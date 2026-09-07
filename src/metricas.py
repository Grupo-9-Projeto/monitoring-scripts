import mysql.connector
from getmac import get_mac_address
import csv


mac = get_mac_address()

cnx = {'host': 'localhost',
            'user': 'argos_user',
            'password': 'sptech',
            'database': 'argos_db'}

conexao = mysql.connector.connect(**cnx)


query = "select d.hostname, e.nome_fantasia from dispositivo d join empresa e on d.empresa_id = e.id_empresa where d.endereco_mac = (%s)"

cursor = conexao.cursor()

cursor.execute(query, [mac])



# fetchone = pega exatamente a primeira linha 

if(cursor.fetchone()):
    print(f"seu mac está no banco")
else:
    print("seu mac NAO esta no banco")

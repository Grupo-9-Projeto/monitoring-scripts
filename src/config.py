#configurações do banco, pegando do .env

import os  
import mysql.connector
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())

cnx = {
    'host': os.getenv('DB_HOST'),
    'user': os.getenv('DB_USER'),
    'password': os.getenv('DB_PASSWORD'),
    'database': os.getenv('DB_DATABASE')
}

conexao = mysql.connector.connect(**cnx)
cursor = conexao.cursor()
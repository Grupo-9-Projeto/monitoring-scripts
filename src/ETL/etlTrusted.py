import os
import re
import json
import base64
import urllib.parse
import urllib.request
from datetime import datetime, timedelta, timezone
from io import BytesIO
from urllib.parse import unquote_plus

import boto3
import pandas as pd

# Horario de Brasilia
try:
    from zoneinfo import ZoneInfo
    FUSO = ZoneInfo("America/Sao_Paulo")
except Exception:
    FUSO = timezone(timedelta(hours=-3))

s3 = boto3.client("s3")


PREFIXO_ENTRADA = "raw/dispositivos/processos/"

# Chamados do Jira 
CAMINHO_CHAMADOS = "trusted/chamados/chamados.csv"
DIAS_DE_HISTORICO = 70      


# ==============================LENDO S3
def ler_arquivo_s3(bucket, caminho_s3):
    resposta = s3.get_object(Bucket=bucket, Key=caminho_s3)

    conteudo = resposta["Body"].read()

    return pd.read_csv(BytesIO(conteudo))


# ===============================Corrigindo tipagem dos campos
def corrige_datetime(df, coluna):

    df[coluna] = pd.to_datetime(
        df[coluna],
        format="%Y-%m-%d %H:%M:%S"
    )

    return df

def corrige_float(df, coluna):
    df[coluna] = pd.to_numeric(
        df[coluna],
        errors="coerce"
    )

    return df


def corrige_int(df, coluna):
    df[coluna] = pd.to_numeric(
        df[coluna],
        errors = "coerce"
    ).astype("Int64")

    return df


def corrige_string(df, coluna):
    df[coluna] = df[coluna].astype("string")

    return df

        

# ===================================VALIDANDO VALORES
def validar_porcentagens(df, coluna):

    df.loc[
        (df[coluna] < 0) |
        (df[coluna] > 100),
        coluna
    ] = pd.NA

    return df

def validar_valores_negativos(df, coluna):
    df.loc[
        (df[coluna] < 0),
        coluna
    ] = pd.NA

    return df

def validar_mac(df, coluna):
    padrao = r"^([0-9A-Fa-f]{2}:){5}[0-9A-Fa-f]{2}$"

    df.loc[
        ~df[coluna].str.match(padrao, na=False),
        coluna
    ] = pd.NA

    return df


# =================================Métodos principais
def corrigirTipos(df):
    #Float
    df = corrige_float(df, "cpu total(%)")
    df = corrige_float(df, "ram(%)")
    df = corrige_float(df, "disco(%)")
    df = corrige_float(df, "Rede recebida(Mbps)")
    df = corrige_float(df, "Rede enviada(Mbps)")
    df = corrige_float(df, "Frequencia de uso da CPU(MHz)")
    df = corrige_float(df, "perda pacotes")
#Int
    df = corrige_int(df, "Pacotes Descartados entrada")
    df = corrige_int(df, "Pacotes descartados saida")
    df = corrige_int(df, "erros entrada")
    df = corrige_int(df, "erros saida")
#String
    df = corrige_string(df, "Endereco MAC")
# Datetime
    df = corrige_datetime(df, "Quando foi Coletado")
    df = corrige_datetime(df, "timestamp_lote")

    return df


def validar_dados(df):
    
#Porcentagens
    df = validar_porcentagens(df, "cpu total(%)")
    df = validar_porcentagens(df, "ram(%)")
    df = validar_porcentagens(df, "disco(%)")
    df = validar_porcentagens(df, "perda pacotes")

#Valores positivos
    df = validar_valores_negativos(df, "Rede recebida(Mbps)")
    df = validar_valores_negativos(df, "Rede enviada(Mbps)")
    df = validar_valores_negativos(df, "Frequencia de uso da CPU(MHz)")
    df = validar_valores_negativos(df, "Pacotes Descartados entrada")
    df = validar_valores_negativos(df, "Pacotes descartados saida")
    df = validar_valores_negativos(df, "erros entrada")
    df = validar_valores_negativos(df, "erros saida")

#Mac Adress
    df = validar_mac(df, "Endereco MAC")

    return df


#ADIÇÃO DE COLUNAS


def adicionar_dados_processos(df, bucket, caminho_raw):

    caminho_processos = caminho_raw.replace(
        "raw/dispositivos/capturas/",
        "raw/dispositivos/processos/",
        1
    ).replace(
        "dados_",
        "processos_",
        1
    )

    df_processos = ler_arquivo_s3(bucket, caminho_processos)

    df_processos["timestamp_lote"] = pd.to_datetime(
        df_processos["timestamp_lote"]
    )

    df_processos["cpu_percent"] = pd.to_numeric(
        df_processos["cpu_percent"], errors="coerce"
    ).fillna(0)

    df_processos["ram_percent"] = pd.to_numeric(
        df_processos["ram_percent"], errors="coerce"
    ).fillna(0)

    # Agrupa os processos por MAC e lote
    resumo = df_processos.groupby(
        ["Endereco MAC", "timestamp_lote"]
    ).agg(
        quantidade_processos=("pid", "count"),

        processo_maior_cpu=(
            "cpu_percent",
            lambda x: df_processos.loc[x.idxmax(), "name"]
        ),
        cpu_processo_maior_cpu=("cpu_percent", "max"),

        processo_maior_ram=(
            "ram_percent",
            lambda x: df_processos.loc[x.idxmax(), "name"]
        ),
        ram_processo_maior_ram=("ram_percent", "max")

    ).reset_index()

    df = df.merge(
        resumo,
        on=["Endereco MAC", "timestamp_lote"],
        how="left"
    )

    return df


def gerar_caminho_capturas(caminho_processos):
    return caminho_processos.replace(
        "raw/dispositivos/processos/",
        "raw/dispositivos/capturas/",
        1
    ).replace(
        "processos_",
        "dados_",
        1
    )


def gerar_caminho_trusted(caminho_raw):
    return caminho_raw.replace("raw/", "trusted/", 1)


def salvar_trusted(df, bucket, caminho_raw):
    caminho_trusted = gerar_caminho_trusted(caminho_raw)

    conteudo_csv = df.to_csv(index=False)

    s3.put_object(
        Bucket=bucket,
        Key=caminho_trusted,
        Body=conteudo_csv.encode("utf-8")
    )

    print(f"Arquivo salvo em: {caminho_trusted}")


# ==================================CHAMADOS DO JIRA

def converter_data_do_jira(texto):
    data = datetime.strptime(texto, "%Y-%m-%dT%H:%M:%S.%f%z")
    return data.astimezone(FUSO).strftime("%Y-%m-%d %H:%M:%S")


def extrair_mac(descricao):
    achou = re.search(r"MAC\):\s*([0-9A-Fa-f:]{17})", descricao or "")
    if not achou:
        return None
    return achou.group(1).lower()


def buscar_chamados_no_jira():
    url = os.getenv("JIRA_URL")
    email = os.getenv("JIRA_EMAIL")
    token = os.getenv("JIRA_TOKEN")
    projeto = os.getenv("JIRA_PROJECT_KEY")

    if not (url and email and token and projeto):
        raise Exception("Faltam variáveis JIRA_URL, JIRA_EMAIL, JIRA_TOKEN ou JIRA_PROJECT_KEY")

    login = base64.b64encode(f"{email}:{token}".encode()).decode()
    jql = f"project = {projeto} AND created >= -{DIAS_DE_HISTORICO}d ORDER BY created ASC"

    chamados = []
    proxima_pagina = None

    # o jira devolve os chamados em paginas de ate 100
    while True:
        endereco = (
            f"{url}/rest/api/2/search/jql?jql={urllib.parse.quote(jql)}"
            "&fields=description,created,resolutiondate&maxResults=100"
        )
        if proxima_pagina:
            endereco += "&nextPageToken=" + urllib.parse.quote(proxima_pagina)

        pedido = urllib.request.Request(endereco, headers={
            "Authorization": "Basic " + login,
            "Accept": "application/json"
        })
        with urllib.request.urlopen(pedido, timeout=20) as resposta:
            corpo = json.loads(resposta.read().decode("utf-8"))

        for issue in corpo.get("issues", []):
            campos = issue["fields"]
            concluido = campos.get("resolutiondate")
            chamados.append({
                "chamado": issue["key"],
                "mac": extrair_mac(campos.get("description")),
                "aberto_em": converter_data_do_jira(campos["created"]),
                "concluido_em": converter_data_do_jira(concluido) if concluido else None
            })

        proxima_pagina = corpo.get("nextPageToken")
        if not proxima_pagina:
            break

    return chamados


# fica so com os chamados que tem o MAC da maquina na descricao
def montar_tabela_chamados(chamados_jira):
    return [chamado for chamado in chamados_jira if chamado["mac"] is not None]


def salvar_csv(bucket, caminho, linhas, colunas):
    conteudo_csv = pd.DataFrame(linhas, columns=colunas).to_csv(index=False)

    s3.put_object(
        Bucket=bucket,
        Key=caminho,
        Body=conteudo_csv.encode("utf-8")
    )

    print(f"Arquivo salvo em: {caminho}")


def atualizar_chamados():
    bucket = os.getenv("BUCKET_S3")
    if not bucket:
        raise Exception("Falta a variável de ambiente BUCKET_S3")

    tabela_chamados = montar_tabela_chamados(buscar_chamados_no_jira())

    # salvar este arquivo e o que dispara a etlClient
    salvar_csv(bucket, CAMINHO_CHAMADOS, tabela_chamados,
               ["chamado", "mac", "aberto_em", "concluido_em"])

    return len(tabela_chamados)


# ==================================LAMBDA
def lambda_handler(event, context):

    # chamado pelo agendamento: atualiza os chamados do Jira
    if "Records" not in event:
        total = atualizar_chamados()
        return {"statusCode": 200, "chamados_salvos": total}

    processados = 0

    for registro in event["Records"]:
        bucket = registro["s3"]["bucket"]["name"]
        #decodifica
        caminho_processos = unquote_plus(registro["s3"]["object"]["key"])

        # so CSV de processos da pasta raw 
        if not caminho_processos.startswith(PREFIXO_ENTRADA) or not caminho_processos.endswith(".csv"):
            continue

        # o CSV de capturas do mesmo lote
        caminho = gerar_caminho_capturas(caminho_processos)

        df = ler_arquivo_s3(bucket, caminho)

        df = corrigirTipos(df)

        df = validar_dados(df)

        df = adicionar_dados_processos(df, bucket, caminho)

        salvar_trusted(df, bucket, caminho)

        processados += 1

    return {"statusCode": 200, "arquivos_processados": processados}


if __name__ == "__main__":
    import sys
    evento = {"Records": [{"s3": {"bucket": {"name": sys.argv[1]}, "object": {"key": sys.argv[2]}}}]}
    print(lambda_handler(evento, None))

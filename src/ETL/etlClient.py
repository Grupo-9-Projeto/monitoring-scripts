import json
from datetime import datetime, timedelta, timezone
from io import BytesIO
from urllib.parse import unquote_plus

import boto3
import pandas as pd

# horario de Brasilia 
try:
    from zoneinfo import ZoneInfo
    FUSO = ZoneInfo("America/Sao_Paulo")
except Exception:
    FUSO = timezone(timedelta(hours=-3))

s3 = boto3.client("s3")

# esta Lambda so processa arquivos que chegam nestas pastas
PREFIXO_ENTRADA = "trusted/dispositivos/capturas/"

# arquivo que a etltrusted gera a partir do Jira
CAMINHO_CHAMADOS = "trusted/chamados/chamados.csv"

SEMANAS_DO_MODELO = 8       
SEMANAS_PREVISTAS = 3       


#----------------------------------Converte csv em df
def ler_arquivo_s3(bucket, caminho_s3):
    resposta = s3.get_object(Bucket=bucket, Key=caminho_s3)

    conteudo = resposta["Body"].read()

    return pd.read_csv(BytesIO(conteudo))


#-----------------------------------------------FILTRO CLIENT
def filtra_colunas_df(df):
    colunas = [
        "Quando foi Coletado",
        "cpu total(%)",
        "ram(%)",
        "perda pacotes",
        "disco(%)",
        "Frequencia de uso da CPU(MHz)",
        "quantidade_processos",
        "processo_maior_ram",
        "ram_processo_maior_ram",
        "processo_maior_cpu",
        "cpu_processo_maior_cpu"
    ]

    return df[colunas].copy()


#------------------------------------------------------------SALVAR NO CLIENT
def gerar_caminho_client(caminho_trusted):
    caminho_client = caminho_trusted.replace("trusted/", "client/", 1)

    return caminho_client.rsplit(".", 1)[0] + ".json"


def salvar_client(df, bucket, caminho_trusted):
    caminho_client = gerar_caminho_client(caminho_trusted)

    conteudo_json = df.to_json(
        orient="records",
        date_format="iso",
        force_ascii=False,
        indent=2
    )

    s3.put_object(
        Bucket=bucket,
        Key=caminho_client,
        Body=conteudo_json.encode("utf-8"),
        ContentType="application/json"
    )

    print(f"Arquivo salvo em: {caminho_client}")



def data_curta(data):
    return data.strftime("%d/%m")


def inicio_da_semana(data):
    segunda = data - timedelta(days=data.weekday())
    return segunda.replace(hour=0, minute=0, second=0, microsecond=0)


def converter_data(texto):
    return datetime.strptime(texto, "%Y-%m-%d %H:%M:%S").replace(tzinfo=FUSO)


def numero_da_semana(data, primeira_semana):
    return (data - primeira_semana).days // 7


def gerar_json_chamados(bucket):
    tabela = ler_arquivo_s3(bucket, CAMINHO_CHAMADOS)

    agora = datetime.now(FUSO)
    semana_atual = inicio_da_semana(agora)   
    inicio_historico = semana_atual - timedelta(weeks=SEMANAS_DO_MODELO)
    proxima_semana = semana_atual + timedelta(weeks=1)

    dispositivos = {}

    for _, linha in tabela.iterrows():
        mac = linha["mac"]
        aberto = converter_data(linha["aberto_em"])
        concluido = None if pd.isna(linha["concluido_em"]) else converter_data(linha["concluido_em"])

        if mac not in dispositivos:
            dispositivos[mac] = {
                "chamadosPorSemana": [0] * SEMANAS_DO_MODELO,     
                "concluidosPorSemana": [0] * SEMANAS_DO_MODELO,   
                "resolvidos": {"quantidade": 0, "horas": 0},      
                "calor": [[0] * 6 for _ in range(7)]                
            }
        dispositivo = dispositivos[mac]

        semana = numero_da_semana(aberto, inicio_historico)
        if 0 <= semana < SEMANAS_DO_MODELO:
            dispositivo["chamadosPorSemana"][semana] += 1
            dispositivo["calor"][aberto.weekday()][min(5, aberto.hour // 4)] += 1

            if concluido is not None and concluido >= aberto:
                dispositivo["resolvidos"]["quantidade"] += 1
                dispositivo["resolvidos"]["horas"] += (concluido - aberto).total_seconds() / 3600

        if concluido is not None:
            semana = numero_da_semana(concluido, inicio_historico)
            if 0 <= semana < SEMANAS_DO_MODELO:
                dispositivo["concluidosPorSemana"][semana] += 1

    for dispositivo in dispositivos.values():
        dispositivo["resolvidos"]["horas"] = round(dispositivo["resolvidos"]["horas"], 4)

    resultado = {
        "geradoEm": agora.isoformat(),
        "proximaSemana": data_curta(proxima_semana) + " a " + data_curta(proxima_semana + timedelta(days=6)),
        "semanasHistorico": [data_curta(inicio_historico + timedelta(weeks=i)) for i in range(SEMANAS_DO_MODELO)],
        "semanasPrevistas": [data_curta(proxima_semana + timedelta(weeks=i)) for i in range(SEMANAS_PREVISTAS)],
        "dispositivos": dispositivos
    }

    caminho = "client/previsoes/previsoes.json"
    s3.put_object(
        Bucket=bucket,
        Key=caminho,
        Body=json.dumps(resultado, ensure_ascii=False, indent=2).encode("utf-8"),
        ContentType="application/json"
    )

    print(f"Arquivo salvo em: {caminho}")
    return len(dispositivos)


#==================================LAMBDA
def lambda_handler(event, context):

    processados = 0

    for registro in event["Records"]:
        bucket = registro["s3"]["bucket"]["name"]
        #decodifica
        caminho = unquote_plus(registro["s3"]["object"]["key"])

        # chegou o arquivo de chamados do jira: refaz o json de chamados por maquina
        if caminho == CAMINHO_CHAMADOS:
            gerar_json_chamados(bucket)
            processados += 1
            continue

        # só CSV da pasta trusted 
        if not caminho.startswith(PREFIXO_ENTRADA) or not caminho.endswith(".csv"):
            continue

        df = ler_arquivo_s3(bucket, caminho)

        df = filtra_colunas_df(df)

        salvar_client(df, bucket, caminho)

        processados += 1

    return {"statusCode": 200, "arquivos_processados": processados}


if __name__ == "__main__":
    import sys
    evento = {"Records": [{"s3": {"bucket": {"name": sys.argv[1]}, "object": {"key": sys.argv[2]}}}]}
    print(lambda_handler(evento, None))

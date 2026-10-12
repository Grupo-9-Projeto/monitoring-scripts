import boto3
import pandas as pd
from io import BytesIO

BUCKET = "NOME_BUCKET_S3"

s3 = boto3.client("s3")

#----------------------------------Converte csv em df
def ler_arquivo_s3(caminho_s3):
    resposta = s3.get_object(
        Bucket = BUCKET,
        Key=caminho_s3
    )

    conteudo = resposta["Body"].read()

    df = pd.read_csv(
        BytesIO(conteudo)
    )

    return df


#-----------------------------------------------------------BUSCA CSVs
def buscar_csvs_pendentes(prefixo_trusted):

    arquivos_trusted = []
    arquivos_client = set()

#Buscando os arquivos no prefixo trusted
    resposta = s3.get_paginator("list_objects_v2")

    for pagina in resposta.paginate(
        Bucket=BUCKET,
        Prefix=prefixo_trusted
    ):
        for objeto in pagina.get("Contents", []):
            chave = objeto["Key"]

            if chave.endswith(".csv"):
                arquivos_trusted.append(chave)

#Busca os json no client, para ver se já existem ou não, para só atuar nos arquivos que não existem no prefixo ainda
    prefixo_client = prefixo_trusted.replace(
        "trusted/", "client/", 1
    )

    for pagina in resposta.paginate(
        Bucket=BUCKET,
        Prefix=prefixo_client
    ):
        for objeto in pagina.get("Contents", []):
            chave = objeto["Key"]

            if chave.endswith(".json"):
                arquivos_client.add(chave)

    pendentes = []

#Compara e retorna só o que precisa
    for caminho_csv in arquivos_trusted:

        caminho_json = caminho_csv.replace(
            "trusted/", "client/", 1
        )

        caminho_json = caminho_json.rsplit(".", 1)[0] + ".json"

        if caminho_json not in arquivos_client:
            pendentes.append(caminho_csv)

    return pendentes

#-----------------------------------------------FILTRO CLIENT
def filtra_colunas_df(df):
    colunas = [
        "Quando foi Coletado",
        "cpu total(%)",
        "ram(%)",
        "perda pacotes",
        "disco(%)"
    ]

    df = df[colunas].copy()

    return df


#------------------------------------------------------------SALVAR NO CLIENT
def gerar_caminho_client(caminho_trusted):
    caminho_client = caminho_trusted.replace(
        "trusted/", "client/", 1
    )

    caminho_client = caminho_client.rsplit(".", 1)[0] + ".json"

    return caminho_client


def salvar_client(df, caminho_trusted):
    buffer = BytesIO()

    caminho_client = gerar_caminho_client(caminho_trusted)

    conteudo_json = df.to_json(
        orient="records",
        date_format="iso",
        force_ascii=False,
        indent=2
    )

    buffer = BytesIO(conteudo_json.encode("utf-8"))

    buffer.seek(0)

    s3.upload_fileobj(
        buffer,
        BUCKET,
        caminho_client,
        ExtraArgs={
            "ContentType": "application/json"
        }
    )

    print(f"Arquivo salvo em: {caminho_client}")

#MAIN
if __name__ == "__main__":

    caminhos = buscar_csvs_pendentes(
        "trusted/dispositivos/capturas/"
    )

    print(f"Arquivos pendentes: {len(caminhos)}")

    for caminho in caminhos:

        df = ler_arquivo_s3(caminho)

        df = filtra_colunas_df(df)

        salvar_client(df, caminho)
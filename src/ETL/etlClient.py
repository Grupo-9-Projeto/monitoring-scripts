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

def listar_arquivos_s3(prefixo):

    arquivos = set()

    paginador = s3.get_paginator("list_objects_v2")

    for pagina in paginador.paginate(
        Bucket=BUCKET,
        Prefix=prefixo
    ):
        for objeto in pagina.get("Contents", []):
            arquivos.add(objeto["Key"])

    return arquivos

#-----------------------------------------------------------BUSCA CSVs

def buscar_arquivos_pendentes(
    prefixo_origem,
    prefixo_destino,
    extensao_origem=".csv",
    extensao_destino=".json"
):

    arquivos_origem = listar_arquivos_s3(prefixo_origem)
    arquivos_destino = listar_arquivos_s3(prefixo_destino)

    pendentes = []

    for caminho_origem in arquivos_origem:

        if not caminho_origem.endswith(extensao_origem):
            continue

        caminho_destino = caminho_origem.replace(
            prefixo_origem,
            prefixo_destino,
            1
        )

        caminho_destino = (
            caminho_destino[:-len(extensao_origem)]
            + extensao_destino
        )

        if caminho_destino not in arquivos_destino:
            pendentes.append(caminho_origem)

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

    caminhos = buscar_arquivos_pendentes(
        "trusted/dispositivos/capturas/", "client/dispositivos/capturas"
    )

    print(f"Arquivos pendentes: {len(caminhos)}")

    for caminho in caminhos:

        df = ler_arquivo_s3(caminho)

        df = filtra_colunas_df(df)

        salvar_client(df, caminho)
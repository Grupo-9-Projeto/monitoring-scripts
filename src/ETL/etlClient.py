import boto3
import pandas as pd
from io import BytesIO
from urllib.parse import unquote_plus

s3 = boto3.client("s3")

# O Lambda é disparado quando um CSV novo chega nesta pasta
PREFIXO_ENTRADA = "trusted/dispositivos/capturas/"

#----------------------------------Converte csv em df
def ler_arquivo_s3(bucket, caminho_s3):
    resposta = s3.get_object(
        Bucket = bucket,
        Key=caminho_s3
    )

    conteudo = resposta["Body"].read()

    df = pd.read_csv(
        BytesIO(conteudo)
    )

    return df

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

    # Acréscimo: colunas extras do mesmo JSON (identificação do equipamento, rede e flags de anomalia).
    # Só entram se existirem no CSV trusted, para não quebrar arquivos gerados antes desta mudança.
    colunas_extras = [
        "Endereco MAC",
        "Rede recebida(Mbps)",
        "Rede enviada(Mbps)",
        "anomalia_cpu",
        "anomalia_ram",
        "anomalia_disco",
        "anomalia_rede"
    ]
    colunas = colunas + [c for c in colunas_extras if c in df.columns]

    df = df[colunas].copy()
    
    return df


#------------------------------------------------------------SALVAR NO CLIENT
def gerar_caminho_client(caminho_trusted):
    caminho_client = caminho_trusted.replace(
        "trusted/", "client/", 1
    )

    caminho_client = caminho_client.rsplit(".", 1)[0] + ".json"

    return caminho_client


def salvar_client(df, bucket, caminho_trusted):
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
        bucket,
        caminho_client,
        ExtraArgs={
            "ContentType": "application/json"
        }
    )

    print(f"Arquivo salvo em: {caminho_client}")

#LAMBDA
# o S3 chama esta função toda vez que chega um CSV novo em trusted/dispositivos/capturas/
def lambda_handler(event, context):

    for registro in event["Records"]:

        bucket = registro["s3"]["bucket"]["name"]

        #decodifica
        caminho = unquote_plus(registro["s3"]["object"]["key"])

        # so CSV da pasta trusted de capturas 
        if not caminho.startswith(PREFIXO_ENTRADA) or not caminho.endswith(".csv"):
            continue

        df = ler_arquivo_s3(bucket, caminho)

        df = filtra_colunas_df(df)

        salvar_client(df, bucket, caminho)

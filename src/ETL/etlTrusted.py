import boto3
import pandas as pd
from io import BytesIO
from urllib.parse import unquote_plus

s3 = boto3.client("s3")

PREFIXO_ENTRADA = "raw/dispositivos/processos/"


# ==============================LENDO S3
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

    # Corrige os tipos de dados
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

    # Junta os dados do lote às capturas individuais
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
    caminho_trusted = caminho_raw.replace(
        "raw/", "trusted/", 1
    )

    return caminho_trusted


def salvar_trusted(df, bucket, caminho_raw):
    buffer = BytesIO()

    caminho_trusted = gerar_caminho_trusted(caminho_raw)

    df.to_csv(
        buffer,
        index=False
    )

    buffer.seek(0)

    s3.upload_fileobj(
        buffer,
        bucket,
        caminho_trusted
    )

    print(f"Arquivo salvo em: {caminho_trusted}")


# ================================LAMBDA
# o S3 chama esta funcao toda vez que chega um CSV de processos novo em raw/dispositivos/processos/
def lambda_handler(event, context):

    for registro in event["Records"]:

        bucket = registro["s3"]["bucket"]["name"]

        #decodifica
        caminho_processos = unquote_plus(registro["s3"]["object"]["key"])

        # só CSV da pasta de processos
        if not caminho_processos.startswith(PREFIXO_ENTRADA) or not caminho_processos.endswith(".csv"):
            continue

        # o CSV de capturas do mesmo lote
        caminho = gerar_caminho_capturas(caminho_processos)

        df = ler_arquivo_s3(bucket, caminho)

        df = corrigirTipos(df)

        df = validar_dados(df)

        df = adicionar_dados_processos(df, bucket, caminho)

        salvar_trusted(df, bucket, caminho)

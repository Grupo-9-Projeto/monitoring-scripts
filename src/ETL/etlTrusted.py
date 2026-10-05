import boto3
import pandas as pd
from io import BytesIO

BUCKET = "nome_bucket_s3"

s3 = boto3.client("s3")


# ==============================LENDO S3
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


def buscar_caminho_csv(prefixo):
    paginator = s3.get_paginator('list_objects_v2')
    paginas = paginator.paginate(
        Bucket=BUCKET, 
        Prefix=prefixo
        )

    arquivo_mais_recente = None
    data_mais_recente = None

    for pagina in paginas:
        if 'Contents' in pagina:
            for objeto in pagina['Contents']:
                chave = objeto['Key']
                
                if chave.endswith('.csv'):
                    data_modificacao = objeto['LastModified']
                    
                    if data_mais_recente is None or data_modificacao > data_mais_recente:
                        data_mais_recente = data_modificacao
                        arquivo_mais_recente = chave

    return arquivo_mais_recente


# ===============================Corrigindo tipagem dos campos
def corrige_datetime(df, coluna):

    df[coluna] = pd.to_datetime(
        df[coluna]
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


def gerar_caminho_trusted(caminho_raw):
    caminho_trusted = caminho_raw.replace(
        "raw/", "trusted/", 1
    )

    return caminho_trusted


def salvar_trusted(df, caminho_raw):
    buffer = BytesIO()

    caminho_trusted = gerar_caminho_trusted(caminho_raw)

    df.to_csv(
        buffer,
        index=False
    )

    buffer.seek(0)

    s3.upload_fileobj(
        buffer,
        BUCKET,
        caminho_trusted
    )

    print(f"Arquivo salvo em: {caminho_trusted}")


# ================================TESTE
if __name__ == "__main__":

    caminho = buscar_caminho_csv("raw/dispositivos/capturas/")

    df = ler_arquivo_s3(caminho)

    df = corrigirTipos(df)

    df = validar_dados(df)

    salvar_trusted(df, caminho)





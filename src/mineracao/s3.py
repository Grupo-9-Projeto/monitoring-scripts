import boto3


BUCKET = "NOME_DO_BUCKET"
#Em caso de erro no upload, VERIFIQUE O ARQUIVO: GUIA_AWS_CLI_COLETA.md



def enviar_arquivo_capturas(arquivo_local, mac, data_lote):

    s3 = boto3.client("s3")

    ano = data_lote.strftime("%Y")
    mes = data_lote.strftime("%m")
    dia = data_lote.strftime("%d")

    nome_arquivo = arquivo_local.split("\\")[-1]

    caminho_s3 = (
        f"raw/dispositivos/capturas/{mac}/"
        f"{ano}/{mes}/{dia}/"
        f"{nome_arquivo}"
    )

    s3.upload_file(
        arquivo_local,
        BUCKET,
        caminho_s3
    )

    print(f"Arquivo enviado para o S3: {caminho_s3}")

def enviar_arquivo_processos(arquivo_local, mac, data_lote):

    s3 = boto3.client("s3")

    ano = data_lote.strftime("%Y")
    mes = data_lote.strftime("%m")
    dia = data_lote.strftime("%d")

    nome_arquivo = arquivo_local.split("\\")[-1]

    caminho_s3 = (
        f"raw/dispositivos/processos/{mac}/"
        f"{ano}/{mes}/{dia}/"
        f"{nome_arquivo}"
    )

    s3.upload_file(
        arquivo_local,
        BUCKET,
        caminho_s3
    )

    print(f"Arquivo enviado para o S3: {caminho_s3}")
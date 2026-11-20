from datetime import datetime
import os
from pathlib import Path
import re
from s3 import enviar_arquivo_capturas, enviar_arquivo_processos

PADRAO_NOME_ARQUIVO = re.compile(
    r"^(dados|processos)_([0-9A-Fa-f]{12})_(\d{8}_\d{6})\.csv$"
)


def formatar_mac(mac_sem_pontos: str) -> str:
    """Converte 'AABBCC112201' de volta para 'AA:BB:CC:11:22:01'."""
    pares = [mac_sem_pontos[i : i + 2].upper() for i in range(0, 12, 2)]
    return ":".join(pares)


def enviar_pasta_simulada(
    pasta_base: str = "simulacoes_output",
    apagar_local_apos_envio: bool = False,
) -> None:
    """Percorre a pasta de simulações e envia capturas e processos para o S3."""
    diretorio = Path(pasta_base)

    if not diretorio.exists():
        print(f"Pasta '{pasta_base}' não encontrada. Rode simular_dados.py antes.")
        return

    arquivos_csv = sorted(diretorio.rglob("*.csv"))
    total_enviados = 0

    for arquivo in arquivos_csv:
        correspondencia = PADRAO_NOME_ARQUIVO.match(arquivo.name)
        if not correspondencia:
            continue

        tipo_arquivo, mac_limpo, selo_data = correspondencia.groups()
        mac = formatar_mac(mac_limpo)
        data_lote = datetime.strptime(selo_data, "%Y%m%d_%H%M%S")

        caminho_para_s3 = str(arquivo)
        if os.sep != "\\":
            caminho_para_s3 = caminho_para_s3.replace("/", "\\")

        if tipo_arquivo == "dados":
            enviar_arquivo_capturas(caminho_para_s3, mac, data_lote)
            total_enviados += 1
        elif tipo_arquivo == "processos":
            enviar_arquivo_processos(caminho_para_s3, mac, data_lote)
            total_enviados += 1

        if apagar_local_apos_envio:
            arquivo.unlink(missing_ok=True)

    print(f"Envio concluído! Total de arquivos enviados ao S3: {total_enviados}")


if __name__ == "__main__":
    enviar_pasta_simulada(
        pasta_base="simulacoes_output",
        apagar_local_apos_envio=False,
    )
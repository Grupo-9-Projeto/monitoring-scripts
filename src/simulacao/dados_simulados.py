from datetime import datetime, timedelta
import math
from pathlib import Path
import random
import pandas as pd

COLUNAS_CAPTURA = [
    "cpu total(%)",
    "ram(%)",
    "disco(%)",
    "Quando foi Coletado",
    "Rede recebida(Mbps)",
    "Rede enviada(Mbps)",
    "Frequencia de uso da CPU(MHz)",
    "Endereco MAC",
    "Pacotes Descartados entrada",
    "Pacotes descartados saida",
    "erros entrada",
    "erros saida",
    "perda pacotes",
    "timestamp_lote",
    "origem_dado",
    "temperatura externa(C)",
]

PROCESSOS_SIMULADOS = [
    "python.exe",
    "java",
    "postgres",
    "nginx",
    "node",
]


def temperatura_simulada(dt: datetime) -> float:
    """Temperatura SIMULADA do ambiente (curva diária: mínima ~6h, máxima ~15h).

    Só para o simulador. Na captura real o valor vem da Open-Meteo.
    """
    curva = 24 + 9 * math.sin(2 * math.pi * (dt.hour + dt.minute / 60 - 9) / 24)
    return round(curva + random.uniform(-0.8, 0.8), 1)


def eh_horario_pico(dt: datetime) -> bool:
    minutos = dt.hour * 60 + dt.minute
    return (11 * 60 + 30 <= minutos <= 14 * 60 + 30) or (
        18 * 60 + 30 <= minutos <= 22 * 60 + 30
    )


def gerar_processos(
    mac: str,
    inicio_lote: datetime,
    fator: float,
) -> pd.DataFrame:
    ts_lote_str = inicio_lote.strftime("%Y-%m-%d %H:%M:%S")
    linhas_processos = []

    for pid, nome in enumerate(PROCESSOS_SIMULADOS, start=1000):
        linhas_processos.append({
            "pid": pid,
            "name": nome,
            "cpu_percent": round(min(95.0, random.uniform(2, 40) * fator), 2),
            "ram_percent": round(min(90.0, random.uniform(2, 25) * fator), 2),
            "username": "simulador",
            "create_time": inicio_lote.timestamp(),
            "timestamp_lote": ts_lote_str,
            "Endereco MAC": mac,
        })

    return pd.DataFrame(linhas_processos)


def gerar_lote_simulado(
    mac: str,
    inicio_lote: datetime,
    pasta_saida: Path,
    qtd_leituras: int = 3,
    intervalo_seg: int = 10,
):
    pico = eh_horario_pico(inicio_lote)
    fator = random.uniform(1.25, 1.6) if pico else random.uniform(0.7, 1.05)

    linhas_captura = []
    ts_lote_str = inicio_lote.strftime("%Y-%m-%d %H:%M:%S")

    for i in range(qtd_leituras):
        dt_coleta = inicio_lote + timedelta(seconds=i * intervalo_seg)
        cpu = round(min(99.5, max(5.0, random.uniform(20, 55) * fator)), 2)
        ram = round(min(98.0, max(15.0, random.uniform(35, 65) * fator)), 2)
        disco = round(min(95.0, max(10.0, random.uniform(30, 75))), 2)

        linhas_captura.append({
            "cpu total(%)": cpu,
            "ram(%)": ram,
            "disco(%)": disco,
            "Quando foi Coletado": dt_coleta.strftime("%Y-%m-%d %H:%M:%S"),
            "Rede recebida(Mbps)": round(max(0.0, random.uniform(10, 120) * fator), 2),
            "Rede enviada(Mbps)": round(max(0.0, random.uniform(5, 60) * fator), 2),
            "Frequencia de uso da CPU(MHz)": round(random.uniform(1800, 3600), 2),
            "Endereco MAC": mac,
            "Pacotes Descartados entrada": random.randint(0, 5 if pico else 1),
            "Pacotes descartados saida": random.randint(0, 3 if pico else 1),
            "erros entrada": 0,
            "erros saida": 0,
            "perda pacotes": round(random.uniform(0.0, 2.5 if pico else 0.5), 2),
            "timestamp_lote": ts_lote_str,
            "origem_dado": "simulado",
            "temperatura externa(C)": temperatura_simulada(dt_coleta),
        })

    df_processos = gerar_processos(mac=mac, inicio_lote=inicio_lote, fator=fator)

    selo = inicio_lote.strftime("%Y%m%d_%H%M%S")
    mac_limpo = mac.replace(":", "")

    pasta_lote = pasta_saida / mac_limpo / inicio_lote.strftime("%Y/%m/%d")
    pasta_lote.mkdir(parents=True, exist_ok=True)

    arq_captura = pasta_lote / f"dados_{mac_limpo}_{selo}.csv"
    arq_processos = pasta_lote / f"processos_{mac_limpo}_{selo}.csv"

    pd.DataFrame(linhas_captura)[COLUNAS_CAPTURA].to_csv(arq_captura, index=False)
    df_processos.to_csv(arq_processos, index=False)


def gerar_simulacao(
    macs: list[str],
    dias: int = 2,
    passo_minutos: int = 5,
    pasta_saida: str = "simulacoes_output",
):
    base_dir = Path(pasta_saida)
    fim = datetime.now().replace(microsecond=0)
    inicio = fim - timedelta(days=dias)

    atual = inicio
    total_lotes = 0
    while atual <= fim:
        for mac in macs:
            gerar_lote_simulado(mac, atual, base_dir)
            total_lotes += 1
        atual += timedelta(minutes=passo_minutos)

    print(f"Simulação concluída: {total_lotes} lotes gerados em '{base_dir}'.")


if __name__ == "__main__":
    macs_simulados = [
        "AA:BB:CC:11:22:01",
        "AA:BB:CC:11:22:02",
    ]
    gerar_simulacao(macs=macs_simulados, dias=2, passo_minutos=5)
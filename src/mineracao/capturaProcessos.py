import psutil
import pandas as pd
from getmac import get_mac_address
from datetime import datetime
import time

def capturarProcessos(timestamp_lote):
    processos = []
    data_lote = timestamp_lote.strftime("%Y-%m-%d %H:%M:%S")

    for processo in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent', 'username', 'create_time']): 
        processos.append({
            'pid': processo.info['pid'],
            'name': processo.info['name'],
            'cpu_percent': processo.info['cpu_percent'],
            'ram_percent': processo.info['memory_percent'],
            'username': processo.info['username'],
            'create_time': processo.info['create_time'],
            'timestamp_lote': data_lote,
            'Endereco MAC': get_mac_address()

        })

        

    return pd.DataFrame(processos);


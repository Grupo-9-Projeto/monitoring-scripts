import psutil
import pandas as pd
from datetime import datetime
import time

def capturarProcessos():
    processos = []
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S") 


    for processo in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent', 'username', 'create_time']): 
        processos.append({
            'pid': processo.info['pid'],
            'name': processo.info['name'],
            'cpu_percent': processo.info['cpu_percent'],
            'ram_percent': processo.info['memory_percent'],
            'username': processo.info['username'],
            'create_time': processo.info['create_time'],
            'timestamp': timestamp
        })
        

    return pd.DataFrame(processos);


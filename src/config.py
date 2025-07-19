import os
from datetime import datetime

def today():
    return datetime.now().strftime('%Y-%m-%d')

OUTPUT_PATHS_PROCESSED = {
    'pichau_cpu': os.path.join('data', 'processed', 'pichau', 'cpus', f'cpus_{today()}.csv'),
    'pichau_gpu': os.path.join('data', 'processed', 'pichau', 'gpus', f'gpus_{today()}.csv'),
    'kabum_cpu': os.path.join('data', 'processed', 'kabum', 'cpus', f'cpus_{today()}.csv'),
    'kabum_gpu': os.path.join('data', 'processed', 'kabum', 'gpus', f'gpus_{today()}.csv'),
    'terabyte_cpu': os.path.join('data', 'processed', 'terabyte', 'cpus', f'cpus_{today()}.csv'),
    'terabyte_gpu': os.path.join('data', 'processed', 'terabyte', 'gpus', f'gpus_{today()}.csv'),
} 

OUTPUT_PATHS_RAW = {
    'pichau_cpu_raw': os.path.join('data', 'raw', 'pichau', 'cpus', f'cpus_{today()}.csv'),
    'pichau_gpu_raw': os.path.join('data', 'raw', 'pichau', 'gpus', f'gpus_{today()}.csv'),
    'kabum_cpu_raw': os.path.join('data', 'raw', 'kabum', 'cpus', f'cpus_{today()}.csv'),
    'kabum_gpu_raw': os.path.join('data', 'raw', 'kabum', 'gpus', f'gpus_{today()}.csv'),
    'terabyte_cpu_raw': os.path.join('data', 'raw', 'terabyte', 'cpus', f'cpus_{today()}.csv'),
    'terabyte_gpu_raw': os.path.join('data', 'raw', 'terabyte', 'gpus', f'gpus_{today()}.csv'),
}
from src.extraction.pichau_scraper import pichau_cpu_scraper, pichau_gpu_scraper
from src.extraction.kabum_scraper import kabum_cpu_scraper, kabum_gpu_scraper
from src.extraction.terabyte_scraper import terabyte_cpu_scraper, terabyte_gpu_scraper
from src.transform.transform import transform_raw_data
from src.load.load import save_to_csv, save_to_database
from src.config import OUTPUT_PATHS_PROCESSED, OUTPUT_PATHS_RAW
from src.logger import get_logger
import pandas as pd

def run_pipeline():
    logger = get_logger()
    logger.info("Iniciando pipeline ETL...")

    # Extração
    logger.info("Extraindo dados da Pichau...")
    pichau_cpu = pd.DataFrame(pichau_cpu_scraper())
    pichau_gpu = pd.DataFrame(pichau_gpu_scraper())

    logger.info("Extraindo dados da Kabum...")
    kabum_cpu = pd.DataFrame(kabum_cpu_scraper())
    kabum_gpu = pd.DataFrame(kabum_gpu_scraper())
    
    logger.info("Extraindo dados da Terabyte...")
    terabyte_cpu = pd.DataFrame(terabyte_cpu_scraper())
    terabyte_gpu = pd.DataFrame(terabyte_gpu_scraper())

    # Salvar dados brutos
    logger.info("Salvando dados brutos...")
    save_to_csv(pichau_cpu, OUTPUT_PATHS_RAW['pichau_cpu_raw'])
    save_to_csv(pichau_gpu, OUTPUT_PATHS_RAW['pichau_gpu_raw'])

    save_to_csv(kabum_cpu, OUTPUT_PATHS_RAW['kabum_cpu_raw'])
    save_to_csv(kabum_gpu, OUTPUT_PATHS_RAW['kabum_gpu_raw'])
    
    save_to_csv(terabyte_cpu, OUTPUT_PATHS_RAW['terabyte_cpu_raw'])
    save_to_csv(terabyte_gpu, OUTPUT_PATHS_RAW['terabyte_gpu_raw'])


    # Transformação
    logger.info("Transformando dados...")
    pichau_cpu_t = transform_raw_data(pichau_cpu)
    pichau_gpu_t = transform_raw_data(pichau_gpu)

    kabum_cpu_t = transform_raw_data(kabum_cpu)
    kabum_gpu_t = transform_raw_data(kabum_gpu)

    terabyte_cpu_t = transform_raw_data(terabyte_cpu)
    terabyte_gpu_t = transform_raw_data(terabyte_gpu)

    # Salvar dados transformados
    logger.info("Salvando dados transformados...")
    save_to_csv(pichau_cpu_t, OUTPUT_PATHS_PROCESSED['pichau_cpu'])
    save_to_csv(pichau_gpu_t, OUTPUT_PATHS_PROCESSED['pichau_gpu'])

    save_to_csv(kabum_cpu_t, OUTPUT_PATHS_PROCESSED['kabum_cpu'])
    save_to_csv(kabum_gpu_t, OUTPUT_PATHS_PROCESSED['kabum_gpu'])

    save_to_csv(terabyte_cpu_t, OUTPUT_PATHS_PROCESSED['terabyte_cpu'])
    save_to_csv(terabyte_gpu_t, OUTPUT_PATHS_PROCESSED['terabyte_gpu'])

    # Persistir dados no Banco de Dados
    logger.info("Salvando dados no Banco de Dados...")
    save_to_database(pichau_cpu_t, 'cpus')
    save_to_database(pichau_gpu_t, 'gpus')

    save_to_database(kabum_cpu_t, 'cpus')
    save_to_database(kabum_gpu_t, 'gpus')

    save_to_database(terabyte_cpu_t, 'cpus')
    save_to_database(terabyte_gpu_t, 'gpus')

    logger.info("Pipeline ETL finalizado.") 
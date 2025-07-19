import pandas as pd
import os
from src.logger import get_logger
from sqlalchemy import create_engine
from dotenv import load_dotenv

load_dotenv()

DB_USER = os.getenv("POSTGRESQL_USER")
DB_PASSWORD = os.getenv("POSTGRESQL_PASSWORD")
DB_HOST = os.getenv("POSTGRESQL_HOST")
DB_PORT = os.getenv("POSTGRESQL_PORT")
DB_NAME = os.getenv("DB_NAME")

DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"


def save_to_csv(df: pd.DataFrame, path: str):
    logger = get_logger()
    try:
        os.makedirs(os.path.dirname(path), exist_ok=True)
        df.to_csv(path, index=False)
        logger.info(f"Arquivo salvo com sucesso em: {path}")
    except Exception as e:
        logger.error(f"Erro ao salvar arquivo em {path}: {e}") 


def save_to_postgresql(df: pd.DataFrame, table_name: str):
    logger = get_logger()
    try:
        engine = create_engine(DATABASE_URL)
        df.to_sql(table_name, engine, index=False, if_exists='append')
        logger.info(f"Tabela '{table_name}' salva com sucesso no PostgreSQL.")
    except Exception as e:
        logger.error(f"Erro ao salvar tabela '{table_name}' no PostgreSQL: {e}")


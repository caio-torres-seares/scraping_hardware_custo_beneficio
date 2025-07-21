import pandas as pd
import os
from src.logger import get_logger
from sqlalchemy import create_engine, inspect
from dotenv import load_dotenv

load_dotenv()

DB_USER = os.getenv("POSTGRESQL_USER")
DB_PASSWORD = os.getenv("POSTGRESQL_PASSWORD")
DB_HOST = os.getenv("POSTGRESQL_HOST")
DB_PORT = os.getenv("POSTGRESQL_PORT")
DB_NAME = os.getenv("DB_NAME")

DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"


logger = get_logger()

def save_to_csv(df: pd.DataFrame, path: str):
    if df.empty:
        logger.warning("DataFrame vazio. Nenhum dado será salvo.")
        return
    try:
        os.makedirs(os.path.dirname(path), exist_ok=True)
        df.to_csv(path, index=False)
        logger.info(f"Arquivo salvo com sucesso em: {path}")
    except Exception as e:
        logger.error(f"Erro ao salvar arquivo em {path}: {e}") 


def save_to_database(df: pd.DataFrame, table_name: str):
    if df.empty:
        logger.warning("DataFrame vazio. Nenhum dado será salvo.")
        return
    
    save_to_postgresql(df, table_name)


def save_to_postgresql(df: pd.DataFrame, table_name: str):
    try:
        engine = create_engine(DATABASE_URL)
        inspector = inspect(engine)
        
        # 1. Verifica se a tabela existe e obtém a última data
        if inspector.has_table(table_name):
            # Busca registros existentes com as mesmas datas, lojas, base_model e cash_price
            existing_query = f"SELECT extraction_date, store, base_model, cash_price FROM {table_name}"
            existing_df = pd.read_sql_query(existing_query, engine)

            if existing_df.empty:
                new_data = df
            else:
                # Converte as colunas de data para o formato adequado: YYYY-MM-DD
                df['extraction_date'] = pd.to_datetime(df['extraction_date'], errors='coerce').dt.date
                existing_df['extraction_date'] = pd.to_datetime(existing_df['extraction_date'], errors='coerce').dt.date

                # Faz merge com base nos campos relevantes
                merge_keys = ['extraction_date', 'store', 'base_model', 'cash_price']
                df_merged = df.merge(existing_df, on=merge_keys, how='left', indicator=True)

                new_data = df_merged[df_merged['_merge'] == 'left_only'].drop(columns=['_merge'])
    
        else:
            new_data = df  # Tabela não existe (primeira inserção)
        
        # 2. Insere apenas dados novos
        if not new_data.empty:
            new_data.to_sql(
                table_name,
                engine,
                index=False,
                if_exists='append'
            )
            logger.info(f"Dados inseridos na tabela '{table_name}': {len(new_data)} registros")
        else:
            logger.info(f"Sem novos dados da {df['store'].iloc[0]} para inserir em '{table_name}'. Data mais recente já existe.")
            
    except Exception as e:
        logger.error(f"Erro ao salvar tabela '{table_name}': {e}")

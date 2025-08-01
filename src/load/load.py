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
        logger.warning("Empty DataFrame. No data will be saved.")
        return
    try:
        os.makedirs(os.path.dirname(path), exist_ok=True)
        df.to_csv(path, index=False)
        # em ingles
        logger.info(f"File saved successfully in: {path}")
    except Exception as e:
        logger.error(f"Error saving file in {path}: {e}") 


def save_to_database(df: pd.DataFrame, table_name: str):
    if df.empty:
        # em ingles
        logger.warning("Empty DataFrame. No data will be saved.")
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
            logger.info(f"Inserting {len(new_data)} records from {df['store'].iloc[0]} into table '{table_name}'")
        else:
            logger.info(f"No new data from {df['store'].iloc[0]} to insert into table '{table_name}'. Most recent date already exists.")
            
    except Exception as e:
        logger.error(f"Error saving in table '{table_name}': {e}")

def load_from_database(table_name: str) -> pd.DataFrame:
    try:
        engine = create_engine(DATABASE_URL)
        df = pd.read_sql_table(table_name, engine)
        logger.info(f"Loaded {len(df)} records from table '{table_name}'")

        return df
    except Exception as e:
        logger.error(f"Error loading table '{table_name}': {e}")
        return pd.DataFrame()
    
# função pra buscar os dados mais recentes do banco
def load_latest_data_from_database(table_name: str) -> pd.DataFrame:
    """
    Carrega dados de uma tabela específica no PostgreSQL, mas APENAS
    para a data de extração mais recente disponível naquela tabela.
    """
    logger = get_logger()
    logger.info(f"Carregando dados mais recentes da tabela: {table_name}")
    
    try:
        engine = create_engine(DATABASE_URL)
        
        # Esta query SQL primeiro encontra a data mais recente na tabela
        # e depois seleciona todas as linhas que correspondem a essa data.
        query = f"""
            SELECT *
            FROM {table_name}
            WHERE extraction_date = (SELECT MAX(extraction_date) FROM {table_name});
        """
        
        with engine.connect() as connection:
            df = pd.read_sql(query, connection)
        
        logger.info(f"✅ {len(df)} linhas carregadas com sucesso da extração mais recente.")
        return df

    except Exception as e:
        logger.error(f"❌ Erro ao carregar dados do PostgreSQL: {e}")
        return pd.DataFrame() # Retorna um DataFrame vazio em caso de erro

def load_product_history_from_database(table_name: str, base_model: str) -> pd.DataFrame:
    """
    Busca no banco de dados o histórico de preços completo para uma chave de produto normalizada específica.
    """
    try:
        logger = get_logger()

        engine = create_engine(DATABASE_URL)
        table_name = table_name.lower()

        query = f"""
            SELECT extraction_date, cash_price, store
            FROM {table_name}
            WHERE base_model = %(model)s
        """
        params = {'model': base_model}

        logger.info(f"Buscando histórico para o modelo '{base_model}' na tabela '{table_name}'")


        with engine.connect() as connection:
            df_history = pd.read_sql(query, connection, params=params)
            
        return df_history

    except Exception as e:
        print(f"Erro ao buscar histórico do produto {base_model}: {e}")
        return pd.DataFrame() # Retorna um DataFrame vazio em caso de erro

import pandas as pd
import numpy as np


def clean_price(price_str: str) -> float:
    if not isinstance(price_str, str):
        return np.nan
    try:
        # Remove o símbolo da moeda, espaços, e o separador de milhar. Troca a vírgula decimal por ponto.
        cleaned_str = price_str.replace("R$", "").strip().replace(".", "").replace(",", ".")
        return float(cleaned_str)
    except (ValueError, AttributeError):
        return np.nan

def transform_raw_data(raw_df: pd.DataFrame) -> pd.DataFrame:
    df = raw_df.copy()
    
    print("Iniciando transformação: Normalizando colunas numéricas...")

    # 1. Normaliza as colunas de preço e parcelas para o formato numérico
    df['cash_price'] = df['cash_price'].apply(clean_price)
    df['installments'] = pd.to_numeric(df['installments'], errors='coerce')
    df['installment_price'] = pd.to_numeric(df['installment_price'], errors='coerce')

    print(f"Encontrados {len(df)} itens brutos. Descartando itens sem estoque (sem preço)...")
    # 2. Descarta os itens sem preço à vista (considerados fora de estoque)
    # .dropna() remove as linhas onde o valor na coluna 'cash_price' é Nulo/NaN, pois significa que o item não está em estoque
    df.dropna(subset=['cash_price'], inplace=True)
    print(f"Restaram {len(df)} itens em estoque.")

    # Se não sobrar nenhum item após o filtro, retorna um DataFrame vazio para evitar erros
    if df.empty:
        return pd.DataFrame()
    
    # 4. Garante que os tipos de dados estejam corretos (ex: Int64 para parcelas, que lida com nulos)
    df['installments'] = df['installments'].astype('Int64')

    # 5. Adiciona uma coluna com a data de extração
    df['extraction_date'] = pd.to_datetime('today').strftime('%Y-%m-%d')

    print("Transformação concluída.")
    return df
import sys
import streamlit as st
import pandas as pd
import re
import os
import locale

# Garante que o Python encontre os módulos na pasta src
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from src.load.load import load_from_database

# --- Configuração de Localização para Moeda Brasileira (NOVA IMPLEMENTAÇÃO) ---
try:
    locale.setlocale(locale.LC_ALL, 'pt_BR.UTF-8')
except locale.Error:
    locale.setlocale(locale.LC_ALL, 'Portuguese_Brazil.1252') # Fallback para Windows

# --- Funções de Apoio (Parsing e Análise) ---

def normalizar_nome_cpu(nome):
    if not isinstance(nome, str):
        return ""
    n = nome.lower()
    n = re.sub(r'\b(amd|intel|core|ryzen|ultra)\b', '', n)
    n = n.replace('-', ' ')
    n = re.sub(r'[^a-z0-9\s]', '', n)
    partes = sorted(n.split())
    return " ".join(partes)

def normalizar_nome_gpu(nome):
    if not isinstance(nome, str):
        return ""
    n = nome.lower()
    n = n.replace('-', ' ')
    n = re.sub(r'[^a-z0-9\s]', '', n)
    partes = sorted(n.split())
    return " ".join(partes)

def formatar_preco(preco):
    """Formata um número para o padrão de moeda brasileiro."""
    if pd.isna(preco):
        return "N/A"
    return locale.currency(preco, grouping=True)

def analyze_cost_benefit_ratio(df):
    df['cost_benefit_ratio'] = df['Pontuação'] / df['cash_price']
    return df

@st.cache_data
def carregar_dados():
    try:
        df_benchmarks_cpu = pd.read_csv('benchmarks/results/cpu/2025_media_games.csv')
        df_db_cpu = load_from_database("cpus")

        df_benchmarks_gpu = pd.read_csv('benchmarks/results/gpu/2025_media_games.csv')
        df_db_gpu = load_from_database("gpus")

    except FileNotFoundError as e:
        st.error("❌ Ocorreu um erro ao carregar os dados. Verifique os caminhos dos arquivos.")
        st.stop()

    # CPU
    df_benchmarks_cpu['chave_normalizada'] = df_benchmarks_cpu['Processador'].apply(normalizar_nome_cpu)
    df_db_cpu['chave_normalizada'] = (df_db_cpu['variant'] + ' ' + df_db_cpu['base_model']).apply(normalizar_nome_cpu)

    df_cpu = pd.merge(df_db_cpu, df_benchmarks_cpu, on='chave_normalizada', how='inner')
    df_cpu = analyze_cost_benefit_ratio(df_cpu)
    df_cpu['cash_price_formatted'] = df_cpu['cash_price'].apply(formatar_preco) # Formata o preço

    # Mantém apenas o produto mais barato para cada modelo de CPU
    df_cpu = df_cpu.loc[df_cpu.groupby('chave_normalizada')['cash_price'].idxmin()].reset_index(drop=True)

    # GPU
    df_benchmarks_gpu['chave_normalizada'] = df_benchmarks_gpu['Placa de Vídeo'].apply(normalizar_nome_gpu)
    df_db_gpu['chave_normalizada'] = df_db_gpu['base_model'].apply(normalizar_nome_gpu)

    df_gpu = pd.merge(df_db_gpu, df_benchmarks_gpu, on='chave_normalizada', how='inner')
    df_gpu = analyze_cost_benefit_ratio(df_gpu)
    df_gpu['cash_price_formatted'] = df_gpu['cash_price'].apply(formatar_preco) # Formata o preço

    # Mantém apenas o produto mais barato para cada modelo de GPU
    df_gpu = df_gpu.loc[df_gpu.groupby('chave_normalizada')['cash_price'].idxmin()].reset_index(drop=True)

    return df_cpu, df_gpu

# --- Interface Streamlit ---
st.set_page_config(page_title="Ranking de Hardware", layout="wide", initial_sidebar_state="expanded")
st.title("⚙️ Análise de Custo-Benefício de Hardware")

df_cpu, df_gpu = carregar_dados()

st.sidebar.header("Filtros 🔎")
tipo_produto = st.sidebar.radio("Selecione o Tipo de Hardware", ["CPUs", "GPUs"], key="tipo_produto")

# Filtros dinâmicos baseados na seleção do usuário
if tipo_produto == "CPUs" and not df_cpu.empty:
    df_selecionado = df_cpu
    marcas = st.sidebar.multiselect("Marca", options=df_selecionado['brand'].unique(), default=df_selecionado['brand'].unique(), key="cpu_brand")
    lojas = st.sidebar.multiselect("Loja", options=df_selecionado['store'].unique(), default=df_selecionado['store'].unique(), key="cpu_store")
    faixa_preco = st.sidebar.slider(
        "Faixa de Preço (R$)",
        min_value=float(df_selecionado['cash_price'].min()),
        max_value=float(df_selecionado['cash_price'].max()),
        value=(float(df_selecionado['cash_price'].min()), float(df_selecionado['cash_price'].max())),
        key="cpu_price"
    )
    df_filtrado = df_selecionado[
        (df_selecionado['brand'].isin(marcas)) &
        (df_selecionado['store'].isin(lojas)) &
        (df_selecionado['cash_price'] >= faixa_preco[0]) &
        (df_selecionado['cash_price'] <= faixa_preco[1])
    ]
    nome_coluna_modelo = "Processador"

elif tipo_produto == "GPUs" and not df_gpu.empty:
    df_selecionado = df_gpu
    marcas = st.sidebar.multiselect("Marca", options=df_selecionado['brand'].unique(), default=df_selecionado['brand'].unique(), key="gpu_brand")
    fabricantes = st.sidebar.multiselect("Fabricante", options=df_selecionado['manufacturer'].unique(), default=df_selecionado['manufacturer'].unique(), key="gpu_manufacturer")
    lojas = st.sidebar.multiselect("Loja", options=df_selecionado['store'].unique(), default=df_selecionado['store'].unique(), key="gpu_store")
    faixa_preco = st.sidebar.slider(
        "Faixa de Preço (R$)",
        min_value=float(df_selecionado['cash_price'].min()),
        max_value=float(df_selecionado['cash_price'].max()),
        value=(float(df_selecionado['cash_price'].min()), float(df_selecionado['cash_price'].max())),
        key="gpu_price"
    )
    df_filtrado = df_selecionado[
        (df_selecionado['brand'].isin(marcas)) &
        (df_selecionado['manufacturer'].isin(fabricantes)) &
        (df_selecionado['store'].isin(lojas)) &
        (df_selecionado['cash_price'] >= faixa_preco[0]) &
        (df_selecionado['cash_price'] <= faixa_preco[1])
    ]
    nome_coluna_modelo = "Placa de Vídeo"
else:
    df_filtrado = pd.DataFrame() # Cria um dataframe vazio se não houver dados

# --- Painel Principal ---
st.header(f"Analisando {tipo_produto}")

if df_filtrado.empty:
    st.warning("Nenhum produto encontrado com os filtros selecionados.")
else:
    st.subheader("📈 Métricas Gerais")
    col1, col2, col3 = st.columns(3)
    col1.metric(f"Total de {tipo_produto}", df_filtrado.shape[0])
    col2.metric("Pontuação Máxima", f"{df_filtrado['Pontuação'].max():.0f}")
    col3.metric("Melhor Custo-Benefício", f"{df_filtrado['cost_benefit_ratio'].max():.2f}")

    st.subheader("🔥 Top 10 por Pontuação")
    st.dataframe(
        df_filtrado.sort_values(by="Pontuação", ascending=False).head(10),
        column_config={
            nome_coluna_modelo: "Modelo",
            "cash_price": None, # Esconde a coluna numérica original
            "cash_price_formatted": "Preço", # Mostra a coluna formatada
            "Pontuação": st.column_config.ProgressColumn("Pontuação", format="%d", min_value=0, max_value=int(df_filtrado["Pontuação"].max())),
            "store": "Loja",
            "link": st.column_config.LinkColumn("Link da Loja", display_text="Ver na Loja")
        },
        column_order=[nome_coluna_modelo, "Pontuação", "cash_price_formatted", "store", "link"],
        hide_index=True
    )

    st.subheader("💸 Top 10 por Custo-Benefício")
    st.dataframe(
        df_filtrado.sort_values(by="cost_benefit_ratio", ascending=False).head(10),
        column_config={
            nome_coluna_modelo: "Modelo",
            "cash_price": None, # Esconde a coluna numérica original
            "cash_price_formatted": "Preço", # Mostra a coluna formatada
            "Pontuação": "Pontuação",
            "cost_benefit_ratio": st.column_config.NumberColumn("Custo-Benefício (Pontos/R$)", format="%.2f"),
            "store": "Loja",
            "link": st.column_config.LinkColumn("Link da Loja", display_text="Ver na Loja")
        },
        column_order=[nome_coluna_modelo, "cost_benefit_ratio", "Pontuação", "cash_price_formatted", "store", "link"],
        hide_index=True
    )

    st.subheader("📊 Gráficos Interativos")
    st.scatter_chart(df_filtrado, x="cash_price", y="Pontuação", color="store", size="cost_benefit_ratio",
                     x_label="Preço (R$)", y_label="Pontuação de Benchmark")

    st.bar_chart(df_filtrado.sort_values(by="cost_benefit_ratio", ascending=False).head(20).set_index(nome_coluna_modelo)['cost_benefit_ratio'])

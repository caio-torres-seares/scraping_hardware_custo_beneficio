import sys
import streamlit as st
import plotly.express as px
import pandas as pd
import re
import os
import locale


# Garante que o Python encontre os módulos na pasta src
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
if project_root not in sys.path:
    sys.path.append(project_root)

from src.load.load import load_latest_data_from_database, load_product_history_from_database

try:
    locale.setlocale(locale.LC_ALL, 'pt_BR.UTF-8')
except locale.Error:
    locale.setlocale(locale.LC_ALL, 'Portuguese_Brazil.1252') # Fallback para Windows

def normalizar_nome_cpu(nome):
    if not isinstance(nome, str): return ""
    n = nome.lower()
    n = re.sub(r'\b(amd|intel|core|ryzen|ultra)\b', '', n)
    n = n.replace('-', ' ')

    n = re.sub(r'(\d+k)f$', r'\1', n) # Trata o caso 'KF' -> 'K'
    n = re.sub(r'(\d+)f$', r'\1', n)  # Trata o caso 'F' -> ''

    n = re.sub(r'[^a-z0-9\s]', '', n)
    return " ".join(sorted(n.split()))

def normalizar_nome_gpu(nome):
    if not isinstance(nome, str): return ""
    n = nome.lower()
    n = n.replace('-', ' ')
    n = re.sub(r'[^a-z0-9\s]', '', n)
    return " ".join(sorted(n.split()))

def formatar_preco(preco):
    if pd.isna(preco): return "N/A"
    return locale.currency(preco, grouping=True)

def analyze_cost_benefit_ratio(df):
    if not df.empty:
        df['cost_benefit_ratio'] =  df['cash_price'] / df['Pontuação']
        df['cost_benefit_ratio_formatted'] = df['cost_benefit_ratio'].apply(formatar_preco)
    return df

@st.cache_data
def carregar_e_processar_dados():
    try:
        df_db_cpu_full = load_latest_data_from_database("cpus")
        df_db_gpu_full = load_latest_data_from_database("gpus")
        df_benchmarks_cpu = pd.read_csv('benchmarks/results/cpu/2025_media_games.csv')
        df_benchmarks_gpu = pd.read_csv('benchmarks/results/gpu/2025_media_games.csv')
    except Exception as e:
        st.error(f"❌ Erro ao carregar os dados: {e}. Verifique a conexão com o banco e os arquivos de benchmark.")
        st.stop()

    # Filtra para manter apenas os dados da extração mais recente
    if not df_db_cpu_full.empty:
        latest_date_cpu = df_db_cpu_full['extraction_date'].max()
        df_db_cpu = df_db_cpu_full[df_db_cpu_full['extraction_date'] == latest_date_cpu].copy()
    else:
        df_db_cpu = pd.DataFrame()

    if not df_db_gpu_full.empty:
        latest_date_gpu = df_db_gpu_full['extraction_date'].max()
        df_db_gpu = df_db_gpu_full[df_db_gpu_full['extraction_date'] == latest_date_gpu].copy()
    else:
        df_db_gpu = pd.DataFrame()

    # --- Processamento de CPU ---
    if not df_db_cpu.empty:
        df_benchmarks_cpu['chave_normalizada'] = df_benchmarks_cpu['Processador'].apply(normalizar_nome_cpu)
        df_db_cpu['chave_normalizada'] = (df_db_cpu['variant'] + ' ' + df_db_cpu['base_model']).apply(normalizar_nome_cpu)
        df_cpu_all = pd.merge(df_db_cpu, df_benchmarks_cpu, on='chave_normalizada', how='inner')
        if not df_cpu_all.empty:
            df_cpu_all = analyze_cost_benefit_ratio(df_cpu_all)
            df_cpu_all['cash_price_formatted'] = df_cpu_all['cash_price'].apply(formatar_preco)
    else:
        df_cpu_all = pd.DataFrame()

    # --- Processamento de GPU ---
    if not df_db_gpu.empty:
        df_benchmarks_gpu['chave_normalizada'] = df_benchmarks_gpu['Placa de Vídeo'].apply(normalizar_nome_gpu)
        df_db_gpu['chave_normalizada'] = df_db_gpu['base_model'].apply(normalizar_nome_gpu)
        df_gpu_all = pd.merge(df_db_gpu, df_benchmarks_gpu, on='chave_normalizada', how='inner')
        if not df_gpu_all.empty:
            df_gpu_all = analyze_cost_benefit_ratio(df_gpu_all)
            df_gpu_all['cash_price_formatted'] = df_gpu_all['cash_price'].apply(formatar_preco)
    else:
        df_gpu_all = pd.DataFrame()

    return df_cpu_all, df_gpu_all

# --- Interface Streamlit ---
st.set_page_config(page_title="Ranking de Hardware", layout="wide", initial_sidebar_state="expanded")
st.title("⚙️ Análise de Custo-Benefício de Hardware")

df_cpu_all, df_gpu_all = carregar_e_processar_dados()

latest_extraction_date_cpu = df_cpu_all['extraction_date'].max()
latest_extraction_date_gpu = df_gpu_all['extraction_date'].max()

st.sidebar.header("Filtros 🔎")
tipo_produto = st.sidebar.radio("Selecione o Tipo de Hardware", ["CPUs", "GPUs"], key="tipo_produto")


if tipo_produto == "CPUs":
    df_all = df_cpu_all
    nome_coluna_modelo = "Processador"

    if latest_extraction_date_cpu:
        formatted_date = pd.to_datetime(latest_extraction_date_cpu).strftime('%d/%m/%Y')
        st.caption(f"🗓️ Preços de CPUs atualizados em: **{formatted_date}**")
else:
    df_all = df_gpu_all
    nome_coluna_modelo = "Placa de Vídeo"

    if latest_extraction_date_gpu:
        formatted_date = pd.to_datetime(latest_extraction_date_gpu).strftime('%d/%m/%Y')
        st.caption(f"🗓️ Preços de GPUs atualizados em: **{formatted_date}**")

# Filtros dinâmicos
if not df_all.empty:
    marcas = st.sidebar.multiselect("Marca", options=sorted(df_all['brand'].unique()), default=sorted(df_all['brand'].unique()))
    lojas = st.sidebar.multiselect("Loja", options=sorted(df_all['store'].unique()), default=sorted(df_all['store'].unique()))
    faixa_preco = st.sidebar.slider(
        "Faixa de Preço (R$)",
        min_value=float(df_all['cash_price'].min()),
        max_value=float(df_all['cash_price'].max()),
        value=(float(df_all['cash_price'].min()), float(df_all['cash_price'].max()))
    )
    df_filtrado_all = df_all[
        (df_all['brand'].isin(marcas)) &
        (df_all['store'].isin(lojas)) &
        (df_all['cash_price'] >= faixa_preco[0]) &
        (df_all['cash_price'] <= faixa_preco[1])
    ]
    if not df_filtrado_all.empty:
        df_filtrado_cheapest = df_filtrado_all.loc[df_filtrado_all.groupby('chave_normalizada')['cash_price'].idxmin()]
    else:
        df_filtrado_cheapest = pd.DataFrame()
else:
    df_filtrado_all = pd.DataFrame()
    df_filtrado_cheapest = pd.DataFrame()

# --- Painel Principal ---
st.header(f"Analisando {tipo_produto}")

if df_filtrado_cheapest.empty:
    st.warning("Nenhum produto encontrado com os filtros selecionados.")
else:
    st.subheader("📈 Métricas Gerais")
    col1, col2, col3 = st.columns(3)
    col1.metric(f"Modelos Únicos", df_filtrado_cheapest.shape[0])
    col2.metric("Pontuação Máxima", f"{df_filtrado_cheapest['Pontuação'].max():.0f}")
    col3.metric("Melhor Custo-Benefício", f"{df_filtrado_cheapest['cost_benefit_ratio_formatted'].min()}")
    
    st.subheader("🔍 Ver todas as ofertas para um modelo")
    
    modelos_disponiveis = df_filtrado_cheapest[nome_coluna_modelo].unique().tolist()
    
    modelo_selecionado = st.selectbox(
        "Selecione um modelo das listas abaixo para ver todas as ofertas:",
        options=modelos_disponiveis, index=None, placeholder="Escolha um modelo..."
    )

    if modelo_selecionado:
        chave_selecionada = df_filtrado_cheapest[df_filtrado_cheapest[nome_coluna_modelo] == modelo_selecionado]['chave_normalizada'].iloc[0]
        # Usa o dataframe com TODAS as ofertas filtradas para mostrar as opções
        opcoes_modelo = df_filtrado_all[df_filtrado_all['chave_normalizada'] == chave_selecionada].sort_values(by="cash_price")
        
        st.write(f"**Exibindo {len(opcoes_modelo)} ofertas encontradas para {modelo_selecionado}:**")
        st.dataframe(
            opcoes_modelo,
            column_config={
                "full_title": "Descrição Completa", "cash_price_formatted": "Preço",
                "store": "Loja", "link": st.column_config.LinkColumn("Link", display_text="Ver na Loja ▸")
            },
            column_order=["full_title", "cash_price_formatted", "store", "link"],
            hide_index=True, use_container_width=True
        )

        base_model_selecionado = df_filtrado_cheapest[df_filtrado_cheapest[nome_coluna_modelo] == modelo_selecionado]['base_model'].iloc[0]
        st.subheader(f"📈 Histórico de Menores Preços para {modelo_selecionado}")

        #1: Selecionar o dataframe histórico correto (CPUs ou GPUs)
        table_name = "CPUs" if tipo_produto == "CPUs" else "GPUs"
        
        #2: Filtrar o histórico para o modelo selecionado
        with st.spinner("Buscando histórico de preços..."):
            historico_do_modelo = load_product_history_from_database(
                table_name=table_name,
                base_model=base_model_selecionado
            )
        
        #3: Encontrar a oferta mais barata de cada dia de extração
        if not historico_do_modelo.empty:
            melhores_ofertas_diarias = historico_do_modelo.loc[
                historico_do_modelo.groupby('extraction_date')['cash_price'].idxmin()
            ].sort_values(by='extraction_date')

            #4: Gerar e exibir o gráfico apenas se houver histórico suficiente
            if len(melhores_ofertas_diarias) > 1:
                fig_historico = px.line(
                    melhores_ofertas_diarias,
                    x='extraction_date',
                    y='cash_price',
                    title=f'Evolução do Menor Preço Encontrado para {modelo_selecionado}',
                    markers=True, # Adiciona pontos sobre a linha para cada data
                    hover_data={
                        'store': True, # Mostra a loja no hover
                        'cash_price': ':.2f' # Formata o preço no hover
                    },
                    labels={
                        'extraction_date': 'Data da Coleta',
                        'cash_price': 'Menor Preço (R$)',
                        'store': 'Loja com Melhor Preço'
                    }
                )
                fig_historico.update_traces(line=dict(width=3))
                fig_historico.update_layout(
                    xaxis_title="Data",
                    yaxis_title="Preço (R$)"
                )
                st.plotly_chart(fig_historico, use_container_width=True)
            else:
                st.info("Não há dados históricos suficientes para gerar um gráfico de evolução de preços para este modelo.")

    st.subheader("🔥 Ranking por Pontuação (Melhor Oferta de Cada Modelo)")
    st.info("Pontuação de Benchmark. Quanto maior a pontuação, melhor o desempenho.")

    top_pontuacao = df_filtrado_cheapest.sort_values(by="Pontuação", ascending=False)

    st.dataframe(
        top_pontuacao,
        column_config={
            nome_coluna_modelo: "Modelo", 
            "cash_price": None, 
            "cash_price_formatted": "Preço (R$)",
            "Pontuação": st.column_config.ProgressColumn("Pontuação", format="%d", min_value=0, max_value=int(df_filtrado_cheapest["Pontuação"].max())),
            "cost_benefit_ratio_formatted": "Preço por Pontuação", "store": "Loja",
            "link": st.column_config.LinkColumn("Link da Melhor Oferta", display_text="Ver na Loja ▸")
        },
        column_order=[nome_coluna_modelo, "Pontuação", "cost_benefit_ratio_formatted", "cash_price_formatted", "store", "link"],
        hide_index=True, use_container_width=True
    )

    st.subheader("💸 Ranking de Custo-Benefício (Melhor Oferta de Cada Modelo)")
    st.info("Preço por pontuação. Quanto menor o Preço por pontuação, melhor o custo-benefício.")

    top_custo_beneficio = df_filtrado_cheapest.sort_values(by="cost_benefit_ratio", ascending=True)
    
    st.dataframe(
        top_custo_beneficio,
        column_config={
            nome_coluna_modelo: "Modelo", 
            "cash_price": None, 
            "cash_price_formatted": "Preço (R$)",
            "Pontuação": st.column_config.ProgressColumn("Pontuação", format="%d", min_value=0, max_value=int(df_filtrado_cheapest["Pontuação"].max())),
            "cost_benefit_ratio_formatted": "Preço por Pontuação", "store": "Loja",
            "link": st.column_config.LinkColumn("Link da Melhor Oferta", display_text="Ver na Loja ▸")
        },
        column_order=[nome_coluna_modelo, "Pontuação", "cost_benefit_ratio_formatted", "cash_price_formatted", "store", "link"],
        hide_index=True, use_container_width=True
    )


    st.subheader("📊 Gráfico Interativo de Custo vs. Performance")
    st.info("Passe o mouse sobre os pontos para ver detalhes. Use o zoom para explorar áreas específicas.")

    color_map = {
        'AMD': '#FF0000',      # Vermelho para AMD
        'NVIDIA': '#76B900',   # Verde para NVIDIA
        'INTEL': '#0071C5'     # Azul para Intel (usando INTEL em maiúsculas como no seu 'brand')
    }
    
    unique_stores = df_filtrado_cheapest['store'].unique()
    symbol_map = {store: symbol for store, symbol in zip(unique_stores, ['circle', 'square', 'diamond', 'cross', 'x'])}

    fig = px.scatter(
        df_filtrado_cheapest,
        x="cash_price",
        y="Pontuação",
        color="brand",
        symbol="store",
        log_x=True, 
        color_discrete_map=color_map,
        symbol_map=symbol_map,       
        hover_name=nome_coluna_modelo,
        hover_data={
            'cash_price_formatted': True,
            'cost_benefit_ratio': ':.2f',
            'store': True,
            'brand': False,
            'cash_price': False 
        },
        labels={
            "cash_price": "Preço (R$, Escala Log)",
            "Pontuação": "Pontuação de Benchmark",
            "brand": "Marca",
            "store": "Loja",
            "cash_price_formatted": "Preço",
            "cost_benefit_ratio": "Preço/Ponto"
        },
        title="Análise de Custo vs. Performance (Melhor Oferta por Modelo)"
    )

    fig.update_traces(marker=dict(size=10, line=dict(width=1, color='DarkSlateGrey')), selector=dict(mode='markers'))

    fig.update_layout(
        legend_title_text='Legenda',
        xaxis_title="Preço (R$) - Escala Logarítmica",
        yaxis_title="Pontuação de Benchmark"
    )

    st.plotly_chart(fig, use_container_width=True)



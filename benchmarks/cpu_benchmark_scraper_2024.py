import os
import re
import ast
from playwright.sync_api import sync_playwright
import pandas as pd

URL_BENCHMARK_CYBERPUNK = "https://benchmarks.com.br/graficos/v/22184"
URL_BENCHMARK_RDR2 = "https://benchmarks.com.br/graficos/v/22180"
URL_BENCHMARK_CINEBENCH = "https://benchmarks.com.br/graficos/v/22182"

PATH_BENCHMARK_CYBERPUNK = "benchmarks/results/cpu/2024_media_cyberpunk.csv"
PATH_BENCHMARK_RDR2 = "benchmarks/results/cpu/2024_media_rdr2.csv"
PATH_BENCHMARK_CINEBENCH = "benchmarks/results/cpu/2024_media_cinebench_multithread.csv"

def scraping_benchmark(url):
    url = url
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(url, timeout=60000)
        html_content = page.content()
        browser.close()

    # Captura o nome (grupo 1) e a pontuação (grupo 2)
    item_pattern = r"\[\s*'(.*?)',\s*(\d+),\s*'.*?'\s*,\s*'.*?'\s*\]"
    matches = re.findall(item_pattern, html_content)

    if not matches:
        print("❌ Nenhum item de benchmark foi encontrado.")
        return None

    results = []
    for match in matches:
        results.append({
            "Processador": match[0],
            "Pontuação": int(match[1]) 
        })
    return results


def save_results(results, filename):
    filename = filename
    """Salva os resultados em CSV e mostra estatísticas"""
    if not results:
        return
        
    df = pd.DataFrame(results)

    os.makedirs(os.path.dirname(filename), exist_ok=True)
    
    # Salva em CSV
    df.to_csv(filename, index=False, encoding='utf-8')
    print(f"💾 Resultados salvos em '{filename}'")

if __name__ == "__main__":

                                                    ### BENCHMARK DO CINEBENCH ###

    print("🚀 Iniciando raspagem de dados do benchmark do Cinebench...")
    
    benchmark_cinebench_results = scraping_benchmark(URL_BENCHMARK_CINEBENCH)
    
    if benchmark_cinebench_results:
        print(f"✅ Dados extraídos com sucesso! {len(benchmark_cinebench_results)} processadores encontrados.")
        
        save_results(benchmark_cinebench_results, PATH_BENCHMARK_CINEBENCH)
        
        df = pd.DataFrame(benchmark_cinebench_results)
        print(f"\n📋 PRIMEIROS 5 RESULTADOS:")
        print(df.head().to_string(index=False))
        
    else:
        print("❌ Falha na extração dos dados de benchmark do cinebench.")


                                                    ### BENCHMARK DO CYBERPUNK ###

    print("\n🚀 Iniciando raspagem de dados do benchmark do Cyberpunk...")
    
    benchmark_cyberpunk_results = scraping_benchmark(URL_BENCHMARK_CYBERPUNK)
    
    if benchmark_cyberpunk_results:
        print(f"✅ Dados extraídos com sucesso! {len(benchmark_cyberpunk_results)} processadores encontrados.")
        
        save_results(benchmark_cyberpunk_results, PATH_BENCHMARK_CYBERPUNK)
        
        df = pd.DataFrame(benchmark_cyberpunk_results)
        print(f"\n📋 PRIMEIROS 5 RESULTADOS:")
        print(df.head().to_string(index=False))
        
    else:
        print("❌ Falha na extração dos dados de benchmark do cyberpunk.")

                                                    ### BENCHMARK DO RDR2 ###

    print("\n🚀 Iniciando raspagem de dados do benchmark do Red Dead Redemption 2...")
    
    benchmark_rdr2_results = scraping_benchmark(URL_BENCHMARK_RDR2)
    
    if benchmark_rdr2_results:
        print(f"✅ Dados extraídos com sucesso! {len(benchmark_rdr2_results)} processadores encontrados.")
        
        save_results(benchmark_rdr2_results, PATH_BENCHMARK_RDR2)
        
        df = pd.DataFrame(benchmark_rdr2_results)
        print(f"\n📋 PRIMEIROS 5 RESULTADOS:")
        print(df.head().to_string(index=False))
        
    else:
        print("❌ Falha na extração dos dados de benchmark do Red Dead Redemption 2.")
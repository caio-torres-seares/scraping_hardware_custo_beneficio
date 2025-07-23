import os
import re
from playwright.sync_api import sync_playwright
import pandas as pd

URL_BENCHMARK_GAMES = "https://flo.uri.sh/visualisation/23789259/embed"

PATH_BENCHMARK_GAMES = "benchmarks/results/gpu/2025_media_games.csv"


def scraping_benchmark(url):

    url = url

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(url, timeout=20000)

        page.wait_for_selector("path.data-point", timeout=10000)

        elements = page.query_selector_all("path.data-point")
        resultados = []

        for el in elements:
            aria = el.get_attribute("aria-label")
            if aria:
                match = re.search(r",\s*(.*?):\s*(\d+)", aria)

                pontos_match = re.search(r"médio:\s*(\d+)", aria)

                if match:
                    nome = match.group(1).strip()
                    if pontos_match:
                        pontos = int(pontos_match.group(1))
                    else:
                        # Pega o valor da média, quando é benchmark de games
                        pontos = int(match.group(2))

                    resultados.append({
                        "Placa de Vídeo": nome,
                        "Pontuação": pontos
                    })

        browser.close()

    if not resultados:
        print("❌ Nenhum item de benchmark foi encontrado.")
        return None

    return resultados

def save_results(results, filename):
    filename = filename
    if not results:
        return
    df = pd.DataFrame(results)
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    df.to_csv(filename, index=False, encoding='utf-8')
    print(f"💾 Resultados salvos em '{filename}'")

if __name__ == "__main__":

                                                    ### BENCHMARK DE CINEBENCH ###
    print("🚀 Iniciando raspagem de dados do benchmark do cinebench...")
    
    benchmark_results = scraping_benchmark(URL_BENCHMARK_GAMES)
    
    if benchmark_results:
        print(f"✅ Dados extraídos com sucesso! {len(benchmark_results)} processadores encontrados.")
        save_results(benchmark_results, PATH_BENCHMARK_GAMES)
        
        df = pd.DataFrame(benchmark_results)
        print(f"\n📋 PRIMEIROS 5 RESULTADOS:")
        print(df.head().to_string(index=False))
    else:
        print("❌ Falha na extração dos dados do benchmark do cinebench.")


                                            
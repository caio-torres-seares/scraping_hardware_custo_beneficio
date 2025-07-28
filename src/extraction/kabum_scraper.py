from playwright.sync_api import sync_playwright
import pandas as pd
import sys
import os
import time

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from src.logger import get_logger


from src.extraction.scraper_utils import (
    extract_parcel_info_kabum,
    extract_gpu_memory,
    extract_brand,
    extract_cpu_model_and_variant,
    extract_gpu_model_and_variant,
    extract_cpu_socket
)

logger = get_logger()


# Kabum não padroniza a posição do nome dos fabricantes, então vamos usamos uma abordagem diferente
def extract_gpu_manufacturer_kabum(title: str) -> str:
    title_upper = title.upper()
    
    # Lista comum de fabricantes
    manufacturers = ["ASROCK", "GIGABYTE", "XFX", "MSI", "ZOTAC", "GALAX", "PNY", "EVGA", "POWER COLOR", "SAPPHIRE", "ASUS", "INNO3D", "COLORFUL", "GAINWARD", "AFOX", "PCYES"]

    for m in manufacturers:
        if m in title_upper:
            return m  
    return None 

def kabum_scraper(base_url: str, product_type: str):    
    product_type = product_type.upper()
    page_number = 1
    all_products = []
    max_pages = 3 # Até 5 páginas já é o suficiente, rendendo 100 produtos ao todo
    
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=False)  # set to False to see the browser
            page = browser.new_page(user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/114.0.0.0 Safari/537.36")
            
            while True:
                if page_number == 1:
                    url = base_url
                else:
                    url = f"{base_url}?page_number={page_number}"
                
                logger.info(f"Fazendo scraping da página {page_number}: {url}")
                
                try:
                    page.goto(url, timeout=60000)
                    
                    # Aguardar um pouco para garantir que a página carregou
                    page.wait_for_timeout(2000)
                    
                    # Get all items
                    products = page.query_selector_all('a.productLink')
                    if not products:
                        logger.info(f"Nenhum produto encontrado na página {page_number}. Parando paginação.")
                        break
                    
                    logger.info(f"Encontrados {len(products)} produtos na página {page_number}")
                    
                    for product in products:
                        try:
                            name_tag = product.query_selector("span.nameCard")
                            product_title = name_tag.inner_text().strip() if name_tag else "N/A"

                            link = product.get_attribute("href")
                            product_link = "https://www.kabum.com.br/" + link if link else "N/A"

                            price_tag = product.query_selector("span.priceCard")
                            product_price_cash = price_tag.inner_text().strip() if price_tag else None

                            product_parcel_info = extract_parcel_info_kabum(product)

                            product_brand = extract_brand(product_title)

                            product_data = {
                                "brand": product_brand,
                                "full_title": product_title, 
                                "cash_price": product_price_cash,
                                "installments": product_parcel_info["installments"],
                                "installment_price": product_parcel_info["installment_price"],
                                "link": product_link, 
                                "store": "Kabum"
                            }

                            if product_type == "CPU":
                                base_model, variant = extract_cpu_model_and_variant(product_title, product_brand)
                                product_data["socket"] = extract_cpu_socket(product_title)
                                product_data["base_model"] = base_model
                                product_data["variant"] = variant
                                
                            elif product_type == 'GPU':
                                base_model, custom_model = extract_gpu_model_and_variant(product_title, product_data["brand"])
                                product_data["manufacturer"] = extract_gpu_manufacturer_kabum(product_title)
                                product_data["base_model"] = base_model
                                product_data["custom_model"] = custom_model
                                product_data["vram_memory"] = extract_gpu_memory(product_title)

                            all_products.append(product_data)


                        except Exception as e:
                            logger.error(f"Erro ao processar um produto na página {page_number}: {e}")
                            continue
                    
                    if max_pages and page_number >= max_pages:
                        logger.info(f"Limite de {max_pages} páginas atingido.")
                        break
                    
                    page_number += 1
                    
                    time.sleep(1)
                    
                except Exception as e:
                    logger.error(f"Erro ao acessar página {page_number}: {e}")
                    break

            browser.close()
            logger.info(f"Scraping concluído. Total de {len(all_products)} {product_type} coletados de {page_number - 1} páginas.")
            return all_products
            
    except Exception as e:
        logger.error(f"Erro no scraper da Kabum para o item {product_type}: {e}")
        return []

if __name__ == "__main__":
    cpus = kabum_scraper("https://www.kabum.com.br/hardware/processadores","CPU")
    gpus = kabum_scraper("https://www.kabum.com.br/hardware/placa-de-video-vga","GPU")

    pd.options.display.max_columns = None

    df_cpus = pd.DataFrame(cpus)
    df_gpus = pd.DataFrame(gpus)

    print("CPUs:\n", df_cpus.head(50))
    print("\nGPUs:\n", df_gpus.head(50))
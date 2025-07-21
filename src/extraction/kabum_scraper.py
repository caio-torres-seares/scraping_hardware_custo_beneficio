from playwright.sync_api import sync_playwright
import pandas as pd
import sys
import os
from src.logger import get_logger

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from extraction.scraper_utils import (
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


def kabum_cpu_scraper():
    url = "https://www.kabum.com.br/hardware/processadores"
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=False)  # set to False to see the browser
            page = browser.new_page(user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/114.0.0.0 Safari/537.36")
            page.goto(url, timeout=60000)

            # Get all CPU items
            products = page.query_selector_all('a.productLink')
            if not products:
                logger.info("No CPU products found.")
                browser.close()
                return []
            
            cpus = []

            
            for product in products:
                try:
                    name_tag = product.query_selector("span.nameCard")
                    product_title = name_tag.inner_text().strip() if name_tag else "N/A"

                    link = product.get_attribute("href")
                    product_link = "https://www.kabum.com.br/produto" + link if link else "N/A"

                    price_tag = product.query_selector("span.priceCard")
                    product_price_cash = price_tag.inner_text().strip() if price_tag else None

                    product_parcel_info = extract_parcel_info_kabum(product)

                    product_socket = extract_cpu_socket(product_title)

                    product_brand = extract_brand(product_title)

                    product_cpu_base_model, product_cpu_variant = extract_cpu_model_and_variant(product_title, product_brand)

                    cpus.append({
                        "brand": product_brand,
                        "socket": product_socket,
                        "base_model": product_cpu_base_model,
                        "variant": product_cpu_variant,
                        "cash_price": product_price_cash,
                        "installments": product_parcel_info["installments"],
                        "installment_price": product_parcel_info["installment_price"],
                        "full_title": product_title,
                        "link": product_link,
                        "store": "Kabum"
                    })

                except Exception as e:
                    logger.error(f"Error processing an product: {e}")
                    continue

            browser.close()
            return cpus
    except Exception as e:
        logger.error(f"Error in Kabum CPU scraper: {e}")
        return []

def kabum_gpu_scraper():
    url = "https://www.kabum.com.br/hardware/placa-de-video-vga"
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=False)  # set to False to see the browser
            page = browser.new_page(user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/114.0.0.0 Safari/537.36")
            page.goto(url, timeout=60000)

            # Get all GPU items
            products = page.query_selector_all('a.productLink')
            if not products:
                logger.info("No GPU products found.")
                browser.close()
                return []
            
            gpus = []

            
            for product in products:
                try:
                    name_tag = product.query_selector("span.nameCard")
                    product_title = name_tag.inner_text().strip() if name_tag else "N/A"

                    link = product.get_attribute("href")
                    product_link = "https://www.kabum.com.br/produto" + link if link else "N/A"

                    price_tag = product.query_selector("span.priceCard")
                    product_price_cash = price_tag.inner_text().strip() if price_tag else None

                    product_parcel_info = extract_parcel_info_kabum(product)

                    product_memory = extract_gpu_memory(product_title)

                    product_gpu_brand = extract_brand(product_title)

                    product_manufacturer = extract_gpu_manufacturer_kabum(product_title)

                    product_gpu_base_model, product_gpu_custom_model = extract_gpu_model_and_variant(product_title, product_gpu_brand)

                    gpus.append({
                        "brand": product_gpu_brand,
                        "manufacturer": product_manufacturer,
                        "base_model": product_gpu_base_model,
                        "custom_model": product_gpu_custom_model,
                        "vram_memory": product_memory,
                        "cash_price": product_price_cash,
                        "installments": product_parcel_info["installments"],
                        "installment_price": product_parcel_info["installment_price"],
                        "full_title": product_title,
                        "store": "Kabum",
                        "link": product_link
                    })

                except Exception as e:
                    logger.error(f"Error processing an product: {e}")
                    continue

            browser.close()
            return gpus
    except Exception as e:
        logger.error(f"Error in Kabum GPU scraper: {e}")
        return []

if __name__ == "__main__":
    cpus = kabum_cpu_scraper()
    gpus = kabum_gpu_scraper()

    pd.options.display.max_columns = None

    if cpus:
        print(f"Scraped {len(cpus)} CPUs from Kabum.")
        df = pd.DataFrame(cpus)
        print(df.head())
    else:
        print("No CPUs found.")

    if gpus:
        print(f"Scraped {len(gpus)} GPUs from Kabum.")
        df_gpus = pd.DataFrame(gpus)
        print(df_gpus.head(50))
    else:
        print("No GPUs found.")
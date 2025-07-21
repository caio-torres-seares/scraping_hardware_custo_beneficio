from playwright.sync_api import sync_playwright
import pandas as pd
import re
import sys
import os

from src.logger import get_logger
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from extraction.scraper_utils import (
    extract_parcel_info_pichau,
    extract_gpu_memory,
    extract_brand,
    extract_gpu_manufacturer,
    extract_cpu_model_and_variant,
    extract_gpu_model_and_variant,
    extract_cpu_socket
)

logger = get_logger()

def pichau_cpu_scraper():
    url = "https://www.pichau.com.br/hardware/processadores"
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)  # set to False to see the browser
            page = browser.new_page(user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/114.0.0.0 Safari/537.36")
            page.goto(url, timeout=60000)

            # Get all CPU items
            products = page.query_selector_all('a[data-cy="list-product"]')
            if not products:
                logger.info("No CPU products found.")
                browser.close()
                return []
            
            cpus = []

            
            for product in products:
                try:
                    title = product.query_selector("h2")
                    product_title = title.inner_text().strip() if title else "N/A"

                    price = product.query_selector(".mui-12athy2-price_vista")
                    product_price_cash = price.inner_text().strip() if price else "N/A"

                    link = product.get_attribute("href")
                    product_link = "https://www.pichau.com.br" + link if link else "N/A"

                    product_parcel_info = extract_parcel_info_pichau(product)

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
                        "store": "Pichau"
                    })

                except Exception as e:
                    logger.error(f"Error processing an product: {e}")
                    continue

            browser.close()
            return cpus
        
    except Exception as e:
        logger.error(f"Error in Pichau CPU scraper: {e}")
        return []

def pichau_gpu_scraper():
    url = "https://www.pichau.com.br/hardware/placa-de-video"
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)  # set to False to see the browser
            page = browser.new_page(user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/114.0.0.0 Safari/537.36")
            page.goto(url, timeout=60000)

            # Get all GPU items
            products = page.query_selector_all('a[data-cy="list-product"]')
            if not products:
                logger.info("No GPU products found.")
                browser.close()
                return []

            gpus = []

            
            for product in products:
                try:
                    title = product.query_selector("h2")
                    product_title = title.inner_text().strip() if title else "N/A"

                    price = product.query_selector(".mui-12athy2-price_vista")
                    product_price_cash = price.inner_text().strip() if price else "N/A"

                    link = product.get_attribute("href")
                    product_link = "https://www.pichau.com.br" + link if link else "N/A"

                    product_parcel_info = extract_parcel_info_pichau(product)

                    product_memory = extract_gpu_memory(product_title)

                    product_gpu_brand = extract_brand(product_title)

                    product_manufacturer = extract_gpu_manufacturer(product_title)

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
                        "store": "Pichau",
                        "link": product_link
                    })

                except Exception as e:
                    logger.error(f"Error processing an product: {e}")
                    continue

            browser.close()
            return gpus
    except Exception as e:
        logger.error(f"Error in Pichau GPU scraper: {e}")
        return []

if __name__ == "__main__":
    cpus = pichau_cpu_scraper()
    gpus = pichau_gpu_scraper()

    df_cpus = pd.DataFrame(cpus)
    df_gpus = pd.DataFrame(gpus)

    print("CPUs:\n", df_cpus.head(50))
    print("\nGPUs:\n", df_gpus.head())

   
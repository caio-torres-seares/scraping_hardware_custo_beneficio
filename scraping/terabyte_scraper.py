from playwright.sync_api import sync_playwright
import pandas as pd
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from scraping.scraper_utils import (
    extract_parcel_info_terabyte,
    extract_gpu_memory,
    extract_brand,
    extract_gpu_manufacturer,
    extract_cpu_model_and_variant,
    extract_gpu_model_and_variant,
    extract_cpu_socket
)

def terabyte_cpu_scraper():
    url = "https://www.terabyteshop.com.br/hardware/processadores"
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)  # set to False to see the browser
        page = browser.new_page(user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/114.0.0.0 Safari/537.36")
        print("Navigating to Terabyte CPU page...")
        page.goto(url, timeout=60000)

        print("Product cards loaded. Scraping CPU data...")
        # Get all CPU items
        products = page.query_selector_all('div.product-item__box')
        if not products:
            print("No CPU products found.")
            browser.close()
            return []
        
        cpus = []

        
        for product in products:
            try:
                name_tag = product.query_selector("a.product-item__name")
                product_title = name_tag.inner_text().strip() if name_tag else "N/A"

                link = name_tag.get_attribute("href") if name_tag else "N/A"
                product_link = link if link else "N/A"

                price_tag = product.query_selector("div.product-item__new-price span")
                product_price_cash = price_tag.inner_text().strip() if price_tag else "N/A"

                product_parcel_info = extract_parcel_info_terabyte(product)

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
                    "store": "Terabyte"
                })

            except Exception as e:
                print(f"Error processing an product: {e}")
                continue

        browser.close()
        return cpus

def terabyte_gpu_scraper():
    url = "https://www.terabyteshop.com.br/hardware/placas-de-video"
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)  # set to False to see the browser
        page = browser.new_page(user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/114.0.0.0 Safari/537.36")
        print("Navigating to Terabyte GPU page...")
        page.goto(url, timeout=60000)

        print("Product cards loaded. Scraping GPU data...")
        # Get all GPU items
        products = page.query_selector_all('div.product-item__box')
        if not products:
            print("No GPU products found.")
            browser.close()
            return []
        
        gpus = []

        
        for product in products:
            try:
                name_tag = product.query_selector("a.product-item__name")
                product_title = name_tag.inner_text().strip() if name_tag else "N/A"

                link = name_tag.get_attribute("href") if name_tag else "N/A"
                product_link = link if link else "N/A"

                price_tag = product.query_selector("div.product-item__new-price span")
                product_price_cash = price_tag.inner_text().strip() if price_tag else "N/A"

                product_parcel_info = extract_parcel_info_terabyte(product)

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
                    "store": "Terabyte",
                    "link": product_link
                })

            except Exception as e:
                print(f"Error processing an product: {e}")
                continue

        browser.close()
        return gpus

if __name__ == "__main__":
    cpus = terabyte_cpu_scraper()
    gpus = terabyte_gpu_scraper()
    pd.options.display.max_columns = None

    # if cpus:
    #     print(f"Scraped {len(cpus)} CPUs from Terabyte.")
    #     # Convert to DataFrame for better visualization
    #     df = pd.DataFrame(cpus)
    #     print(df.head())
    # else:
    #     print("No CPUs found.")

    if gpus:
        print(f"Scraped {len(gpus)} GPUs from Terabyte.")
        # Convert to DataFrame for better visualization
        df_gpus = pd.DataFrame(gpus)
        print(df_gpus.head())
    else:
        print("No GPUs found.")
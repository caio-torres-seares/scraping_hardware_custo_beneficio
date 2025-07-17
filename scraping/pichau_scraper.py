from playwright.sync_api import sync_playwright
import re

def pichau_cpu_scraper():
    url = "https://www.pichau.com.br/hardware/processadores"
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)  # set to False to see the browser
        page = browser.new_page(user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/114.0.0.0 Safari/537.36")
        print("Navigating to Pichau CPU page...")
        page.goto(url, timeout=60000)

        print("Waiting for product cards to load...")

        print("Product cards loaded. Scraping CPU data...")
        # Get all CPU items
        products = page.query_selector_all('a[data-cy="list-product"]')
        if not products:
            print("No CPU products found.")
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

                product_parcel_info = extract_parcel_info(product)

                product_cores, product_threads = extract_cpu_cores_threads(product_title)
                product_socket = extract_cpu_socket(product_title)
                product_clock_speed_base, product_clock_speed_max = extract_cpu_clock_speeds(product_title)
                product_cache = extract_cpu_cache(product_title)

                cpus.append({
                    "full_title": product_title,
                    "cash_price": product_price_cash,
                    "installments": product_parcel_info["installments"],
                    "installment_price": product_parcel_info["installment_price"],
                    "socket": product_socket,
                    "cores": product_cores,
                    "threads": product_threads,
                    "clock_speed_base": product_clock_speed_base,
                    "clock_speed_max": product_clock_speed_max,
                    "cache_mb": product_cache,
                    "link": product_link,
                    "store": "Pichau"
                })

            except Exception as e:
                print(f"Error processing an product: {e}")
                continue

        browser.close()
        return cpus
    

def extract_parcel_info(item):
    try:
        installments_div = item.query_selector(".mui-144008r-mainWrapper")

        installments_p = installments_div.query_selector("p")

        p_text = installments_p.inner_text().strip()

        match = re.search(r"(\d+)\s*x\s*de\s*R\$\s*([\d.,]+)", p_text, re.IGNORECASE)
        if match:
            installments = int(match.group(1))
            installment_price = float(match.group(2).replace(".", "").replace(",", "."))
        else:
            print("Não foi possível extrair os dados.")
        return {
            "installments": installments,
            "installment_price": installment_price
        }

    except Exception as e:
        print(f"Erro ao extrair parcelamento: {e}")
        return {"installments": "N/A", "installment_price": "N/A"}

def extract_cpu_socket(title: str) -> str:
    match = re.search(r"\b(AM3|AM4|AM5|LGA\d{4})\b", title)
    return match.group(1) if match else "N/A"

def extract_cpu_cores_threads(title: str) -> tuple[str, str]:
    cores_match = re.search(r"(\d+)\s*-\s*Core", title, re.IGNORECASE)
    threads_match = re.search(r"(\d+)\s*-\s*Threads?", title, re.IGNORECASE)
    
    cores = cores_match.group(1) if cores_match else "N/A"
    threads = threads_match.group(1) if threads_match else "N/A"
    
    return cores, threads

def extract_cpu_clock_speeds(title: str) -> tuple[str, str]:
    match = re.search(r"(\d+(?:\.\d+)?)\s*GHz\s*\(\s*(\d+(?:\.\d+)?)\s*GHz Turbo\)", title, re.IGNORECASE)
    if match:
        return match.group(1), match.group(2)
    return "N/A", "N/A"

def extract_cpu_cache(title: str) -> str:
    match = re.search(r"Cache\s+(\d+MB)", title)
    return match.group(1) if match else "N/A"

if __name__ == "__main__":
    cpus = pichau_cpu_scraper()
    for cpu in cpus:
        print(f"Title: {cpu['full_title']}, Price: {cpu['cash_price']}, cores: {cpu['cores']}, threads: {cpu['threads']}, Base Clock: {cpu['clock_speed_base']}, Max Clock: {cpu['clock_speed_max']}, Cache: {cpu['cache_mb']}")
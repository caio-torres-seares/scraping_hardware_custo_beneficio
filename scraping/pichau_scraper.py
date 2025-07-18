from playwright.sync_api import sync_playwright
import re

def pichau_cpu_scraper():
    url = "https://www.pichau.com.br/hardware/processadores?page=1"
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

def pichau_gpu_scraper():
    url = "https://www.pichau.com.br/hardware/placa-de-video"
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)  # set to False to see the browser
        page = browser.new_page(user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/114.0.0.0 Safari/537.36")
        print("Navigating to Pichau GPU page...")
        page.goto(url, timeout=60000)

        print("Waiting for product cards to load...")

        print("Product cards loaded. Scraping GPU data...")
        # Get all GPU items
        products = page.query_selector_all('a[data-cy="list-product"]')
        if not products:
            print("No GPU products found.")
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

                product_parcel_info = extract_parcel_info(product)

                product_memory = extract_gpu_memory(product_title)

                product_gpu_brand = extract_gpu_brand(product_title)

                product_manufacturer = extract_gpu_manufacturer(product_title)

                product_gpu_base_model, product_gpu_custom_model = extract_gpu_model_and_variant(product_title, product_gpu_brand)

                gpus.append({
                    "brand": product_gpu_brand,
                    "manufacturer": product_manufacturer,
                    "base_model": product_gpu_base_model,
                    "custom_model": product_gpu_custom_model,
                    "full_title": product_title,
                    "cash_price": product_price_cash,
                    "installments": product_parcel_info["installments"],
                    "installment_price": product_parcel_info["installment_price"],
                    "vram_memory": product_memory,
                    "store": "Pichau",
                    "link": product_link
                })

            except Exception as e:
                print(f"Error processing an product: {e}")
                continue

        browser.close()
        return gpus

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

def extract_gpu_memory(title: str) -> str:
    match = re.search(r"(\d+)\s*GB", title, re.IGNORECASE)
    return match.group(1) + "GB" if match else "N/A"

def extract_gpu_brand(title: str) -> str:
    title = title.lower()

    if "radeon" in title or re.search(r"\brx\s?\d+", title):
        return "AMD"
    elif "geforce" in title or re.search(r"\b(gtx|rtx)\s?\d+", title):
        return "NVIDIA"
    elif "arc" in title or "intel" in title:
        return "INTEL"
    else:
        return "N/A"

def extract_gpu_model_and_variant(title: str, product_brand: str) -> tuple[str, str]:
    original_title = title.strip()
    title_upper = original_title.upper()
    product_brand_upper = product_brand.upper()

    model = "Unknown model"
    variant = ""

    if "AMD" in product_brand_upper or "RADEON" in product_brand_upper:
        match = re.search(r"(RX\s?\d{3,4}(?:\s?(XT|XTX|GRE)?)?)", title_upper)
    elif "NVIDIA" in product_brand_upper or "GEFORCE" in product_brand_upper:
        match = re.search(r"((RTX|GTX|GT)\s?\d{3,4}(?:\s?(SUPER|TI)?)?)", title_upper)
    elif "INTEL" in product_brand_upper or "ARC" in product_brand_upper:
        match = re.search(r"(ARC\s+[A-Z]?\d{3,4}(?:\s?(M|PRO|OC)?)?)", title_upper)
    else:
        match = None

    if match:
        model = match.group(1).replace("  ", " ").strip()

        end_index = match.end()
        after_model = original_title[end_index:].strip()

        custom_model_part = after_model.split(',')[0].strip(" -–")  

        variant = custom_model_part.strip()

    else:
        variant = original_title 

    return model, variant

def extract_gpu_manufacturer(title: str) -> str:
    fab_match = re.search(r"Placa de Video\s+([\w\-]+)", title, re.IGNORECASE)
    manufacturer = fab_match.group(1) if fab_match else "N/A"
    return manufacturer

if __name__ == "__main__":
    cpus = pichau_cpu_scraper()
    gpus = pichau_gpu_scraper()

    for cpu in cpus:
         print(f"Title: {cpu['full_title']}, Price: {cpu['cash_price']}, cores: {cpu['cores']}, threads: {cpu['threads']}, Base Clock: {cpu['clock_speed_base']}, Max Clock: {cpu['clock_speed_max']}, Cache: {cpu['cache_mb']}")
    
    for gpu in gpus:
        print(f"Brand: {gpu['brand']}, Model: {gpu['base_model']}, custom_model: {gpu['custom_model']}, Price: {gpu['cash_price']}, Memory: {gpu['vram_memory']}, Manufacturer: {gpu['manufacturer']}, title: {gpu['full_title']}")
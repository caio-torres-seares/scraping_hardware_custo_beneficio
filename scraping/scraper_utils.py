import re
import unicodedata

def normalize_text(text: str) -> str:
    return unicodedata.normalize("NFKD", text).encode("ASCII", "ignore").decode("ASCII")

def extract_parcel_info_pichau(item):
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
            "installments": installments if installments else None,
            "installment_price": installment_price if installment_price else None
        }

    except Exception as e:
        print(f"Error extracting installment information: {e}")
        return {"installments": None, "installment_price": None}
    
def extract_parcel_info_terabyte(item):
    try:
        installments_div = item.query_selector(".product-item__juros")
        if not installments_div:
            return {"installments": None, "installment_price": None}

        spans = installments_div.query_selector_all("span")
        if len(spans) < 2:
            return {"installments": None, "installment_price": None}

        # Primeiro span: número de parcelas (ex: 12x)
        installments_text = spans[0].inner_text().strip()
        installments = int(re.search(r"\d+", installments_text).group())

        # Segundo span: valor da parcela (ex: R$ 74,01)
        price_text = spans[1].inner_text().strip()
        installment_price = float(price_text.replace("R$", "").replace(".", "").replace(",", "."))

        return {
            "installments": installments if installments else None,
            "installment_price": installment_price if installment_price else None
        }

    except Exception as e:
        print(f"Error extracting installment information: {e}")
        return {"installments": None, "installment_price": None}
    
def extract_cpu_socket(title: str) -> str:
    match = re.search(r"\b(AM3|AM4|AM5|LGA\s?\d{4})\b", title.upper())
    return match.group(1).replace(" ", "") if match else "N/A"

def extract_brand(title: str) -> str:
    title = title.lower()

    # Marca AMD: GPUs Radeon RX / CPUs Ryzen
    if ("ryzen" in title or "radeon" in title or re.search(r"\brx\s?\d+", title)):
        return "AMD"

    # Marca NVIDIA: GPUs RTX / GTX
    elif ("geforce" in title or re.search(r"\b(gtx|rtx)\s?\d+", title)):
        return "NVIDIA"

    # Marca Intel: GPUs ARC / CPUs Core iX
    elif ("intel" in title or "core i" in title or "arc" in title):
        return "INTEL"

    return "N/A"

def extract_cpu_model_and_variant(title: str, brand: str) -> tuple[str, str]:
    title_upper = title.upper()
    brand_upper = brand.upper()
    
    base_model = "N/A"
    variant = "N/A"

    if "AMD" in brand_upper:
        match = re.search(r"RYZEN\s*(\d\s*)?(\d{3,5}[A-Z0-9]{0,3})", title_upper)
        if match:
            base_model = match.group(2).strip()

            pre_match = re.search(r"(RYZEN\s*\d?)", title_upper)
            if pre_match:
                variant = pre_match.group(0).strip()

    
    elif "INTEL" in brand_upper:
        match = re.search(r"CORE\sULTRA\s\d\s(\d{3,5}[A-Z]{0,2})", title_upper)
        if match:
            base_model = match.group(1).strip()
            variant_match = re.search(r"CORE\sULTRA\s(\d)", title_upper)
            if variant_match:
                variant = f"Ultra {variant_match.group(1)}"

        else:
            match = re.search(r"I[3579]-?\s?(\d{4,5}[A-Z]{0,2})", title_upper)
            if match:
                base_model = match.group(1).strip()
                variant_match = re.search(r"CORE\s(I[3579])", title_upper)
                if variant_match:
                    variant = variant_match.group(1)


    return base_model, variant

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
    normalized_title = normalize_text(title)
    fab_match = re.search(r"Placa de Video\s+([\w\-]+)", normalized_title, re.IGNORECASE)
    manufacturer = fab_match.group(1) if fab_match else "N/A"
    return manufacturer

def extract_gpu_memory(title: str) -> str:
    match = re.search(r"(\d+)\s*GB", title, re.IGNORECASE)
    return match.group(1) + "GB" if match else "N/A"
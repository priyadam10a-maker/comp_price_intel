# utils/brand_category.py

def get_brand_name(product_name):

    if product_name.startswith("Heavy Duty"):
        return "Heavy Duty"

    elif product_name.startswith("Premium Quality"):
        return "Premium Quality"

    elif product_name.startswith("Black+Decker"):
        return "Black+Decker"

    else:
        return product_name.split()[0]
    
def get_category_id(product_name):
    name = product_name.lower()
    if "grinder"         in name: return 2
    elif "rotary hammer" in name: return 5
    elif "drill"         in name: return 1
    elif "circular saw"  in name: return 4
    elif "impact"        in name: return 3
    elif "compressor"    in name: return 6
    elif "welding"       in name: return 7
    elif "hand tool"     in name: return 8
    elif "measuring"     in name: return 9
    else: return 10

def clean_price(raw):
    try:
        return float(
            raw.replace("₹", "").replace(",", "").strip()
        )
    except ValueError:
        return None
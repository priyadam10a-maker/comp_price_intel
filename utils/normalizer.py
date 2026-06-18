# utils/normalizer.py

import re


def normalize_product_name(name):

    name = name.lower()

    # remove punctuation
    name = re.sub(r"[^a-z0-9\s]", " ", name)

    # remove extra spaces
    name = " ".join(name.split())

    return name



def extract_wattage(name):

    match = re.search(
        r"(\d+)\s*w\b",
        name.lower()
    )

    if match:
        return int(match.group(1))

    return None



def extract_voltage(name):

    match = re.search(
        r"(\d+)\s*v\b",
        name.lower()
    )

    if match:
        return int(match.group(1))

    return None


def extract_model_number(name):

    text = name.lower()

    patterns = [

        r"\b[a-z]{1,}\d{2,}[a-z]*\b",

        r"\b[a-z]{2,}\s+\d{2,}[a-z]*\b"
    ]

    INVALID_PREFIXES = {

        "bosch",
        "ingco",
        "makita",
        "dongcheng",
        "yiking",

        "duty",
        "quality",
        "drill",
        "shear",
        "crossbee",
        "supreme"
    }

    candidates = []

    for pattern in patterns:

        candidates.extend(
            re.findall(
                pattern,
                text
            )
        )

    for model in candidates:

        model = model.replace(
            " ",
            ""
        )

        if model.endswith("v"):
            continue

        if model.endswith("w"):
            continue

        if any(
            model.startswith(prefix)
            for prefix in INVALID_PREFIXES
        ):
            continue

        return model

    return None



def get_product_signature(name):

    return {

        "normalized":
            normalize_product_name(
                name
            ),

        "model":
            extract_model_number(
                name
            ),

        "voltage":
            extract_voltage(
                name
            ),

        "wattage":
            extract_wattage(
                name
            )
    }
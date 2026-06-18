# utils/product_matcher.py

import re
from rapidfuzz import fuzz

from utils.normalizer import (
    get_product_signature
)

from utils.brand_category import (
    get_brand_name,
    get_category_id
)

def normalize_name(name):

    name = name.lower()

    # remove punctuation
    name = re.sub(r"[^a-z0-9\s]", " ", name)

    # collapse multiple spaces
    name = " ".join(name.split())

    return name


def similarity_score(name1, name2):

    n1 = normalize_name(name1)
    n2 = normalize_name(name2)

    return fuzz.token_sort_ratio(n1, n2)


def find_matching_product(cursor,name,threshold=80, debug=False):

    cursor.execute(
        """
        SELECT product_id,
               product_name
        FROM products
        """
    )

    products = cursor.fetchall()

    best_match = None
    best_score = float("-inf")

    for product_id, product_name in products:

        score = calculate_match_score(
            name,
            product_name,
            debug=debug
        )

        if score > best_score:

            best_score = score
            best_match = product_id

    if debug:

        print(
            f"BEST MATCH SCORE: "
            f"{best_score}"
        )

    if best_score >= threshold:
        return best_match, best_score 

    return None

def calculate_match_score(name1,name2, debug=False):

    score = 0
    
    brand1 = get_brand_name(name1)
    brand2 = get_brand_name(name2)

    if brand1 and brand2:

        if brand1 == brand2:
            score += 20
        else:
            score -= 20

    cat1 = get_category_id(name1)
    cat2 = get_category_id(name2)

    if cat1 and cat2:

        if cat1 == cat2:
            score += 15

        else:
            score -= 15

    sig1 = get_product_signature(name1)
    sig2 = get_product_signature(name2)


    # Model number
    if sig1["model"] and sig2["model"]:

        if sig1["model"] == sig2["model"]:
            score += 50

        else:
            score -= 30

    # Voltage
    if sig1["voltage"] and sig2["voltage"]:

        if sig1["voltage"] == sig2["voltage"]:
            score += 10

        else:
            score -= 10

    # Wattage
    if sig1["wattage"] and sig2["wattage"]:

        if sig1["wattage"] == sig2["wattage"]:
            score += 10

        else:
            score -= 10

    # Fuzzy similarity
    fuzzy = similarity_score(
        name1,
        name2
    )

    score += fuzzy * 0.2

    if debug:

        print(
            f"""
            Brand: {brand1} vs {brand2}
            Category: {cat1} vs {cat2}
            Model: {sig1['model']} vs {sig2['model']}
            Voltage: {sig1['voltage']} vs {sig2['voltage']}
            Wattage: {sig1['wattage']} vs {sig2['wattage']}
            Fuzzy: {fuzzy}
            Final Score: {score}
            """
        )

    return score
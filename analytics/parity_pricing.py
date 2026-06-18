#parity_pricing.py
def competitive_parity_price(cursor, user_product_id):

    cursor.execute("""
        SELECT
            cp.listed_price
        FROM user_product_matches upm

        JOIN competitor_products cp
        ON cp.competitor_product_id =
           upm.competitor_product_id

        WHERE upm.user_product_id = %s
    """, (user_product_id,))

    prices = [
        float(row['listed_price'])
        for row in cursor.fetchall()
        if row.get('listed_price') is not None
    ]

    if not prices:
        return None

    return sum(prices) / len(prices)
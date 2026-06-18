#demand_pricing.py
def demand_based_price(
    cursor,
    user_product_id,
    current_price
):

    cursor.execute("""
        SELECT demand_score
        FROM product_demand
        WHERE user_product_id = %s
    """, (user_product_id,))

    row = cursor.fetchone()

    if not row or row.get('demand_score') is None:
        return None

    demand_score = float(row['demand_score'])

    if demand_score >= 80:
        return round(current_price * 1.10, 2)

    elif demand_score >= 50:
        return round(current_price * 1.07, 2)

    elif demand_score >= 20:
        return round(current_price * 1.03, 2)

    else:
        return None
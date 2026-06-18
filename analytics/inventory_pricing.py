#inventory_pricing.py
def inventory_based_price(
    cursor,
    user_product_id,
    current_price
):

    cursor.execute("""
        SELECT
            quantity_available,
            reorder_level
        FROM inventory
        WHERE user_product_id = %s
    """, (user_product_id,))

    row = cursor.fetchone()

    if not row:
        return round(current_price * 1.10, 2)

    quantity_available = row.get('quantity_available', 0)
    reorder_level = row.get('reorder_level', 0)

    if quantity_available <= reorder_level:
        return round(current_price * 1.10, 2)
    elif quantity_available > reorder_level * 2:
        return round(current_price * 0.90, 2)
    else:

        return round(current_price * 0.95, 2)
#recommendation_engine.py
from analytics.parity_pricing import competitive_parity_price
from analytics.demand_pricing import demand_based_price
from analytics.inventory_pricing import inventory_based_price


def generate_recommendation(
    cursor,
    user_product_id,
    current_price
):

    parity_price = competitive_parity_price(
        cursor,
        user_product_id
    )

    demand_price = demand_based_price(
        cursor,
        user_product_id,
        current_price
    )

    inventory_price = inventory_based_price(
        cursor,
        user_product_id,
        current_price
    )

    # Determine primary strategy
    cursor.execute("SELECT quantity_available, reorder_level FROM inventory WHERE user_product_id = %s", (user_product_id,))
    inv_row = cursor.fetchone()
    # In dict cursor, keys are column names
    qty = inv_row["quantity_available"] if inv_row and "quantity_available" in inv_row else 0
    reorder = inv_row["reorder_level"] if inv_row and "reorder_level" in inv_row else 0
    
    cursor.execute("SELECT demand_score FROM product_demand WHERE user_product_id = %s", (user_product_id,))
    dem_row = cursor.fetchone()
    demand_score = float(dem_row["demand_score"]) if dem_row and "demand_score" in dem_row and dem_row["demand_score"] is not None else 0.0

    if qty <= reorder:
        strategy = "Inventory Pricing"
        recommended_price = inventory_price
    elif demand_score >= 80:
        strategy = "Demand Pricing"
        recommended_price = demand_price if demand_price is not None else current_price
    else:
        strategy = "Parity Pricing"
        recommended_price = parity_price if parity_price is not None else current_price

    return {
        "parity_price": parity_price,
        "demand_price": demand_price,
        "inventory_price": inventory_price,
        "recommended_price": recommended_price,
        "strategy": strategy
    }
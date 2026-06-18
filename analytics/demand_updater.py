#analytics/demand_updater.py

def update_product_demand(
    cursor,
    user_product_id,
    product_name
):

    cursor.execute("""
        SELECT COUNT(*)
        FROM search_history
        WHERE search_keyword = %s
    """, (product_name,))

    search_count = cursor.fetchone()[0]

    demand_score = min(search_count * 10, 100)

    cursor.execute("""
        SELECT demand_id
        FROM product_demand
        WHERE user_product_id = %s
    """, (user_product_id,))

    existing = cursor.fetchone()

    if existing:

        cursor.execute("""
            UPDATE product_demand
            SET
                search_count = %s,
                demand_score = %s,
                last_updated = NOW()
            WHERE user_product_id = %s
        """,
        (
            search_count,
            demand_score,
            user_product_id
        ))

    else:

        cursor.execute("""
            INSERT INTO product_demand
            (
                user_product_id,
                search_count,
                demand_score,
                last_updated
            )
            VALUES
            (
                %s,
                %s,
                %s,
                NOW()
            )
        """,
        (
            user_product_id,
            search_count,
            demand_score
        ))
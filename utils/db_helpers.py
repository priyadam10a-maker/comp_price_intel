# utils/db_helpers.py
from utils.product_matcher import find_matching_product

def get_or_create_brand(cursor, brand_name):

    cursor.execute(
        """
        SELECT brand_id
        FROM brands
        WHERE brand_name = %s
        """,
        (brand_name,)
    )

    result = cursor.fetchone()

    if result:
        return result[0]

    cursor.execute(
        """
        INSERT INTO brands
        (
            brand_name
        )
        VALUES
        (%s)
        """,
        (brand_name,)
    )

    brand_id = cursor.lastrowid

    print(
        f"Created new brand "
        f"(id={brand_id}): {brand_name}"
    )

    return brand_id

def save_product(cursor, name, price, brand_id, category_id, platform_id, product_url=None):

    if len(name.split()) < 3:

        print(
            f"Skipping suspicious product: {name}"
        )

        return
            
    
    cursor.execute(
        """
        SELECT product_id
        FROM products
        WHERE product_name = %s
        LIMIT 1
        """,
        (name,)
    )

    existing = cursor.fetchone()

    if existing:

        product_id = existing[0]

        print(
            f"Exact match found "
            f"(id={product_id})"
        )

    else:

        matched = find_matching_product(
            cursor,
            name
        )

        if matched:

            product_id, score = matched

            print(
                f"Matched existing product "
                f"(id={product_id}) "
                f"score={score:.2f}"
            )

        else:

            cursor.execute("""
                INSERT INTO products
                    (
                        product_name,
                        brand_id,
                        category_id,
                        current_price,
                        average_rating,
                        total_reviews
                    )
                VALUES
                    (
                        %s,
                        %s,
                        %s,
                        %s,
                        0,
                        0
                    )
            """,
            (
                name,
                brand_id,
                category_id,
                price
            ))

            product_id = cursor.lastrowid

            print(
                f"Inserted new product "
                f"(id={product_id}): {name}"
            )

    cursor.execute("""
            INSERT INTO competitor_products
                (
                    product_id, 
                    platform_id,
                    platform_product_name,
                    platform_product_url,
                    listed_price,
                    stock_status,
                    last_scraped
                )
            VALUES
                (
                    %s,
                    %s,
                    %s,
                    %s,
                    %s,
                    'In Stock',
                    NOW()
                )
        """,
        (
            product_id,
            platform_id,
            name,
            product_url,
            price
        ))

    comp_id = cursor.lastrowid

    cursor.execute("""
            INSERT INTO price_history (competitor_product_id, price)
            VALUES (%s, %s)
        """, (comp_id, price))

    print(f"  ₹{price} saved to competitor_products + price_history")
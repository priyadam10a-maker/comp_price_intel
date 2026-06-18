# clean_duplicates.py

from database.db_connection import get_connection

conn = get_connection()
cursor = conn.cursor()

try:

    cursor.execute("""
    SELECT
        product_name,
        GROUP_CONCAT(product_id ORDER BY product_id) AS ids
    FROM products
    GROUP BY product_name
    HAVING COUNT(*) > 1
    """)

    duplicates = cursor.fetchall()

    print("\nStarting cleanup...")
    print(
        f"Duplicate groups found: "
        f"{len(duplicates)}"
    )

    for product_name, ids_str in duplicates:

        ids = [int(x) for x in ids_str.split(",")]

        keep_id = ids[0]
        delete_ids = ids[1:]
        
        if not delete_ids:
            continue

        print()
        print(product_name)
        print("KEEP:", keep_id)
        print("DELETE:", delete_ids)

        placeholders = ",".join(
            ["%s"] * len(delete_ids)
        )

        # Move competitor records
        cursor.execute(
            f"""
            UPDATE competitor_products
            SET product_id = %s
            WHERE product_id IN ({placeholders})
            """,
            (keep_id, *delete_ids)
        )

        print(
            f"Rows updated: {cursor.rowcount}"
        )

        print(
            "Updated competitor_products"
        )

        # Delete duplicate products
        cursor.execute(
            f"""
            DELETE FROM products
            WHERE product_id IN ({placeholders})
            """,
            delete_ids
        )

        print(
            f"Rows deleted: {cursor.rowcount}"
        )

        print(
            "Deleted duplicate products"
        )

    conn.commit()

    print(
        "\nDuplicate cleanup complete."
    )

except Exception as e:

    conn.rollback()

    print(
        f"\nERROR: {e}"
    )

finally:

    conn.close()
# utils/scrape_logger.py

def log_scrape(
    cursor,
    scraper_name,
    start_time,
    end_time,
    status,
    notes=None
):

    cursor.execute(
        """
        INSERT INTO scrape_logs
        (
            scraper_name,
            started_at,
            finished_at,
            status,
            notes
        )
        VALUES
        (%s,%s,%s,%s,%s)
        """,
        (
            scraper_name,
            start_time,
            end_time,
            status,
            notes
        )
    )
#scheduler.py
import os
import django

from apscheduler.schedulers.blocking import BlockingScheduler
from django.core.management import call_command

os.environ.setdefault(
    "DJANGO_SETTINGS_MODULE",
    "CPI.settings"
)

django.setup()

scheduler = BlockingScheduler()


def run_all_scrapers():

    print("Starting scrape_all...")

    call_command("scrape_all")

    print("Finished scrape_all")


scheduler.add_job(
    run_all_scrapers,
    "cron",
    hour=2,
    minute=0
)

print("Scheduler started...")

scheduler.start()
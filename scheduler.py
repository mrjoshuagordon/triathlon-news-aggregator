import os
from datetime import datetime, time
import pytz
from pull_instagram import run_instagram_task
from pull_news import run_news_task 
from pull_reddit import run_reddit_task
from pull_youtube import run_youtube_task

LAST_RUN_FILE = "last_run_date.txt"  # Assuming this is defined somewhere

def check_and_run_scripts():
    """Check if scripts have run today after UTC 12pm; if not, execute them."""
    # Get current UTC time and compute today's noon time
    now_utc = datetime.now(pytz.utc)
    today_noon = now_utc.replace(hour=12, minute=0, second=0, microsecond=0)
    
    # Read the last run timestamp from file, if it exists
    if os.path.exists(LAST_RUN_FILE):
        with open(LAST_RUN_FILE, "r") as f:
            last_run_str = f.read().strip()
        try:
            # Expecting ISO format string
            last_run_date = datetime.fromisoformat(last_run_str)
            # Ensure timezone info is set; if not, assume UTC
            if last_run_date.tzinfo is None:
                last_run_date = last_run_date.replace(tzinfo=pytz.utc)
        except Exception:
            last_run_date = None
    else:
        last_run_date = None

    # Run scripts if never run before or if last run was at or before today's UTC noon
    if last_run_date is None or last_run_date <= today_noon:
        print("Running scripts for the first time today...")
        
        # Run your tasks here
        run_instagram_task()
        run_news_task()
        run_reddit_task()
        run_youtube_task()

        # Update the file with the current UTC timestamp in ISO format
        with open(LAST_RUN_FILE, "w") as f:
            f.write(datetime.now(pytz.utc).isoformat())
    else:
        print("Scripts already ran today after UTC 12pm. Skipping execution.")

if __name__ == '__main__':
    check_and_run_scripts()

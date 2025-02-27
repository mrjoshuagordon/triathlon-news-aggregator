from datetime import datetime
import requests
import time
import pandas as pd
from apify_client import ApifyClient
# Replace with your actual Apify API Key
from config import APIFY_API_KEY, TASK_ID
import os
from apify_client import ApifyClient
import pandas as pd


def fetch_all_fields():
    """Fetch all Instagram post data fields dynamically and save as Pandas DataFrame."""

    # Initialize Apify Client
    client = ApifyClient(APIFY_API_KEY)

    # Run the Apify task and wait for it to finish
    run = client.task(TASK_ID).call()

    # Fetch results from the dataset
    data = []
    for item in client.dataset(run["defaultDatasetId"]).iterate_items():
        data.append(item)  # Save entire JSON response for each post

    # Convert to Pandas DataFrame (captures all possible fields)
    df = pd.DataFrame(data)

    return df


def run_instagram_task():
# Construct the filename for today's date
    new_data_file = 'data/new_insta_data/new_insta_data' + datetime.now().strftime('%d%m%Y') + '.csv'

    # Check if the file already exists
    if not os.path.exists(new_data_file):
        print(f"Fetching new Instagram data and saving to {new_data_file}")
        
        df_posts = fetch_all_fields()  # Fetch latest posts
        
        # Save to CSV
        df_posts.to_csv(new_data_file, index=False)
    else:
        print(f"File already exists: {new_data_file}. Skipping fetch.")

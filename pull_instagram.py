from datetime import datetime
import requests
import time
import pandas as pd
from apify_client import ApifyClient
# Replace with your actual Apify API Key
from config import APIFY_API_KEY, TASK_ID

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

# Fetch latest posts and return as DataFrame
df_posts = fetch_all_fields()

# Save to CSV (modify path as needed)
new_data_file = 'data/new_insta_data/new_insta_data' + datetime.now().strftime('%d%m%Y') + '.csv'
df_posts.to_csv(new_data_file, index=False)
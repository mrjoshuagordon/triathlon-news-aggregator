from datetime import datetime
import requests
import time
import pandas as pd
from apify_client import ApifyClient
# Replace with your actual Apify API Key
from config import APIFY_API_KEY, TASK_ID, API_URL, DATA_PATH
import os
from apify_client import ApifyClient
import pandas as pd


# def fetch_all_fields():
#     """Fetch all Instagram post data fields dynamically and save as Pandas DataFrame."""

#     # Initialize Apify Client
#     client = ApifyClient(APIFY_API_KEY)

#     # Run the Apify task and wait for it to finish
#     run = client.task(TASK_ID).call()

#     # Fetch results from the dataset
#     data = []
#     for item in client.dataset(run["defaultDatasetId"]).iterate_items():
#         data.append(item)  # Save entire JSON response for each post

#     # Convert to Pandas DataFrame (captures all possible fields)
#     df = pd.DataFrame(data)

#     return df


# def run_instagram_task():
#     print(os.listdir('data'))
# # Construct the filename for today's date
#     new_data_file = 'data/new_insta_data/new_insta_data' + datetime.now().strftime('%d%m%Y') + '.csv'

#     # Check if the file already exists
#     if not os.path.exists(new_data_file):
#         print(f"Fetching new Instagram data and saving to {new_data_file}")
        
#         df_posts = fetch_all_fields()  # Fetch latest posts
        
#         # Save to CSV
#         df_posts.to_csv(new_data_file, index=False)
#     else:
#         print(f"File already exists: {new_data_file}. Skipping fetch.")

# Apify API URL for the latest dataset items

def run_instagram_task():
    """
    Fetches the latest dataset from Apify's Instagram Post Scraper task,
    converts it to a Pandas DataFrame, and saves it as a CSV file.
    
    Returns:
        pd.DataFrame: DataFrame containing the fetched Instagram post data.
    """
    try:
        # Make a GET request to fetch the data
        response = requests.get(f"{API_URL}?token={APIFY_API_KEY}")

        # Check if request was successful
        if response.status_code == 200:
            data = response.json()  # Convert JSON response to a Python object
            
            # Convert to Pandas DataFrame
            df = pd.DataFrame(data)

            # Define output file path
            new_data_file = f'{DATA_PATH}new_insta_data/new_insta_data_' + datetime.now().strftime('%d%m%Y') + '.csv'

            # Save DataFrame to CSV
            df.to_csv(new_data_file, index=False)
            df.to_csv(f'{DATA_PATH}insta_today.csv', index=False)
            print(f"Data successfully saved to {new_data_file}")
            return df
        else:
            print(f"Failed to fetch data: {response.status_code} - {response.text}")
            return None

    except Exception as e:
        print(f"An error occurred: {e}")
        return None

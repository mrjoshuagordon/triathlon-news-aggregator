import os
import requests
import xmltodict
import pandas as pd
from datetime import datetime
from bs4 import BeautifulSoup
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()
DATA_PATH = os.getenv("DATA_PATH")

def fetch_and_parse_rss(urls):
    """
    Fetches and parses RSS feeds from the provided list of URLs.
    
    Parameters:
        urls (list): A list of RSS feed URLs.
    
    Returns:
        dict: A dictionary where each key is a URL and its value is the parsed XML content as a Python dict.
    """
    headers = {
        "User-Agent": ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                       "AppleWebKit/537.36 (KHTML, like Gecko) "
                       "Chrome/115.0.0.0 Safari/537.36")
    }
    
    feeds = {}
    for url in urls:
        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            # Decode the content, removing BOM if present, and strip leading whitespace.
            xml_content = response.content.decode('utf-8-sig').lstrip()
            parsed_feed = xmltodict.parse(xml_content)
            feeds[url] = parsed_feed
        except Exception as e:
            print(f"Error fetching {url}: {e}")
    return feeds

def extract_items(feeds_json):
    """
    Extracts the 'item' elements from each feed's channel and returns them as a list of dictionaries.
    
    Parameters:
        feeds_json (dict): Dictionary of parsed RSS feeds.
        
    Returns:
        list: A list of dictionaries, each representing an RSS item.
    """
    items_list = []
    for url, feed in feeds_json.items():
        # Safely access the channel
        channel = feed.get("rss", {}).get("channel", {})
        items = channel.get("item", [])
        # Ensure items is always a list (RSS feeds with a single item sometimes return a dict)
        if isinstance(items, dict):
            items = [items]
        for item in items:
            # Optionally, add the source URL to each item for traceability.
            item['feed_url'] = url
            items_list.append(item)
    return items_list

def clean_html(html):
    """
    Remove HTML tags from a string using BeautifulSoup.
    
    Parameters:
        html (str): A string that contains HTML.
    
    Returns:
        str: The plain text with HTML tags removed.
    """
    if not isinstance(html, str):
        return html
    soup = BeautifulSoup(html, "html.parser")
    return soup.get_text(separator=" ", strip=True)

def run_news_task():
    # Path to the new data file
    new_data_file = f'{DATA_PATH}newdata/newdata_{datetime.now().strftime("%d%m%Y")}.csv'

    # Check if the new data file exists
    if not os.path.exists(new_data_file):
        print(f"{new_data_file} not found. Pulling new data...")

        # URLs for the RSS feeds
        urls = [
            "https://www.tri247.com/triathlon-news/rss",
            "https://www.triathlete.com/category/culture/news/rss",
            "https://tri-today.com/rss",
            "https://www.220triathlon.com/news/rss",
            "https://triathlonmagazine.ca/rss",
            "https://protriathletes.org/news/rss",
            "https://slowtwitch.com/rss",
            "http://beyondgoinglong.co.uk/?feed=rss2",
            "https://triathloninsight.com/category/triathlon-news/rss"
        ]
        
        # Fetch and parse the RSS feeds
        feeds_json = fetch_and_parse_rss(urls)
        
        # Extract items from each feed into a list of dictionaries
        items_data = extract_items(feeds_json)
        
        # Convert the list of dictionaries to a pandas DataFrame
        df = pd.DataFrame(items_data)

        # Clean the HTML in the 'description' column
        df['description'] = df['description'].apply(clean_html)

        # Save the new data to a CSV file
        df[['link', 'title', 'description', 'pubDate']].to_csv(new_data_file, index=False)

        # Now proceed with the rest of the logic (e.g., union, remove duplicates, etc.)
        new_data = df

        # Read the existing 'today.csv' file
        if os.path.exists(os.path.join(DATA_PATH, 'today.csv')):
            today_data = pd.read_csv(os.path.join(DATA_PATH, 'today.csv'), usecols=['link', 'title', 'description', 'pubDate'])
        # Union the new data with the existing data
            combined_data = pd.concat([today_data, new_data], ignore_index=True)
        else:
            combined_data = new_data

        # Remove duplicates based on the 'link' column (assuming 'link' is unique for each article)
        combined_data = combined_data.drop_duplicates(subset='link', keep='last')

        # Convert 'pubDate' to datetime format to sort by date
        combined_data['pubDate'] = pd.to_datetime(combined_data['pubDate'], errors='coerce')

        # Sort by 'pubDate' and keep the 100 most recent rows
        combined_data_sorted = combined_data.sort_values(by='pubDate', ascending=False).head(100)

        # Save the combined and sorted data back to 'today.csv'
        combined_data_sorted.to_csv(os.path.join(DATA_PATH, 'today.csv'), index=False)

        print("Data update complete: today.csv saved.")

    else:
        print(f"{new_data_file} exists. Skipping data pull.")


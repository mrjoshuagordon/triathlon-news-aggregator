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

def fetch_and_parse_podcast_rss(podcasts):
    """
    Fetches and parses RSS feeds from the provided dictionary of podcasts.
    
    Parameters:
        podcasts (dict): A dictionary where keys are podcast names and values are RSS feed URLs.
    
    Returns:
        dict: A dictionary where each key is an RSS feed URL and its value is the parsed XML content as a Python dict.
    """
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/115.0.0.0 Safari/537.36"
        )
    }
    
    feeds = {}
    for podcast_name, url in podcasts.items():
        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            # Decode the content, removing BOM if present, and strip leading whitespace.
            xml_content = response.content.decode('utf-8-sig').lstrip()
            parsed_feed = xmltodict.parse(xml_content)
            feeds[url] = parsed_feed
        except Exception as e:
            print(f"Error fetching podcast '{podcast_name}': {e}")
    return feeds

def extract_items(feeds_json, podcasts):
    """
    Extracts the 'item' elements from each feed's channel and returns them as a list of dictionaries,
    adding the feed URL and the associated podcast name to each item.
    
    Parameters:
        feeds_json (dict): Dictionary of parsed RSS feeds keyed by feed URL.
        podcasts (dict): Dictionary of podcasts where keys are podcast names and values are feed URLs.
        
    Returns:
        list: A list of dictionaries, each representing an RSS item with 'feed_url' and 'podcast_name' added.
    """
    # Create a reverse mapping: feed URL -> podcast name
    url_to_podcast = {url: name for name, url in podcasts.items()}
    items_list = []
    for url, feed in feeds_json.items():
        # Safely access the channel
        channel = feed.get("rss", {}).get("channel", {})
        items = channel.get("item", [])
        # Ensure items is always a list
        if isinstance(items, dict):
            items = [items]
        for item in items:
            item['feed_url'] = url
            item['podcast_name'] = url_to_podcast.get(url, "Unknown Podcast")
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

def run_podcast_task():
    # Path to the new data file
    new_data_file = f'{DATA_PATH}new_podcast_data/new_podcast_data_{datetime.now().strftime("%d%m%Y")}.csv'

    # Check if the new data file exists
    if not os.path.exists(new_data_file):
        print(f"{new_data_file} not found. Pulling new data...")

        # URLs for the RSS feeds
        podcasts = {
            "That Triathlon Life Podcast": "https://feeds.buzzsprout.com/1922707.rss",
            "That Triathlon Show": "https://feeds.simplecast.com/RxABNZH0",
            "Triathlon Therapy": "https://media.rss.com/triathlontherapy/feed.xml",
            #"Tri Velo Coaching": "https://www.omnycontent.com/d/playlist/e47441f6-05a4-494f-8b56-ab9001865616/29c15e9a-11d9-4426-84e6-ab910017268d/podcast.rss",
            "TrainerRoad": "https://anchor.fm/s/ee9bd108/podcast/rss",
            "Crushing Iron": "https://crushingiron.libsyn.com/rss",
            "Pro Tri News": "https://feeds.buzzsprout.com/1736374.rss",
            "TriVelo Coaching": "https://www.omnycontent.com/d/playlist/e47441f6-05a4-494f-8b56-ab9001865616/29c15e9a-11d9-4426-84e6-ab9100172662/6f68cfc5-21a8-41d8-8f91-ab910017268d/podcast.rss",
            "Oxygen Addict" : "http://feeds.podtrac.com/YdHIp7gcgnlh",
            "The Triathlon Hour" : "https://feed.podbean.com/HowTheyTrain/feed.xml",
            "Ironman Insider" : "https://feeds.buzzsprout.com/2360650.rss"
        }
        
        # Fetch and parse the RSS feeds
        feeds_json = fetch_and_parse_podcast_rss(podcasts)
        
        # Extract items from each feed into a list of dictionaries
        items_data = extract_items(feeds_json, podcasts)
        
        # Convert the list of dictionaries to a pandas DataFrame
        df = pd.DataFrame(items_data)

        # Clean the HTML in the 'description' column
        df['description'] = df['description'].apply(clean_html)
        print(df['enclosure'])

        def extract_url(enclosure):
            if isinstance(enclosure, dict):
                return enclosure.get('@url')
            else:
                return None

        df['url'] = df['enclosure'].apply(extract_url)

        # Save the new data to a CSV file
        df.to_csv(new_data_file, index=False)

        # Now proceed with the rest of the logic (e.g., union, remove duplicates, etc.)
        new_data = df
        #print(new_data)
        # Read the existing 'today.csv' file
        if os.path.exists(os.path.join(DATA_PATH, 'podcast_today.csv')):
            today_data = pd.read_csv(os.path.join(DATA_PATH, 'podcast_today.csv'), usecols=['url', 'title', 'description', 'pubDate'])
        # Union the new data with the existing data
            combined_data = pd.concat([today_data, new_data], ignore_index=True)
        else:
            combined_data = new_data

        # Remove duplicates based on the 'link' column (assuming 'link' is unique for each article)
        combined_data = combined_data.drop_duplicates(subset='link', keep='last')

        # Convert 'pubDate' to datetime format to sort by date
        combined_data.loc[:, 'pubDate'] = pd.to_datetime(combined_data['pubDate'], errors='coerce', utc=True)

        # Calculate the current UTC time and the threshold for three weeks ago
        current_time = pd.Timestamp.now(tz='UTC')
        three_weeks_ago = current_time - pd.Timedelta(weeks=3)

        # Filter the DataFrame for rows with pubDate >= three_weeks_ago
        combined_data = combined_data[combined_data['pubDate'] >= three_weeks_ago]

        # Sort by 'pubDate' and keep the 100 most recent rows
        combined_data_sorted = combined_data.sort_values(by='pubDate', ascending=False).head(100)

        # Save the combined and sorted data back to 'today.csv'
        combined_data_sorted.to_csv(os.path.join(DATA_PATH, 'podcast_today.csv'), index=False)

        print("Data update complete: today.csv saved.")

    else:
        print(f"{new_data_file} exists. Skipping data pull.")

#if __name__ == '__main__':
#    run_podcast_task()
from flask import Flask, render_template, request
import pandas as pd
import os
import subprocess
from urllib.parse import urlparse
from datetime import datetime
import pytz
from pull_instagram import run_instagram_task
from pull_news import run_news_task 
from pull_reddit import run_reddit_task
from pull_youtube import run_youtube_task
from pull_podcasts import run_podcast_task
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()
DATA_PATH = os.getenv("DATA_PATH")

app = Flask(__name__)

# File to store the last run date
LAST_RUN_FILE = f"{DATA_PATH}last_run_date.txt"


def check_and_run_scripts():
    """Check if scripts have run today after UTC 12pm; if not, execute them."""
    # Get current UTC time and compute today's noon time
    now_utc = datetime.now(pytz.utc)
    today_noon = now_utc.replace(hour=7, minute=0, second=0, microsecond=0)
    
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
        run_podcast_task()

        # Update the file with the current UTC timestamp in ISO format
        with open(LAST_RUN_FILE, "w") as f:
            f.write(datetime.now(pytz.utc).isoformat())
    else:
        print("Scripts already ran today after UTC 12pm. Skipping execution.")

@app.route('/', methods=['GET', 'POST'])
def index():
    # Check and run scripts if needed
    check_and_run_scripts()

    # --- Process News Articles (today.csv) ---
    new_data_file = f'{DATA_PATH}newdata/newdata_{datetime.now().strftime("%d%m%Y")}.csv'
    print(new_data_file)
    if os.path.exists(new_data_file):
        df = pd.read_csv(new_data_file, usecols=['link', 'title', 'description', 'pubDate'], on_bad_lines='skip')
    else:
        print('running news task')
        run_news_task()
        df = pd.read_csv(new_data_file, usecols=['link', 'title', 'description', 'pubDate'], on_bad_lines='skip')
    
    # Add a new column for the base URL (domain)
    df['base_url'] = df['link'].apply(lambda x: urlparse(x).netloc)
    
    # Convert 'pubDate' to datetime, handle tz-awareness
    df['pubDate'] = pd.to_datetime(df['pubDate'], errors='coerce')
    if df['pubDate'].dt.tz is None:
        df['pubDate'] = df['pubDate'].dt.tz_localize('UTC')
    else:
        df['pubDate'] = df['pubDate'].dt.tz_convert('UTC')
    
    # Get the current time in UTC
    today = datetime.now(pytz.utc)
    
    # Calculate the difference in days from today
    df['days_old'] = (today - df['pubDate']).dt.days
    
    # Apply the card class logic based on article age
    def get_card_class(days_old):
        if days_old > 60:
            return 'red'
        elif days_old > 3:
            return 'orange'
        else:
            return 'normal'
    
    df['card_class'] = df['days_old'].apply(get_card_class)
    
    # Filter the dataframe based on the selected date range
    filter_range = request.args.get('date_filter', 'all')
    if filter_range == 'last_3':
        df = df[df['days_old'] <= 3]
    elif filter_range == 'last_60':
        df = df[df['days_old'] <= 60]
    
    # Sort the dataframe by 'pubDate' in descending order and format the date
    df = df.sort_values(by='pubDate', ascending=False)
    df['formatted_pubDate'] = df['pubDate'].dt.strftime('%B %d, %Y')
    
    # --- Process Instagram Posts ---
    # Read the Instagram CSV only if it exists
    print('start instagram')
    new_data_file = f'{DATA_PATH}new_insta_data/new_insta_data_{datetime.now().strftime("%d%m%Y")}.csv'
    if os.path.exists(new_data_file):
        print('reading instagram data')
        instagram_df = pd.read_csv(f'{DATA_PATH}insta_today.csv')
        instagram_df = instagram_df[instagram_df['url'].str.contains('/p/', na=False)]
        #print(instagram_df)
    else:
        print('cannot find insta data')
        instagram_df = pd.DataFrame(columns=['url', 'timestamp'])  # Empty DataFrame fallback
    
    ## Process Reddit Posts --
    print('start reddit')
    new_data_file = f'{DATA_PATH}new_reddit_data/new_reddit_data_{datetime.now().strftime("%d%m%Y")}.csv'
    if os.path.exists(new_data_file):
        reddit_df = pd.read_csv(f'{DATA_PATH}reddit_today.csv')
    else:
        print('running reddit task')
        run_reddit_task()
        reddit_df = pd.read_csv(f'{DATA_PATH}reddit_today.csv')
 
     ## Process Youtube Posts --
    print('start youtube')
    new_data_file = f'{DATA_PATH}new_yt_data/new_yt_data_{datetime.now().strftime("%d%m%Y")}.csv'
    if os.path.exists(new_data_file):
        try:
            latest_videos_df = pd.read_csv(f'{DATA_PATH}yt_today.csv') 
        except:
            run_youtube_task()
            latest_videos_df = pd.read_csv(f'{DATA_PATH}yt_today.csv')
    else:
        print('running youtube task')
        run_youtube_task()
        latest_videos_df = pd.read_csv(f'{DATA_PATH}yt_today.csv')
       
    latest_videos_df = latest_videos_df.sort_values(by='publishedAt', ascending=False)
    latest_videos_df['publishedAt'] = pd.to_datetime(latest_videos_df['publishedAt'])
    latest_videos_df['formatted_publishedAt'] = latest_videos_df['publishedAt'].dt.strftime('%B %d, %Y')
    #print(latest_videos_df)

    ## Process Podcast
    new_data_file = f'{DATA_PATH}new_podcast_data/new_podcast_data_{datetime.now().strftime("%d%m%Y")}.csv'
    print(new_data_file)
    if os.path.exists(new_data_file):
        pod_df = pd.read_csv(new_data_file, usecols=['url', 'title', 'description', 'pubDate','podcast_name'], on_bad_lines='skip')
    else:
        print('running podcast task')
        run_podcast_task()
        pod_df = pd.read_csv(new_data_file, usecols=['url', 'title', 'description', 'pubDate', 'podcast_name'], on_bad_lines='skip')
    
    # Add a new column for the base URL (domain)
    #pod_df['base_url'] = pod_df['link'].apply(lambda x: urlparse(x).netloc)
    
    # Convert 'pubDate' to datetime, handle tz-awareness
    pod_df['pubDate'] = pd.to_datetime(pod_df['pubDate'], errors='coerce', utc=True)
    print(pod_df)
    if pod_df['pubDate'].dt.tz is None:
        pod_df['pubDate'] = pod_df['pubDate'].dt.tz_localize('UTC')
    else:
        pod_df['pubDate'] = pod_df['pubDate'].dt.tz_convert('UTC')
    pod_df = (
        pod_df
        .sort_values(by='pubDate', ascending=False)
        .groupby('podcast_name')
        .head(2)                # take the first 2 rows in each group
        .reset_index(drop=True) # optional, just to clean up the index
    )

    pod_df['formatted_pubDate'] = pod_df['pubDate'].dt.strftime('%B %d, %Y')
    pod_df = pod_df.sort_values(by='pubDate', ascending=False)
    current_time = pd.Timestamp.now(tz='UTC')
    three_weeks_ago = current_time - pd.Timedelta(weeks=3)
    pod_df = pod_df[pod_df['pubDate'] >= three_weeks_ago]
    pod_df = pod_df[pod_df['formatted_pubDate'].notna()]
    # Filter the DataFrame for rows with pubDate >= three_weeks_ago
        
    pod_df['card_class'] = 'normal'
    print(pod_df.head())
    
    return render_template(
        'index.html', 
        articles=df.to_dict(orient='records'),
        instagram_posts=instagram_df.to_dict(orient='records'),
        reddit_posts = reddit_df.to_dict(orient='records'),
        youtube_videos = latest_videos_df[['title', 'videoId', 'thumbnail', 'formatted_publishedAt']].to_dict(orient='records'),
        podcasts = pod_df[['url', 'title', 'description', 'formatted_pubDate','card_class','podcast_name']].to_dict(orient='records')
    )

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)

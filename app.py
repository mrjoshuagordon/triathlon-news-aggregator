from flask import Flask, render_template, request
import pandas as pd
import os
import subprocess
from urllib.parse import urlparse
from datetime import datetime
import pytz

app = Flask(__name__)

# File to store the last run date
LAST_RUN_FILE = "data/last_run_date.txt"

def check_and_run_scripts():
    """Check if scripts have run today; if not, execute them."""
    today_str = datetime.now(pytz.utc).strftime('%Y-%m-%d')
    
    # Check if last_run_date.txt exists and read its contents
    if os.path.exists(LAST_RUN_FILE):
        with open(LAST_RUN_FILE, "r") as f:
            last_run_date = f.read().strip()
    else:
        last_run_date = ""

    # If the last run date is different from today, execute scripts
    if last_run_date != today_str:
        print("Running scripts for the first time today...")
        
        # Run scripts
        subprocess.run(["python", "pull_news.py"], check=True)
        subprocess.run(["python", "pull_instagram.py"], check=True)

        # Update last run date
        with open(LAST_RUN_FILE, "w") as f:
            f.write(today_str)
    else:
        print("Scripts already ran today. Skipping execution.")

@app.route('/', methods=['GET', 'POST'])
def index():
    # Check and run scripts if needed
    check_and_run_scripts()

    # --- Process News Articles (today.csv) ---
    df = pd.read_csv('data/today.csv', usecols=['link', 'title', 'description', 'pubDate'])
    
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
    new_data_file = 'data/new_insta_data/new_insta_data' + datetime.now().strftime('%d%m%Y') + '.csv'
    
    # Read the Instagram CSV only if it exists
    if os.path.exists(new_data_file):
        instagram_df = pd.read_csv(new_data_file)
        instagram_df = instagram_df[instagram_df['url'].str.contains('/p/')]
    else:
        instagram_df = pd.DataFrame(columns=['url', 'timestamp'])  # Empty DataFrame fallback
    
    return render_template(
        'index.html', 
        articles=df.to_dict(orient='records'),
        instagram_posts=instagram_df.to_dict(orient='records')
    )

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)

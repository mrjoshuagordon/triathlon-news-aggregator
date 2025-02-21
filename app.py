from flask import Flask, render_template, request
import pandas as pd
from urllib.parse import urlparse
from datetime import datetime
import pytz

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def index():
    # Read the CSV file and include the 'pubDate' column
    df = pd.read_csv('data/today.csv', usecols=['link', 'title', 'description', 'pubDate'])

    # Add a new column for the base URL (domain)
    df['base_url'] = df['link'].apply(lambda x: urlparse(x).netloc)

    # Convert 'pubDate' to datetime, handle tz-awareness
    df['pubDate'] = pd.to_datetime(df['pubDate'], errors='coerce')

    # Check if 'pubDate' is tz-aware, if not, localize to UTC
    if df['pubDate'].dt.tz is None:
        df['pubDate'] = df['pubDate'].dt.tz_localize('UTC')  # Localize if tz-naive
    else:
        df['pubDate'] = df['pubDate'].dt.tz_convert('UTC')  # Convert to UTC if tz-aware

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
    filter_range = request.args.get('date_filter', 'all')  # Default to 'all' if no filter is selected
    if filter_range == 'last_3':
        df = df[df['days_old'] <= 3]
    elif filter_range == 'last_60':
        df = df[df['days_old'] <= 60]

    # Sort the dataframe by 'pubDate' in descending order
    df = df.sort_values(by='pubDate', ascending=False)

    # Format 'pubDate' as 'Month day, Year'
    df['formatted_pubDate'] = df['pubDate'].dt.strftime('%B %d, %Y')

    return render_template('index.html', articles=df.to_dict(orient='records'))

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)

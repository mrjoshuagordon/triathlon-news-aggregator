from config import DATA_PATH, REDDIT_CLIENT_ID, REDDIT_CLIENT_SECRET
import praw
import pandas as pd

def run_reddit_task():
    """
    Fetches top posts from specified subreddits for the past week, processes the data by sorting and ranking,
    and saves the results to CSV files.
    
    Returns:
        pd.DataFrame: DataFrame containing the fetched Reddit post data.
    """
    try:
        import praw
        import pandas as pd
        from datetime import datetime

        # Initialize the Reddit instance with your credentials
        reddit = praw.Reddit(
            client_id=REDDIT_CLIENT_ID,
            client_secret=REDDIT_CLIENT_SECRET,
            user_agent='web:tri-news-agg:v1.0 (by /u/precisemultisport)'
        )

        # List of subreddits to extract data from
        subreddits = ['triathlon', 'ironmantriathlon', 'garmin', 'zwift', 'AdvancedRunning']
        posts_list = []

        # Loop through each subreddit and fetch top 5 posts from the past week
        for sub in subreddits:
            subreddit = reddit.subreddit(sub)
            for submission in subreddit.top(time_filter='week', limit=5):
                posts_list.append({
                    'sub': sub,
                    'title': submission.title,
                    'score': submission.score,
                    'url': submission.url,
                    'author': submission.author.name if submission.author else None
                })

        # Create a DataFrame from the list of posts
        df = pd.DataFrame(posts_list)

        # Sort by 'sub' and then by 'score'
        df = df.sort_values(['sub', 'score'])

        # For each group in 'sub', assign a rank based on the order of 'score'
        # First method using cumcount (this line is optional, as the next line overrides it)
        df['rank'] = df.groupby('sub').cumcount() + 1
        
        # Alternatively, rank based on 'score' ensuring ties are broken by order of appearance
        df['rank'] = df.groupby('sub')['score'].rank(method='first').astype(int)

        # Sort the DataFrame by 'rank' in descending order
        df = df.sort_values(['rank'], ascending=False)

        # Define output file paths
        new_data_file = f'{DATA_PATH}/new_reddit_data/new_reddit_data_' + datetime.now().strftime('%d%m%Y') + '.csv'
        today_data_file = f'{DATA_PATH}reddit_today.csv'

        # Save DataFrame to CSV files
        df.to_csv(new_data_file, index=False)
        df.to_csv(today_data_file, index=False)
        print(f"Data successfully saved to {new_data_file} and {today_data_file}")
        return df

    except Exception as e:
        print(f"An error occurred: {e}")
        return None

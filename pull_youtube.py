from datetime import datetime, timedelta
import requests
import pandas as pd  
from dotenv import load_dotenv
import os
import glob
# Load environment variables from .env file
load_dotenv()
DATA_PATH = os.getenv("DATA_PATH")
API_KEY = os.getenv("YT_API_KEY")
print(API_KEY)


def find_newest_csv_by_mtime(data_path):
    folder = os.path.join(data_path, "new_yt_data")
    pattern = os.path.join(folder, "new_yt_data_*.csv")
    csv_files = glob.glob(pattern)
    
    if not csv_files:
        return None  # No CSV files found

    # Sort the files by their modification time (oldest first)
    csv_files.sort(key=lambda x: os.path.getmtime(x))
    # Pop the last file from the sorted list, which is the newest
    newest_file = csv_files.pop()
    return newest_file

def run_youtube_task():
    
    # Fetch the latest videos and store them in a DataFrame
    channel_ids = ['UC-gct8TB_8l5HsQHBBr8hyQ', 'UCaJDcjxkg5YSTLWwxIUMsxA', 'UCNQaItQ0LLVu5987SD88s2w', 
                'UC6PP69DCmBwMCPf9RSSTNTg', 'UC8AySUd_LUSiT3nX8XlDFlQ', 'UCJVMrR290HU9pDxaP35u_cg',
                'UCjx2dRZxwnSVBNONIBOGQ1Q', 'UCuGZGcO5LvIH4u9g_2ZsHGQ', 'UCUlPrWg9Ef-IGsKRfDCPPew',
                'UCITB6kXrkXZBD9e_sHCVE1Q', 'UC9GTUpGeWTxRdtAK6Jg_Jsw', 'UC54u52Zmy0Os2RJihw2FiwA',
                'UCRzwfX1kxKTyb6IeZpik9OQ', 'UCS9H2SIvJnH47tDUwCb0Ixw', 'UC9jBSAEPF5egz7S2dT7zxEQ',
                'UCMv-CGWRT5yVMFXjRJmBVOw', 'UCP6EsU9T2RykT1quNR5moeg', 'UCXEsrQcmNK6gCAVSmhoIYZw', 
                'UC0VKd5PFrhj-qsnWw8VVmyQ']

    # List to store the video details for each channel
    all_videos = []

    # Iterate over each channel ID to fetch latest videos
    for channel_id in channel_ids:
        URL_VIDEOS = (
            f"https://www.googleapis.com/youtube/v3/search?part=snippet"
            f"&channelId={channel_id}&maxResults=1&order=date&type=video&key={API_KEY}"
        )
        response = requests.get(URL_VIDEOS)
        data = response.json()

        # Extract video details
        for item in data.get("items", []):
            # Get the video publish date
            publish_date = datetime.strptime(item["snippet"]["publishedAt"], "%Y-%m-%dT%H:%M:%SZ")

            # Only include videos published within the last 7 days

            video = {
                "channel_id": channel_id,
                "title": item["snippet"]["title"],
                "videoId": item["id"]["videoId"],
                "thumbnail": item["snippet"]["thumbnails"]["medium"]["url"],
                "publishedAt": item["snippet"]["publishedAt"]
            }
            all_videos.append(video)

    # Convert the list of video details to a pandas DataFrame
    videos_df = pd.DataFrame(all_videos)
    print(videos_df)
    # Define output file paths
    new_data_file = f'{DATA_PATH}/new_yt_data/new_yt_data_' + datetime.now().strftime('%d%m%Y') + '.csv'
    today_data_file = f'{DATA_PATH}yt_today.csv'

    # Save DataFrame to CSV files
    
    if videos_df.shape[0] > 0:
        videos_df.to_csv(new_data_file, index=False)
        videos_df.to_csv(today_data_file, index=False)
    else:
        try:
            videos_df = find_newest_csv_by_mtime(DATA_PATH)
            videos_df.to_csv(today_data_file, index=False)
        except:
            print("No new videos found")
    print(f"Data successfully saved to {new_data_file} and {today_data_file}")
    
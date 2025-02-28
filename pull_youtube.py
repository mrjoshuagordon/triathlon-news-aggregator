from datetime import datetime, timedelta
import requests
import pandas as pd
from config import YT_API_KEY, DATA_PATH    

API_KEY = YT_API_KEY

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
        URL_VIDEOS = f"https://www.googleapis.com/youtube/v3/search?part=snippet&channelId={channel_id}&maxResults=10&order=date&type=video&key={API_KEY}"

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
    videos_df.to_csv(new_data_file, index=False)
    videos_df.to_csv(today_data_file, index=False)
    print(f"Data successfully saved to {new_data_file} and {today_data_file}")
    
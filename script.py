import pandas as pd
from datetime import datetime

# Read the new data file (assuming the filename will be in the form of newdata_ddmmyyyy.csv)
new_data_file = 'data/newdata/newdata_' + datetime.now().strftime('%d%m%Y') + '.csv'
new_data = pd.read_csv(new_data_file, usecols=['link', 'title', 'description', 'pubDate'])

# Read the existing 'today.csv' file
today_data = pd.read_csv('data/today.csv', usecols=['link', 'title', 'description', 'pubDate'])

# Union the new data with the existing data
combined_data = pd.concat([today_data, new_data], ignore_index=True)

# Remove duplicates based on the 'link' column (assuming 'link' is unique for each article)
combined_data = combined_data.drop_duplicates(subset='link', keep='last')

# Convert 'pubDate' to datetime format to sort by date
combined_data['pubDate'] = pd.to_datetime(combined_data['pubDate'], errors='coerce')

# Sort by 'pubDate' and keep the 100 most recent rows
combined_data_sorted = combined_data.sort_values(by='pubDate', ascending=False).head(100)

# Save the combined and sorted data back to 'today.csv'
combined_data_sorted.to_csv('data/today.csv', index=False)

print("Data update complete: today.csv saved.")

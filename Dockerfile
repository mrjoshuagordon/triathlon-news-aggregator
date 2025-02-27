# Use the official Python base image
FROM python:3.9-slim

# Set the working directory
WORKDIR /app

# Copy the application files to the container
COPY . /app

# Install necessary dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Install cron
RUN apt-get update && apt-get install -y cron

# Add the cron job to run the script.py daily
RUN echo "0 0 * * * python /app/script.py" > /etc/cron.d/scraper-cron
RUN chmod 0644 /etc/cron.d/scraper-cron
RUN crontab /etc/cron.d/scraper-cron

# Create the necessary directories
RUN mkdir -p /app/data/newdata
# Expose the port Flask runs on
EXPOSE 5000

# Run cron in the background and then start the Flask app
#CMD cp /data/config.py /app/config.py && python app.py
CMD CMD cron && python app.py

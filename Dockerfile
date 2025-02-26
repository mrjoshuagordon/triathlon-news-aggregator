# Use the official Python base image
FROM python:3.9-slim

# Set the working directory
WORKDIR /app

# Copy the application files to the container
COPY . /app

# Install necessary dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Create the necessary directories
RUN mkdir -p /app/data/newdata

# Expose the port Flask runs on
EXPOSE 5000

# Run cron in the background and then start the Flask app
CMD cron && python app.py

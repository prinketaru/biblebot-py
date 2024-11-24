# Use an official Python runtime as a parent image
FROM python:latest
# Set the working directory in the container
WORKDIR /app
# Copy the requirements file into the container
COPY requirements.txt /app/requirements.txt
# Install any Python dependencies
RUN pip install --no-cache-dir -r requirements.txt
# Copy the rest of the bot's code into the container
COPY . /app
# Run the bot
CMD ["python3", "bot.py"]

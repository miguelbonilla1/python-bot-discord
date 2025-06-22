FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Copy requirements
COPY requirements.txt .

# Install specific versions of dependencies
RUN pip install --no-cache-dir discord.py==2.1.1 pycoingecko==3.1.0 requests==2.31.0

# Copy bot code
COPY crypto_bot.py .

# Set environment variable for the bot token
ENV DISCORD_TOKEN="YOUR_NEW_TOKEN_HERE"

# Run the bot
CMD ["python", "crypto_bot.py"]

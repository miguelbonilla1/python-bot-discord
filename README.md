# Cryptocurrency Discord Bot

## Features
- Fetch current cryptocurrency prices
- Get 24-hour price changes
- Retrieve top cryptocurrencies by market cap

## Setup
1. Install dependencies:
```
pip install -r requirements.txt
```

2. Replace `YOUR_DISCORD_BOT_TOKEN` in `crypto_bot.py` with your actual Discord bot token

## Commands
- `!price [coin_name]`: Get price and 24h change for a specific cryptocurrency (default: bitcoin)
- `!top [count]`: Get top cryptocurrencies by market cap (default: 5)

## Example Usage
- `!price ethereum`
- `!top 10`

## Dependencies
- discord.py
- pycoingecko
- requests

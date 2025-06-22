import os
import discord
from discord.ext import commands
import logging
from pycoingecko import CoinGeckoAPI

# Set up logging
logging.basicConfig(level=logging.INFO)

# Initialize CoinGecko API
cg = CoinGeckoAPI()

# Set up Discord bot with minimal intents
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)

@bot.event
async def on_ready():
    print(f'\n=== BOT STARTED ===')
    print(f'Username: {bot.user.name}#{bot.user.discriminator}')
    print(f'User ID: {bot.user.id}')
    print(f'Guilds: {len(bot.guilds)}')
    print('Connected to guilds:')
    for guild in bot.guilds:
        print(f'- {guild.name} (ID: {guild.id})')
    print('=== READY ===\n')

@bot.event
async def on_message(message):
    try:
        print(f'\n=== MESSAGE RECEIVED ===')
        print(f'Content: {message.content}')
        print(f'Author: {message.author}')
        print(f'Channel: {message.channel}')
        print('=== END MESSAGE ===\n')
        
        # Process commands
        await bot.process_commands(message)
    except Exception as e:
        print(f'Error in on_message: {str(e)}')
        logging.error(f'on_message error: {str(e)}')

@bot.command(name='price')
async def get_crypto_price(ctx, coin: str = 'bitcoin'):
    try:
        print(f'\n=== COMMAND: price {coin} ===')
        print(f'Channel: {ctx.channel}')
        print(f'Guild: {ctx.guild}')
        
        # Search for coin by name or symbol
        search_result = cg.get_coins_markets(
            vs_currency='usd',
            ids=coin.lower(),
            order='market_cap_desc',
            per_page=1,
            page=1,
            sparkline=False
        )
        
        if not search_result:
            # Try searching by name or symbol if ID lookup fails
            all_coins = cg.get_coins_list()
            matching_coins = [c for c in all_coins 
                            if coin.lower() in c['name'].lower() or 
                            coin.lower() in c['symbol'].lower()]
            
            if not matching_coins:
                await ctx.send(f"No coin found matching '{coin}'")
                return
            
            # Get the first matching coin
            coin_id = matching_coins[0]['id']
            search_result = cg.get_coins_markets(
                vs_currency='usd',
                ids=coin_id,
                order='market_cap_desc',
                per_page=1,
                page=1,
                sparkline=False
            )
            
        coin_data = search_result[0]
        
        # Create an embed with detailed information
        embed = discord.Embed(
            title=f"{coin_data['name']} ({coin_data['symbol'].upper()})",
            color=discord.Color.green() if coin_data['price_change_percentage_24h'] >= 0 else discord.Color.red()
        )
        
        embed.add_field(name="Current Price", value=f"${coin_data['current_price']:,.2f}", inline=False)
        embed.add_field(name="24h Change", value=f"{coin_data['price_change_percentage_24h']:.2f}%", inline=False)
        embed.add_field(name="Market Cap", value=f"${coin_data['market_cap']:,.0f}", inline=False)
        embed.add_field(name="24h Volume", value=f"${coin_data['total_volume']:,.0f}", inline=False)
        embed.add_field(name="24h High", value=f"${coin_data['high_24h']:,.2f}", inline=False)
        embed.add_field(name="24h Low", value=f"${coin_data['low_24h']:,.2f}", inline=False)
        
        if coin_data.get('image'):
            embed.set_thumbnail(url=coin_data['image'])
        
        await ctx.send(embed=embed)
    
    except Exception as e:
        await ctx.send(f"Error fetching price for {coin}: {str(e)}")
        print(f"Error in get_crypto_price: {str(e)}")

@bot.command(name='coins')
async def list_coins(ctx):
    """List available cryptocurrencies"""
    try:
        # Get all coins
        coins = cg.get_coins_list()
        
        # Create embed with pagination
        embed = discord.Embed(
            title="Available Cryptocurrencies",
            description="Use !price [coin_name] to get detailed information",
            color=discord.Color.blue()
        )
        
        # Add first 20 coins (to keep the message manageable)
        for coin in coins[:20]:
            embed.add_field(
                name=f"{coin['name']} ({coin['symbol'].upper()})",
                value=coin['id'],
                inline=True
            )
        
        await ctx.send(embed=embed)
    
    except Exception as e:
        await ctx.send(f"Error fetching coin list: {str(e)}")
        print(f"Error in list_coins: {str(e)}")

@bot.command(name='search')
async def search_coin(ctx, *, query: str):
    """Search for a cryptocurrency by name"""
    try:
        # Search coins
        results = cg.get_search_trending()
        coins = results['coins']
        
        # Filter results by query
        filtered_coins = [coin for coin in coins if query.lower() in coin['item']['name'].lower() or 
                        query.lower() in coin['item']['symbol'].lower()]
        
        if not filtered_coins:
            await ctx.send(f"No coins found matching '{query}'")
            return
        
        # Create embed
        embed = discord.Embed(
            title=f"Search results for '{query}'",
            color=discord.Color.blue()
        )
        
        for coin in filtered_coins:
            embed.add_field(
                name=f"{coin['item']['name']} ({coin['item']['symbol'].upper()})",
                value=f"ID: {coin['item']['id']}\n" +
                      f"Current Price: ${coin['item']['price_btc']:.8f} BTC",
                inline=False
            )
        
        await ctx.send(embed=embed)
    
    except Exception as e:
        await ctx.send(f"Error searching for coin: {str(e)}")
        print(f"Error in search_coin: {str(e)}")

@bot.command(name='top')
async def get_top_cryptocurrencies(ctx, count: int = 5):
    """Fetch top cryptocurrencies by market cap"""
    try:
        # Fetch top cryptocurrencies
        top_coins = cg.get_coins_markets(vs_currency='usd', order='market_cap_desc', per_page=count, page=1)
        
        # Create an embed
        embed = discord.Embed(title="Top Cryptocurrencies", color=discord.Color.blue())
        
        for coin in top_coins:
            embed.add_field(
                name=coin['name'], 
                value=f"Price: ${coin['current_price']:,.2f}\n24h Change: {coin['price_change_percentage_24h']:.2f}%", 
                inline=False
            )
        
        await ctx.send(embed=embed)
    
    except Exception as e:
        await ctx.send(f"Error fetching top cryptocurrencies: {str(e)}")
        print(f"Error in get_top_cryptocurrencies: {str(e)}")

# Run the bot
bot_token = os.getenv('DISCORD_TOKEN')
if not bot_token:
    print("Error: DISCORD_TOKEN environment variable not set")
    exit(1)

bot.run(bot_token)

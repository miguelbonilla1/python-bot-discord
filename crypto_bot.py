import discord
from discord.ext import commands
from pycoingecko import CoinGeckoAPI
import os

cg = CoinGeckoAPI()

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)

@bot.event
async def on_ready():
    print(f'Bot has connected as {bot.user}')

@bot.command(name='price')
async def get_crypto_price(ctx, coin: str = 'bitcoin'):
    try:
        # First try direct ID lookup
        try:
            # Try to get price directly
            coin_data = cg.get_price(
                ids=coin.lower(),
                vs_currencies='usd',
                include_market_cap='true',
                include_24hr_change='true'
            )
            if coin_data:
                coin_name = list(coin_data.keys())[0]
                data = coin_data[coin_name]
                embed = discord.Embed(
                    title=f"{coin_name.title()} Price",
                    color=discord.Color.green() if data['usd_24h_change'] >= 0 else discord.Color.red()
                )
                embed.add_field(name="Price", value=f"${data['usd']:,.2f}", inline=False)
                embed.add_field(name="24h Change", value=f"{data['usd_24h_change']:.2f}%", inline=False)
                embed.add_field(name="Market Cap", value=f"${data['usd_market_cap']:,.0f}", inline=False)
                await ctx.send(embed=embed)
                return
        except:
            pass

        # If direct lookup failed, try searching by name
        try:
            # Get list of all coins
            all_coins = cg.get_coins_list()
            
            # Find matching coins
            matching_coins = [c for c in all_coins 
                            if coin.lower() in c['name'].lower() or 
                            coin.lower() in c['symbol'].lower()]
            
            if not matching_coins:
                await ctx.send(f"Could not find any coin matching '{coin}'")
                return
                
            # Show matching coins if multiple found
            if len(matching_coins) > 1:
                embed = discord.Embed(
                    title=f"Multiple coins found for '{coin}'",
                    description="Please specify the exact coin name or ID from the list below",
                    color=discord.Color.blue()
                )
                for c in matching_coins:
                    embed.add_field(
                        name=f"{c['name']} ({c['symbol'].upper()})",
                        value=c['id'],
                        inline=False
                    )
                await ctx.send(embed=embed)
                return
                
            # Get price for the single matching coin
            coin_id = matching_coins[0]['id']
            coin_data = cg.get_price(
                ids=coin_id,
                vs_currencies='usd',
                include_market_cap='true',
                include_24hr_change='true'
            )
            
            coin_name = list(coin_data.keys())[0]
            data = coin_data[coin_name]
            
            embed = discord.Embed(
                title=f"{coin_name.title()} Price",
                color=discord.Color.green() if data['usd_24h_change'] >= 0 else discord.Color.red()
            )
            embed.add_field(name="Price", value=f"${data['usd']:,.2f}", inline=False)
            embed.add_field(name="24h Change", value=f"{data['usd_24h_change']:.2f}%", inline=False)
            embed.add_field(name="Market Cap", value=f"${data['usd_market_cap']:,.0f}", inline=False)
            await ctx.send(embed=embed)
            
        except Exception as e:
            await ctx.send(f"Error searching for coin: {str(e)}")
            
    except Exception as e:
        await ctx.send(f"Error fetching price: {str(e)}")

@bot.command(name='top')
async def get_top_cryptocurrencies(ctx, count: int = 5):
    try:
        # Get top coins by market cap
        coins = cg.get_coins_markets(
            vs_currency='usd',
            order='market_cap_desc',
            per_page=count,
            page=1,
            sparkline=False
        )
        
        # Create embed
        embed = discord.Embed(
            title=f"Top {count} Cryptocurrencies",
            color=discord.Color.blue()
        )
        
        for coin in coins:
            embed.add_field(
                name=f"{coin['name']} ({coin['symbol'].upper()})",
                value=f"Price: ${coin['current_price']:,.2f}\n" +
                      f"Market Cap: ${coin['market_cap']:,.0f}",
                inline=False
            )
        
        await ctx.send(embed=embed)
    
    except Exception as e:
        await ctx.send(f"Error fetching top cryptocurrencies: {str(e)}")

bot.run(os.getenv('DISCORD_TOKEN'))

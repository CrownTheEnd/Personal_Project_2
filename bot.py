import discord
from functions import create_fighter
from discord.ext import commands

bot = commands.Bot(command_prefix='!')

@bot.event
async def on_ready():
    print(f'We have logged in as {bot.user}')

bot.run('YOUR_BOT_TOKEN')

# Define the bot and prefix
bot = commands.Bot(command_prefix='!')

# Define a simple command
@bot.command()
async def create(ctx, name, source):
    """Responds with a greeting."""
    create_fighter(name, source)
    await ctx.send('Hello!')

# Run the bot with your token
bot.run('YOUR_BOT_TOKEN')

#Replace 'YOUR_BOT_TOKEN' with the token from the bot you created in the Discord Developer Portal.
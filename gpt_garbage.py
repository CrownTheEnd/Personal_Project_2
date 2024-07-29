import discord
from discord.ext import commands
import random
import os
import json

# File path for storing fighters
file_path = './fighter_dictionary.json'

def load_token():
    with open('token.txt', 'r') as file:
        return file.read().strip()

DISCORD_TOKEN = load_token()

# Ensure the file exists
if not os.path.exists(file_path):
    with open(file_path, "w") as file:
        json.dump({}, file)  # Initialize with an empty dictionary

# Function to write fighters to the file
def write_to_fighters(fighter_dict):
    with open(file_path, 'w') as file:
        json.dump(fighter_dict, file, indent=4)  # Use indent=4 for pretty-printing

# Function to load fighters from the file
def load_fighters():
    with open(file_path, 'r') as file:
        try:
            fighter_dict = json.load(file)
        except json.JSONDecodeError:
            fighter_dict = {}  # Handle cases where the file might be empty or corrupted
    return fighter_dict

# Initialize the dictionary
fighter = load_fighters()

# Function to create a fighter
def create_fighter(name, source):
    if name not in fighter:
        fighter[name] = {
            'source': source,
            'wins': 0
        }
        write_to_fighters(fighter)
    else:
        # Update source if the fighter already exists
        fighter[name]['source'] = source
        write_to_fighters(fighter)

# Intents are required for certain operations
intents = discord.Intents.default()
intents.message_content = True  # Enable the message content intent

# Bot prefix and initialization
bot = commands.Bot(command_prefix='!', intents=intents)

# Event that runs when the bot is ready
@bot.event
async def on_ready():
    print(f'Bot is ready. Logged in as {bot.user}')

# Command to create a fighter
@bot.command()
async def create(ctx, name, source: str = None):
    if source is None:
        if ctx.message.attachments:
            source = ctx.message.attachments[0].url
        else:
            await ctx.send("You must provide a source link or upload an image.")
            return

    create_fighter(name, source)
    await ctx.send(f'{name} created with source: {source}')

@bot.command(name='fight')
async def fight(ctx, fighter_a_name: str, fighter_b_name: str):
    # Check if both fighters exist in the dictionary
    if fighter_a_name not in fighter or fighter_b_name not in fighter:
        await ctx.send("One or both of the fighters do not exist. Please create them first.")
        return

    result = simulate_fight(fighter_a_name, fighter_b_name)

    # Extract the winner's name from the result
    winner_name = result.split()[0]  # Assumes the result starts with the winner's name

    # Retrieve the winner's image URL and win count
    winner_image_url = fighter.get(winner_name, {}).get('source', '')
    current_wins = fighter.get(winner_name, {}).get('wins', 0)

    # Update the win tally for the winner
    if winner_name in fighter:
        fighter[winner_name]['wins'] += 1
    else:
        fighter[winner_name] = {
            'source': '',
            'wins': 1
        }
    
    # Save updated fighter information
    write_to_fighters(fighter)

    # Create an embed with the winner's image
    embed = discord.Embed(title=f"{winner_name} wins!", description=result)
    if winner_image_url and winner_image_url.startswith(('http://', 'https://')):
        embed.set_image(url=winner_image_url)
    
    # Display the tally of wins for the winning fighter
    embed.add_field(name="Current Tally", value=f"{winner_name}: {fighter[winner_name]['wins']} wins")

    await ctx.send(embed=embed)

def simulate_fight(fighter_a_name, fighter_b_name):
    # Initialize the fighters' stats
    fighter_a_hp = 100
    fighter_b_hp = 100

    # Assign random damage values (1 to 3)
    fighter_a_damage = random.randint(1, 3)
    fighter_b_damage = random.randint(1, 3)

    print(f"{fighter_a_name} damage: {fighter_a_damage}")
    print(f"{fighter_b_name} damage: {fighter_b_damage}")

    # Simulation loop
    while fighter_a_hp > 0 and fighter_b_hp > 0:
        # Coin flip determines who attacks first
        if random.choice([True, False]):
            # Fighter A attacks first
            fighter_b_hp -= fighter_a_damage
            if fighter_b_hp <= 0:
                return f"{fighter_a_name} wins!"

            # Fighter B attacks second
            fighter_a_hp -= fighter_b_damage
            if fighter_a_hp <= 0:
                return f"{fighter_b_name} wins!"
        else:
            # Fighter B attacks first
            fighter_a_hp -= fighter_b_damage
            if fighter_a_hp <= 0:
                return f"{fighter_b_name} wins!"

            # Fighter A attacks second
            fighter_b_hp -= fighter_a_damage
            if fighter_b_hp <= 0:
                return f"{fighter_a_name} wins!"


# Run the bot with the token
bot.run(DISCORD_TOKEN)

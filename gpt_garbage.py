import discord
from discord.ext import commands
import random
import os
import json
import asyncio
import io
import time
from abilities import abilities

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

# Intents are required for certain operations
intents = discord.Intents.default()
intents.message_content = True  # Enable the message content intent

# Bot prefix and initialization
bot = commands.Bot(command_prefix='!', intents=intents)

# Event that runs when the bot is ready
@bot.event
async def on_ready():
    print(f'Bot is ready. Logged in as {bot.user}')

@bot.command()
async def create(ctx, name, source: str = None):
    if source is None:
        if ctx.message.attachments:
            source = ctx.message.attachments[0].url
        else:
            await ctx.send("You must provide a source link or upload an image.")
            return

    user_id = str(ctx.author.id)  # Ensure user_id is a string
    name_lower = name.lower()  # Normalize the name to lowercase

    # Check if the name already exists across all users
    for user_fighters in fighter.values():
        if name_lower in [n.lower() for n in user_fighters]:
            await ctx.send("A fighter with that name already exists. Please choose a different name.")
            return

    # Create the fighter if the name is unique
    create_fighter(user_id, name, source)
    await ctx.send(f'{name} created with source: {source}')

def create_fighter(user_id, name, source):
    user_id_str = str(user_id)  # Ensure user_id is a string
    name_lower = name.lower()  # Normalize the name to lowercase

    if user_id_str not in fighter:
        fighter[user_id_str] = {}

    # Add the fighter if the name does not already exist for this user
    if name_lower not in [n.lower() for n in fighter[user_id_str]]:
        fighter[user_id_str][name] = {
            'source': source,
            'wins': 0
        }
        write_to_fighters(fighter)
    else:
        # Update source if the fighter already exists
        fighter[user_id_str][name]['source'] = source
        write_to_fighters(fighter)

@bot.command(name='fighterinfo')
async def my_fighters(ctx):
    user_id = str(ctx.author.id)  # Ensure the user_id is a string
    user_fighters = fighter.get(user_id, {})

    # Prepare the message content
    if not user_fighters:
        message = "You haven't created any fighters yet."
    else:
        fighter_list = '\n'.join(f"{name}: {details['source']}" for name, details in user_fighters.items())
        message = f"Your fighters:\n{fighter_list}"

    # Send the message to the user's DM
    try:
        await ctx.author.send(message)
        await ctx.send("I've sent you the details of your fighters in your DMs.")
    except Exception as e:
        await ctx.send("I couldn't send you a DM. Please make sure your DMs are open.")
        print(f"Failed to send DM: {e}")

@bot.command(name='fighterdetail')
async def get_fighter(ctx, name):
    user_id = str(ctx.author.id)  # Ensure the user_id is a string
    user_fighters = fighter.get(user_id, {})

    # Debugging: Print the user's fighters
    print(f"User ID: {user_id}")
    print(f"User Fighters: {user_fighters}")

    # Prepare the message content
    if name in user_fighters:
        message = f"Fighter {name}: {user_fighters[name]['source']}"
    else:
        message = f"You don't have a fighter named {name}."

    # Send the message to the user's DM
    try:
        await ctx.author.send(message)
        await ctx.send("I've sent you the details in your DMs.")
    except Exception as e:
        await ctx.send("I couldn't send you a DM. Please make sure your DMs are open.")
        print(f"Failed to send DM: {e}")

@bot.command(name='fight')
async def fight(ctx, fighter_a_name: str, fighter_b_name: str):
    user_id = str(ctx.author.id)  # Ensure user_id is a string

    # Normalize input names to lowercase
    fighter_a_name_lower = fighter_a_name.lower()
    fighter_b_name_lower = fighter_b_name.lower()

    fighter_a = None
    fighter_b = None

    # Search for fighters across all users
    for user_fighters in fighter.values():
        for name, details in user_fighters.items():
            if name.lower() == fighter_a_name_lower:
                fighter_a = details
            if name.lower() == fighter_b_name_lower:
                fighter_b = details

    # Check if both fighters were found
    if not fighter_a or not fighter_b:
        await ctx.send("One or both of the fighters do not exist. Please create them first.")
        return

    # Generate attack stats for this fight
    attack_stat_a = random.randint(8, 10)
    attack_stat_b = random.randint(8, 10)

    # Simulate the fight and get turn-by-turn results
    turn_results, stats = simulate_fight(
        fighter_a_name,
        fighter_b_name,
        attack_stat_a,
        attack_stat_b,
        detailed=True
    )

    # Extract detailed stats
    critical_hits_a = stats.get('critical_rate_a', 0) * 100  # Convert to percentage
    critical_hits_b = stats.get('critical_rate_b', 0) * 100  # Convert to percentage
    critical_rate_a = stats.get('critical_rate_a', 0)
    critical_rate_b = stats.get('critical_rate_b', 0)
    miss_rate_a = stats.get('miss_rate_a', 0)
    miss_rate_b = stats.get('miss_rate_b', 0)
    fighter_a_ability_name = stats.get('fighter_a_ability_name', 'None')
    fighter_b_ability_name = stats.get('fighter_b_ability_name', 'None')

    # Determine winner
    winner_name = turn_results[-1][0]  # Winner's name from the last turn
    winner_name_lower = winner_name.lower()

    # Retrieve the winner's image URL and win count
    winner_image_url = None
    current_wins = 0
    found_winner = False
    for user_fighters in fighter.values():
        if winner_name_lower in [name.lower() for name in user_fighters]:
            for name, details in user_fighters.items():
                if name.lower() == winner_name_lower:
                    winner_image_url = details['source']
                    current_wins = details['wins']
                    user_fighters[name]['wins'] += 1
                    found_winner = True
                    break
            if found_winner:
                break

    if not found_winner:
        # If the winner wasn't found, create it
        for user_fighters in fighter.values():
            user_fighters[winner_name] = {
                'source': '',
                'wins': 1
            }
            break

    # Save updated fighter information
    write_to_fighters(fighter)

    # Create and send the initial embed with fight updates
    message = await ctx.send(embed=discord.Embed(
        title=f"{fighter_a_name.capitalize()} vs {fighter_b_name.capitalize()}",
        description="Fight in progress...\n\n"
                    f"{fighter_a_name.capitalize()}: Attack Stat: {attack_stat_a}, Ability: {fighter_a_ability_name.capitalize()}\n"
                    f"{fighter_b_name.capitalize()}: Attack Stat: {attack_stat_b}, Ability: {fighter_b_ability_name.capitalize()}"
    ))

    # Send turn-by-turn results
    log_lines = []
    plain_log_lines = []
    for turn_result in turn_results:
        attacker, defender, damage, defender_hp, critical, miss = turn_result
        damage_text = f"**{int(damage)}**"  # Ensure damage is an integer
        defender_hp = int(defender_hp)  # Ensure HP is an integer

        if miss:
            turn_description = f"{attacker} misses the attack! {defender}'s HP is still {defender_hp}."
            plain_description = f"{attacker} misses the attack! {defender}'s HP is still {defender_hp}."
        elif critical:
            turn_description = f"{attacker} attacks {defender} for {damage_text} **CRITICAL** damage! {defender}'s HP is now {defender_hp}."
            plain_description = f"{attacker} attacks {defender} for {int(damage)} CRITICAL damage! {defender}'s HP is now {defender_hp}."
        else:
            turn_description = f"{attacker} attacks {defender} for {damage_text} damage! {defender}'s HP is now {defender_hp}."
            plain_description = f"{attacker} attacks {defender} for {int(damage)} damage! {defender}'s HP is now {defender_hp}."

        # Append turn description to fight log and embed update
        log_lines.append(turn_description)
        plain_log_lines.append(plain_description)
        
        # Update embed with the last 3 turns
        embed = discord.Embed(
            title=f"{fighter_a_name.capitalize()} vs {fighter_b_name.capitalize()}",
            description="\n".join(log_lines[-3:]) + "\n\n" +
                        f"{fighter_a_name.capitalize()}: Attack Stat: {attack_stat_a}, Ability: {fighter_a_ability_name.capitalize()}\n"
                        f"{fighter_b_name.capitalize()}: Attack Stat: {attack_stat_b}, Ability: {fighter_b_ability_name.capitalize()}"
        )
        await message.edit(embed=embed)
        await asyncio.sleep(0.10)  # Adjust this value for different intervals

    # Update embed to show winner with fight information
    embed = discord.Embed(
        title=f"{winner_name.capitalize()} wins!",
        description=(
            f"Current Tally: {current_wins + 1} wins\n\n"
            f"Fight Information:\n"
            f"{fighter_a_name.capitalize()}: Attack Stat: {attack_stat_a}, Ability: {fighter_a_ability_name.capitalize()}, Critical Rate: {critical_rate_a:.2f}%, Miss Rate: {miss_rate_a:.2f}%\n"
            f"{fighter_b_name.capitalize()}: Attack Stat: {attack_stat_b}, Ability: {fighter_b_ability_name.capitalize()}, Critical Rate: {critical_rate_b:.2f}%, Miss Rate: {miss_rate_b:.2f}%"
        )
    )
    if winner_image_url and winner_image_url.startswith(('http://', 'https://')):
        embed.set_image(url=winner_image_url)
    await message.edit(embed=embed)

    # Create and send the fight log as a .txt file
    log_content = "\n".join(plain_log_lines)  # Use plain log lines without bold formatting
    log_file = io.BytesIO(log_content.encode())
    log_file.seek(0)
    await ctx.send(file=discord.File(log_file, filename='fight_log.txt'))

def simulate_fight(fighter_a_name, fighter_b_name, attack_stat_a, attack_stat_b, detailed=False):
    import random
    import time

    random.seed(time.time())  # Seed the RNG for reproducibility

    # Initialize the fighters' stats
    fighter_a_hp = 100
    fighter_b_hp = 100
    max_hp = 100  # Maximum HP
    fighter_a_stats = {
        'attack_stat': attack_stat_a,
        'miss_chance': 0.05,
        'hp': fighter_a_hp,
        'max_hp': max_hp,
        'critical_chance': 0.10,
        'turn_order_change': False
    }
    fighter_b_stats = {
        'attack_stat': attack_stat_b,
        'miss_chance': 0.05,
        'hp': fighter_b_hp,
        'max_hp': max_hp,
        'critical_chance': 0.10,
        'turn_order_change': False
    }

    # Capitalize fighter names
    fighter_a_name = fighter_a_name.capitalize()
    fighter_b_name = fighter_b_name.capitalize()

    # Assign and apply random abilities to fighters for this fight
    fighter_a_ability_name = random.choice(list(abilities.keys()))
    fighter_b_ability_name = random.choice(list(abilities.keys()))

    apply_ability(fighter_a_stats, fighter_a_ability_name)
    apply_ability(fighter_b_stats, fighter_b_ability_name)

    # Initialize results list
    results = []

    critical_hits_a = 0
    critical_hits_b = 0
    miss_count_a = 0
    miss_count_b = 0
    total_attacks_a = 0
    total_attacks_b = 0

    # Determine turn order based on abilities
    fighter_a_goes_first = fighter_a_stats['turn_order_change']
    fighter_b_goes_first = fighter_b_stats['turn_order_change']

    if fighter_a_goes_first and fighter_b_goes_first:
        # If both have the turn order change ability, revert to random choice
        fighter_a_goes_first = fighter_b_goes_first = False

    # Simulation loop
    while fighter_a_hp > 0 and fighter_b_hp > 0:
        if (fighter_a_goes_first and not fighter_b_goes_first) or (not fighter_a_goes_first and not fighter_b_goes_first and random.choice([True, False])):
            # Fighter A attacks first
            total_attacks_a += 1
            damage_a, critical_a, miss_a = get_damage(fighter_a_stats['attack_stat'], fighter_a_stats)
            if miss_a:
                miss_count_a += 1
                results.append((fighter_a_name, fighter_b_name, int(damage_a), int(fighter_b_hp), '', miss_a))
            if not miss_a:
                fighter_b_hp -= damage_a
                if damage_a > 0:
                    if critical_a:
                        critical_hits_a += 1
                    if fighter_b_hp <= 0:
                        results.append((fighter_a_name, fighter_b_name, int(damage_a), 0, 'CRITICAL' if critical_a else '', miss_a))
                        break
                    else:
                        results.append((fighter_a_name, fighter_b_name, int(damage_a), int(fighter_b_hp), 'CRITICAL' if critical_a else '', miss_a))

            # Fighter B attacks second
            total_attacks_b += 1
            damage_b, critical_b, miss_b = get_damage(fighter_b_stats['attack_stat'], fighter_b_stats)
            if miss_b:
                miss_count_b += 1
                results.append((fighter_b_name, fighter_a_name, int(damage_b), int(fighter_a_hp), '', miss_b))
            if not miss_b:
                fighter_a_hp -= damage_b
                if damage_b > 0:
                    if critical_b:
                        critical_hits_b += 1
                    if fighter_a_hp <= 0:
                        results.append((fighter_b_name, fighter_a_name, int(damage_b), 0, 'CRITICAL' if critical_b else '', miss_b))
                        break
                    else:
                        results.append((fighter_b_name, fighter_a_name, int(damage_b), int(fighter_a_hp), 'CRITICAL' if critical_b else '', miss_b))

        else:
            # Fighter B attacks first
            total_attacks_b += 1
            damage_b, critical_b, miss_b = get_damage(fighter_b_stats['attack_stat'], fighter_b_stats)
            if miss_b:
                miss_count_b += 1
                results.append((fighter_b_name, fighter_a_name, int(damage_b), int(fighter_a_hp), '', miss_b))
            if not miss_b:
                fighter_a_hp -= damage_b
                if damage_b > 0:
                    if critical_b:
                        critical_hits_b += 1
                    if fighter_a_hp <= 0:
                        results.append((fighter_b_name, fighter_a_name, int(damage_b), 0, 'CRITICAL' if critical_b else '', miss_b))
                        break
                    else:
                        results.append((fighter_b_name, fighter_a_name, int(damage_b), int(fighter_a_hp), 'CRITICAL' if critical_b else '', miss_b))

            # Fighter A attacks second
            total_attacks_a += 1
            damage_a, critical_a, miss_a = get_damage(fighter_a_stats['attack_stat'], fighter_a_stats)
            if miss_a:
                miss_count_a += 1
                results.append((fighter_a_name, fighter_b_name, int(damage_a), int(fighter_b_hp), '', miss_a))
            if not miss_a:
                fighter_b_hp -= damage_a
                if damage_a > 0:
                    if critical_a:
                        critical_hits_a += 1
                    if fighter_b_hp <= 0:
                        results.append((fighter_a_name, fighter_b_name, int(damage_a), 0, 'CRITICAL' if critical_a else '', miss_a))
                        break
                    else:
                        results.append((fighter_a_name, fighter_b_name, int(damage_a), int(fighter_b_hp), 'CRITICAL' if critical_a else '', miss_a))

    # Calculate critical and miss rates
    critical_rate_a = critical_hits_a / total_attacks_a if total_attacks_a else 0
    critical_rate_b = critical_hits_b / total_attacks_b if total_attacks_b else 0
    miss_rate_a = miss_count_a / total_attacks_a if total_attacks_a else 0
    miss_rate_b = miss_count_b / total_attacks_b if total_attacks_b else 0

    # Determine winner
    if fighter_a_hp <= 0 and fighter_b_hp <= 0:
        winner = "Draw"
    elif fighter_a_hp <= 0:
        winner = fighter_b_name
    elif fighter_b_hp <= 0:
        winner = fighter_a_name
    else:
        winner = "None"

    if detailed:
        return results, {
            'fighter_a_name': fighter_a_name,
            'fighter_b_name': fighter_b_name,
            'fighter_a_hp': fighter_a_hp,
            'fighter_b_hp': fighter_b_hp,
            'critical_rate_a': critical_rate_a,
            'critical_rate_b': critical_rate_b,
            'miss_rate_a': miss_rate_a,
            'miss_rate_b': miss_rate_b,
            'fighter_a_ability_name': fighter_a_ability_name,
            'fighter_b_ability_name': fighter_b_ability_name
        }
    else:
        return results, winner


def get_damage(damage, fighter_stats):
    """Returns the damage with a chance to double it (critical hit) or miss."""
    if random.random() < fighter_stats['critical_chance']:
        return round(damage * 2), True, False
    elif random.random() < fighter_stats['miss_chance']:
        return 0, False, True
    return round(damage), False, False

def apply_ability(fighter_stats, ability_name, **kwargs):
    """Apply the effect of the fighter's ability dynamically."""
    ability_instance = abilities.get(ability_name)
    if ability_instance:
        # Extract necessary arguments for the effect function
        effect_kwargs = {k: v for k, v in kwargs.items() if k in ability_instance.effect.__code__.co_varnames}
        ability_instance.apply(fighter_stats, **effect_kwargs)

def calculate_damage(base_damage):
    """Calculate damage with a 10% chance to double it for critical hits."""
    if random.random() < 0.10:  # 10% chance
        return base_damage * 2, True
    return base_damage, False

def calculate_critical_rate(critical_hits, total_attacks):
    """Calculate the critical hit rate as a percentage."""
    if total_attacks == 0:
        return 0
    return (critical_hits / total_attacks) * 100

def apply_miss_chance(damage, miss_probability):
    """Determine if an attack misses based on the given miss probability."""
    if random.random() < miss_probability:
        return 0, True  # Attack missed
    return damage, False  # Attack hit

def calculate_miss_rate(missed_attacks, total_attacks):
    """Calculate the miss rate as a percentage."""
    if total_attacks == 0:
        return 0
    return (missed_attacks / total_attacks) * 100

# Run the bot with the token
bot.run(DISCORD_TOKEN)

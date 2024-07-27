import os
import random
import ast
from utility_functions import write_to_fighters

file_path = './fighter_dictionary.txt'
if not os.path.exists(file_path):
  file = open(file_path, "w")
  file.close()
  
with open(file_path, 'r') as file:
    fighter_content = file.read()
if fighter_content != "": 
    fighter = ast.literal_eval(fighter_content) 
else: 
    fighter = {}

def create_fighter(name, source):
    fighter[name] = source
    write_to_fighters(fighter)
    
def simulate_fight(fighter_a_name, fighter_b_name):
    # Initialize the fighters' stats
    fighter_a_hp = 100
    fighter_b_hp = 100

    # Assign random speed values (1 or 2)
    fighter_a_speed = random.choice([1, 2])
    fighter_b_speed = random.choice([1, 2])

    # Assign random damage values (1 to 3)
    fighter_a_damage = random.randint(1, 3)
    fighter_b_damage = random.randint(1, 3)

    print(f"{fighter_a_name} speed: {fighter_a_speed}, damage: {fighter_a_damage}")
    print(f"{fighter_b_name} speed: {fighter_b_speed}, damage: {fighter_b_damage}")

    # Simulation loop
    while fighter_a_hp > 0 and fighter_b_hp > 0:
        if fighter_a_speed > fighter_b_speed:
            # Fighter A attacks first
            fighter_b_hp -= fighter_a_damage
            if fighter_b_hp <= 0:
                return f"{fighter_a_name} wins!"

            # Fighter B attacks second
            fighter_a_hp -= fighter_b_damage
            if fighter_a_hp <= 0:
                return f"{fighter_b_name} wins!"
        elif fighter_b_speed > fighter_a_speed:
            # Fighter B attacks first
            fighter_a_hp -= fighter_b_damage
            if fighter_a_hp <= 0:
                return f"{fighter_b_name} wins!"

            # Fighter A attacks second
            fighter_b_hp -= fighter_a_damage
            if fighter_b_hp <= 0:
                return f"{fighter_a_name} wins!"
        else:
            # Speed is the same, roll to determine who attacks first
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


# Example usage
"""result = simulate_fight("Mira", "Cake")
print(result)"""

def calculate_odds(fighter_a_name, fighter_b_name, simulations=1000):
    wins_for_a = 0
    wins_for_b = 0

    for _ in range(simulations):
        result = simulate_fight(fighter_a_name, fighter_b_name)
        if f"{fighter_a_name} wins!" in result:
            wins_for_a += 1
        elif f"{fighter_b_name} wins!" in result:
            wins_for_b += 1

    odds_a = (wins_for_a / simulations) * 100
    odds_b = (wins_for_b / simulations) * 100

    return odds_a, odds_b

def calculate_payout(bet_amount, fighter_odds):
    # Calculate the payout multiplier (inverted odds)
    # Higher odds imply a lower payout multiplier
    payout_multiplier = 100 / fighter_odds
    return bet_amount * payout_multiplier

def betting_simulation(fighter_a_name, fighter_b_name, bet_amount, chosen_fighter):
    # Calculate odds
    odds_a, odds_b = calculate_odds(fighter_a_name, fighter_b_name, simulations=1000)
    
    # Determine which fighter the user bet on
    if chosen_fighter == fighter_a_name:
        fighter_odds = odds_a
    elif chosen_fighter == fighter_b_name:
        fighter_odds = odds_b
    else:
        return "Invalid fighter name."

    # Simulate the fight
    result = simulate_fight(fighter_a_name, fighter_b_name)
    
    # Determine the payout
    payout = 0
    if (chosen_fighter == fighter_a_name and f"{fighter_a_name} wins!" in result) or \
       (chosen_fighter == fighter_b_name and f"{fighter_b_name} wins!" in result):
        payout = calculate_payout(bet_amount, fighter_odds)
        # Round to the nearest whole number
        payout = round(payout)
        return f"You win! Your payout is ${payout}"
    else:
        return "You lose. Better luck next time!"

# Example usage
fighter_a_name = "Warrior A"
fighter_b_name = "Warrior B"
bet_amount = 100
chosen_fighter = "Warrior A"

result = betting_simulation(fighter_a_name, fighter_b_name, bet_amount, chosen_fighter)
print(result)
    

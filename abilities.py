class Ability:
    def __init__(self, name, effect):
        self.name = name
        self.effect = effect

    def apply(self, fighter_stats, **kwargs):
        """Apply the effect of the ability to the fighter's stats and other parameters."""
        self.effect(fighter_stats, **kwargs)

def apply_attack_buff(fighter_stats, **kwargs):
    fighter_stats['attack_stat'] *= 1.2  # 20% attack boost

def apply_miss_chance_debuff(fighter_stats, **kwargs):
    fighter_stats['miss_chance'] += 0.10  # 10% more miss chance

def apply_hp_heal(fighter_stats, **kwargs):
    # This will be handled directly in the fight simulation
    pass

def apply_critical_chance_buff(fighter_stats, **kwargs):
    # Increase critical chance by 10%
    fighter_stats['critical_chance'] += 0.10
    # Round critical chance to the nearest integer percentage
    fighter_stats['critical_chance'] = round(fighter_stats['critical_chance'] * 100) / 100

def apply_turn_order_change(fighter_stats, **kwargs):
    # This will be handled directly in the fight simulation
    pass

# Define abilities with their effects
abilities = {
    'power_strike': Ability('Power Strike', apply_attack_buff),
    'blindness': Ability('Blindness', apply_miss_chance_debuff),
    'heal': Ability('Heal', apply_hp_heal),
    'critical_boost': Ability('Critical Boost', apply_critical_chance_buff),
    'turn_swap': Ability('Turn Swap', apply_turn_order_change)
}
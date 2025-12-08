"""
Battle system for Pokemon battles
"""

import random

class BattleSystem:
    """Handles Pokemon battle logic"""
    
    def __init__(self, player_pokemon, enemy_pokemon):
        self.player = player_pokemon
        self.enemy = enemy_pokemon
        self.turn = "player"
        self.message = f"Wild {self.enemy.name} appeared!"
        self.battle_active = True
        self.winner = None
    
    def calculate_damage(self, attacker, defender, move):
        """Calculate damage based on stats and move"""
        if move.get('damage_class') == 'status':
            return 0
        
        power = move.get('power', 40)
        level = attacker.level
        attack = attacker.attack
        defense = defender.defense
        
        # Basic damage formula
        damage = ((2 * level / 5 + 2) * power * attack / defense / 50) + 2
        
        # Random factor
        damage *= random.uniform(0.85, 1.0)
        
        # Type effectiveness
        effectiveness = self.get_type_effectiveness(move['type'], defender.types)
        damage *= effectiveness
        
        return int(damage)
    
    def get_type_effectiveness(self, move_type, defender_types):
        """Get type effectiveness multiplier"""
        effectiveness_chart = {
            'fire': {'grass': 2.0, 'ice': 2.0, 'bug': 2.0, 'steel': 2.0,
                    'water': 0.5, 'fire': 0.5, 'rock': 0.5, 'dragon': 0.5},
            'water': {'fire': 2.0, 'ground': 2.0, 'rock': 2.0,
                     'water': 0.5, 'grass': 0.5, 'dragon': 0.5},
            'grass': {'water': 2.0, 'ground': 2.0, 'rock': 2.0,
                     'fire': 0.5, 'grass': 0.5, 'poison': 0.5, 'flying': 0.5, 'bug': 0.5, 'dragon': 0.5, 'steel': 0.5},
            'electric': {'water': 2.0, 'flying': 2.0,
                        'electric': 0.5, 'grass': 0.5, 'dragon': 0.5, 'ground': 0.0},
            'normal': {'rock': 0.5, 'steel': 0.5, 'ghost': 0.0},
            'fighting': {'normal': 2.0, 'ice': 2.0, 'rock': 2.0, 'dark': 2.0, 'steel': 2.0,
                        'poison': 0.5, 'flying': 0.5, 'psychic': 0.5, 'bug': 0.5, 'fairy': 0.5, 'ghost': 0.0},
            'flying': {'grass': 2.0, 'fighting': 2.0, 'bug': 2.0,
                      'electric': 0.5, 'rock': 0.5, 'steel': 0.5},
            'poison': {'grass': 2.0, 'fairy': 2.0,
                      'poison': 0.5, 'ground': 0.5, 'rock': 0.5, 'ghost': 0.5, 'steel': 0.0},
            'ground': {'fire': 2.0, 'electric': 2.0, 'poison': 2.0, 'rock': 2.0, 'steel': 2.0,
                      'grass': 0.5, 'bug': 0.5, 'flying': 0.0},
            'rock': {'fire': 2.0, 'ice': 2.0, 'flying': 2.0, 'bug': 2.0,
                    'fighting': 0.5, 'ground': 0.5, 'steel': 0.5},
            'bug': {'grass': 2.0, 'psychic': 2.0, 'dark': 2.0,
                   'fire': 0.5, 'fighting': 0.5, 'poison': 0.5, 'flying': 0.5, 'ghost': 0.5, 'steel': 0.5, 'fairy': 0.5},
            'ghost': {'psychic': 2.0, 'ghost': 2.0,
                     'dark': 0.5, 'normal': 0.0},
            'steel': {'ice': 2.0, 'rock': 2.0, 'fairy': 2.0,
                     'fire': 0.5, 'water': 0.5, 'electric': 0.5, 'steel': 0.5},
            'psychic': {'fighting': 2.0, 'poison': 2.0,
                       'psychic': 0.5, 'steel': 0.5, 'dark': 0.0},
            'ice': {'grass': 2.0, 'ground': 2.0, 'flying': 2.0, 'dragon': 2.0,
                   'fire': 0.5, 'water': 0.5, 'ice': 0.5, 'steel': 0.5},
            'dragon': {'dragon': 2.0, 'steel': 0.5, 'fairy': 0.0},
            'dark': {'psychic': 2.0, 'ghost': 2.0,
                    'fighting': 0.5, 'dark': 0.5, 'fairy': 0.5},
            'fairy': {'fighting': 2.0, 'dragon': 2.0, 'dark': 2.0,
                     'fire': 0.5, 'poison': 0.5, 'steel': 0.5}
        }
        
        multiplier = 1.0
        chart = effectiveness_chart.get(move_type, {})
        
        for def_type in defender_types:
            if def_type in chart:
                multiplier *= chart[def_type]
        
        return multiplier
    
    def player_attack(self, move_index):
        """Player attacks with selected move"""
        if move_index >= len(self.player.moves):
            return
        
        move = self.player.moves[move_index]
        
        # Check accuracy
        if random.randint(1, 100) > move.get('accuracy', 100):
            self.message = f"{self.player.name}'s attack missed!"
            self.turn = "enemy"
            return
        
        damage = self.calculate_damage(self.player, self.enemy, move)
        self.enemy.take_damage(damage)
        
        effectiveness = self.get_type_effectiveness(move['type'], self.enemy.types)
        eff_text = ""
        if effectiveness > 1:
            eff_text = " It's super effective!"
        elif effectiveness < 1 and effectiveness > 0:
            eff_text = " It's not very effective..."
        elif effectiveness == 0:
            eff_text = " It had no effect..."
        
        self.message = f"{self.player.name} used {move['name']}! Dealt {damage} damage.{eff_text}"
        
        if self.enemy.is_fainted():
            self.battle_active = False
            self.winner = "player"
            self.message = f"Wild {self.enemy.name} fainted! You won!"
            self.player.gain_exp(50)
        else:
            self.turn = "enemy"
    
    def enemy_attack(self):
        """Enemy attacks with random move"""
        if not self.enemy.moves:
            self.turn = "player"
            return
        
        move = random.choice(self.enemy.moves)
        
        # Check accuracy
        if random.randint(1, 100) > move.get('accuracy', 100):
            self.message = f"Wild {self.enemy.name}'s attack missed!"
            self.turn = "player"
            return
        
        damage = self.calculate_damage(self.enemy, self.player, move)
        self.player.take_damage(damage)
        
        self.message = f"Wild {self.enemy.name} used {move['name']}! Dealt {damage} damage."
        
        if self.player.is_fainted():
            self.battle_active = False
            self.winner = "enemy"
            self.message = f"{self.player.name} fainted! You lost!"
        else:
            self.turn = "player"
    
    def run_away(self):
        """Attempt to run from battle"""
        if random.random() < 0.5:
            self.battle_active = False
            self.message = "Got away safely!"
            return True
        else:
            self.message = "Couldn't escape!"
            self.turn = "enemy"
            return False

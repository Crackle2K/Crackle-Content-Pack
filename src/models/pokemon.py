"""
Pokemon class and battle system
"""

import random
import pygame

class Pokemon:
    """Pokemon class to store Pokemon data and battle stats"""
    
    def __init__(self, pokemon_data, api_client, level=5):
        self.data = pokemon_data
        self.api_client = api_client
        
        self.name = pokemon_data['name'].capitalize()
        self.types = pokemon_data['types']
        self.level = level
        
        # Calculate stats based on level
        base_hp = pokemon_data['stats']['hp']
        self.max_hp = base_hp + self.level * 2
        self.hp = self.max_hp
        self.attack = pokemon_data['stats']['attack']
        self.defense = pokemon_data['stats']['defense']
        self.speed = pokemon_data['stats']['speed']
        
        self.moves = pokemon_data['moves'][:4]  # Max 4 moves
        self.exp = 0
        self.max_exp = 100
        
        # Sprite references (URLs)
        self.sprite_data = pokemon_data['sprites']
        self._sprite_front = None
        self._sprite_back = None
    
    def get_sprite_front(self, scale=(192, 192)):
        """Get front sprite (lazy load)"""
        if self._sprite_front is None:
            self._sprite_front = self.api_client.get_pokemon_sprite(
                self.data, 'front_default', scale
            )
        return self._sprite_front
    
    def get_sprite_back(self, scale=(192, 192)):
        """Get back sprite (lazy load)"""
        if self._sprite_back is None:
            self._sprite_back = self.api_client.get_pokemon_sprite(
                self.data, 'back_default', scale
            )
        return self._sprite_back
    
    def take_damage(self, damage):
        """Apply damage to Pokemon"""
        self.hp = max(0, self.hp - damage)
    
    def heal(self, amount):
        """Heal Pokemon"""
        self.hp = min(self.max_hp, self.hp + amount)
    
    def is_fainted(self):
        """Check if Pokemon has fainted"""
        return self.hp <= 0
    
    def gain_exp(self, amount):
        """Gain experience points"""
        self.exp += amount
        if self.exp >= self.max_exp:
            self.level_up()
    
    def level_up(self):
        """Level up the Pokemon"""
        self.level += 1
        self.exp = 0
        self.max_exp = int(self.max_exp * 1.2)
        
        # Stat increases
        self.max_hp += 5
        self.hp = self.max_hp
        self.attack += 2
        self.defense += 2
        self.speed += 2

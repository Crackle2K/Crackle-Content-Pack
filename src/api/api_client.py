"""
Pokemon API Client
Fetches data and images directly from PokeAPI without local caching
"""

import requests
import io
from PIL import Image
import pygame

class PokeAPIClient:
    """Client for fetching Pokemon data from PokeAPI"""
    
    def __init__(self):
        self.base_url = "https://pokeapi.co/api/v2"
        self.session = requests.Session()
        
        # Cache for current session only (in-memory)
        self.pokemon_cache = {}
        self.move_cache = {}
        self.sprite_cache = {}
    
    def get_pokemon_data(self, pokemon_id_or_name):
        """Fetch Pokemon data from API"""
        key = str(pokemon_id_or_name).lower()
        
        if key in self.pokemon_cache:
            return self.pokemon_cache[key]
        
        try:
            response = self.session.get(f"{self.base_url}/pokemon/{key}", timeout=10)
            response.raise_for_status()
            data = response.json()
            
            # Parse into simplified format
            pokemon_info = {
                'id': data['id'],
                'name': data['name'],
                'types': [t['type']['name'] for t in data['types']],
                'stats': {
                    'hp': next(s['base_stat'] for s in data['stats'] if s['stat']['name'] == 'hp'),
                    'attack': next(s['base_stat'] for s in data['stats'] if s['stat']['name'] == 'attack'),
                    'defense': next(s['base_stat'] for s in data['stats'] if s['stat']['name'] == 'defense'),
                    'speed': next(s['base_stat'] for s in data['stats'] if s['stat']['name'] == 'speed'),
                },
                'sprites': data['sprites'],
                'moves': []
            }
            
            # Get first 4 moves
            for move_entry in data['moves'][:4]:
                move_name = move_entry['move']['name']
                move_data = self.get_move_data(move_name)
                if move_data:
                    pokemon_info['moves'].append(move_data)
            
            # Ensure at least one move
            if not pokemon_info['moves']:
                pokemon_info['moves'].append({
                    'name': 'tackle',
                    'power': 40,
                    'accuracy': 100,
                    'pp': 35,
                    'type': 'normal',
                    'damage_class': 'physical'
                })
            
            self.pokemon_cache[key] = pokemon_info
            return pokemon_info
            
        except Exception as e:
            print(f"Error fetching Pokemon {pokemon_id_or_name}: {e}")
            return None
    
    def get_move_data(self, move_name):
        """Fetch move data from API"""
        key = move_name.lower()
        
        if key in self.move_cache:
            return self.move_cache[key]
        
        try:
            response = self.session.get(f"{self.base_url}/move/{key}", timeout=10)
            response.raise_for_status()
            data = response.json()
            
            move_info = {
                'name': data['name'],
                'power': data.get('power') or 40,
                'accuracy': data.get('accuracy') or 100,
                'pp': data.get('pp') or 20,
                'type': data['type']['name'],
                'damage_class': data['damage_class']['name']
            }
            
            self.move_cache[key] = move_info
            return move_info
            
        except Exception as e:
            print(f"Error fetching move {move_name}: {e}")
            return None
    
    def get_sprite(self, url, scale=(192, 192)):
        """Fetch and convert sprite from URL to pygame Surface"""
        if url in self.sprite_cache:
            return self.sprite_cache[url]
        
        try:
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            
            # Load image from bytes
            image_data = io.BytesIO(response.content)
            pil_image = Image.open(image_data).convert('RGBA')
            
            # Resize
            pil_image = pil_image.resize(scale, Image.NEAREST)
            
            # Convert to pygame surface
            mode = pil_image.mode
            size = pil_image.size
            data = pil_image.tobytes()
            
            pygame_surface = pygame.image.fromstring(data, size, mode)
            
            self.sprite_cache[url] = pygame_surface
            return pygame_surface
            
        except Exception as e:
            print(f"Error loading sprite from {url}: {e}")
            # Return placeholder
            surf = pygame.Surface(scale)
            surf.fill((200, 200, 200))
            return surf
    
    def get_pokemon_sprite(self, pokemon_data, sprite_type='front_default', scale=(192, 192)):
        """Get a specific sprite for a Pokemon"""
        url = pokemon_data['sprites'].get(sprite_type)
        
        if not url:
            # Fallback to default
            url = pokemon_data['sprites'].get('front_default')
        
        if url:
            return self.get_sprite(url, scale)
        
        # Return placeholder if no sprite available
        surf = pygame.Surface(scale)
        surf.fill((200, 200, 200))
        return surf

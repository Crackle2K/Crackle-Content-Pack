"""
Pokemon Game - Asset Downloader
Downloads sprites and data from PokeAPI
"""

import requests
import os
import json
from pathlib import Path

class AssetDownloader:
    def __init__(self):
        self.base_url = "https://pokeapi.co/api/v2"
        self.assets_dir = Path("game_assets")
        self.sprites_dir = self.assets_dir / "sprites"
        self.data_dir = self.assets_dir / "data"
        
        # Create directories
        self.assets_dir.mkdir(exist_ok=True)
        self.sprites_dir.mkdir(exist_ok=True)
        self.data_dir.mkdir(exist_ok=True)
        
    def download_image(self, url, filepath):
        """Download an image from URL to filepath"""
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            with open(filepath, 'wb') as f:
                f.write(response.content)
            return True
        except Exception as e:
            print(f"Error downloading {url}: {e}")
            return False
    
    def get_pokemon_data(self, pokemon_id):
        """Get Pokemon data from PokeAPI"""
        try:
            response = requests.get(f"{self.base_url}/pokemon/{pokemon_id}", timeout=10)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"Error fetching Pokemon {pokemon_id}: {e}")
            return None
    
    def get_move_data(self, move_name):
        """Get move data from PokeAPI"""
        try:
            response = requests.get(f"{self.base_url}/move/{move_name}", timeout=10)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"Error fetching move {move_name}: {e}")
            return None
    
    def download_pokemon(self, pokemon_id, pokemon_name):
        """Download a single Pokemon's sprites and data"""
        print(f"Downloading {pokemon_name}...")
        
        # Create Pokemon directory
        pokemon_dir = self.sprites_dir / pokemon_name.lower()
        pokemon_dir.mkdir(exist_ok=True)
        
        # Get Pokemon data
        data = self.get_pokemon_data(pokemon_id)
        if not data:
            return False
        
        # Extract and save relevant data
        pokemon_info = {
            'id': data['id'],
            'name': data['name'],
            'types': [t['type']['name'] for t in data['types']],
            'stats': {stat['stat']['name']: stat['base_stat'] for stat in data['stats']},
            'height': data['height'],
            'weight': data['weight'],
            'moves': []
        }
        
        # Get first 4 moves
        for i, move_entry in enumerate(data['moves'][:4]):
            move_name = move_entry['move']['name']
            move_data = self.get_move_data(move_name)
            if move_data:
                pokemon_info['moves'].append({
                    'name': move_data['name'],
                    'power': move_data.get('power', 40),
                    'accuracy': move_data.get('accuracy', 100),
                    'pp': move_data.get('pp', 20),
                    'type': move_data['type']['name'],
                    'damage_class': move_data['damage_class']['name']
                })
        
        # Save Pokemon data
        with open(self.data_dir / f"{pokemon_name.lower()}.json", 'w') as f:
            json.dump(pokemon_info, f, indent=2)
        
        # Download sprites
        sprites = data.get('sprites', {})
        
        # Front default
        if sprites.get('front_default'):
            self.download_image(
                sprites['front_default'],
                pokemon_dir / 'front.png'
            )
        
        # Back default
        if sprites.get('back_default'):
            self.download_image(
                sprites['back_default'],
                pokemon_dir / 'back.png'
            )
        
        # Front shiny
        if sprites.get('front_shiny'):
            self.download_image(
                sprites['front_shiny'],
                pokemon_dir / 'front_shiny.png'
            )
        
        # Back shiny
        if sprites.get('back_shiny'):
            self.download_image(
                sprites['back_shiny'],
                pokemon_dir / 'back_shiny.png'
            )
        
        print(f"✓ {pokemon_name} downloaded successfully")
        return True
    
    def download_starter_pokemon(self):
        """Download the classic starter Pokemon"""
        starters = [
            (1, 'bulbasaur'),
            (4, 'charmander'),
            (7, 'squirtle'),
        ]
        
        print("Downloading starter Pokemon...")
        for pokemon_id, name in starters:
            self.download_pokemon(pokemon_id, name)
    
    def download_wild_pokemon(self):
        """Download some common wild Pokemon"""
        wild_pokemon = [
            (16, 'pidgey'),
            (19, 'rattata'),
            (10, 'caterpie'),
            (13, 'weedle'),
            (25, 'pikachu'),
            (133, 'eevee'),
            (152, 'chikorita'),
            (155, 'cyndaquil'),
            (158, 'totodile'),
        ]
        
        print("\nDownloading wild Pokemon...")
        for pokemon_id, name in wild_pokemon:
            self.download_pokemon(pokemon_id, name)
    
    def download_all(self):
        """Download all necessary assets"""
        print("=" * 50)
        print("Pokemon Game Asset Downloader")
        print("=" * 50)
        
        self.download_starter_pokemon()
        self.download_wild_pokemon()
        
        print("\n" + "=" * 50)
        print("Asset download complete!")
        print(f"Assets saved to: {self.assets_dir.absolute()}")
        print("=" * 50)

if __name__ == "__main__":
    downloader = AssetDownloader()
    downloader.download_all()

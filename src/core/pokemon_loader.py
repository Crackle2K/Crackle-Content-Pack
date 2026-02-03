"""Load Pokemon data from downloaded JSON files."""

import json
from pathlib import Path
from typing import Dict, Any, Optional, List
from .type_chart import PokemonType


class PokemonDataLoader:
    """Loads and manages Pokemon data from JSON files."""
    
    def __init__(self, data_folder: str = "assets/pokemon_data"):
        """
        Initialize the Pokemon data loader.
        
        Args:
            data_folder: Path to folder containing Pokemon JSON files
        """
        self.data_folder = Path(data_folder)
        self._cache: Dict[int, Dict[str, Any]] = {}
        self._load_all_data()
    
    def _load_all_data(self):
        """Load all Pokemon data from JSON files into cache."""
        if not self.data_folder.exists():
            print(f"Warning: Pokemon data folder not found at {self.data_folder}")
            return
        
        json_files = sorted(self.data_folder.glob("*.json"))
        for json_file in json_files:
            try:
                with open(json_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    pokemon_id = data.get('id')
                    if pokemon_id:
                        self._cache[pokemon_id] = data
            except Exception as e:
                print(f"Error loading {json_file}: {e}")
        
        if self._cache:
            print(f"Loaded {len(self._cache)} Pokemon from JSON files")
    
    def get_pokemon_data(self, pokemon_id: int) -> Optional[Dict[str, Any]]:
        """
        Get Pokemon data by ID.
        
        Args:
            pokemon_id: The Pokemon's national dex number
            
        Returns:
            Dictionary containing Pokemon data, or None if not found
        """
        return self._cache.get(pokemon_id)
    
    def get_pokemon_name(self, pokemon_id: int) -> str:
        """Get Pokemon name by ID."""
        data = self.get_pokemon_data(pokemon_id)
        return data['name'].title() if data else f"Pokemon #{pokemon_id}"
    
    def get_pokemon_types(self, pokemon_id: int) -> List[PokemonType]:
        """Get Pokemon types by ID."""
        data = self.get_pokemon_data(pokemon_id)
        if not data:
            return [PokemonType.NORMAL]
        
        type_map = {
            'normal': PokemonType.NORMAL,
            'fire': PokemonType.FIRE,
            'water': PokemonType.WATER,
            'electric': PokemonType.ELECTRIC,
            'grass': PokemonType.GRASS,
            'ice': PokemonType.ICE,
            'fighting': PokemonType.FIGHTING,
            'poison': PokemonType.POISON,
            'ground': PokemonType.GROUND,
            'flying': PokemonType.FLYING,
            'psychic': PokemonType.PSYCHIC,
            'bug': PokemonType.BUG,
            'rock': PokemonType.ROCK,
            'ghost': PokemonType.GHOST,
            'dragon': PokemonType.DRAGON,
        }
        
        # Map Pokemon types, defaulting to NORMAL for unsupported types (Dark, Steel, Fairy)
        return [type_map.get(t.lower(), PokemonType.NORMAL) for t in data['types']]
    
    def get_base_stats(self, pokemon_id: int) -> Dict[str, int]:
        """
        Get Pokemon base stats by ID.
        
        Returns:
            Dictionary with hp, attack, defense, sp_attack, sp_defense, speed
        """
        data = self.get_pokemon_data(pokemon_id)
        if not data:
            return {"hp": 50, "attack": 50, "defense": 50, "sp_attack": 50, "sp_defense": 50, "speed": 50}
        
        stats = data.get('base_stats', {})
        # PokeAPI uses different naming conventions
        return {
            "hp": stats.get('hp', 50),
            "attack": stats.get('attack', 50),
            "defense": stats.get('defense', 50),
            "sp_attack": stats.get('special-attack', 50),
            "sp_defense": stats.get('special-defense', 50),
            "speed": stats.get('speed', 50)
        }
    
    def get_learnable_moves(self, pokemon_id: int, level_limit: Optional[int] = None) -> List[str]:
        """
        Get list of moves a Pokemon can learn.
        
        Args:
            pokemon_id: The Pokemon's ID
            level_limit: If specified, only return moves learned up to this level
            
        Returns:
            List of move names (filtered to only include moves available in the game)
        """
        data = self.get_pokemon_data(pokemon_id)
        if not data:
            return ["tackle"]
        
        moves = data.get('moves', [])
        
        # Filter for level-up moves only
        level_up_moves = [
            m for m in moves 
            if m.get('learn_method') == 'level-up'
        ]
        
        # Sort by level learned
        level_up_moves.sort(key=lambda m: m.get('level_learned', 0))
        
        # Apply level limit if specified
        if level_limit is not None:
            level_up_moves = [m for m in level_up_moves if m.get('level_learned', 0) <= level_limit]
        
        # Get move names (remove hyphens, use underscores)
        move_names = [m['name'].replace('-', '_') for m in level_up_moves]
        
        # Filter to only include moves that exist in MOVES_DATA
        try:
            from src.core.moves_data import MOVES_DATA
            available_moves = set(MOVES_DATA.keys())
            move_names = [m for m in move_names if m in available_moves]
        except Exception:
            pass
        
        return move_names if move_names else ["tackle"]
    
    def get_all_pokemon_ids(self) -> List[int]:
        """Get list of all available Pokemon IDs."""
        return sorted(self._cache.keys())
    
    def is_data_available(self) -> bool:
        """Check if Pokemon data is available."""
        return len(self._cache) > 0
    
    def get_pokemon_description(self, pokemon_id: int) -> str:
        """Get Pokemon flavor text/description."""
        data = self.get_pokemon_data(pokemon_id)
        if not data:
            return "A mysterious Pokemon."
        return data.get('flavor_text', 'A mysterious Pokemon.')
    
    def get_pokemon_genus(self, pokemon_id: int) -> str:
        """Get Pokemon genus (e.g., 'Seed Pokemon')."""
        data = self.get_pokemon_data(pokemon_id)
        if not data:
            return "Unknown Pokemon"
        return data.get('genus', 'Unknown Pokemon')


# Global instance
_loader: Optional[PokemonDataLoader] = None


def get_pokemon_loader() -> PokemonDataLoader:
    """Get or create the global Pokemon data loader instance."""
    global _loader
    if _loader is None:
        _loader = PokemonDataLoader()
    return _loader


def reload_pokemon_data():
    """Force reload of Pokemon data from disk."""
    global _loader
    _loader = PokemonDataLoader()
    return _loader

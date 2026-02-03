"""Pokemon base stats and data for Gen 1 Pokemon."""

from .type_chart import PokemonType


# Pokemon data format:
# pokemon_id: {
#     "name": str,
#     "types": [PokemonType, ...],
#     "base_stats": {"hp": int, "attack": int, "defense": int, "sp_attack": int, "sp_defense": int, "speed": int},
#     "learnable_moves": [move_name, ...]
# }

POKEMON_DATA = {
    1: {
        "name": "Bulbasaur",
        "types": [PokemonType.GRASS, PokemonType.POISON],
        "base_stats": {"hp": 45, "attack": 49, "defense": 49, "sp_attack": 65, "sp_defense": 65, "speed": 45},
        "learnable_moves": ["tackle", "vine_whip", "razor_leaf", "solar_beam", "sludge"]
    },
    2: {
        "name": "Ivysaur",
        "types": [PokemonType.GRASS, PokemonType.POISON],
        "base_stats": {"hp": 60, "attack": 62, "defense": 63, "sp_attack": 80, "sp_defense": 80, "speed": 60},
        "learnable_moves": ["tackle", "vine_whip", "razor_leaf", "solar_beam", "sludge"]
    },
    3: {
        "name": "Venusaur",
        "types": [PokemonType.GRASS, PokemonType.POISON],
        "base_stats": {"hp": 80, "attack": 82, "defense": 83, "sp_attack": 100, "sp_defense": 100, "speed": 80},
        "learnable_moves": ["tackle", "vine_whip", "razor_leaf", "solar_beam", "sludge", "earthquake"]
    },
    4: {
        "name": "Charmander",
        "types": [PokemonType.FIRE],
        "base_stats": {"hp": 39, "attack": 52, "defense": 43, "sp_attack": 60, "sp_defense": 50, "speed": 65},
        "learnable_moves": ["scratch", "ember", "flamethrower", "fire_blast", "dig"]
    },
    5: {
        "name": "Charmeleon",
        "types": [PokemonType.FIRE],
        "base_stats": {"hp": 58, "attack": 64, "defense": 58, "sp_attack": 80, "sp_defense": 65, "speed": 80},
        "learnable_moves": ["scratch", "ember", "flamethrower", "fire_blast", "dig"]
    },
    6: {
        "name": "Charizard",
        "types": [PokemonType.FIRE, PokemonType.FLYING],
        "base_stats": {"hp": 78, "attack": 84, "defense": 78, "sp_attack": 109, "sp_defense": 85, "speed": 100},
        "learnable_moves": ["scratch", "ember", "flamethrower", "fire_blast", "fly", "earthquake", "dragon_rage"]
    },
    7: {
        "name": "Squirtle",
        "types": [PokemonType.WATER],
        "base_stats": {"hp": 44, "attack": 48, "defense": 65, "sp_attack": 50, "sp_defense": 64, "speed": 43},
        "learnable_moves": ["tackle", "bubble", "water_gun", "surf", "ice_beam"]
    },
    8: {
        "name": "Wartortle",
        "types": [PokemonType.WATER],
        "base_stats": {"hp": 59, "attack": 63, "defense": 80, "sp_attack": 65, "sp_defense": 80, "speed": 58},
        "learnable_moves": ["tackle", "bubble", "water_gun", "surf", "hydro_pump", "ice_beam"]
    },
    9: {
        "name": "Blastoise",
        "types": [PokemonType.WATER],
        "base_stats": {"hp": 79, "attack": 83, "defense": 100, "sp_attack": 85, "sp_defense": 105, "speed": 78},
        "learnable_moves": ["tackle", "water_gun", "surf", "hydro_pump", "ice_beam", "earthquake"]
    },
    25: {
        "name": "Pikachu",
        "types": [PokemonType.ELECTRIC],
        "base_stats": {"hp": 35, "attack": 55, "defense": 40, "sp_attack": 50, "sp_defense": 50, "speed": 90},
        "learnable_moves": ["tackle", "quick_attack", "thunder_shock", "thunderbolt", "thunder"]
    },
    26: {
        "name": "Raichu",
        "types": [PokemonType.ELECTRIC],
        "base_stats": {"hp": 60, "attack": 90, "defense": 55, "sp_attack": 90, "sp_defense": 80, "speed": 110},
        "learnable_moves": ["tackle", "quick_attack", "thunder_shock", "thunderbolt", "thunder", "body_slam"]
    },
    39: {
        "name": "Jigglypuff",
        "types": [PokemonType.NORMAL],
        "base_stats": {"hp": 115, "attack": 45, "defense": 20, "sp_attack": 45, "sp_defense": 25, "speed": 20},
        "learnable_moves": ["pound", "body_slam", "psychic", "ice_beam"]
    },
    52: {
        "name": "Meowth",
        "types": [PokemonType.NORMAL],
        "base_stats": {"hp": 40, "attack": 45, "defense": 35, "sp_attack": 40, "sp_defense": 40, "speed": 90},
        "learnable_moves": ["scratch", "bite", "quick_attack", "body_slam"]
    },
    63: {
        "name": "Abra",
        "types": [PokemonType.PSYCHIC],
        "base_stats": {"hp": 25, "attack": 20, "defense": 15, "sp_attack": 105, "sp_defense": 55, "speed": 90},
        "learnable_moves": ["confusion", "psychic", "shadow_ball"]
    },
    64: {
        "name": "Kadabra",
        "types": [PokemonType.PSYCHIC],
        "base_stats": {"hp": 40, "attack": 35, "defense": 30, "sp_attack": 120, "sp_defense": 70, "speed": 105},
        "learnable_moves": ["confusion", "psychic", "shadow_ball", "thunder"]
    },
    65: {
        "name": "Alakazam",
        "types": [PokemonType.PSYCHIC],
        "base_stats": {"hp": 55, "attack": 50, "defense": 45, "sp_attack": 135, "sp_defense": 95, "speed": 120},
        "learnable_moves": ["confusion", "psychic", "shadow_ball", "thunder", "ice_beam"]
    },
    74: {
        "name": "Geodude",
        "types": [PokemonType.ROCK, PokemonType.GROUND],
        "base_stats": {"hp": 40, "attack": 80, "defense": 100, "sp_attack": 30, "sp_defense": 30, "speed": 20},
        "learnable_moves": ["tackle", "rock_throw", "rock_slide", "earthquake", "dig"]
    },
    94: {
        "name": "Gengar",
        "types": [PokemonType.GHOST, PokemonType.POISON],
        "base_stats": {"hp": 60, "attack": 65, "defense": 60, "sp_attack": 130, "sp_defense": 75, "speed": 110},
        "learnable_moves": ["lick", "shadow_ball", "sludge", "psychic", "thunderbolt"]
    },
    129: {
        "name": "Magikarp",
        "types": [PokemonType.WATER],
        "base_stats": {"hp": 20, "attack": 10, "defense": 55, "sp_attack": 15, "sp_defense": 20, "speed": 80},
        "learnable_moves": ["tackle"]
    },
    130: {
        "name": "Gyarados",
        "types": [PokemonType.WATER, PokemonType.FLYING],
        "base_stats": {"hp": 95, "attack": 125, "defense": 79, "sp_attack": 60, "sp_defense": 100, "speed": 81},
        "learnable_moves": ["tackle", "hydro_pump", "surf", "thunder", "ice_beam", "earthquake", "hyper_beam"]
    },
    143: {
        "name": "Snorlax",
        "types": [PokemonType.NORMAL],
        "base_stats": {"hp": 160, "attack": 110, "defense": 65, "sp_attack": 65, "sp_defense": 110, "speed": 30},
        "learnable_moves": ["tackle", "body_slam", "hyper_beam", "earthquake", "ice_beam", "thunder", "psychic"]
    },
    144: {
        "name": "Articuno",
        "types": [PokemonType.ICE, PokemonType.FLYING],
        "base_stats": {"hp": 90, "attack": 85, "defense": 100, "sp_attack": 95, "sp_defense": 125, "speed": 85},
        "learnable_moves": ["gust", "ice_beam", "blizzard", "fly", "hyper_beam"]
    },
    145: {
        "name": "Zapdos",
        "types": [PokemonType.ELECTRIC, PokemonType.FLYING],
        "base_stats": {"hp": 90, "attack": 90, "defense": 85, "sp_attack": 125, "sp_defense": 90, "speed": 100},
        "learnable_moves": ["gust", "thunder_shock", "thunderbolt", "thunder", "fly", "hyper_beam"]
    },
    146: {
        "name": "Moltres",
        "types": [PokemonType.FIRE, PokemonType.FLYING],
        "base_stats": {"hp": 90, "attack": 100, "defense": 90, "sp_attack": 125, "sp_defense": 85, "speed": 90},
        "learnable_moves": ["gust", "ember", "flamethrower", "fire_blast", "fly", "hyper_beam"]
    },
    147: {
        "name": "Dratini",
        "types": [PokemonType.DRAGON],
        "base_stats": {"hp": 41, "attack": 64, "defense": 45, "sp_attack": 50, "sp_defense": 50, "speed": 50},
        "learnable_moves": ["tackle", "dragon_rage", "thunder", "ice_beam", "surf"]
    },
    148: {
        "name": "Dragonair",
        "types": [PokemonType.DRAGON],
        "base_stats": {"hp": 61, "attack": 84, "defense": 65, "sp_attack": 70, "sp_defense": 70, "speed": 70},
        "learnable_moves": ["tackle", "dragon_rage", "thunder", "ice_beam", "surf", "flamethrower"]
    },
    149: {
        "name": "Dragonite",
        "types": [PokemonType.DRAGON, PokemonType.FLYING],
        "base_stats": {"hp": 91, "attack": 134, "defense": 95, "sp_attack": 100, "sp_defense": 100, "speed": 80},
        "learnable_moves": ["tackle", "dragon_rage", "thunder", "ice_beam", "surf", "flamethrower", "hyper_beam", "earthquake", "fly"]
    },
    150: {
        "name": "Mewtwo",
        "types": [PokemonType.PSYCHIC],
        "base_stats": {"hp": 106, "attack": 110, "defense": 90, "sp_attack": 154, "sp_defense": 90, "speed": 130},
        "learnable_moves": ["confusion", "psychic", "shadow_ball", "thunder", "ice_beam", "flamethrower", "hyper_beam"]
    },
    151: {
        "name": "Mew",
        "types": [PokemonType.PSYCHIC],
        "base_stats": {"hp": 100, "attack": 100, "defense": 100, "sp_attack": 100, "sp_defense": 100, "speed": 100},
        "learnable_moves": ["pound", "psychic", "shadow_ball", "thunder", "ice_beam", "flamethrower", "surf", "earthquake"]
    },
}


# Helper functions to get Pokemon data
# These will use JSON loader if available, otherwise fall back to POKEMON_DATA
def get_pokemon_data(pokemon_id: int):
    """
    Get Pokemon data by ID, preferring JSON loader if available.
    
    Args:
        pokemon_id: The Pokemon's national dex number
        
    Returns:
        Dictionary containing Pokemon data
    """
    try:
        from .pokemon_loader import get_pokemon_loader
        loader = get_pokemon_loader()
        
        if loader.is_data_available():
            # Use loader data
            return {
                "name": loader.get_pokemon_name(pokemon_id),
                "types": loader.get_pokemon_types(pokemon_id),
                "base_stats": loader.get_base_stats(pokemon_id),
                "learnable_moves": loader.get_learnable_moves(pokemon_id, level_limit=50)
            }
    except Exception as e:
        print(f"Warning: Could not load Pokemon data from JSON: {e}")
    
    # Fall back to hardcoded data
    return POKEMON_DATA.get(pokemon_id, {
        "name": f"Pokemon #{pokemon_id}",
        "types": [PokemonType.NORMAL],
        "base_stats": {"hp": 50, "attack": 50, "defense": 50, "sp_attack": 50, "sp_defense": 50, "speed": 50},
        "learnable_moves": ["tackle"]
    })


def get_available_pokemon_ids():
    """Get list of all available Pokemon IDs."""
    try:
        from .pokemon_loader import get_pokemon_loader
        loader = get_pokemon_loader()
        
        if loader.is_data_available():
            return loader.get_all_pokemon_ids()
    except Exception:
        pass
    
    # Fall back to hardcoded data
    return sorted(POKEMON_DATA.keys())


def is_pokemon_available(pokemon_id: int) -> bool:
    """Check if a Pokemon ID is available."""
    return pokemon_id in get_available_pokemon_ids()

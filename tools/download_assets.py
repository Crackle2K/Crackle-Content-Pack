"""Download Pokemon sprite assets and data from PokeAPI."""

import requests
import json
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Optional, Dict, Any


def download_single_pokemon(pokemon_id: int, sprites_folder: Path, data_folder: Path) -> tuple[int, bool, Optional[str]]:
    """
    Download a single Pokemon's sprite and data.
    
    Returns:
        Tuple of (pokemon_id, success, error_message)
    """
    try:
        # Download Pokemon data
        response = requests.get(f"https://pokeapi.co/api/v2/pokemon/{pokemon_id}", timeout=10)
        response.raise_for_status()
        pokemon_data = response.json()
        
        # Download species data for additional info
        species_response = requests.get(pokemon_data['species']['url'], timeout=10)
        species_response.raise_for_status()
        species_data = species_response.json()
        
        pokemon_name = pokemon_data['name']
        
        # Download sprite
        sprite_url = pokemon_data['sprites'].get('front_default')
        if sprite_url:
            sprite_response = requests.get(sprite_url, timeout=10)
            sprite_response.raise_for_status()
            sprite_path = sprites_folder / f"{pokemon_id:03d}_{pokemon_name}.png"
            sprite_path.write_bytes(sprite_response.content)
        
        # Extract and save Pokemon data
        processed_data = {
            "id": pokemon_id,
            "name": pokemon_name,
            "types": [t['type']['name'] for t in pokemon_data['types']],
            "base_stats": {
                stat['stat']['name']: stat['base_stat'] 
                for stat in pokemon_data['stats']
            },
            "moves": [
                {
                    "name": move['move']['name'],
                    "learn_method": move['version_group_details'][0]['move_learn_method']['name'] if move['version_group_details'] else 'unknown',
                    "level_learned": move['version_group_details'][0]['level_learned_at'] if move['version_group_details'] else 0
                }
                for move in pokemon_data['moves']
            ],
            "height": pokemon_data['height'],
            "weight": pokemon_data['weight'],
            "abilities": [ability['ability']['name'] for ability in pokemon_data['abilities']],
            "sprite_url": sprite_url,
            "genus": next((genus['genus'] for genus in species_data.get('genera', []) if genus['language']['name'] == 'en'), ''),
            "flavor_text": next((entry['flavor_text'].replace('\n', ' ').replace('\f', ' ') 
                               for entry in species_data.get('flavor_text_entries', []) 
                               if entry['language']['name'] == 'en'), '')
        }
        
        # Save JSON data
        json_path = data_folder / f"{pokemon_id:03d}_{pokemon_name}.json"
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(processed_data, f, indent=2, ensure_ascii=False)
        
        return (pokemon_id, True, None)
        
    except requests.RequestException as e:
        return (pokemon_id, False, f"Network error: {str(e)}")
    except Exception as e:
        return (pokemon_id, False, f"Processing error: {str(e)}")


def download_pokemon_assets(assets_folder: str = "assets/sprites", max_pokemon: int = 151, max_workers: int = 10):
    """
    Download Pokemon sprites and data from PokeAPI using parallel requests.
    
    Args:
        assets_folder: Path to sprites folder
        max_pokemon: Maximum Pokemon ID to download (151 for Gen 1)
        max_workers: Number of parallel download threads
    """
    sprites_path = Path(assets_folder)
    sprites_path.mkdir(parents=True, exist_ok=True)
    
    data_path = Path("assets/pokemon_data")
    data_path.mkdir(parents=True, exist_ok=True)

    print(f"Downloading {max_pokemon} Pokemon from PokeAPI with {max_workers} parallel workers...")
    print(f"  Sprites: {sprites_path}")
    print(f"  Data: {data_path}")
    
    successful = 0
    failed = 0
    failed_ids = []

    # Use ThreadPoolExecutor for parallel downloads
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        # Submit all download tasks
        future_to_id = {
            executor.submit(download_single_pokemon, pokemon_id, sprites_path, data_path): pokemon_id
            for pokemon_id in range(1, max_pokemon + 1)
        }
        
        # Process completed downloads
        for future in as_completed(future_to_id):
            pokemon_id, success, error = future.result()
            
            if success:
                successful += 1
                if successful % 10 == 0:
                    print(f"  Progress: {successful}/{max_pokemon} Pokemon downloaded...")
            else:
                failed += 1
                failed_ids.append(pokemon_id)
                print(f"  Failed Pokemon #{pokemon_id}: {error}")

    print(f"\nDownload complete!")
    print(f"  Successfully downloaded: {successful}")
    print(f"  Failed: {failed}")
    if failed_ids:
        print(f"  Failed IDs: {failed_ids}")
    
    return successful > 0


def check_assets_exist(assets_folder: str = "assets/sprites") -> bool:
    """
    Check if assets folder exists and contains files.

    Args:
        assets_folder: Path to the assets folder

    Returns:
        True if assets exist, False otherwise
    """
    assets_path = Path(assets_folder)
    if not assets_path.exists():
        return False

    # Check if there are any PNG files in the assets folder
    png_files = list(assets_path.glob("*.png"))
    return len(png_files) > 0


if __name__ == "__main__":
    # Can be run standalone to download assets
    download_pokemon_assets()

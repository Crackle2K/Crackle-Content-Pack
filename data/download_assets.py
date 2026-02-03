import os
import requests
from pathlib import Path


def download_pokemon_assets(assets_folder: str = "assets", max_pokemon: int = 151):
    assets_path = Path(assets_folder)
    assets_path.mkdir(parents=True, exist_ok=True)
    
    print(f"Downloading Pokemon assets from PokeAPI...")
    successful = 0
    failed = 0
    
    for pokemon_id in range(1, max_pokemon + 1):
        try:
            response = requests.get(f"https://pokeapi.co/api/v2/pokemon/{pokemon_id}")
            response.raise_for_status()
            pokemon_data = response.json()
            
            sprite_url = pokemon_data['sprites'].get('front_default')
            if not sprite_url:
                print(f"  No sprite available for Pokemon #{pokemon_id}")
                failed += 1
                continue
            
            # Download the sprite
            sprite_response = requests.get(sprite_url)
            sprite_response.raise_for_status()
            
            # Save the sprite
            pokemon_name = pokemon_data['name']
            file_path = assets_path / f"{pokemon_id:03d}_{pokemon_name}.png"
            file_path.write_bytes(sprite_response.content)
            
            successful += 1
            if successful % 10 == 0:
                print(f"  Downloaded {successful}/{max_pokemon} Pokemon...")
                
        except requests.RequestException as e:
            print(f"  Failed to download Pokemon #{pokemon_id}: {e}")
            failed += 1
        except Exception as e:
            print(f"  Error processing Pokemon #{pokemon_id}: {e}")
            failed += 1
    
    print(f"\nDownload complete!")
    print(f"  Successfully downloaded: {successful}")
    print(f"  Failed: {failed}")
    return successful > 0


def check_assets_exist(assets_folder: str = "assets") -> bool:
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

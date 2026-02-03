import os
from data.download_assets import check_assets_exist, download_pokemon_assets


def main():
    # Check if assets exist, download if not
    if not check_assets_exist("assets"):
        print("No Pokemon assets found. Downloading from PokeAPI...")
        download_pokemon_assets("assets", max_pokemon=151)
    else:
        print("Pokemon assets found. Starting game...")
    
    # Your game code goes here
    pass

if __name__ == '__main__':
    main()

"""Pokemon Juno - Main Entry Point"""

import os
import sys

# Add project root to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from tools.download_assets import check_assets_exist, download_pokemon_assets


def main():
    """Main entry point for Pokemon Juno."""
    # Check if assets exist, download if not
    if not check_assets_exist("assets/sprites"):
        print("No Pokemon assets found. Downloading from PokeAPI...")
        download_pokemon_assets("assets/sprites", max_pokemon=151)
        print("Assets downloaded successfully!")

    # Start the game
    from src.game import Game
    game = Game()
    game.run()


if __name__ == '__main__':
    main()

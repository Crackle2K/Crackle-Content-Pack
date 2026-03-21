"""Pokemon Juno - Main Entry Point"""

import os
import sys
from pathlib import Path

# Add project root to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from tools.download_assets import check_assets_exist, download_pokemon_assets


def _ensure_pixel_font():
    """Download Press Start 2P pixel font if not already present."""
    font_path = Path("assets/fonts/PressStart2P-Regular.ttf")
    if font_path.exists():
        return
    font_path.parent.mkdir(parents=True, exist_ok=True)
    try:
        import requests
        url = "https://github.com/google/fonts/raw/main/ofl/pressstart2p/PressStart2P-Regular.ttf"
        print("Downloading pixel font (Press Start 2P)...")
        r = requests.get(url, timeout=15)
        r.raise_for_status()
        font_path.write_bytes(r.content)
        print("Pixel font downloaded!")
    except Exception as e:
        print(f"Could not download pixel font (will use system font): {e}")


def main():
    """Main entry point for Pokemon Juno."""
    # Ensure pixel font is present
    _ensure_pixel_font()

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

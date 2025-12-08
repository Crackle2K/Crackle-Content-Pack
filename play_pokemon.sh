#!/bin/bash

echo "========================================"
echo "Pokemon Game Launcher"
echo "========================================"
echo ""

# Check if assets exist
if [ ! -d "game_assets/data" ]; then
    echo "Assets not found! Downloading from PokeAPI..."
    echo "This may take 2-5 minutes..."
    echo ""
    python3 download_assets.py
    echo ""
    echo "Download complete!"
    echo ""
fi

echo "Starting Pokemon Game..."
echo ""
python3 pokemon_game.py

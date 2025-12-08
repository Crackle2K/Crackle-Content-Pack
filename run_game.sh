#!/bin/bash

echo "========================================"
echo "Pokemon Game - Real-time PokeAPI"
echo "========================================"
echo ""

echo "Installing dependencies..."
pip install -r game_requirements.txt

echo ""
echo "Starting Pokemon Game..."
echo "All assets will be fetched from PokeAPI in real-time"
echo ""
python3 main.py

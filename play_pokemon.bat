@echo off
echo ========================================
echo Pokemon Game Launcher
echo ========================================
echo.

REM Check if assets exist
if not exist "game_assets\data" (
    echo Assets not found! Downloading from PokeAPI...
    echo This may take 2-5 minutes...
    echo.
    python download_assets.py
    echo.
    echo Download complete!
    echo.
)

echo Starting Pokemon Game...
echo.
python pokemon_game.py

pause

# Quick Start Guide - Pokemon Game

## 🚀 Get Started in 3 Steps

### 1. Install Python Dependencies
```bash
pip install -r game_requirements.txt
```

### 2. Download Pokemon Assets (First Time Only)
```bash
python download_assets.py
```
⏱️ This takes 2-5 minutes and downloads Pokemon sprites and data from PokeAPI.

### 3. Play the Game!

**Option A - Windows:** Double-click `play_pokemon.bat`

**Option B - Command Line:**
```bash
python pokemon_game.py
```

---

## 🎮 Controls

### Title Screen
- **SPACE** - Start game

### Starter Selection
- **Mouse Click** - Choose your starter Pokemon

### Overworld
- **Arrow Keys** - Move around
- Walk through **dark green grass** for wild encounters

### Battle
- **Mouse Click** - Select moves
- **ESC** - Exit after battle

---

## 💡 Tips

1. **Type Advantage Matters!**
   - Fire beats Grass
   - Water beats Fire  
   - Grass beats Water

2. **Level Up Your Pokemon**
   - Win battles to gain 50 EXP
   - Stats increase when leveling up

3. **Watch Your HP**
   - Green = Healthy
   - Yellow = Moderate damage
   - Red = Critical HP

4. **Explore the World**
   - The world is large (1920x1440)
   - More grass = more encounters

---

## 🐛 Troubleshooting

**"Game assets not found"**
→ Run `python download_assets.py`

**No encounters happening**
→ Walk through the **dark green grass tiles** (5% chance per tile)

**Battle seems frozen**
→ Wait 2 seconds for messages to clear, then click your move

---

## 🎯 Starter Recommendations

- **Bulbasaur** - Balanced, good for beginners
- **Charmander** - High attack, challenging early game
- **Squirtle** - Good defense, reliable choice

---

**Have fun and catch 'em all!** ✨

# Pokemon Game - Real-time PokeAPI Edition

A complete Pokemon game that fetches all assets and data directly from PokeAPI in real-time. No local asset storage required!

## 🌟 Features

- **Real-time Data Fetching** - All Pokemon sprites and data loaded from PokeAPI on-demand
- **No Asset Downloads** - No need to pre-download any files
- **Starter Selection** - Choose from Bulbasaur, Charmander, or Squirtle
- **Overworld Exploration** - Move around a large world with arrow keys
- **Wild Encounters** - Random Pokemon battles in grass
- **Turn-Based Battles** - Strategic combat with type effectiveness
- **Experience System** - Pokemon level up and get stronger

## 📁 Project Structure

```
Pokemon-Juno/
├── main.py              # Main game file (primary entry point)
├── api_client.py        # PokeAPI client for fetching data
├── pokemon.py           # Pokemon and Battle classes
├── game_requirements.txt # Dependencies
└── run_game.bat/sh      # Launcher scripts
```

## 🚀 Quick Start

### Option 1: Use Launcher Script

**Windows:**
```bash
run_game.bat
```

**Linux/Mac:**
```bash
bash run_game.sh
```

### Option 2: Manual Setup

1. **Install Dependencies:**
```bash
pip install -r game_requirements.txt
```

2. **Run the Game:**
```bash
python main.py
```

## 🎮 How to Play

### Controls

**Title Screen:**
- Press `SPACE` to start

**Starter Selection:**
- Click on a Pokemon to select it

**Overworld:**
- `Arrow Keys` - Move your character
- Walk through dark green grass for encounters

**Battle:**
- `Mouse Click` - Select moves or run away
- `ESC` - Exit battle (after it ends)

### Game Flow

1. Start game and press SPACE
2. Choose your starter Pokemon (Bulbasaur, Charmander, or Squirtle)
3. Explore the overworld
4. Walk through grass to trigger wild encounters
5. Battle wild Pokemon using moves
6. Gain experience and level up!

## 🔧 Technical Details

### How It Works

- **API Client** (`api_client.py`): Handles all HTTP requests to PokeAPI
- **In-Memory Caching**: Sprites and data cached during gameplay session
- **Lazy Loading**: Pokemon sprites loaded only when needed
- **PIL Integration**: Converts API images to Pygame surfaces on-the-fly

### API Fetching

The game fetches from PokeAPI:
- Pokemon base stats (HP, Attack, Defense, Speed)
- Type information
- Move data (power, accuracy, PP, type)
- Sprites (front and back views)

All data is fetched in real-time as needed, with session caching to minimize API calls.

## 📦 Dependencies

- **pygame** - Game engine
- **requests** - HTTP client for API calls
- **Pillow** - Image processing for sprite conversion

## 🎯 Starter Pokemon

- **Bulbasaur** (ID: 1) - Grass type
- **Charmander** (ID: 4) - Fire type  
- **Squirtle** (ID: 7) - Water type

## 🐛 Wild Pokemon

You may encounter:
- Pidgey (ID: 16)
- Rattata (ID: 19)
- Caterpie (ID: 10)
- Weedle (ID: 13)
- Pikachu (ID: 25)

All fetched from PokeAPI in real-time!

## ⚡ Type Effectiveness

The game includes a complete type effectiveness chart:
- Fire beats Grass
- Water beats Fire
- Grass beats Water
- And many more interactions!

## 🎨 Customization

### Add More Wild Pokemon

Edit `main.py` around line 190:
```python
wild_pokemon_ids = [16, 19, 10, 13, 25]  # Add more IDs here
```

### Change Encounter Rate

Edit `main.py` around line 160:
```python
if random.random() < 0.05:  # Change to 0.1 for 10% rate
```

### Add Different Starters

Edit `main.py` around line 270:
```python
starters = [
    (1, "Bulbasaur", "Grass"),
    (4, "Charmander", "Fire"),
    (7, "Squirtle", "Water"),
    # Add more here using (ID, Name, Type)
]
```

## 🌐 Network Requirements

This game requires an active internet connection to fetch data from PokeAPI. First-time loads may take a few seconds as sprites are downloaded.

## 💡 Advantages of Real-Time Fetching

- ✅ No large asset folder to download
- ✅ Always get latest Pokemon data
- ✅ Easy to add new Pokemon
- ✅ Smaller repository size
- ✅ No outdated cached data

## 🔮 Future Enhancements

Possible additions:
- [ ] Offline mode with persistent caching
- [ ] More Pokemon species
- [ ] Pokemon catching mechanic
- [ ] Items and inventory
- [ ] Save/Load system
- [ ] Sound effects
- [ ] Multiple maps

## 📝 Credits

- **Pokemon Data & Sprites**: [PokeAPI](https://pokeapi.co)
- **Game Engine**: Pygame
- **Pokemon**: © Nintendo/Game Freak

## 🎓 Educational Purpose

This is a fan-made educational project demonstrating real-time API integration with game development.

---

**Enjoy your Pokemon adventure powered by PokeAPI!** 🎮✨

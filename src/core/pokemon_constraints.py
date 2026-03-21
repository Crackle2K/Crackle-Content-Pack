"""Pokemon encounter constraints: legendaries, evolution floors, level helpers."""

from __future__ import annotations
import random
from typing import List

# ── Legendaries ─────────────────────────────────────────────────────────────
# Gen 1 legendary / mythical — never appear in random encounters
LEGENDARY_IDS: set[int] = {144, 145, 146, 150, 151}

# ── Evolution minimum levels ─────────────────────────────────────────────────
# Maps pokemon_id → minimum level at which that species realistically exists.
# Stone/trade evolutions use a proxy of 36 (the level where many NPC trainers
# first field them in the games).
EVOLUTION_MIN_LEVEL: dict[int, int] = {
    # Bulbasaur line
    2: 16,   # Ivysaur
    3: 32,   # Venusaur
    # Charmander line
    5: 16,   # Charmeleon
    6: 36,   # Charizard
    # Squirtle line
    8: 16,   # Wartortle
    9: 36,   # Blastoise
    # Caterpie line
    11: 7,   # Metapod
    12: 10,  # Butterfree
    # Weedle line
    14: 7,   # Kakuna
    15: 10,  # Beedrill
    # Pidgey line
    17: 18,  # Pidgeotto
    18: 36,  # Pidgeot
    # Rattata line
    20: 20,  # Raticate
    # Spearow line
    22: 20,  # Fearow
    # Ekans line
    24: 22,  # Arbok
    # Pikachu → Raichu (Thunder Stone proxy)
    26: 36,  # Raichu
    # Sandshrew line
    28: 22,  # Sandslash
    # Nidoran♀ line
    30: 16,  # Nidorina
    31: 36,  # Nidoqueen (Moon Stone)
    # Nidoran♂ line
    33: 16,  # Nidorino
    34: 36,  # Nidoking (Moon Stone)
    # Clefairy → Clefable (Moon Stone)
    36: 36,
    # Vulpix → Ninetales (Fire Stone)
    38: 36,
    # Jigglypuff → Wigglytuff (Moon Stone)
    40: 36,
    # Zubat line
    42: 22,  # Golbat
    # Oddish line
    44: 21,  # Gloom
    45: 36,  # Vileplume (Leaf Stone)
    # Paras line
    47: 24,  # Parasect
    # Venonat line
    49: 31,  # Venomoth
    # Diglett line
    51: 26,  # Dugtrio
    # Meowth line
    53: 28,  # Persian
    # Psyduck line
    55: 33,  # Golduck
    # Mankey line
    57: 28,  # Primeape
    # Growlithe → Arcanine (Fire Stone)
    59: 36,
    # Poliwag line
    61: 25,  # Poliwhirl
    62: 36,  # Poliwrath (Water Stone)
    # Abra line
    64: 16,  # Kadabra
    65: 36,  # Alakazam (Trade)
    # Machop line
    67: 28,  # Machoke
    68: 36,  # Machamp (Trade)
    # Bellsprout line
    70: 21,  # Weepinbell
    71: 36,  # Victreebel (Leaf Stone)
    # Tentacool line
    73: 30,  # Tentacruel
    # Geodude line
    75: 25,  # Graveler
    76: 36,  # Golem (Trade)
    # Ponyta line
    78: 40,  # Rapidash
    # Slowpoke line
    80: 37,  # Slowbro
    # Magnemite line
    82: 30,  # Magneton
    # Doduo line
    85: 31,  # Dodrio
    # Seel line
    87: 34,  # Dewgong
    # Grimer line
    89: 38,  # Muk
    # Shellder → Cloyster (Water Stone)
    91: 36,
    # Gastly line
    93: 25,  # Haunter
    94: 36,  # Gengar (Trade)
    # Drowzee line
    97: 26,  # Hypno
    # Krabby line
    99: 28,  # Kingler
    # Voltorb line
    101: 30, # Electrode
    # Exeggcute → Exeggutor (Leaf Stone)
    103: 36,
    # Cubone line
    105: 28, # Marowak
    # Koffing line
    110: 35, # Weezing
    # Rhyhorn line
    112: 42, # Rhydon
    # Horsea line
    117: 32, # Seadra
    # Goldeen line
    119: 33, # Seaking
    # Staryu → Starmie (Water Stone)
    121: 36,
    # Magikarp → Gyarados
    130: 20,
    # Eevee → evolutions (Stone)
    134: 36, # Vaporeon
    135: 36, # Jolteon
    136: 36, # Flareon
    # Fossil line
    139: 40, # Omastar
    141: 40, # Kabutops
    # Dratini line
    148: 30, # Dragonair
    149: 55, # Dragonite
}

# ── First-battle type advantage ──────────────────────────────────────────────
# Maps player's starter ID → opponent ID whose type the starter beats
STARTER_COUNTERS: dict[int, int] = {
    1: 7,    # Bulbasaur (Grass) beats Water → Squirtle
    4: 1,    # Charmander (Fire) beats Grass → Bulbasaur
    7: 4,    # Squirtle (Water) beats Fire → Charmander
    25: 7,   # Pikachu (Electric) beats Water → Squirtle
}


# ── Public helpers ────────────────────────────────────────────────────────────

def get_min_level(pokemon_id: int) -> int:
    """Return the minimum sensible encounter level for a Pokemon."""
    return EVOLUTION_MIN_LEVEL.get(pokemon_id, 1)


def pick_encounter_pokemon(
    available_ids: List[int],
    target_level: int,
    rng: random.Random | None = None,
) -> tuple[int, int]:
    """
    Choose a random Pokemon appropriate for an encounter at *target_level*.

    - Legendaries are never selected.
    - Fully-evolved Pokemon that evolve far above target_level are excluded
      (avoids e.g. a level-10 Dragonite).

    Returns:
        (pokemon_id, clamped_level)
    """
    if rng is None:
        rng = random

    # Only species whose min-level is AT OR BELOW the target so they actually
    # appear at that level (prevents a level-5 encounter with Ivysaur/Pidgeotto).
    valid = [
        pid for pid in available_ids
        if pid not in LEGENDARY_IDS and get_min_level(pid) <= target_level
    ]
    if not valid:
        # Small tolerance fallback (e.g. very low target levels)
        valid = [
            pid for pid in available_ids
            if pid not in LEGENDARY_IDS and get_min_level(pid) <= target_level + 5
        ]
    if not valid:
        valid = [pid for pid in available_ids if pid not in LEGENDARY_IDS]
    if not valid:
        valid = available_ids  # last resort

    pid = rng.choice(valid)
    min_lv = get_min_level(pid)
    level = max(min_lv, min(100, target_level))
    return pid, level

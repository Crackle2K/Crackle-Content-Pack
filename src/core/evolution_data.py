"""Gen 1 level-based evolution data.

Maps pokemon_id -> (evolved_id, level_required).

Stone and trade evolutions that have no level in the original games are
converted to level 36 so they are reachable in normal play.
Pokemon with no Gen-1 evolution are omitted.
"""

EVOLUTION_DATA: dict[int, tuple[int, int]] = {
    # Bulbasaur line
    1:   (2,   16),   # Bulbasaur  → Ivysaur
    2:   (3,   32),   # Ivysaur    → Venusaur

    # Charmander line
    4:   (5,   16),   # Charmander  → Charmeleon
    5:   (6,   36),   # Charmeleon  → Charizard

    # Squirtle line
    7:   (8,   16),   # Squirtle   → Wartortle
    8:   (9,   36),   # Wartortle  → Blastoise

    # Bug lines
    10:  (11,  7),    # Caterpie   → Metapod
    11:  (12,  10),   # Metapod    → Butterfree
    13:  (14,  7),    # Weedle     → Kakuna
    14:  (15,  10),   # Kakuna     → Beedrill

    # Bird lines
    16:  (17,  18),   # Pidgey     → Pidgeotto
    17:  (18,  36),   # Pidgeotto  → Pidgeot

    # Rat / Crow lines
    19:  (20,  20),   # Rattata    → Raticate
    21:  (22,  20),   # Spearow    → Fearow

    # Snake / rodent lines
    23:  (24,  22),   # Ekans      → Arbok
    27:  (28,  22),   # Sandshrew  → Sandslash

    # Pikachu (Thunder Stone → converted to level)
    25:  (26,  22),   # Pikachu    → Raichu

    # Nidoran lines
    29:  (30,  16),   # Nidoran♀   → Nidorina
    32:  (33,  16),   # Nidoran♂   → Nidorino

    # Bat line
    41:  (42,  22),   # Zubat      → Golbat

    # Grass lines
    43:  (44,  21),   # Oddish     → Gloom
    46:  (47,  24),   # Paras      → Parasect
    48:  (49,  31),   # Venonat    → Venomoth

    # Diglett / Meowth / Psyduck / Mankey
    50:  (51,  26),   # Diglett    → Dugtrio
    52:  (53,  28),   # Meowth     → Persian
    54:  (55,  33),   # Psyduck    → Golduck
    56:  (57,  28),   # Mankey     → Primeape

    # Poliwag line
    60:  (61,  25),   # Poliwag    → Poliwhirl

    # Abra line (trade → level)
    63:  (64,  16),   # Abra       → Kadabra
    64:  (65,  36),   # Kadabra    → Alakazam

    # Machop line (trade → level)
    66:  (67,  28),   # Machop     → Machoke
    67:  (68,  36),   # Machoke    → Machamp

    # Bellsprout line
    69:  (70,  21),   # Bellsprout → Weepinbell

    # Water lines
    72:  (73,  30),   # Tentacool  → Tentacruel
    79:  (80,  37),   # Slowpoke   → Slowbro
    86:  (87,  34),   # Seel       → Dewgong
    98:  (99,  28),   # Krabby     → Kingler
    116: (117, 32),   # Horsea     → Seadra
    118: (119, 33),   # Goldeen    → Seaking

    # Rock/Ground lines
    74:  (75,  25),   # Geodude    → Graveler
    75:  (76,  36),   # Graveler   → Golem (trade → level)

    # Fire horse
    77:  (78,  40),   # Ponyta     → Rapidash

    # Electric lines
    81:  (82,  30),   # Magnemite  → Magneton
    100: (101, 30),   # Voltorb    → Electrode

    # Bird
    84:  (85,  31),   # Doduo      → Dodrio

    # Poison
    88:  (89,  38),   # Grimer     → Muk
    109: (110, 35),   # Koffing    → Weezing

    # Ghost line (trade → level)
    92:  (93,  25),   # Gastly     → Haunter
    93:  (94,  36),   # Haunter    → Gengar

    # Psychic
    96:  (97,  26),   # Drowzee    → Hypno

    # Ground
    104: (105, 28),   # Cubone     → Marowak

    # Rhyhorn line
    111: (112, 42),   # Rhyhorn    → Rhydon

    # Magikarp
    129: (130, 20),   # Magikarp   → Gyarados

    # Fossil lines
    138: (139, 40),   # Omanyte    → Omastar
    140: (141, 40),   # Kabuto     → Kabutops

    # Dragon line
    147: (148, 30),   # Dratini    → Dragonair
    148: (149, 55),   # Dragonair  → Dragonite
}

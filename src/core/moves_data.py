"""Pokemon moves database."""

from .type_chart import PokemonType


class MoveCategory:
    PHYSICAL = "physical"
    SPECIAL = "special"
    STATUS = "status"


# Move data format:
# "move_name": {
#     "type": PokemonType,
#     "category": MoveCategory,
#     "power": int (0 for status moves),
#     "accuracy": int (percentage),
#     "pp": int,
#     "description": str
# }

MOVES_DATA = {
    # Normal moves
    "tackle": {
        "type": PokemonType.NORMAL,
        "category": MoveCategory.PHYSICAL,
        "power": 40,
        "accuracy": 100,
        "pp": 35,
        "description": "A physical attack in which the user charges and slams into the target."
    },
    "scratch": {
        "type": PokemonType.NORMAL,
        "category": MoveCategory.PHYSICAL,
        "power": 40,
        "accuracy": 100,
        "pp": 35,
        "description": "Hard, pointed, sharp claws rake the target to inflict damage."
    },
    "pound": {
        "type": PokemonType.NORMAL,
        "category": MoveCategory.PHYSICAL,
        "power": 40,
        "accuracy": 100,
        "pp": 35,
        "description": "The target is physically pounded with a long tail, a foreleg, or the like."
    },
    "quick_attack": {
        "type": PokemonType.NORMAL,
        "category": MoveCategory.PHYSICAL,
        "power": 40,
        "accuracy": 100,
        "pp": 30,
        "priority": 1,
        "description": "The user lunges at the target at a speed that makes it almost invisible."
    },
    "hyper_beam": {
        "type": PokemonType.NORMAL,
        "category": MoveCategory.SPECIAL,
        "power": 150,
        "accuracy": 90,
        "pp": 5,
        "description": "The target is attacked with a powerful beam."
    },
    "body_slam": {
        "type": PokemonType.NORMAL,
        "category": MoveCategory.PHYSICAL,
        "power": 85,
        "accuracy": 100,
        "pp": 15,
        "description": "The user drops onto the target with its full body weight."
    },
    "bite": {
        "type": PokemonType.NORMAL,
        "category": MoveCategory.PHYSICAL,
        "power": 60,
        "accuracy": 100,
        "pp": 25,
        "description": "The target is bitten with viciously sharp fangs."
    },

    # Fire moves
    "ember": {
        "type": PokemonType.FIRE,
        "category": MoveCategory.SPECIAL,
        "power": 40,
        "accuracy": 100,
        "pp": 25,
        "description": "The target is attacked with small flames."
    },
    "flamethrower": {
        "type": PokemonType.FIRE,
        "category": MoveCategory.SPECIAL,
        "power": 90,
        "accuracy": 100,
        "pp": 15,
        "description": "The target is scorched with an intense blast of fire."
    },
    "fire_blast": {
        "type": PokemonType.FIRE,
        "category": MoveCategory.SPECIAL,
        "power": 110,
        "accuracy": 85,
        "pp": 5,
        "description": "The target is attacked with an intense blast of all-consuming fire."
    },
    "fire_spin": {
        "type": PokemonType.FIRE,
        "category": MoveCategory.SPECIAL,
        "power": 35,
        "accuracy": 85,
        "pp": 15,
        "description": "The target becomes trapped within a fierce vortex of fire."
    },

    # Water moves
    "bubble": {
        "type": PokemonType.WATER,
        "category": MoveCategory.SPECIAL,
        "power": 40,
        "accuracy": 100,
        "pp": 30,
        "description": "A spray of countless bubbles is jetted at the opposing team."
    },
    "water_gun": {
        "type": PokemonType.WATER,
        "category": MoveCategory.SPECIAL,
        "power": 40,
        "accuracy": 100,
        "pp": 25,
        "description": "The target is blasted with a forceful shot of water."
    },
    "surf": {
        "type": PokemonType.WATER,
        "category": MoveCategory.SPECIAL,
        "power": 90,
        "accuracy": 100,
        "pp": 15,
        "description": "The user attacks everything around it by swamping its surroundings with a giant wave."
    },
    "hydro_pump": {
        "type": PokemonType.WATER,
        "category": MoveCategory.SPECIAL,
        "power": 110,
        "accuracy": 80,
        "pp": 5,
        "description": "The target is blasted by a huge volume of water launched under great pressure."
    },

    # Grass moves
    "vine_whip": {
        "type": PokemonType.GRASS,
        "category": MoveCategory.PHYSICAL,
        "power": 45,
        "accuracy": 100,
        "pp": 25,
        "description": "The target is struck with slender, whiplike vines."
    },
    "razor_leaf": {
        "type": PokemonType.GRASS,
        "category": MoveCategory.PHYSICAL,
        "power": 55,
        "accuracy": 95,
        "pp": 25,
        "description": "Sharp-edged leaves are launched to slash at opposing Pokemon."
    },
    "solar_beam": {
        "type": PokemonType.GRASS,
        "category": MoveCategory.SPECIAL,
        "power": 120,
        "accuracy": 100,
        "pp": 10,
        "description": "A two-turn attack. The user gathers light, then blasts a bundled beam."
    },

    # Electric moves
    "thunder_shock": {
        "type": PokemonType.ELECTRIC,
        "category": MoveCategory.SPECIAL,
        "power": 40,
        "accuracy": 100,
        "pp": 30,
        "description": "A jolt of electricity crashes down on the target."
    },
    "thunderbolt": {
        "type": PokemonType.ELECTRIC,
        "category": MoveCategory.SPECIAL,
        "power": 90,
        "accuracy": 100,
        "pp": 15,
        "description": "A strong electric blast crashes down on the target."
    },
    "thunder": {
        "type": PokemonType.ELECTRIC,
        "category": MoveCategory.SPECIAL,
        "power": 110,
        "accuracy": 70,
        "pp": 10,
        "description": "A wicked thunderbolt is dropped on the target to inflict damage."
    },

    # Ice moves
    "ice_beam": {
        "type": PokemonType.ICE,
        "category": MoveCategory.SPECIAL,
        "power": 90,
        "accuracy": 100,
        "pp": 10,
        "description": "The target is struck with an icy-cold beam of energy."
    },
    "blizzard": {
        "type": PokemonType.ICE,
        "category": MoveCategory.SPECIAL,
        "power": 110,
        "accuracy": 70,
        "pp": 5,
        "description": "A howling blizzard is summoned to strike opposing Pokemon."
    },

    # Fighting moves
    "karate_chop": {
        "type": PokemonType.FIGHTING,
        "category": MoveCategory.PHYSICAL,
        "power": 50,
        "accuracy": 100,
        "pp": 25,
        "description": "The target is attacked with a sharp chop."
    },
    "low_kick": {
        "type": PokemonType.FIGHTING,
        "category": MoveCategory.PHYSICAL,
        "power": 50,
        "accuracy": 100,
        "pp": 20,
        "description": "A powerful low kick that makes the target fall over."
    },
    "submission": {
        "type": PokemonType.FIGHTING,
        "category": MoveCategory.PHYSICAL,
        "power": 80,
        "accuracy": 80,
        "pp": 20,
        "description": "The user grabs the target and recklessly dives for the ground."
    },

    # Poison moves
    "poison_sting": {
        "type": PokemonType.POISON,
        "category": MoveCategory.PHYSICAL,
        "power": 15,
        "accuracy": 100,
        "pp": 35,
        "description": "The user stabs the target with a poisonous stinger."
    },
    "sludge": {
        "type": PokemonType.POISON,
        "category": MoveCategory.SPECIAL,
        "power": 65,
        "accuracy": 100,
        "pp": 20,
        "description": "Unsanitary sludge is hurled at the target."
    },

    # Ground moves
    "dig": {
        "type": PokemonType.GROUND,
        "category": MoveCategory.PHYSICAL,
        "power": 80,
        "accuracy": 100,
        "pp": 10,
        "description": "The user burrows into the ground, then attacks on the next turn."
    },
    "earthquake": {
        "type": PokemonType.GROUND,
        "category": MoveCategory.PHYSICAL,
        "power": 100,
        "accuracy": 100,
        "pp": 10,
        "description": "The user sets off an earthquake that strikes every Pokemon around it."
    },

    # Flying moves
    "gust": {
        "type": PokemonType.FLYING,
        "category": MoveCategory.SPECIAL,
        "power": 40,
        "accuracy": 100,
        "pp": 35,
        "description": "A gust of wind is whipped up by wings and launched at the target."
    },
    "wing_attack": {
        "type": PokemonType.FLYING,
        "category": MoveCategory.PHYSICAL,
        "power": 60,
        "accuracy": 100,
        "pp": 35,
        "description": "The target is struck with large, imposing wings spread wide."
    },
    "fly": {
        "type": PokemonType.FLYING,
        "category": MoveCategory.PHYSICAL,
        "power": 90,
        "accuracy": 95,
        "pp": 15,
        "description": "The user flies up into the sky and then strikes its target."
    },

    # Psychic moves
    "confusion": {
        "type": PokemonType.PSYCHIC,
        "category": MoveCategory.SPECIAL,
        "power": 50,
        "accuracy": 100,
        "pp": 25,
        "description": "The target is hit by a weak telekinetic force."
    },
    "psychic": {
        "type": PokemonType.PSYCHIC,
        "category": MoveCategory.SPECIAL,
        "power": 90,
        "accuracy": 100,
        "pp": 10,
        "description": "The target is hit by a strong telekinetic force."
    },

    # Bug moves
    "leech_life": {
        "type": PokemonType.BUG,
        "category": MoveCategory.PHYSICAL,
        "power": 80,
        "accuracy": 100,
        "pp": 10,
        "description": "The user drains the target's blood. The user's HP is restored."
    },
    "pin_missile": {
        "type": PokemonType.BUG,
        "category": MoveCategory.PHYSICAL,
        "power": 25,
        "accuracy": 95,
        "pp": 20,
        "description": "Sharp spikes are shot at the target in rapid succession."
    },

    # Rock moves
    "rock_throw": {
        "type": PokemonType.ROCK,
        "category": MoveCategory.PHYSICAL,
        "power": 50,
        "accuracy": 90,
        "pp": 15,
        "description": "The user picks up and throws a small rock at the target."
    },
    "rock_slide": {
        "type": PokemonType.ROCK,
        "category": MoveCategory.PHYSICAL,
        "power": 75,
        "accuracy": 90,
        "pp": 10,
        "description": "Large boulders are hurled at opposing Pokemon."
    },

    # Ghost moves
    "lick": {
        "type": PokemonType.GHOST,
        "category": MoveCategory.PHYSICAL,
        "power": 30,
        "accuracy": 100,
        "pp": 30,
        "description": "The target is licked with a long tongue, causing damage."
    },
    "shadow_ball": {
        "type": PokemonType.GHOST,
        "category": MoveCategory.SPECIAL,
        "power": 80,
        "accuracy": 100,
        "pp": 15,
        "description": "The user hurls a shadowy blob at the target."
    },

    # Dragon moves
    "dragon_rage": {
        "type": PokemonType.DRAGON,
        "category": MoveCategory.SPECIAL,
        "power": 40,
        "accuracy": 100,
        "pp": 10,
        "description": "This attack hits the target with a shock wave of pure rage."
    },

    # ── Status moves (power=0, lower/raise stats) ─────────────────────────────
    "growl": {
        "type": PokemonType.NORMAL, "category": MoveCategory.STATUS,
        "power": 0, "accuracy": 100, "pp": 40,
        "description": "The user growls in an endearing way, lowering the target's Attack.",
        "stat_effects": [{"stat": "attack", "change": -1, "target": "opponent"}],
    },
    "tail_whip": {
        "type": PokemonType.NORMAL, "category": MoveCategory.STATUS,
        "power": 0, "accuracy": 100, "pp": 30,
        "description": "The user wags its tail to lower the target's Defense.",
        "stat_effects": [{"stat": "defense", "change": -1, "target": "opponent"}],
    },
    "leer": {
        "type": PokemonType.NORMAL, "category": MoveCategory.STATUS,
        "power": 0, "accuracy": 100, "pp": 30,
        "description": "The user gives the target an intimidating leer to lower its Defense.",
        "stat_effects": [{"stat": "defense", "change": -1, "target": "opponent"}],
    },
    "smokescreen": {
        "type": PokemonType.NORMAL, "category": MoveCategory.STATUS,
        "power": 0, "accuracy": 100, "pp": 20,
        "description": "The user releases an obscuring cloud of smoke to lower accuracy.",
        "stat_effects": [{"stat": "accuracy", "change": -1, "target": "opponent"}],
    },
    "sand_attack": {
        "type": PokemonType.GROUND, "category": MoveCategory.STATUS,
        "power": 0, "accuracy": 100, "pp": 15,
        "description": "Sand is hurled in the target's face to lower its accuracy.",
        "stat_effects": [{"stat": "accuracy", "change": -1, "target": "opponent"}],
    },
    "string_shot": {
        "type": PokemonType.BUG, "category": MoveCategory.STATUS,
        "power": 0, "accuracy": 95, "pp": 40,
        "description": "The targets are bound with silk blown from the user's mouth, lowering Speed.",
        "stat_effects": [{"stat": "speed", "change": -1, "target": "opponent"}],
    },
    "swords_dance": {
        "type": PokemonType.NORMAL, "category": MoveCategory.STATUS,
        "power": 0, "accuracy": 100, "pp": 20,
        "description": "A frenetic dance to uplift the fighting spirit — sharply raises Attack.",
        "stat_effects": [{"stat": "attack", "change": 2, "target": "self"}],
    },
    "harden": {
        "type": PokemonType.NORMAL, "category": MoveCategory.STATUS,
        "power": 0, "accuracy": 100, "pp": 30,
        "description": "The user stiffens all the muscles in its body to raise its Defense.",
        "stat_effects": [{"stat": "defense", "change": 1, "target": "self"}],
    },
    "withdraw": {
        "type": PokemonType.WATER, "category": MoveCategory.STATUS,
        "power": 0, "accuracy": 100, "pp": 40,
        "description": "The user withdraws its body into its hard shell to raise its Defense.",
        "stat_effects": [{"stat": "defense", "change": 1, "target": "self"}],
    },
    "defense_curl": {
        "type": PokemonType.NORMAL, "category": MoveCategory.STATUS,
        "power": 0, "accuracy": 100, "pp": 40,
        "description": "The user curls up to conceal weak spots and boosts its Defense.",
        "stat_effects": [{"stat": "defense", "change": 1, "target": "self"}],
    },
    "agility": {
        "type": PokemonType.PSYCHIC, "category": MoveCategory.STATUS,
        "power": 0, "accuracy": 100, "pp": 30,
        "description": "The user relaxes and lightens its body to move faster — sharply raises Speed.",
        "stat_effects": [{"stat": "speed", "change": 2, "target": "self"}],
    },
    "amnesia": {
        "type": PokemonType.PSYCHIC, "category": MoveCategory.STATUS,
        "power": 0, "accuracy": 100, "pp": 20,
        "description": "The user temporarily empties its mind to forget its concerns — sharply raises Sp. Def.",
        "stat_effects": [{"stat": "sp_defense", "change": 2, "target": "self"}],
    },
    "meditate": {
        "type": PokemonType.PSYCHIC, "category": MoveCategory.STATUS,
        "power": 0, "accuracy": 100, "pp": 40,
        "description": "The user meditates to awaken the power deep within its body — raises Attack.",
        "stat_effects": [{"stat": "attack", "change": 1, "target": "self"}],
    },
    "screech": {
        "type": PokemonType.NORMAL, "category": MoveCategory.STATUS,
        "power": 0, "accuracy": 85, "pp": 40,
        "description": "An earsplitting screech harshly lowers the target's Defense.",
        "stat_effects": [{"stat": "defense", "change": -2, "target": "opponent"}],
    },
    "scary_face": {
        "type": PokemonType.NORMAL, "category": MoveCategory.STATUS,
        "power": 0, "accuracy": 100, "pp": 10,
        "description": "The user frightens the target with a scary face, sharply lowering its Speed.",
        "stat_effects": [{"stat": "speed", "change": -2, "target": "opponent"}],
    },
    "acid": {
        "type": PokemonType.POISON, "category": MoveCategory.SPECIAL,
        "power": 40, "accuracy": 100, "pp": 30,
        "description": "Opposing Pokemon are attacked with a spray of harsh acid.",
        "stat_effects": [{"stat": "defense", "change": -1, "target": "opponent"}],
    },
    "bubble_beam": {
        "type": PokemonType.WATER, "category": MoveCategory.SPECIAL,
        "power": 65, "accuracy": 100, "pp": 20,
        "description": "A spray of bubbles is forcefully ejected — may lower Speed.",
        "stat_effects": [],
    },
}

"""Pokemon type effectiveness chart."""

from enum import Enum


class PokemonType(Enum):
    NORMAL = "normal"
    FIRE = "fire"
    WATER = "water"
    ELECTRIC = "electric"
    GRASS = "grass"
    ICE = "ice"
    FIGHTING = "fighting"
    POISON = "poison"
    GROUND = "ground"
    FLYING = "flying"
    PSYCHIC = "psychic"
    BUG = "bug"
    ROCK = "rock"
    GHOST = "ghost"
    DRAGON = "dragon"


# Type effectiveness multipliers
# Key: (attacking_type, defending_type) -> multiplier
TYPE_CHART = {
    # Normal
    (PokemonType.NORMAL, PokemonType.ROCK): 0.5,
    (PokemonType.NORMAL, PokemonType.GHOST): 0.0,

    # Fire
    (PokemonType.FIRE, PokemonType.FIRE): 0.5,
    (PokemonType.FIRE, PokemonType.WATER): 0.5,
    (PokemonType.FIRE, PokemonType.GRASS): 2.0,
    (PokemonType.FIRE, PokemonType.ICE): 2.0,
    (PokemonType.FIRE, PokemonType.BUG): 2.0,
    (PokemonType.FIRE, PokemonType.ROCK): 0.5,
    (PokemonType.FIRE, PokemonType.DRAGON): 0.5,

    # Water
    (PokemonType.WATER, PokemonType.FIRE): 2.0,
    (PokemonType.WATER, PokemonType.WATER): 0.5,
    (PokemonType.WATER, PokemonType.GRASS): 0.5,
    (PokemonType.WATER, PokemonType.GROUND): 2.0,
    (PokemonType.WATER, PokemonType.ROCK): 2.0,
    (PokemonType.WATER, PokemonType.DRAGON): 0.5,

    # Electric
    (PokemonType.ELECTRIC, PokemonType.WATER): 2.0,
    (PokemonType.ELECTRIC, PokemonType.ELECTRIC): 0.5,
    (PokemonType.ELECTRIC, PokemonType.GRASS): 0.5,
    (PokemonType.ELECTRIC, PokemonType.GROUND): 0.0,
    (PokemonType.ELECTRIC, PokemonType.FLYING): 2.0,
    (PokemonType.ELECTRIC, PokemonType.DRAGON): 0.5,

    # Grass
    (PokemonType.GRASS, PokemonType.FIRE): 0.5,
    (PokemonType.GRASS, PokemonType.WATER): 2.0,
    (PokemonType.GRASS, PokemonType.GRASS): 0.5,
    (PokemonType.GRASS, PokemonType.POISON): 0.5,
    (PokemonType.GRASS, PokemonType.GROUND): 2.0,
    (PokemonType.GRASS, PokemonType.FLYING): 0.5,
    (PokemonType.GRASS, PokemonType.BUG): 0.5,
    (PokemonType.GRASS, PokemonType.ROCK): 2.0,
    (PokemonType.GRASS, PokemonType.DRAGON): 0.5,

    # Ice
    (PokemonType.ICE, PokemonType.FIRE): 0.5,
    (PokemonType.ICE, PokemonType.WATER): 0.5,
    (PokemonType.ICE, PokemonType.GRASS): 2.0,
    (PokemonType.ICE, PokemonType.ICE): 0.5,
    (PokemonType.ICE, PokemonType.GROUND): 2.0,
    (PokemonType.ICE, PokemonType.FLYING): 2.0,
    (PokemonType.ICE, PokemonType.DRAGON): 2.0,

    # Fighting
    (PokemonType.FIGHTING, PokemonType.NORMAL): 2.0,
    (PokemonType.FIGHTING, PokemonType.ICE): 2.0,
    (PokemonType.FIGHTING, PokemonType.POISON): 0.5,
    (PokemonType.FIGHTING, PokemonType.FLYING): 0.5,
    (PokemonType.FIGHTING, PokemonType.PSYCHIC): 0.5,
    (PokemonType.FIGHTING, PokemonType.BUG): 0.5,
    (PokemonType.FIGHTING, PokemonType.ROCK): 2.0,
    (PokemonType.FIGHTING, PokemonType.GHOST): 0.0,

    # Poison
    (PokemonType.POISON, PokemonType.GRASS): 2.0,
    (PokemonType.POISON, PokemonType.POISON): 0.5,
    (PokemonType.POISON, PokemonType.GROUND): 0.5,
    (PokemonType.POISON, PokemonType.ROCK): 0.5,
    (PokemonType.POISON, PokemonType.GHOST): 0.5,

    # Ground
    (PokemonType.GROUND, PokemonType.FIRE): 2.0,
    (PokemonType.GROUND, PokemonType.ELECTRIC): 2.0,
    (PokemonType.GROUND, PokemonType.GRASS): 0.5,
    (PokemonType.GROUND, PokemonType.POISON): 2.0,
    (PokemonType.GROUND, PokemonType.FLYING): 0.0,
    (PokemonType.GROUND, PokemonType.BUG): 0.5,
    (PokemonType.GROUND, PokemonType.ROCK): 2.0,

    # Flying
    (PokemonType.FLYING, PokemonType.ELECTRIC): 0.5,
    (PokemonType.FLYING, PokemonType.GRASS): 2.0,
    (PokemonType.FLYING, PokemonType.FIGHTING): 2.0,
    (PokemonType.FLYING, PokemonType.BUG): 2.0,
    (PokemonType.FLYING, PokemonType.ROCK): 0.5,

    # Psychic
    (PokemonType.PSYCHIC, PokemonType.FIGHTING): 2.0,
    (PokemonType.PSYCHIC, PokemonType.POISON): 2.0,
    (PokemonType.PSYCHIC, PokemonType.PSYCHIC): 0.5,

    # Bug
    (PokemonType.BUG, PokemonType.FIRE): 0.5,
    (PokemonType.BUG, PokemonType.GRASS): 2.0,
    (PokemonType.BUG, PokemonType.FIGHTING): 0.5,
    (PokemonType.BUG, PokemonType.POISON): 0.5,
    (PokemonType.BUG, PokemonType.FLYING): 0.5,
    (PokemonType.BUG, PokemonType.PSYCHIC): 2.0,
    (PokemonType.BUG, PokemonType.GHOST): 0.5,

    # Rock
    (PokemonType.ROCK, PokemonType.FIRE): 2.0,
    (PokemonType.ROCK, PokemonType.ICE): 2.0,
    (PokemonType.ROCK, PokemonType.FIGHTING): 0.5,
    (PokemonType.ROCK, PokemonType.GROUND): 0.5,
    (PokemonType.ROCK, PokemonType.FLYING): 2.0,
    (PokemonType.ROCK, PokemonType.BUG): 2.0,

    # Ghost
    (PokemonType.GHOST, PokemonType.NORMAL): 0.0,
    (PokemonType.GHOST, PokemonType.PSYCHIC): 2.0,
    (PokemonType.GHOST, PokemonType.GHOST): 2.0,

    # Dragon
    (PokemonType.DRAGON, PokemonType.DRAGON): 2.0,
}


class TypeChart:
    """Handles type effectiveness calculations."""

    @staticmethod
    def get_effectiveness(attack_type: PokemonType, defend_types: list[PokemonType]) -> float:
        """
        Calculate type effectiveness multiplier.

        Args:
            attack_type: The type of the attacking move
            defend_types: List of defending Pokemon's types

        Returns:
            Effectiveness multiplier (0.0, 0.25, 0.5, 1.0, 2.0, or 4.0)
        """
        multiplier = 1.0
        for defend_type in defend_types:
            multiplier *= TYPE_CHART.get((attack_type, defend_type), 1.0)
        return multiplier

    @staticmethod
    def get_effectiveness_message(multiplier: float) -> str:
        """Get a message describing the effectiveness."""
        if multiplier == 0.0:
            return "It had no effect..."
        elif multiplier < 1.0:
            return "It's not very effective..."
        elif multiplier > 1.0:
            return "It's super effective!"
        return ""

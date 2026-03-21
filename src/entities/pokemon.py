"""Pokemon class representing a battle-ready Pokemon."""

import random
from typing import Optional

from src.core.type_chart import PokemonType, TypeChart
from src.core.pokemon_data import get_pokemon_data, is_pokemon_available
from src.entities.move import Move


class Pokemon:
    """Represents a Pokemon with stats, moves, and battle capabilities."""

    def __init__(self, pokemon_id: int, level: int = 5, nickname: str = None):
        """
        Initialize a Pokemon from the database.

        Args:
            pokemon_id: The Pokedex number of the Pokemon
            level: The Pokemon's level (1-100)
            nickname: Optional nickname for the Pokemon
        """
        if not is_pokemon_available(pokemon_id):
            raise ValueError(f"Unknown Pokemon ID: {pokemon_id}")

        data = get_pokemon_data(pokemon_id)

        self.id = pokemon_id
        self.name = data["name"]
        self.nickname = nickname
        self.level = max(1, min(100, level))
        self.types: list[PokemonType] = data["types"]
        self.base_stats = data["base_stats"].copy()
        self.learnable_moves = data["learnable_moves"]

        # Calculate actual stats based on level
        self.max_hp = self._calculate_hp()
        self.current_hp = self.max_hp
        self.attack = self._calculate_stat("attack")
        self.defense = self._calculate_stat("defense")
        self.sp_attack = self._calculate_stat("sp_attack")
        self.sp_defense = self._calculate_stat("sp_defense")
        self.speed = self._calculate_stat("speed")

        # Moves (max 4)
        self.moves: list[Move] = []
        self._learn_initial_moves()

        # Battle state
        self.is_fainted = False

        # Experience
        self.experience_points: int = 0

    def _calculate_hp(self) -> int:
        """Calculate HP stat using the Pokemon formula."""
        base = self.base_stats["hp"]
        # Simplified stat formula
        return int(((2 * base + 31) * self.level / 100) + self.level + 10)

    def _calculate_stat(self, stat_name: str) -> int:
        """Calculate a non-HP stat using the Pokemon formula."""
        base = self.base_stats[stat_name]
        # Simplified stat formula
        return int(((2 * base + 31) * self.level / 100) + 5)

    def _learn_initial_moves(self):
        """Learn initial moves based on level."""
        # Learn moves based on level (higher level = more moves available)
        available_moves = self.learnable_moves.copy()
        num_moves = min(4, max(1, self.level // 10 + 1))

        # Select moves, prioritizing later moves in the list (stronger)
        selected = available_moves[-num_moves:] if len(available_moves) > num_moves else available_moves

        for move_name in selected:
            self.moves.append(Move(move_name))

    def learn_move(self, move_name: str, slot: int = None) -> bool:
        """
        Learn a new move.

        Args:
            move_name: The move to learn
            slot: If specified, replace move in this slot (0-3). If None, add if space available.

        Returns:
            True if move was learned, False otherwise.
        """
        if move_name not in self.learnable_moves:
            return False

        new_move = Move(move_name)

        if slot is not None and 0 <= slot < 4:
            if slot < len(self.moves):
                self.moves[slot] = new_move
            else:
                self.moves.append(new_move)
            return True
        elif len(self.moves) < 4:
            self.moves.append(new_move)
            return True

        return False

    def take_damage(self, damage: int) -> int:
        """
        Take damage and update HP.

        Args:
            damage: Amount of damage to take

        Returns:
            Actual damage taken
        """
        actual_damage = min(self.current_hp, max(0, damage))
        self.current_hp -= actual_damage

        if self.current_hp <= 0:
            self.current_hp = 0
            self.is_fainted = True

        return actual_damage

    def heal(self, amount: int) -> int:
        """
        Heal the Pokemon.

        Args:
            amount: Amount to heal

        Returns:
            Actual amount healed
        """
        if self.is_fainted:
            return 0

        actual_heal = min(self.max_hp - self.current_hp, max(0, amount))
        self.current_hp += actual_heal
        return actual_heal

    def gain_exp(self, amount: int) -> bool:
        """
        Gain experience points.

        Returns:
            True if the Pokemon leveled up
        """
        if self.level >= 100:
            return False
        self.experience_points += amount
        xp_needed = self.level * 100
        if self.experience_points >= xp_needed:
            self.experience_points -= xp_needed
            self.level = min(100, self.level + 1)
            old_max_hp = self.max_hp
            self.max_hp = self._calculate_hp()
            self.current_hp += self.max_hp - old_max_hp
            self.attack = self._calculate_stat("attack")
            self.defense = self._calculate_stat("defense")
            self.sp_attack = self._calculate_stat("sp_attack")
            self.sp_defense = self._calculate_stat("sp_defense")
            self.speed = self._calculate_stat("speed")
            return True
        return False

    def full_restore(self):
        """Fully restore HP and PP."""
        self.current_hp = self.max_hp
        self.is_fainted = False
        for move in self.moves:
            move.restore_pp()

    def get_display_name(self) -> str:
        """Get the display name (nickname or species name)."""
        return self.nickname if self.nickname else self.name

    def get_hp_percentage(self) -> float:
        """Get HP as a percentage."""
        return (self.current_hp / self.max_hp) * 100

    def get_sprite_path(self) -> str:
        """Get the sprite path for this Pokemon."""
        return f"assets/sprites/{self.id:03d}_{self.name.lower()}.png"

    def calculate_damage(self, move: Move, defender: "Pokemon") -> tuple[int, float, bool]:
        """
        Calculate damage for an attack.

        Args:
            move: The move being used
            defender: The defending Pokemon

        Returns:
            Tuple of (damage, effectiveness_multiplier, is_critical)
        """
        if move.power == 0:
            return 0, 1.0, False

        # Determine which stats to use
        if move.is_physical():
            attack_stat = self.attack
            defense_stat = defender.defense
        else:
            attack_stat = self.sp_attack
            defense_stat = defender.sp_defense

        # Base damage formula (simplified)
        base_damage = ((2 * self.level / 5 + 2) * move.power * attack_stat / defense_stat) / 50 + 2

        # STAB (Same Type Attack Bonus)
        stab = 1.5 if move.type in self.types else 1.0

        # Type effectiveness
        effectiveness = TypeChart.get_effectiveness(move.type, defender.types)

        # Critical hit (6.25% chance)
        is_critical = random.random() < 0.0625
        critical = 1.5 if is_critical else 1.0

        # Random factor (85-100%)
        random_factor = random.uniform(0.85, 1.0)

        # Final damage
        damage = int(base_damage * stab * effectiveness * critical * random_factor)

        return max(1, damage) if effectiveness > 0 else 0, effectiveness, is_critical

    def __str__(self) -> str:
        types_str = "/".join(t.value.title() for t in self.types)
        return f"{self.get_display_name()} (Lv.{self.level} {types_str}) - HP: {self.current_hp}/{self.max_hp}"

    def __repr__(self) -> str:
        return f"Pokemon({self.id}, level={self.level})"

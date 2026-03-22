"""Trainer class representing a Pokemon trainer."""

from typing import Optional
from src.entities.pokemon import Pokemon


class Trainer:
    """Represents a Pokemon trainer with a team of Pokemon."""

    MAX_TEAM_SIZE = 6

    def __init__(self, name: str, is_player: bool = False, is_wild: bool = False):
        """
        Initialize a trainer.

        Args:
            name: The trainer's name
            is_player: Whether this is the player character
        """
        self.name = name
        self.is_player = is_player
        self.is_wild = is_wild
        self.team: list[Pokemon] = []
        self.box: list[Pokemon] = []
        self.active_pokemon_index: int = 0
        self.money: int = 0
        self.items: dict = {}  # item_name -> count

    def add_pokemon(self, pokemon: Pokemon) -> bool:
        """
        Add a Pokemon to the trainer's team.

        Args:
            pokemon: The Pokemon to add

        Returns:
            True if added successfully, False if team is full
        """
        if len(self.team) >= self.MAX_TEAM_SIZE:
            return False
        self.team.append(pokemon)
        return True

    def get_active_pokemon(self) -> Optional[Pokemon]:
        """Get the currently active Pokemon."""
        if not self.team:
            return None
        return self.team[self.active_pokemon_index]

    def switch_pokemon(self, index: int) -> bool:
        """
        Switch to a different Pokemon.

        Args:
            index: The index of the Pokemon to switch to

        Returns:
            True if switch was successful
        """
        if index < 0 or index >= len(self.team):
            return False
        if self.team[index].is_fainted:
            return False
        if index == self.active_pokemon_index:
            return False
        self.active_pokemon_index = index
        return True

    def get_available_pokemon(self) -> list[tuple[int, Pokemon]]:
        """Get list of non-fainted Pokemon with their indices."""
        return [(i, p) for i, p in enumerate(self.team) if not p.is_fainted]

    def has_usable_pokemon(self) -> bool:
        """Check if trainer has any non-fainted Pokemon."""
        return any(not p.is_fainted for p in self.team)

    def force_switch(self) -> bool:
        """
        Force switch to first available Pokemon (when active faints).

        Returns:
            True if a switch was made, False if no Pokemon available
        """
        for i, pokemon in enumerate(self.team):
            if not pokemon.is_fainted:
                self.active_pokemon_index = i
                return True
        return False

    def add_money(self, amount: int):
        """Add money to the trainer."""
        self.money += amount

    def spend_money(self, amount: int) -> bool:
        """Spend money. Returns False if insufficient funds."""
        if self.money < amount:
            return False
        self.money -= amount
        return True

    def add_item(self, item_name: str, count: int = 1):
        """Add items to inventory."""
        self.items[item_name] = self.items.get(item_name, 0) + count

    def use_item(self, item_name: str) -> bool:
        """Remove one use of an item. Returns False if none available."""
        if self.items.get(item_name, 0) <= 0:
            return False
        self.items[item_name] -= 1
        if self.items[item_name] == 0:
            del self.items[item_name]
        return True

    def deposit_to_box(self, team_index: int) -> bool:
        """Move a Pokemon from team to box. Team must keep at least 1."""
        if len(self.team) <= 1:
            return False
        if team_index < 0 or team_index >= len(self.team):
            return False
        pk = self.team.pop(team_index)
        self.box.append(pk)
        # Fix active index if needed
        if self.active_pokemon_index >= len(self.team):
            self.active_pokemon_index = max(0, len(self.team) - 1)
        # Make sure active pokemon is not fainted
        if self.team[self.active_pokemon_index].is_fainted:
            self.force_switch()
        return True

    def withdraw_from_box(self, box_index: int) -> bool:
        """Move a Pokemon from box to team. Team must have room (< MAX_TEAM_SIZE)."""
        if len(self.team) >= self.MAX_TEAM_SIZE:
            return False
        if box_index < 0 or box_index >= len(self.box):
            return False
        pk = self.box.pop(box_index)
        self.team.append(pk)
        return True

    def heal_team(self):
        """Fully heal all Pokemon in the team."""
        for pokemon in self.team:
            pokemon.full_restore()

    def __str__(self) -> str:
        pokemon_count = len(self.team)
        active = self.get_active_pokemon()
        active_str = f" - Active: {active.get_display_name()}" if active else ""
        return f"{self.name} ({pokemon_count} Pokemon){active_str}"

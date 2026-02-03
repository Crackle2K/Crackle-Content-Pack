"""Move class for Pokemon attacks."""

from src.core.type_chart import PokemonType
from src.core.moves_data import MOVES_DATA, MoveCategory


class Move:
    """Represents a Pokemon move/attack."""

    def __init__(self, move_name: str):
        """
        Initialize a move from the moves database.

        Args:
            move_name: The internal name of the move (e.g., "thunderbolt")
        """
        if move_name not in MOVES_DATA:
            raise ValueError(f"Unknown move: {move_name}")

        move_data = MOVES_DATA[move_name]

        self.name = move_name
        self.display_name = move_name.replace("_", " ").title()
        self.type: PokemonType = move_data["type"]
        self.category: str = move_data["category"]
        self.power: int = move_data["power"]
        self.accuracy: int = move_data["accuracy"]
        self.max_pp: int = move_data["pp"]
        self.current_pp: int = self.max_pp
        self.priority: int = move_data.get("priority", 0)
        self.description: str = move_data["description"]

    def use(self) -> bool:
        """
        Use the move, consuming PP.

        Returns:
            True if the move can be used, False if out of PP.
        """
        if self.current_pp <= 0:
            return False
        self.current_pp -= 1
        return True

    def restore_pp(self, amount: int = None):
        """
        Restore PP to the move.

        Args:
            amount: Amount to restore. If None, fully restores.
        """
        if amount is None:
            self.current_pp = self.max_pp
        else:
            self.current_pp = min(self.current_pp + amount, self.max_pp)

    def is_physical(self) -> bool:
        """Check if this is a physical move."""
        return self.category == MoveCategory.PHYSICAL

    def is_special(self) -> bool:
        """Check if this is a special move."""
        return self.category == MoveCategory.SPECIAL

    def is_status(self) -> bool:
        """Check if this is a status move."""
        return self.category == MoveCategory.STATUS

    def __str__(self) -> str:
        return f"{self.display_name} ({self.type.value.title()}) - PP: {self.current_pp}/{self.max_pp}"

    def __repr__(self) -> str:
        return f"Move('{self.name}')"

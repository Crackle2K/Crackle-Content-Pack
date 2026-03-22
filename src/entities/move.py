"""Move class for Pokemon attacks."""

import json
from pathlib import Path
from src.core.type_chart import PokemonType
from src.core.moves_data import MOVES_DATA, MoveCategory


# Module-level cache so the JSON is read only once per process
_moves_json_cache: dict | None = None


def _get_moves_json() -> dict:
    global _moves_json_cache
    if _moves_json_cache is None:
        p = Path("assets/moves/moves_data.json")
        try:
            _moves_json_cache = json.loads(p.read_text()) if p.exists() else {}
        except Exception:
            _moves_json_cache = {}
    return _moves_json_cache


class Move:
    """Represents a Pokemon move/attack."""

    def __init__(self, move_name: str):
        moves_json = _get_moves_json()

        if move_name in moves_json:
            d = moves_json[move_name]
            self.name         = move_name
            self.display_name = d.get("display_name", move_name.replace("_", " ").title())
            self.type         = PokemonType(d["type"])
            self.category     = d["category"]   # "physical" / "special" / "status"
            self.power        = int(d.get("power",    0))
            self.accuracy     = int(d.get("accuracy", 100))
            self.max_pp       = int(d.get("pp",       5))
            self.current_pp   = self.max_pp
            self.priority     = int(d.get("priority", 0))
            self.description  = d.get("description", "")
            # JSON may lack stat_effects/status_effect; fall back to Python data dict
            py = MOVES_DATA.get(move_name, {})
            self.stat_effects  = d.get("stat_effects")  or py.get("stat_effects",  [])
            self.status_effect = d.get("status_effect") or py.get("status_effect", None)
            self.special_effect = d.get("special_effect") or py.get("special_effect", None)

        elif move_name in MOVES_DATA:
            d                 = MOVES_DATA[move_name]
            self.name         = move_name
            self.display_name = move_name.replace("_", " ").title()
            self.type         = d["type"]
            self.category     = d["category"]
            self.power        = d["power"]
            self.accuracy     = d["accuracy"]
            self.max_pp       = d["pp"]
            self.current_pp   = self.max_pp
            self.priority     = d.get("priority", 0)
            self.description  = d["description"]
            self.stat_effects  = d.get("stat_effects",  [])
            self.status_effect = d.get("status_effect", None)
            self.special_effect = d.get("special_effect", None)

        else:
            raise ValueError(f"Unknown move: {move_name}")

    def use(self) -> bool:
        """Use the move, consuming 1 PP. Returns False if out of PP."""
        if self.current_pp <= 0:
            return False
        self.current_pp -= 1
        return True

    def restore_pp(self, amount: int = None):
        """Restore PP. If amount is None, fully restores."""
        if amount is None:
            self.current_pp = self.max_pp
        else:
            self.current_pp = min(self.current_pp + amount, self.max_pp)

    def is_physical(self) -> bool:
        return self.category == MoveCategory.PHYSICAL

    def is_special(self) -> bool:
        return self.category == MoveCategory.SPECIAL

    def is_status(self) -> bool:
        return self.category == MoveCategory.STATUS

    def __str__(self) -> str:
        return f"{self.display_name} ({self.type.value.title()}) - PP: {self.current_pp}/{self.max_pp}"

    def __repr__(self) -> str:
        return f"Move('{self.name}')"

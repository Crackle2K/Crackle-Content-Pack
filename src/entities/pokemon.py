"""Pokemon class representing a battle-ready Pokemon."""

import json
import random
from pathlib import Path
from typing import Optional

from src.core.type_chart import PokemonType, TypeChart
from src.core.pokemon_data import get_pokemon_data, is_pokemon_available
from src.entities.move import Move


# ── Learnset JSON cache ───────────────────────────────────────────────────────
_learnsets_cache: dict | None = None


def _get_learnsets() -> dict:
    global _learnsets_cache
    if _learnsets_cache is None:
        p = Path("assets/moves/learnsets.json")
        try:
            _learnsets_cache = json.loads(p.read_text()) if p.exists() else {}
        except Exception:
            _learnsets_cache = {}
    return _learnsets_cache


class Pokemon:
    """Represents a Pokemon with stats, moves, and battle capabilities."""

    def __init__(self, pokemon_id: int, level: int = 5, nickname: str = None):
        if not is_pokemon_available(pokemon_id):
            raise ValueError(f"Unknown Pokemon ID: {pokemon_id}")

        data = get_pokemon_data(pokemon_id)

        self.id               = pokemon_id
        self.name             = data["name"]
        self.nickname         = nickname
        self.level            = max(1, min(100, level))
        self.types: list[PokemonType] = data["types"]
        self.base_stats       = data["base_stats"].copy()
        self.learnable_moves  = data["learnable_moves"]   # fallback list

        # Calculate stats
        self.max_hp      = self._calculate_hp()
        self.current_hp  = self.max_hp
        self.attack      = self._calculate_stat("attack")
        self.defense     = self._calculate_stat("defense")
        self.sp_attack   = self._calculate_stat("sp_attack")
        self.sp_defense  = self._calculate_stat("sp_defense")
        self.speed       = self._calculate_stat("speed")

        # Moves (max 4)
        self.moves: list[Move] = []
        self._learn_initial_moves()

        # Battle state
        self.is_fainted      = False
        self.experience_points: int = 0
        self.stat_stages: dict = {
            "attack": 0, "defense": 0,
            "sp_attack": 0, "sp_defense": 0,
            "speed": 0, "accuracy": 0, "evasion": 0,
        }

    # ── Stat formulae ─────────────────────────────────────────────────────────

    def _calculate_hp(self) -> int:
        base = self.base_stats["hp"]
        return int(((2 * base + 31) * self.level / 100) + self.level + 10)

    def _calculate_stat(self, stat_name: str) -> int:
        base = self.base_stats[stat_name]
        return int(((2 * base + 31) * self.level / 100) + 5)

    # ── Move learning ─────────────────────────────────────────────────────────

    def _learnset(self) -> list[dict]:
        """Return the PokeAPI learnset for this Pokemon (may be empty)."""
        return _get_learnsets().get(str(self.id), [])

    def _learn_initial_moves(self):
        """Populate self.moves based on current level."""
        learnset = self._learnset()

        if learnset:
            # All moves learnable at or below current level, keep last 4
            eligible = [e["move"] for e in learnset if e["level"] <= self.level]
            selected = eligible[-4:] if len(eligible) > 4 else eligible
        else:
            # Fallback: use the hand-coded learnable_moves list
            available = self.learnable_moves.copy()
            count     = min(4, max(1, self.level // 10 + 1))
            selected  = available[-count:] if len(available) > count else available

        for move_name in selected:
            try:
                self.moves.append(Move(move_name))
            except ValueError:
                pass  # Skip moves not in either data source

    def get_available_moves(self) -> list[str]:
        """Return all move names learnable at or below this Pokemon's current level."""
        learnset = self._learnset()
        if learnset:
            return [e["move"] for e in learnset if e["level"] <= self.level]
        return list(self.learnable_moves)

    def _moves_at_level(self, level: int) -> list[str]:
        """Return move names learned at exactly this level (from learnset JSON)."""
        return [e["move"] for e in self._learnset() if e["level"] == level]

    def learn_move(self, move_name: str, slot: int = None) -> bool:
        """
        Learn a new move.

        Returns True if learned, False if move unknown or no slot available.
        """
        try:
            new_move = Move(move_name)
        except ValueError:
            return False

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

    # ── Stat stages ───────────────────────────────────────────────────────────

    def get_stat_stage_mult(self, stat: str) -> float:
        """Return the multiplier for a stat based on its stage (Gen 2 formula)."""
        stage = max(-6, min(6, self.stat_stages.get(stat, 0)))
        return max(2, 2 + stage) / max(2, 2 - stage)

    def apply_stat_change(self, stat: str, change: int) -> tuple[bool, int]:
        """
        Apply a stat stage change. Returns (changed, new_stage).
        changed is False if already at the limit.
        """
        current = self.stat_stages.get(stat, 0)
        new     = max(-6, min(6, current + change))
        self.stat_stages[stat] = new
        return new != current, new

    def reset_stat_stages(self):
        for stat in self.stat_stages:
            self.stat_stages[stat] = 0

    # ── Damage / healing ──────────────────────────────────────────────────────

    def take_damage(self, damage: int) -> int:
        actual = min(self.current_hp, max(0, damage))
        self.current_hp -= actual
        if self.current_hp <= 0:
            self.current_hp = 0
            self.is_fainted  = True
        return actual

    def heal(self, amount: int) -> int:
        if self.is_fainted:
            return 0
        actual = min(self.max_hp - self.current_hp, max(0, amount))
        self.current_hp += actual
        return actual

    def full_restore(self):
        self.current_hp = self.max_hp
        self.is_fainted = False
        for move in self.moves:
            move.restore_pp()

    # ── Experience ────────────────────────────────────────────────────────────

    def gain_exp(self, amount: int) -> tuple[bool, list[str]]:
        """
        Gain experience points.

        Returns:
            (leveled_up: bool, new_move_names: list[str])
        """
        if self.level >= 100:
            return False, []

        self.experience_points += amount
        xp_needed = self.level * 100
        if self.experience_points >= xp_needed:
            self.experience_points -= xp_needed
            self.level    = min(100, self.level + 1)
            old_max_hp    = self.max_hp
            self.max_hp   = self._calculate_hp()
            self.current_hp += self.max_hp - old_max_hp
            self.attack   = self._calculate_stat("attack")
            self.defense  = self._calculate_stat("defense")
            self.sp_attack  = self._calculate_stat("sp_attack")
            self.sp_defense = self._calculate_stat("sp_defense")
            self.speed    = self._calculate_stat("speed")
            return True, self._moves_at_level(self.level)

        return False, []

    # ── Damage calculation ────────────────────────────────────────────────────

    def calculate_damage(self, move: Move, defender: "Pokemon") -> tuple[int, float, bool]:
        if move.power == 0:
            return 0, 1.0, False

        if move.is_physical():
            attack_stat  = self.attack  * self.get_stat_stage_mult("attack")
            defense_stat = defender.defense * defender.get_stat_stage_mult("defense")
        else:
            attack_stat  = self.sp_attack  * self.get_stat_stage_mult("sp_attack")
            defense_stat = defender.sp_defense * defender.get_stat_stage_mult("sp_defense")

        base_damage = ((2 * self.level / 5 + 2) * move.power * attack_stat / defense_stat) / 50 + 2
        stab        = 1.5 if move.type in self.types else 1.0
        effectiveness = TypeChart.get_effectiveness(move.type, defender.types)
        is_critical = random.random() < 0.0625
        critical    = 1.5 if is_critical else 1.0
        rand_factor = random.uniform(0.85, 1.0)

        damage = int(base_damage * stab * effectiveness * critical * rand_factor)
        return (max(1, damage) if effectiveness > 0 else 0), effectiveness, is_critical

    # ── Helpers ───────────────────────────────────────────────────────────────

    def get_display_name(self) -> str:
        return self.nickname if self.nickname else self.name

    def get_hp_percentage(self) -> float:
        return (self.current_hp / self.max_hp) * 100

    def get_sprite_path(self) -> str:
        return f"assets/sprites/{self.id:03d}_{self.name.lower()}.png"

    def __str__(self) -> str:
        types_str = "/".join(t.value.title() for t in self.types)
        return f"{self.get_display_name()} (Lv.{self.level} {types_str}) - HP: {self.current_hp}/{self.max_hp}"

    def __repr__(self) -> str:
        return f"Pokemon({self.id}, level={self.level})"

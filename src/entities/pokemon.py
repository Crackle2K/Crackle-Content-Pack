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
        self.base_experience  = data.get("base_experience", 64)
        self.growth_rate      = data.get("growth_rate", "medium-fast")

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
        # Start with total XP equal to the threshold for this Pokemon's level
        # so the progress bar begins at 0% within the current level (not negative)
        from src.core.gen1_xp_data import xp_for_level as _xp
        self.experience_points: int = _xp(max(1, self.level), self.growth_rate)
        self.stat_stages: dict = {
            "attack": 0, "defense": 0,
            "sp_attack": 0, "sp_defense": 0,
            "speed": 0, "accuracy": 0, "evasion": 0,
        }

        # Status conditions
        self.status: Optional[str] = None   # "paralyzed","asleep","poisoned","burned","badly_poisoned"
        self.sleep_turns: int = 0
        self.confused: bool = False
        self.confusion_turns: int = 0
        self.leech_seeded: bool = False
        self._poison_counter: int = 1       # escalating counter for badly_poisoned

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

    # ── Status conditions ─────────────────────────────────────────────────────

    def apply_status(self, status: str) -> bool:
        """Apply a status condition. Returns True if successfully applied."""
        # Can't overwrite an existing major status with another major status
        major = {"paralyzed", "asleep", "poisoned", "burned", "badly_poisoned"}
        if status in major and self.status is not None:
            return False

        if status == "asleep":
            self.status = "asleep"
            self.sleep_turns = random.randint(1, 3)
            return True
        elif status == "paralyzed":
            self.status = "paralyzed"
            return True
        elif status == "poisoned":
            if PokemonType.POISON in self.types or PokemonType.STEEL in self.types:
                return False
            self.status = "poisoned"
            return True
        elif status == "badly_poisoned":
            if PokemonType.POISON in self.types or PokemonType.STEEL in self.types:
                return False
            self.status = "badly_poisoned"
            self._poison_counter = 1
            return True
        elif status == "burned":
            if PokemonType.FIRE in self.types:
                return False
            self.status = "burned"
            return True
        elif status == "confused":
            if self.confused:
                return False
            self.confused = True
            self.confusion_turns = random.randint(2, 5)
            return True
        elif status == "leech_seeded":
            if PokemonType.GRASS in self.types:
                return False
            if self.leech_seeded:
                return False
            self.leech_seeded = True
            return True
        return False

    def check_can_move(self) -> "tuple[bool, str]":
        """
        Check whether the Pokemon can act this turn based on its status.
        Returns (can_move, message). May mutate state (e.g. wake up, thaw).
        """
        name = self.get_display_name()

        if self.status == "asleep":
            if self.sleep_turns > 0:
                self.sleep_turns -= 1
                if self.sleep_turns == 0:
                    self.status = None
                    return True, f"{name} woke up!"
                return False, f"{name} is fast asleep..."

        if self.status == "paralyzed":
            if random.random() < 0.25:
                return False, f"{name} is fully paralyzed and can't move!"

        if self.confused:
            self.confusion_turns -= 1
            if self.confusion_turns <= 0:
                self.confused = False
                return True, f"{name} snapped out of its confusion!"
            if random.random() < 0.33:
                # Hit self in confusion
                self_dmg = max(1, int(((2 * self.level / 5 + 2) * 40 * self.attack / self.defense) / 50 + 2))
                self.take_damage(self_dmg)
                return False, f"{name} is confused and hurt itself! ({self_dmg} damage)"

        return True, ""

    def process_end_of_turn(self, healer: "Optional[Pokemon]" = None) -> "list[tuple[str, int]]":
        """
        Process end-of-turn status effects.
        Returns list of (message, hp_delta). Negative hp_delta = damage dealt.
        healer: the Pokemon that benefits from leech seed draining.
        """
        events: list = []
        name = self.get_display_name()

        if self.status == "burned":
            dmg = max(1, self.max_hp // 16)
            actual = self.take_damage(dmg)
            events.append((f"{name} is hurt by its burn!", -actual))

        elif self.status == "poisoned":
            dmg = max(1, self.max_hp // 8)
            actual = self.take_damage(dmg)
            events.append((f"{name} is hurt by poison!", -actual))

        elif self.status == "badly_poisoned":
            dmg = max(1, (self.max_hp * self._poison_counter) // 16)
            actual = self.take_damage(dmg)
            events.append((f"{name} is badly hurt by poison!", -actual))
            self._poison_counter = min(15, self._poison_counter + 1)

        if self.leech_seeded and not self.is_fainted:
            dmg = max(1, self.max_hp // 8)
            actual = self.take_damage(dmg)
            events.append((f"{name}'s HP is sapped by Leech Seed!", -actual))
            if healer and not healer.is_fainted:
                healed = healer.heal(actual)
                if healed > 0:
                    events.append((f"{healer.get_display_name()} had its HP restored!", healed))

        return events

    def cure_status(self):
        """Remove all status conditions."""
        self.status = None
        self.sleep_turns = 0
        self.confused = False
        self.confusion_turns = 0
        self.leech_seeded = False
        self._poison_counter = 1

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
        self.cure_status()
        for move in self.moves:
            move.restore_pp()

    # ── Experience ────────────────────────────────────────────────────────────

    def xp_for_level(self, n: int) -> int:
        """Total XP needed to reach level n."""
        from src.core.gen1_xp_data import xp_for_level as _xp
        return _xp(n, self.growth_rate)

    def xp_to_next_level(self) -> int:
        """XP needed to reach the next level from current total."""
        if self.level >= 100:
            return 0
        return max(0, self.xp_for_level(self.level + 1) - self.experience_points)

    def xp_progress_in_level(self) -> tuple:
        """(xp gained in current level, xp needed for this level). For display."""
        cur_threshold = self.xp_for_level(self.level)
        nxt_threshold = self.xp_for_level(self.level + 1)
        gained = max(0, self.experience_points - cur_threshold)
        needed = max(1, nxt_threshold - cur_threshold)
        return gained, needed

    def gain_exp(self, amount: int) -> tuple:
        """
        Gain experience points.

        Returns:
            (leveled_up: bool, new_move_names: list[str])
        """
        if self.level >= 100:
            return False, []

        self.experience_points += amount
        leveled_up = False
        new_moves: list = []
        while self.level < 100 and self.experience_points >= self.xp_for_level(self.level + 1):
            self.level += 1
            leveled_up = True
            old_max_hp = self.max_hp
            self.max_hp = self._calculate_hp()
            self.current_hp += self.max_hp - old_max_hp
            self.attack = self._calculate_stat("attack")
            self.defense = self._calculate_stat("defense")
            self.sp_attack = self._calculate_stat("sp_attack")
            self.sp_defense = self._calculate_stat("sp_defense")
            self.speed = self._calculate_stat("speed")
            new_moves.extend(self._moves_at_level(self.level))
        return leveled_up, new_moves

    # ── Evolution ─────────────────────────────────────────────────────────────

    def check_evolution(self) -> "Optional[int]":
        """Return the evolved species ID if this Pokemon should evolve now, else None."""
        from src.core.evolution_data import EVOLUTION_DATA
        entry = EVOLUTION_DATA.get(self.id)
        if entry and self.level >= entry[1]:
            return entry[0]
        return None

    def evolve(self, new_id: int):
        """Mutate this Pokemon into a new species in-place."""
        from src.core.pokemon_data import get_pokemon_data, is_pokemon_available
        if not is_pokemon_available(new_id):
            return
        new_data = get_pokemon_data(new_id)
        hp_ratio = self.current_hp / max(1, self.max_hp)

        self.id             = new_id
        self.name           = new_data["name"]
        self.types          = new_data["types"]
        self.base_stats     = new_data["base_stats"].copy()
        self.learnable_moves = new_data["learnable_moves"]
        self.base_experience = new_data.get("base_experience", self.base_experience)
        # growth_rate stays the same (same evolution line)

        self.max_hp    = self._calculate_hp()
        self.current_hp = max(1, int(self.max_hp * hp_ratio))
        self.attack    = self._calculate_stat("attack")
        self.defense   = self._calculate_stat("defense")
        self.sp_attack  = self._calculate_stat("sp_attack")
        self.sp_defense = self._calculate_stat("sp_defense")
        self.speed     = self._calculate_stat("speed")

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

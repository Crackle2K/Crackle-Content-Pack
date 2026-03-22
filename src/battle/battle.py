"""Battle system for Pokemon fights."""

import random
from typing import Optional
from dataclasses import dataclass

from src.entities.pokemon import Pokemon
from src.entities.trainer import Trainer
from src.entities.move import Move
from src.core.type_chart import TypeChart
from src.battle.battle_ai import BattleAI


@dataclass
class BattleEvent:
    """Represents an event that occurred during battle."""
    event_type: str
    message: str
    data: dict = None

    def __post_init__(self):
        if self.data is None:
            self.data = {}


class Battle:
    """Manages a Pokemon battle between two trainers."""

    def __init__(self, player: Trainer, opponent: Trainer):
        """
        Initialize a battle.

        Args:
            player: The player trainer
            opponent: The opponent trainer
        """
        self.player = player
        self.opponent = opponent
        self.ai = BattleAI()
        self.turn_count = 0
        self.is_over = False
        self.winner: Optional[Trainer] = None
        self.events: list[BattleEvent] = []
        self.player_battlers: set = set()  # Pokemon objects that fought for the player
        self.caught_pokemon = None         # Set when a wild Pokemon is caught

    def start(self) -> list[BattleEvent]:
        """Start the battle and return initial events."""
        self.events = []
        self._add_event("battle_start", f"Battle between {self.player.name} and {self.opponent.name}!")

        player_pokemon = self.player.get_active_pokemon()
        opponent_pokemon = self.opponent.get_active_pokemon()

        self.player_battlers.add(player_pokemon)

        self._add_event("send_out", f"{self.opponent.name} sent out {opponent_pokemon.get_display_name()}!")
        self._add_event("send_out", f"Go! {player_pokemon.get_display_name()}!")

        return self.events

    def _add_event(self, event_type: str, message: str, **data):
        """Add a battle event."""
        self.events.append(BattleEvent(event_type, message, data))

    def execute_turn(self, player_action: str, player_action_index: int) -> list[BattleEvent]:
        """
        Execute a turn of battle.

        Args:
            player_action: "move" or "switch"
            player_action_index: Index of move or Pokemon to switch to

        Returns:
            List of events that occurred during the turn
        """
        self.events = []
        self.turn_count += 1

        player_pokemon = self.player.get_active_pokemon()
        opponent_pokemon = self.opponent.get_active_pokemon()

        # Get AI action
        ai_action, ai_action_index = self.ai.choose_action(self.opponent, player_pokemon)

        # Handle switches (switches happen before moves)
        if player_action == "switch":
            self._execute_switch(self.player, player_action_index)
            player_pokemon = self.player.get_active_pokemon()

        if ai_action == "switch":
            self._execute_switch(self.opponent, ai_action_index)
            opponent_pokemon = self.opponent.get_active_pokemon()

        # Execute moves
        if player_action == "move" and ai_action == "move":
            player_move = player_pokemon.moves[player_action_index]
            opponent_move = opponent_pokemon.moves[ai_action_index]

            # Determine order based on speed and priority
            player_first = self._determine_order(
                player_pokemon, player_move,
                opponent_pokemon, opponent_move
            )

            if player_first:
                self._execute_move(player_pokemon, opponent_pokemon, player_move, self.player, self.opponent)
                if not self.is_over and not opponent_pokemon.is_fainted:
                    self._execute_move(opponent_pokemon, player_pokemon, opponent_move, self.opponent, self.player)
            else:
                self._execute_move(opponent_pokemon, player_pokemon, opponent_move, self.opponent, self.player)
                if not self.is_over and not player_pokemon.is_fainted:
                    self._execute_move(player_pokemon, opponent_pokemon, player_move, self.player, self.opponent)

        elif player_action == "move":
            player_move = player_pokemon.moves[player_action_index]
            self._execute_move(player_pokemon, opponent_pokemon, player_move, self.player, self.opponent)

        elif ai_action == "move":
            opponent_move = opponent_pokemon.moves[ai_action_index]
            self._execute_move(opponent_pokemon, player_pokemon, opponent_move, self.opponent, self.player)

        # End-of-turn status damage (poison, burn, leech seed)
        self._process_end_of_turn_status()

        # Check for fainted Pokemon and handle switches
        self._handle_fainting()

        return self.events

    def _determine_order(self, pokemon1: Pokemon, move1: Move, pokemon2: Pokemon, move2: Move) -> bool:
        """Determine if pokemon1 goes first."""
        priority1 = move1.priority if hasattr(move1, 'priority') else 0
        priority2 = move2.priority if hasattr(move2, 'priority') else 0

        if priority1 != priority2:
            return priority1 > priority2

        # Paralyzed Pokemon have halved effective speed
        spd1 = pokemon1.speed * (0.5 if pokemon1.status == "paralyzed" else 1.0)
        spd2 = pokemon2.speed * (0.5 if pokemon2.status == "paralyzed" else 1.0)

        if spd1 != spd2:
            return spd1 > spd2

        return random.random() < 0.5

    def _process_end_of_turn_status(self):
        """Apply end-of-turn status effects (burn, poison, leech seed)."""
        player_pk   = self.player.get_active_pokemon()
        opponent_pk = self.opponent.get_active_pokemon()

        if player_pk and not player_pk.is_fainted:
            for msg, _ in player_pk.process_end_of_turn(healer=opponent_pk):
                self._add_event("status", msg)

        if opponent_pk and not opponent_pk.is_fainted:
            for msg, _ in opponent_pk.process_end_of_turn(healer=player_pk):
                self._add_event("status", msg)

    def _execute_switch(self, trainer: Trainer, pokemon_index: int):
        """Execute a Pokemon switch."""
        old_pokemon = trainer.get_active_pokemon()
        if old_pokemon:
            old_pokemon.reset_stat_stages()
        if trainer.switch_pokemon(pokemon_index):
            new_pokemon = trainer.get_active_pokemon()
            if trainer.is_player:
                self.player_battlers.add(new_pokemon)
                self._add_event("switch", f"Come back, {old_pokemon.get_display_name()}!")
                self._add_event("send_out", f"Go! {new_pokemon.get_display_name()}!")
            else:
                self._add_event("switch", f"{trainer.name} withdrew {old_pokemon.get_display_name()}!")
                self._add_event("send_out", f"{trainer.name} sent out {new_pokemon.get_display_name()}!")

    def _execute_move(self, attacker: Pokemon, defender: Pokemon, move: Move,
                      attacker_trainer: Trainer, defender_trainer: Trainer):
        """Execute a move."""
        attacker_name = attacker.get_display_name()
        defender_name = defender.get_display_name()

        # Check PP
        if not move.use():
            self._add_event("no_pp", f"{attacker_name} tried to use {move.display_name} but has no PP left!")
            return

        # Check if attacker can move (paralysis, sleep, confusion)
        can_move, status_msg = attacker.check_can_move()
        if status_msg:
            self._add_event("status", status_msg)
        if not can_move:
            return

        self._add_event("use_move", f"{attacker_name} used {move.display_name}!")

        stat_effects   = getattr(move, "stat_effects",   [])
        status_effect  = getattr(move, "status_effect",  None)
        special_effect = getattr(move, "special_effect", None)

        # ── Special-effect moves (recover, rest, level_damage, etc.) ──────────
        if special_effect:
            self._handle_special_effect(special_effect, attacker, defender,
                                        attacker_name, defender_name)
            return

        # ── Pure status move (power == 0) ──────────────────────────────────────
        if move.power == 0:
            applied_something = False

            # Stat-stage changes
            for eff in stat_effects:
                target = attacker if eff["target"] == "self" else defender
                target_name = attacker_name if eff["target"] == "self" else defender_name
                changed, _ = target.apply_stat_change(eff["stat"], eff["change"])
                stat_label = eff["stat"].replace("_", " ").title()
                if not changed:
                    direction = "higher" if eff["change"] > 0 else "lower"
                    self._add_event("stat_change",
                                    f"{target_name}'s {stat_label} can't go any {direction}!")
                else:
                    adv = ("sharply " if eff["change"] >= 2 else
                           "harshly " if eff["change"] <= -2 else "")
                    direction = "rose" if eff["change"] > 0 else "fell"
                    self._add_event("stat_change",
                                    f"{target_name}'s {stat_label} {adv}{direction}!")
                    applied_something = True

            # Status condition
            if status_effect:
                tgt = attacker if status_effect.get("target") == "self" else defender
                tgt_name = attacker_name if status_effect.get("target") == "self" else defender_name
                status = status_effect["status"]
                if tgt.apply_status(status):
                    label = status.replace("_", " ")
                    if status == "asleep":
                        self._add_event("status", f"{tgt_name} fell asleep!")
                    elif status == "paralyzed":
                        self._add_event("status", f"{tgt_name} is paralyzed! It may be unable to move!")
                    elif status in ("poisoned", "badly_poisoned"):
                        self._add_event("status", f"{tgt_name} was poisoned!")
                    elif status == "burned":
                        self._add_event("status", f"{tgt_name} was burned!")
                    elif status == "confused":
                        self._add_event("status", f"{tgt_name} became confused!")
                    elif status == "leech_seeded":
                        self._add_event("status", f"{tgt_name} was seeded!")
                    applied_something = True
                else:
                    # Already has status — force-apply confusion as a secondary effect
                    if status == "confused" and not tgt.confused:
                        tgt.apply_status("confused")
                        self._add_event("status", f"{tgt_name} became confused!")
                    applied_something = True

            if not applied_something and not stat_effects and not status_effect:
                # Fallback: deal a small fixed hit so the move always does something
                dmg = max(1, attacker.level // 2)
                actual = defender.take_damage(dmg)
                self._add_event("damage", f"{defender_name} took {actual} damage!",
                                damage=actual, defender_hp=defender.current_hp)
            return

        # ── Damaging move ──────────────────────────────────────────────────────
        damage, effectiveness, is_critical = attacker.calculate_damage(move, defender)

        if effectiveness == 0:
            effectiveness = 0.25  # Never fully immune — always deal reduced damage

        actual_damage = defender.take_damage(damage)

        eff_message = TypeChart.get_effectiveness_message(effectiveness)
        if eff_message:
            self._add_event("effectiveness", eff_message)
        if is_critical:
            self._add_event("critical", "A critical hit!")

        self._add_event("damage", f"{defender_name} took {actual_damage} damage!",
                        damage=actual_damage, defender_hp=defender.current_hp)

        # Secondary stat effects
        for eff in stat_effects:
            target = attacker if eff["target"] == "self" else defender
            target_name = attacker_name if eff["target"] == "self" else defender_name
            changed, _ = target.apply_stat_change(eff["stat"], eff["change"])
            if changed:
                stat_label = eff["stat"].replace("_", " ").title()
                direction = "rose" if eff["change"] > 0 else "fell"
                self._add_event("stat_change", f"{target_name}'s {stat_label} {direction}!")

        # Secondary status effect (e.g. 30% burn from Flamethrower if configured)
        if status_effect and not defender.is_fainted:
            tgt = attacker if status_effect.get("target") == "self" else defender
            tgt_name = attacker_name if status_effect.get("target") == "self" else defender_name
            if tgt.apply_status(status_effect["status"]):
                s = status_effect["status"]
                if s == "paralyzed":
                    self._add_event("status", f"{tgt_name} is paralyzed!")
                elif s in ("poisoned", "badly_poisoned"):
                    self._add_event("status", f"{tgt_name} was poisoned!")
                elif s == "burned":
                    self._add_event("status", f"{tgt_name} was burned!")

    def _handle_special_effect(self, effect: str, attacker: Pokemon, defender: Pokemon,
                                attacker_name: str, defender_name: str):
        """Handle special-effect moves that don't follow normal damage rules."""
        if effect == "recover":
            healed = attacker.heal(attacker.max_hp // 2)
            if healed > 0:
                self._add_event("heal", f"{attacker_name} recovered {healed} HP!")

        elif effect == "rest":
            attacker.cure_status()
            attacker.current_hp = attacker.max_hp
            attacker.is_fainted = False
            attacker.apply_status("asleep")
            attacker.sleep_turns = 2
            self._add_event("heal", f"{attacker_name} went to sleep and fully restored HP!")

        elif effect == "level_damage":
            dmg = attacker.level
            actual = defender.take_damage(dmg)
            self._add_event("damage", f"{defender_name} took {actual} damage!",
                            damage=actual, defender_hp=defender.current_hp)

        elif effect == "fixed_20":
            actual = defender.take_damage(20)
            self._add_event("damage", f"{defender_name} took {actual} damage!",
                            damage=actual, defender_hp=defender.current_hp)

        elif effect == "half_hp":
            dmg = max(1, defender.current_hp // 2)
            actual = defender.take_damage(dmg)
            self._add_event("damage", f"{defender_name} took {actual} damage!",
                            damage=actual, defender_hp=defender.current_hp)

        elif effect == "ohko":
            actual = defender.take_damage(defender.current_hp)
            self._add_event("damage", f"It's a one-hit KO! {defender_name} took {actual} damage!",
                            damage=actual, defender_hp=0)

    def _handle_fainting(self):
        """Handle fainted Pokemon and determine if battle is over."""
        player_pokemon = self.player.get_active_pokemon()
        opponent_pokemon = self.opponent.get_active_pokemon()

        if opponent_pokemon.is_fainted:
            self._add_event("faint", f"{opponent_pokemon.get_display_name()} fainted!")
            if not self.opponent.has_usable_pokemon():
                self.is_over = True
                self.winner = self.player
                self._add_event("battle_end", f"{self.player.name} won the battle!")
            else:
                # AI switches
                new_idx = self.ai.choose_switch(self.opponent, player_pokemon)
                self._execute_switch(self.opponent, new_idx)

        if player_pokemon.is_fainted:
            self._add_event("faint", f"{player_pokemon.get_display_name()} fainted!")
            if not self.player.has_usable_pokemon():
                self.is_over = True
                self.winner = self.opponent
                self._add_event("battle_end", f"{self.player.name} was defeated!")

    def execute_ai_turn(self) -> list[BattleEvent]:
        """Execute only the AI's turn (player spent their turn on an item or failed catch)."""
        self.events = []
        opponent_pokemon = self.opponent.get_active_pokemon()
        player_pokemon  = self.player.get_active_pokemon()
        if opponent_pokemon and not opponent_pokemon.is_fainted:
            ai_action, ai_idx = self.ai.choose_action(self.opponent, player_pokemon)
            if ai_action == "move":
                opp_move = opponent_pokemon.moves[ai_idx]
                self._execute_move(opponent_pokemon, player_pokemon, opp_move,
                                   self.opponent, self.player)
        self._process_end_of_turn_status()
        self._handle_fainting()
        return self.events

    def attempt_catch(self, ball_slug: str) -> tuple[bool, list[BattleEvent]]:
        """
        Attempt to catch the opponent's active Pokemon.

        Returns:
            (caught: bool, events: list[BattleEvent])
        """
        self.events = []
        opponent_pokemon = self.opponent.get_active_pokemon()

        if not self.opponent.is_wild:
            self._add_event("catch_fail", "You can't catch a trainer's Pokemon!")
            # AI still attacks
            ai_events = self.execute_ai_turn()
            self.events.extend(ai_events)
            return False, self.events

        # Simplified catch formula: lower HP → higher chance; better ball → more tries
        hp_ratio  = opponent_pokemon.current_hp / max(1, opponent_pokemon.max_hp)
        ball_mult = {"poke-ball": 1.0, "great-ball": 1.5, "ultra-ball": 2.0}.get(ball_slug, 1.0)
        catch_p   = min(0.95, (1.0 - hp_ratio * 0.65) * ball_mult)

        shakes = 0
        for _ in range(3):
            if random.random() < catch_p:
                shakes += 1
            else:
                break

        if shakes == 3:
            self._add_event("catch_success",
                            f"Gotcha! {opponent_pokemon.get_display_name()} was caught!")
            self.is_over   = True
            self.winner    = self.player
            self.caught_pokemon = opponent_pokemon
            return True, self.events
        else:
            dot = "." * shakes
            self._add_event("catch_fail",
                            f"Oh no! {opponent_pokemon.get_display_name()} broke free{dot}")
            # AI attacks after failed catch
            player_pokemon = self.player.get_active_pokemon()
            ai_action, ai_idx = self.ai.choose_action(self.opponent, player_pokemon)
            if ai_action == "move":
                self._execute_move(opponent_pokemon, player_pokemon,
                                   opponent_pokemon.moves[ai_idx],
                                   self.opponent, self.player)
            self._handle_fainting()
            return False, self.events

    def get_player_options(self) -> dict:
        """Get available options for the player."""
        pokemon = self.player.get_active_pokemon()
        return {
            "moves": [(i, m) for i, m in enumerate(pokemon.moves) if m.current_pp > 0],
            "switches": [(i, p) for i, p in self.player.get_available_pokemon()
                        if i != self.player.active_pokemon_index]
        }

    def player_must_switch(self) -> bool:
        """Check if the player must switch Pokemon."""
        pokemon = self.player.get_active_pokemon()
        return pokemon is not None and pokemon.is_fainted and self.player.has_usable_pokemon()

    def execute_forced_switch(self, pokemon_index: int) -> list[BattleEvent]:
        """Execute a forced switch when the player's Pokemon faints."""
        self.events = []
        self._execute_switch(self.player, pokemon_index)
        return self.events

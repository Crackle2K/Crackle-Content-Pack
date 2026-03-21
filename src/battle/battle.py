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

        # Check for fainted Pokemon and handle switches
        self._handle_fainting()

        return self.events

    def _determine_order(self, pokemon1: Pokemon, move1: Move, pokemon2: Pokemon, move2: Move) -> bool:
        """Determine if pokemon1 goes first."""
        # Check priority
        priority1 = move1.priority if hasattr(move1, 'priority') else 0
        priority2 = move2.priority if hasattr(move2, 'priority') else 0

        if priority1 != priority2:
            return priority1 > priority2

        # Check speed
        if pokemon1.speed != pokemon2.speed:
            return pokemon1.speed > pokemon2.speed

        # Random tiebreaker
        return random.random() < 0.5

    def _execute_switch(self, trainer: Trainer, pokemon_index: int):
        """Execute a Pokemon switch."""
        old_pokemon = trainer.get_active_pokemon()
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

        self._add_event("use_move", f"{attacker_name} used {move.display_name}!")

        # Check accuracy
        if random.randint(1, 100) > move.accuracy:
            self._add_event("miss", f"{attacker_name}'s attack missed!")
            return

        # Calculate and apply damage
        damage, effectiveness, is_critical = attacker.calculate_damage(move, defender)

        if effectiveness == 0:
            self._add_event("no_effect", "It had no effect...")
            return

        actual_damage = defender.take_damage(damage)

        # Report effectiveness
        eff_message = TypeChart.get_effectiveness_message(effectiveness)
        if eff_message:
            self._add_event("effectiveness", eff_message)

        if is_critical:
            self._add_event("critical", "A critical hit!")

        self._add_event("damage", f"{defender_name} took {actual_damage} damage!",
                       damage=actual_damage, defender_hp=defender.current_hp)

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

"""AI for enemy trainers in battle."""

import random
from typing import TYPE_CHECKING

from src.core.type_chart import TypeChart

if TYPE_CHECKING:
    from src.entities.pokemon import Pokemon
    from src.entities.trainer import Trainer


class BattleAI:
    """Simple AI for controlling enemy trainers."""

    def __init__(self):
        """
        Initialize the battle AI.
        """
        pass

    def choose_action(self, trainer: "Trainer", opponent_pokemon: "Pokemon") -> tuple[str, int]:
        """
        Choose an action for the AI trainer.

        Args:
            trainer: The AI-controlled trainer
            opponent_pokemon: The opponent's active Pokemon

        Returns:
            Tuple of (action_type, index) where action_type is "move" or "switch"
        """
        pokemon = trainer.get_active_pokemon()

        # Easy strategy: 25% smart, 75% random
        if random.random() < 0.25:
            return self._choose_smart(trainer, pokemon, opponent_pokemon)
        return self._choose_random(pokemon)

    def _choose_random(self, pokemon: "Pokemon") -> tuple[str, int]:
        """Choose a random move."""
        usable_moves = [i for i, m in enumerate(pokemon.moves) if m.current_pp > 0]
        if not usable_moves:
            return ("move", 0)  # Struggle
        return ("move", random.choice(usable_moves))

    def _choose_smart(self, trainer: "Trainer", pokemon: "Pokemon", opponent: "Pokemon") -> tuple[str, int]:
        """Choose the best move based on effectiveness."""
        best_move_index = 0
        best_score = -1

        for i, move in enumerate(pokemon.moves):
            if move.current_pp <= 0:
                continue

            # Calculate expected damage score
            effectiveness = TypeChart.get_effectiveness(move.type, opponent.types)
            stab = 1.5 if move.type in pokemon.types else 1.0
            score = move.power * effectiveness * stab

            if score > best_score:
                best_score = score
                best_move_index = i

        # Consider switching if current Pokemon is at a type disadvantage
        available = trainer.get_available_pokemon()
        if len(available) > 1 and best_score < 50:
            # Look for a better matchup
            for idx, poke in available:
                if idx == trainer.active_pokemon_index:
                    continue
                # Check if this Pokemon has type advantage
                for poke_type in poke.types:
                    eff = TypeChart.get_effectiveness(poke_type, opponent.types)
                    if eff > 1.0:
                        return ("switch", idx)

        return ("move", best_move_index)

    def choose_switch(self, trainer: "Trainer", opponent_pokemon: "Pokemon") -> int:
        """
        Choose which Pokemon to switch to.

        Args:
            trainer: The AI-controlled trainer
            opponent_pokemon: The opponent's active Pokemon

        Returns:
            Index of Pokemon to switch to
        """
        available = trainer.get_available_pokemon()

        # Find best type matchup (balanced strategy)
        best_idx = available[0][0]
        best_score = 0

        for idx, pokemon in available:
            score = 0
            for poke_type in pokemon.types:
                score += TypeChart.get_effectiveness(poke_type, opponent_pokemon.types)
            if score > best_score:
                best_score = score
                best_idx = idx

        return best_idx

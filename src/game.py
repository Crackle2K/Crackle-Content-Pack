"""Main game class for Pokemon Juno."""

import random
from typing import Optional

from src.entities.pokemon import Pokemon
from src.entities.trainer import Trainer
from src.battle.battle import Battle
from src.ui.pygame_ui import PygameUI
from src.core.pokemon_data import get_available_pokemon_ids


class Game:
    """Main game controller."""

    # Starter Pokemon IDs
    STARTERS = [1, 4, 7, 25]  # Bulbasaur, Charmander, Squirtle, Pikachu

    def __init__(self):
        self.ui = PygameUI()
        self.player: Optional[Trainer] = None
        self.running = True
        self.save_slot: Optional[int] = None

    def run(self):
        """Main game loop."""
        try:
            self.ui.show_message("Welcome to Pokemon Juno!")

            while self.running:
                choice = self.ui.show_main_menu()

                if choice == "new_game":
                    # Show save slot selection
                    slot = self.ui.show_save_slot_selection()
                    if slot is not None:
                        self._new_game(slot)
                elif choice == "exit":
                    self.running = False

            self.ui.show_message("Thanks for playing Pokemon Juno!")
        finally:
            self.ui.quit()

    def _new_game(self, slot: int):
        """Start a new game.
        
        Args:
            slot: Save slot number (1-4)
        """
        self.ui.clear_screen()
        self.save_slot = slot

        # Get player name
        name = self.ui.get_player_name()
        self.player = Trainer(name, is_player=True)

        # Choose starter Pokemon
        self.ui.show_message(f"Welcome, {name}! It's time to choose your first Pokemon!")

        starters = [Pokemon(pid, level=5) for pid in self.STARTERS]
        choice = self.ui.show_pokemon_selection(starters, "Choose your starter Pokemon:")

        starter = starters[choice]
        self.player.add_pokemon(starter)

        self.ui.show_message(f"Excellent choice! You received {starter.name}!")
        self.ui.wait_for_input()

        # Save game
        self._save_game()

        # Start with a rival battle
        self._rival_battle()

    def _rival_battle(self):
        """Battle against the rival."""
        # Rival gets a Pokemon strong against player's choice
        player_pokemon = self.player.get_active_pokemon()
        rival_starters = {
            1: 4,   # Bulbasaur -> Charmander
            4: 7,   # Charmander -> Squirtle
            7: 25,  # Squirtle -> Pikachu (Electric)
            25: 1,  # Pikachu -> Bulbasaur (Ground type counter)
        }

        rival = Trainer("Rival Blue", is_player=False)
        rival_pokemon_id = rival_starters.get(player_pokemon.id, 4)
        rival.add_pokemon(Pokemon(rival_pokemon_id, level=5))

        self.ui.clear_screen()
        self.ui.show_message("Your rival Blue appears!")
        self.ui.show_message(f'"I\'ll show you how it\'s done, {self.player.name}!"')
        self.ui.wait_for_input()

        self._run_battle(rival, "normal")

    def _save_game(self):
        """Save the current game state."""
        import json
        from pathlib import Path
        
        if not hasattr(self, 'save_slot') or self.player is None:
            return
        
        save_folder = Path("saves")
        save_folder.mkdir(exist_ok=True)
        
        save_data = {
            'player_name': self.player.name,
            'pokemon_count': len(self.player.team),
            'pokemon_ids': [p.id for p in self.player.team],
            'pokemon_levels': [p.level for p in self.player.team]
        }
        
        save_file = save_folder / f"save_{self.save_slot}.json"
        with open(save_file, 'w') as f:
            json.dump(save_data, f, indent=2)

    def _run_battle(self, opponent: Trainer, difficulty: str = "normal"):
        """Run a battle against an opponent."""
        battle = Battle(self.player, opponent, difficulty)

        # Initialize battle screen
        self.ui.start_battle(battle)

        self.ui.clear_screen()
        events = battle.start()
        self.ui.show_battle_events(events)

        while not battle.is_over:
            self.ui.show_battle_status(self.player, opponent)

            # Check if player must switch
            if battle.player_must_switch():
                switch_idx = self.ui.show_forced_switch(self.player)
                events = battle.execute_forced_switch(switch_idx)
                self.ui.show_battle_events(events)
                continue

            # Get player action
            action, index = self.ui.show_battle_menu(battle)

            if action == "back":
                continue

            if action == "run":
                self.ui.show_message("Can't escape from a trainer battle!")
                continue

            # Execute turn
            self.ui.clear_screen()
            events = battle.execute_turn(action, index)
            self.ui.show_battle_events(events)

        self.ui.show_battle_result(battle)
        self.ui.wait_for_input()


def main():
    """Entry point for the game."""
    game = Game()
    game.run()


if __name__ == "__main__":
    main()

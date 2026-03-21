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

    # Default starters — Pikachu (25) is unlocked only via Konami code
    STARTERS = [1, 4, 7]            # Bulbasaur, Charmander, Squirtle
    SECRET_STARTER_ID = 25          # Pikachu

    STARTING_MONEY = 500

    def __init__(self):
        self.ui = PygameUI()
        self.player: Optional[Trainer] = None
        self.running = True
        self.save_slot: Optional[int] = None
        self.battles_won = 0

    def run(self):
        """Main game loop."""
        try:
            self.ui.show_message("Welcome to Pokemon Juno!")

            while self.running:
                choice = self.ui.show_main_menu()

                if choice == "new_game":
                    slot = self.ui.show_save_slot_selection()
                    if slot is not None:
                        self._new_game(slot)
                elif choice == "exit":
                    self.running = False

            self.ui.show_message("Thanks for playing Pokemon Juno!")
        finally:
            self.ui.quit()

    def _new_game(self, slot: int):
        """Start a new game."""
        self.ui.clear_screen()
        self.save_slot = slot
        self.battles_won = 0

        name = self.ui.get_player_name()
        self.player = Trainer(name, is_player=True)
        self.player.money = self.STARTING_MONEY

        self.ui.show_message(f"Welcome, {name}! Choose your first Pokemon!")

        starter = self._choose_starter()
        self.player.add_pokemon(starter)

        self.ui.show_message(f"Excellent choice! You received {starter.name}!")
        self.ui.wait_for_input()

        self._save_game()
        self._rival_battle()

    def _choose_starter(self) -> Pokemon:
        """Show starter selection, handling the Konami code unlock."""
        starter_ids = list(self.STARTERS)
        starters = [Pokemon(pid, level=5) for pid in starter_ids]

        while True:
            result = self.ui.show_pokemon_selection(starters, "Choose your starter Pokemon:")

            if result == "konami":
                # Unlock Pikachu
                if self.SECRET_STARTER_ID not in starter_ids:
                    starter_ids.append(self.SECRET_STARTER_ID)
                    starters = [Pokemon(pid, level=5) for pid in starter_ids]
                self.ui.show_message("★ A secret Pokemon has appeared!")
                self.ui.wait_for_input()
                continue

            return starters[int(result)]

    def _rival_battle(self):
        """Battle against the rival."""
        rival = Trainer("Rival Blue", is_player=False)
        rival_pokemon_id = random.choice(self.STARTERS)
        rival.add_pokemon(Pokemon(rival_pokemon_id, level=5))

        self.ui.clear_screen()
        self.ui.show_message("Your rival Blue appears!")
        self.ui.show_message(f'"I\'ll show you how it\'s done, {self.player.name}!"')
        self.ui.wait_for_input()

        self._run_battle(rival)
        self._hub_loop()

    def _hub_loop(self):
        """Main gameplay loop via the 4-quadrant hub."""
        available_ids = get_available_pokemon_ids()

        while self.running:
            self._save_game()
            action = self.ui.show_hub_menu(self.player, self.battles_won)

            if action == "battle":
                self._do_encounter(available_ids)

            elif action == "shop":
                self.ui.show_shop(self.player)

            elif action == "inventory":
                self.ui.show_inventory(self.player)

            elif action == "settings":
                result = self._settings_menu()
                if result == "quit":
                    self.running = False
                    break

    def _do_encounter(self, available_ids: list):
        """Generate and run a random trainer encounter."""
        self.battles_won += 1

        trainer_names = [
            "Youngster", "Lass", "Bug Catcher", "Swimmer",
            "Hiker", "Camper", "Picnicker", "Beauty",
            "Gentleman", "School Kid", "Ace Trainer",
        ]
        opponent_name = random.choice(trainer_names)
        opponent = Trainer(f"{opponent_name} #{self.battles_won}", is_player=False)

        base_level = self.player.get_active_pokemon().level
        level_range = max(1, self.battles_won // 2)
        num_pokemon = min(3, 1 + self.battles_won // 3)

        for _ in range(num_pokemon):
            random_id = random.choice(available_ids)
            level = random.randint(
                max(5, base_level - level_range),
                min(100, base_level + level_range)
            )
            opponent.add_pokemon(Pokemon(random_id, level=level))

        self.ui.clear_screen()
        self.ui.show_message(f"{opponent.name} wants to battle!")
        self.ui.show_message(f"Battle #{self.battles_won}")
        self.ui.wait_for_input()

        won = self._run_battle(opponent)

        if not won:
            # Lose half money as penalty, then return to hub
            penalty = self.player.money // 2
            self.player.money -= penalty
            self.ui.show_message("You were defeated!")
            if penalty:
                self.ui.show_message(f"You lost ${penalty}...")
            self.ui.wait_for_input()
            # Heal team so the game isn't unwinnable
            self.player.heal_team()

    def _settings_menu(self) -> str:
        """Simple settings: save or quit."""
        self._save_game()
        self.ui.show_message("Game saved!")
        self.ui.show_message("Return to hub? (Press any key) or close the window to quit.")
        self.ui.wait_for_input()
        return "continue"

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
            'pokemon_levels': [p.level for p in self.player.team],
            'battles_won': self.battles_won,
            'money': self.player.money,
            'items': self.player.items,
        }

        save_file = save_folder / f"save_{self.save_slot}.json"
        with open(save_file, 'w') as f:
            json.dump(save_data, f, indent=2)

    def _run_battle(self, opponent: Trainer) -> bool:
        """Run a battle. Returns True if the player won."""
        battle = Battle(self.player, opponent)

        self.ui.start_battle(battle)
        self.ui.clear_screen()
        events = battle.start()
        self.ui.show_battle_events(events)

        while not battle.is_over:
            self.ui.show_battle_status(self.player, opponent)

            if battle.player_must_switch():
                switch_idx = self.ui.show_forced_switch(self.player)
                events = battle.execute_forced_switch(switch_idx)
                self.ui.show_battle_events(events)
                continue

            action, index = self.ui.show_battle_menu(battle)

            if action == "back":
                continue

            if action == "run":
                self.ui.show_message("Can't escape from a trainer battle!")
                continue

            self.ui.clear_screen()
            events = battle.execute_turn(action, index)
            self.ui.show_battle_events(events)

        self.ui.show_battle_result(battle)
        self.ui.wait_for_input()

        player_won = battle.winner == self.player

        if player_won:
            self._grant_battle_rewards(battle, opponent)

        return player_won

    def _grant_battle_rewards(self, battle: Battle, opponent: Trainer):
        """Grant XP (only to Pokemon that fought) and money after winning."""
        # --- XP ---
        total_xp = sum(p.level * 50 for p in opponent.team)
        battlers = list(battle.player_battlers) if battle.player_battlers else self.player.team

        xp_each = total_xp // max(1, len(battlers))

        level_ups = []
        for pokemon in battlers:
            leveled = pokemon.gain_exp(xp_each)
            if leveled:
                level_ups.append(pokemon)

        self.ui.show_message(
            f"Victory! {', '.join(p.get_display_name() for p in battlers)} "
            f"gained {xp_each} EXP!"
        )

        for pokemon in level_ups:
            self.ui.show_message(f"{pokemon.get_display_name()} grew to Lv. {pokemon.level}!")
            self.ui.wait_for_input()

        # --- Money ---
        prize = sum(p.level * 30 for p in opponent.team) + 50
        self.player.add_money(prize)
        self.ui.show_message(f"You received ${prize}!")

        # Heal all Pokemon
        self.player.heal_team()
        self.ui.show_message("Your Pokemon have been healed!")
        self.ui.wait_for_input()


def main():
    """Entry point for the game."""
    game = Game()
    game.run()


if __name__ == "__main__":
    main()

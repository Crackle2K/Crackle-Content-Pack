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
        self.battles_won = 0

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
        # Rival gets a random Pokemon from starters
        rival = Trainer("Rival Blue", is_player=False)
        rival_pokemon_id = random.choice(self.STARTERS)
        rival.add_pokemon(Pokemon(rival_pokemon_id, level=5))

        self.ui.clear_screen()
        self.ui.show_message("Your rival Blue appears!")
        self.ui.show_message(f'"I\'ll show you how it\'s done, {self.player.name}!"')
        self.ui.wait_for_input()

        self._run_battle(rival)
        
        # Start continuous battle loop
        self._start_battle_loop()

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
            'battles_won': self.battles_won
        }
        
        save_file = save_folder / f"save_{self.save_slot}.json"
        with open(save_file, 'w') as f:
            json.dump(save_data, f, indent=2)

    def _run_battle(self, opponent: Trainer) -> bool:
        """Run a battle against an opponent.
        
        Returns:
            True if player won, False if player lost
        """
        battle = Battle(self.player, opponent)

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
        
        # Check if player won
        player_won = battle.winner == self.player
        
        if player_won:
            # Grant XP and heal all Pokemon
            self._grant_battle_rewards(opponent)
        
        return player_won
    
    def _grant_battle_rewards(self, opponent: Trainer):
        """Grant XP and heal Pokemon after winning a battle."""
        # Calculate XP based on opponent's team
        total_xp = sum(p.level * 50 for p in opponent.team)
        xp_per_pokemon = total_xp // len(self.player.team)
        
        self.ui.show_message(f"Victory! Your Pokemon gained {xp_per_pokemon} XP each!")
        
        # Grant XP to all player Pokemon
        for pokemon in self.player.team:
            # Simple level up system
            pokemon.level += max(1, xp_per_pokemon // 100)
            if pokemon.level > 100:
                pokemon.level = 100
            
            # Recalculate stats
            pokemon.max_hp = pokemon._calculate_hp()
            pokemon.attack = pokemon._calculate_stat("attack")
            pokemon.defense = pokemon._calculate_stat("defense")
            pokemon.sp_attack = pokemon._calculate_stat("sp_attack")
            pokemon.sp_defense = pokemon._calculate_stat("sp_defense")
            pokemon.speed = pokemon._calculate_stat("speed")
        
        # Heal all Pokemon to full HP
        self.player.heal_team()
        self.ui.show_message("Your Pokemon have been healed to full health!")
        self.ui.wait_for_input()
    
    def _start_battle_loop(self):
        """Start the continuous battle loop."""
        available_ids = get_available_pokemon_ids()
        
        while self.running:
            self.battles_won += 1
            
            # Create a random opponent
            opponent_name = random.choice([
                "Youngster", "Lass", "Bug Catcher", "Swimmer",
                "Hiker", "Camper", "Picnicker", "Beauty",
                "Gentleman", "School Kid", "Ace Trainer"
            ])
            opponent = Trainer(f"{opponent_name} #{self.battles_won}", is_player=False)
            
            # Calculate opponent level based on battles won
            base_level = self.player.get_active_pokemon().level
            level_range = max(1, self.battles_won // 2)
            
            # Give opponent 1-3 random Pokemon
            num_pokemon = min(3, 1 + self.battles_won // 3)
            for _ in range(num_pokemon):
                random_id = random.choice(available_ids)
                level = random.randint(base_level - level_range, base_level + level_range)
                level = max(5, min(100, level))
                opponent.add_pokemon(Pokemon(random_id, level=level))
            
            # Save game before battle
            self._save_game()
            
            # Show opponent
            self.ui.clear_screen()
            self.ui.show_message(f"{opponent.name} wants to battle!")
            self.ui.show_message(f"Battle #{self.battles_won}")
            self.ui.wait_for_input()
            
            # Run the battle
            won = self._run_battle(opponent)
            
            if not won:
                self.ui.show_message("You were defeated!")
                self.ui.show_message("Game Over!")
                self.ui.wait_for_input()
                self.running = False
                break


def main():
    """Entry point for the game."""
    game = Game()
    game.run()


if __name__ == "__main__":
    main()

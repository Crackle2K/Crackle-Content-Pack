"""Pygame-based UI for the Pokemon game."""

import pygame
from typing import List, Tuple, Optional

from src.ui import config
from src.ui.asset_manager import AssetManager
from src.ui.screens.menu_screen import MenuScreen
from src.ui.screens.selection_screen import SelectionScreen, NameInputScreen
from src.ui.screens.battle_screen import BattleScreen
from src.ui.screens.save_slot_screen import SaveSlotScreen
from src.ui.screens.hub_screen import HubScreen
from src.ui.screens.shop_screen import ShopScreen
from src.ui.screens.inventory_screen import InventoryScreen
from src.ui.screens.pokemon_center_screen import PokemonCenterScreen
from src.entities.pokemon import Pokemon
from src.entities.trainer import Trainer
from src.battle.battle import Battle, BattleEvent


class PygameUI:
    """Pygame-based user interface for the game."""

    def __init__(self):
        """Initialize the Pygame UI."""
        pygame.init()
        pygame.display.set_caption(config.TITLE)

        self.display = pygame.display.set_mode((config.SCREEN_WIDTH, config.SCREEN_HEIGHT))
        self.clock = pygame.time.Clock()
        self.assets = AssetManager()

        # Fonts
        self.font_large = self.assets.get_font(config.FONT_SIZE_LARGE)
        self.font_medium = self.assets.get_font(config.FONT_SIZE_MEDIUM)
        self.font_small = self.assets.get_font(config.FONT_SIZE_SMALL)

        # Current battle screen (for reuse during battle)
        self.battle_screen: Optional[BattleScreen] = None

    def clear_screen(self):
        """Clear the screen."""
        self.display.fill(config.COLOR_BG)
        pygame.display.flip()

    def print_title(self):
        """Display the game title (no-op for Pygame, handled by menu)."""
        pass

    def show_main_menu(self) -> str:
        """
        Show the main menu and get selection.

        Returns:
            "new_game" or "exit"
        """
        screen = MenuScreen(self.display, self.assets)
        result = screen.run()
        return result if result else "exit"

    def show_save_slot_selection(self) -> Optional[int]:
        """
        Show save slot selection screen.

        Returns:
            Selected slot number (1-4), or None if cancelled
        """
        screen = SaveSlotScreen(self.display, self.assets)
        result = screen.run()
        return result

    def get_player_name(self) -> str:
        """
        Get the player's name.

        Returns:
            The entered name
        """
        screen = NameInputScreen(self.display, self.assets)
        result = screen.run()
        return result if result else "Trainer"

    def show_pokemon_selection(self, pokemon_list: List[Pokemon], title: str = "Choose your Pokemon:"):
        """
        Show Pokemon selection menu.

        Args:
            pokemon_list: List of Pokemon to choose from
            title: Title to display

        Returns:
            Index of selected Pokemon, or "konami" if Konami code was entered
        """
        screen = SelectionScreen(self.display, self.assets, pokemon_list, title)
        result = screen.run()
        if result == "konami":
            return "konami"
        return result if result is not None else 0

    def show_hub_menu(self, player: Trainer, battles_won: int) -> str:
        """Show the 4-quadrant hub screen. Returns the chosen action token."""
        screen = HubScreen(self.display, self.assets, player, battles_won)
        result = screen.run()
        return result if result else "settings"

    def show_shop(self, player: Trainer):
        """Show the Poke Mart shop screen."""
        screen = ShopScreen(self.display, self.assets, player)
        screen.run()

    def show_inventory(self, player: Trainer):
        """Show the item bag / inventory screen."""
        screen = InventoryScreen(self.display, self.assets, player)
        screen.run()

    def show_pokemon_center(self, player: Trainer):
        """Show the Pokemon Center healing screen."""
        screen = PokemonCenterScreen(self.display, self.assets, player)
        screen.run()

    def show_battle_status(self, player: Trainer, opponent: Trainer):
        """
        Display the current battle status.

        This is called by game.py but in Pygame the battle screen handles this.
        We just need to ensure the battle screen exists and is updated.
        """
        # Battle status is rendered by the battle screen
        pass

    def show_battle_menu(self, battle: Battle) -> Tuple[str, int]:
        """
        Show battle options and get player choice.

        Args:
            battle: The current battle

        Returns:
            Tuple of (action_type, index)
        """
        if self.battle_screen is None:
            self.battle_screen = BattleScreen(self.display, self.assets, battle)

        result = self.battle_screen.get_action()

        if result is None:
            # Window was closed
            return ("run", 0)

        return result

    def show_forced_switch(self, player: Trainer) -> int:
        """
        Show forced switch menu when active Pokemon faints.

        Args:
            player: The player's trainer

        Returns:
            Index of Pokemon to switch to
        """
        if self.battle_screen is not None:
            result = self.battle_screen.get_forced_switch()
            if result is not None:
                return result

        # Fallback: return first available
        available = player.get_available_pokemon()
        if available:
            return available[0][0]
        return 0

    def show_battle_events(self, events: List[BattleEvent]):
        """
        Display battle events with pauses.

        Args:
            events: List of battle events to display
        """
        if self.battle_screen is None:
            return

        self.battle_screen.show_events(events)

        # Run the event display loop
        running = True
        while running and self.battle_screen.event_queue or self.battle_screen.current_event:
            dt = self.clock.tick(config.FPS) / 1000.0

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                else:
                    self.battle_screen.handle_event(event)

            self.battle_screen.update(dt)
            self.battle_screen.render()
            pygame.display.flip()

    def show_battle_result(self, battle: Battle):
        """
        Show the battle result.

        Args:
            battle: The completed battle
        """
        if self.battle_screen is None:
            return

        # Set result state
        if battle.winner == battle.player:
            message = f"{battle.player.name} won the battle!"
        else:
            message = f"{battle.player.name} was defeated!"

        self.battle_screen.message_box.set_message(message)
        self.battle_screen.state = BattleScreen.STATE_RESULT

        # Run until user dismisses
        running = True
        while running:
            dt = self.clock.tick(config.FPS) / 1000.0

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif self.battle_screen.handle_event(event) == "done":
                    running = False

            self.battle_screen.update(dt)
            self.battle_screen.render()
            pygame.display.flip()

        # Clear battle screen for next battle
        self.battle_screen = None

    def show_message(self, message: str):
        """
        Show a simple message.

        Args:
            message: The message to display
        """
        self.display.fill(config.COLOR_BG)

        # Render message centered
        font = self.font_medium
        text_surface = font.render(message, True, config.COLOR_BLACK)
        text_rect = text_surface.get_rect(center=(config.SCREEN_WIDTH // 2, config.SCREEN_HEIGHT // 2))
        self.display.blit(text_surface, text_rect)

        pygame.display.flip()
        pygame.time.wait(500)  # Brief pause

    def wait_for_input(self, prompt: str = "Press any key to continue..."):
        """
        Wait for user input.

        Args:
            prompt: The prompt to display
        """
        self.display.fill(config.COLOR_BG)

        # Render prompt centered
        font = self.font_medium
        text_surface = font.render(prompt, True, config.COLOR_BLACK)
        text_rect = text_surface.get_rect(center=(config.SCREEN_WIDTH // 2, config.SCREEN_HEIGHT // 2))
        self.display.blit(text_surface, text_rect)

        pygame.display.flip()

        # Wait for key press or click
        waiting = True
        while waiting:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    waiting = False
                elif event.type == pygame.KEYDOWN or event.type == pygame.MOUSEBUTTONDOWN:
                    waiting = False

    def start_battle(self, battle: Battle):
        """
        Initialize a new battle screen.

        Args:
            battle: The battle to start
        """
        self.battle_screen = BattleScreen(self.display, self.assets, battle)

    def quit(self):
        """Clean up and quit Pygame."""
        pygame.quit()

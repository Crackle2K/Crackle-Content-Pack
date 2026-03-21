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
from src.ui.screens.settings_screen import SettingsScreen
from src.entities.pokemon import Pokemon
from src.entities.trainer import Trainer
from src.battle.battle import Battle, BattleEvent


class PygameUI:
    """Pygame-based user interface for the game."""

    def __init__(self):
        pygame.init()
        pygame.display.set_caption(config.TITLE)
        self.display = pygame.display.set_mode((config.SCREEN_WIDTH, config.SCREEN_HEIGHT))
        self.clock   = pygame.time.Clock()
        self.assets  = AssetManager()

        self.font_large  = self.assets.get_font(config.FONT_SIZE_LARGE)
        self.font_medium = self.assets.get_font(config.FONT_SIZE_MEDIUM)
        self.font_small  = self.assets.get_font(config.FONT_SIZE_SMALL)

        self.battle_screen: Optional[BattleScreen] = None

        # Set to True when the window X is clicked or Save & Quit is chosen
        self.quit_requested = False

    # ── Internal helpers ──────────────────────────────────────────────────────

    def _pump(self) -> bool:
        """Process pending events, set quit_requested if window closed. Returns True if quit."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.quit_requested = True
                return True
        return False

    def clear_screen(self):
        self.display.fill(config.COLOR_BG)
        pygame.display.flip()

    def print_title(self):
        pass

    # ── Screen wrappers ───────────────────────────────────────────────────────

    def show_main_menu(self) -> str:
        screen = MenuScreen(self.display, self.assets)
        result = screen.run()
        if result is None:
            self.quit_requested = True
            return "exit"
        return result if result else "exit"

    def show_save_slot_selection(self) -> Optional[int]:
        screen = SaveSlotScreen(self.display, self.assets)
        result = screen.run()
        if result is None:
            self.quit_requested = True
        return result

    def get_player_name(self) -> str:
        screen = NameInputScreen(self.display, self.assets)
        result = screen.run()
        if result is None:
            self.quit_requested = True
        return result if result else "Trainer"

    def show_pokemon_selection(self, pokemon_list: List[Pokemon],
                               title: str = "Choose your Pokemon:"):
        screen = SelectionScreen(self.display, self.assets, pokemon_list, title)
        result = screen.run()
        if result is None:
            self.quit_requested = True
            return 0
        if result == "konami":
            return "konami"
        return result if result is not None else 0

    def show_hub_menu(self, player: Trainer, battles_won: int) -> str:
        screen = HubScreen(self.display, self.assets, player, battles_won)
        result = screen.run()
        if result is None:
            self.quit_requested = True
            return "settings"
        return result if result else "settings"

    def show_shop(self, player: Trainer):
        screen = ShopScreen(self.display, self.assets, player)
        result = screen.run()
        if result is None:
            self.quit_requested = True

    def show_inventory(self, player: Trainer):
        screen = InventoryScreen(self.display, self.assets, player)
        result = screen.run()
        if result is None:
            self.quit_requested = True

    def show_pokemon_center(self, player: Trainer):
        screen = PokemonCenterScreen(self.display, self.assets, player)
        result = screen.run()
        if result is None:
            self.quit_requested = True

    def show_settings(self, player: Trainer, battles_won: int) -> str:
        """Show the settings screen. Returns 'return' or 'quit'."""
        screen = SettingsScreen(self.display, self.assets,
                                player.name, battles_won, player.money)
        result = screen.run()
        if result is None:
            self.quit_requested = True
            return "quit"
        return result if result else "return"

    # ── Battle ────────────────────────────────────────────────────────────────

    def show_battle_status(self, player: Trainer, opponent: Trainer):
        pass

    def show_battle_menu(self, battle: Battle) -> Tuple[str, object]:
        if self.battle_screen is None:
            self.battle_screen = BattleScreen(self.display, self.assets, battle)

        result = self.battle_screen.get_action()
        if result is None:
            self.quit_requested = True
            return ("run", 0)
        if result[0] == "quit":
            self.quit_requested = True
            return ("run", 0)
        return result

    def show_forced_switch(self, player: Trainer) -> int:
        if self.battle_screen is not None:
            result = self.battle_screen.get_forced_switch()
            if result is not None:
                return result
        available = player.get_available_pokemon()
        if available:
            return available[0][0]
        return 0

    def show_battle_events(self, events: List[BattleEvent]):
        if self.battle_screen is None:
            return

        self.battle_screen.show_events(events)

        running = True
        while running and (self.battle_screen.event_queue or self.battle_screen.current_event):
            dt = self.clock.tick(config.FPS) / 1000.0

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.quit_requested = True
                    return
                self.battle_screen.handle_event(event)

            self.battle_screen.update(dt)
            self.battle_screen.render()
            pygame.display.flip()

    def show_battle_result(self, battle: Battle):
        if self.battle_screen is None:
            return

        if battle.winner == battle.player:
            message = f"{battle.player.name} won the battle!"
        else:
            message = f"{battle.player.name} was defeated!"

        self.battle_screen.message_box.set_message(message)
        self.battle_screen.state = BattleScreen.STATE_RESULT

        running = True
        while running:
            dt = self.clock.tick(config.FPS) / 1000.0

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.quit_requested = True
                    return
                if self.battle_screen.handle_event(event) == "done":
                    running = False

            self.battle_screen.update(dt)
            self.battle_screen.render()
            pygame.display.flip()

        self.battle_screen = None

    def start_battle(self, battle: Battle):
        self.battle_screen = BattleScreen(self.display, self.assets, battle)

    # ── Simple message / prompt ───────────────────────────────────────────────

    def show_message(self, message: str):
        self.display.fill(config.COLOR_BG)
        font = self.font_medium
        ts   = font.render(message, True, config.COLOR_BLACK)
        self.display.blit(ts, ts.get_rect(center=(config.SCREEN_WIDTH // 2,
                                                   config.SCREEN_HEIGHT // 2)))
        pygame.display.flip()

        # Brief pause while still processing QUIT events
        elapsed = 0
        while elapsed < 500:
            self.clock.tick(60)
            elapsed += 1000 // 60
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.quit_requested = True
                    return

    def wait_for_input(self, prompt: str = "Press any key to continue..."):
        self.display.fill(config.COLOR_BG)
        font = self.font_medium
        ts   = font.render(prompt, True, config.COLOR_BLACK)
        self.display.blit(ts, ts.get_rect(center=(config.SCREEN_WIDTH // 2,
                                                   config.SCREEN_HEIGHT // 2)))
        pygame.display.flip()

        waiting = True
        while waiting:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.quit_requested = True
                    return
                if event.type in (pygame.KEYDOWN, pygame.MOUSEBUTTONDOWN):
                    waiting = False
            self.clock.tick(60)

    def quit(self):
        pygame.quit()

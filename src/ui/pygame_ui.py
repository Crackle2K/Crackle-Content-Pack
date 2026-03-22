"""Pygame-based UI for the Pokemon game."""

import math
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
from src.ui.screens.pokemon_party_screen import PokemonPartyScreen
from src.ui.screens.storage_screen import StorageScreen
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

    def show_pokemon_party(self, player: Trainer):
        screen = PokemonPartyScreen(self.display, self.assets, player)
        result = screen.run()
        if result is None:
            self.quit_requested = True

    def show_storage(self, player: Trainer):
        screen = StorageScreen(self.display, self.assets, player)
        result = screen.run()
        if result is None:
            self.quit_requested = True

    def show_evolution_cutscene(self, old_name: str, new_name: str,
                                old_id: int, old_species: str,
                                new_id: int, new_species: str):
        """Play a flash-and-transform evolution animation."""
        clock  = pygame.time.Clock()
        W, H   = self.display.get_width(), self.display.get_height()
        cx, cy = W // 2, H // 2 - 60

        old_sprite = self.assets.get_sprite(old_id, old_species, scale=4.0)
        new_sprite = self.assets.get_sprite(new_id, new_species, scale=4.0)

        font_lrg = self.font_large
        font_med = self.font_medium
        font_sml = self.font_small

        def _blit_sprite(surf, cx, cy):
            if surf:
                self.display.blit(surf, (cx - surf.get_width() // 2,
                                         cy - surf.get_height() // 2))

        def _draw_base(star_t: float):
            self.display.fill((10, 12, 30))
            for sx, sy, sz, phase in _stars:
                b = int(130 + 90 * math.sin(star_t * 1.5 + phase))
                pygame.draw.circle(self.display, (b, b, min(b + 30, 255)), (sx, sy), sz)

        # Stable star field
        import random as _rnd
        rng = _rnd.Random(42)
        _stars = [(rng.randint(0, W), rng.randint(0, H),
                   rng.randint(1, 2), rng.uniform(0, math.pi * 2)) for _ in range(50)]

        # ── Phase 1: announce (1.2 s) ──────────────────────────────────────
        t = 0.0
        while t < 1.2 and not self.quit_requested:
            dt = clock.tick(60) / 1000.0
            for ev in pygame.event.get():
                if ev.type == pygame.QUIT:
                    self.quit_requested = True
            t += dt
            _draw_base(t)
            _blit_sprite(old_sprite, cx, cy)
            msg = font_med.render(f"What? {old_name} is evolving!", True, (255, 245, 180))
            self.display.blit(msg, (W // 2 - msg.get_width() // 2, cy + 130))
            pygame.display.flip()

        # ── Phase 2: flash animation (2.6 s) ──────────────────────────────
        t = 0.0
        flash_t = 0.0
        flash_interval = 0.18
        show_new = False
        while t < 2.6 and not self.quit_requested:
            dt = clock.tick(60) / 1000.0
            for ev in pygame.event.get():
                if ev.type == pygame.QUIT:
                    self.quit_requested = True
            t += dt
            flash_t -= dt
            if flash_t <= 0:
                show_new = not show_new
                flash_t = max(0.04, flash_interval * (1.0 - t / 3.0))

            _draw_base(t + 1.2)

            # Silhouette of current sprite
            sprite = new_sprite if show_new else old_sprite
            if sprite:
                sil = sprite.copy()
                sil.fill((255, 255, 255), special_flags=pygame.BLEND_RGB_MAX)
                self.display.blit(sil, (cx - sil.get_width() // 2,
                                         cy - sil.get_height() // 2))

            # White flash overlay (fades as animation progresses)
            alpha = int(200 * abs(math.sin(t * 9)) * max(0, 1 - t / 2.6))
            if alpha > 0:
                flash_surf = pygame.Surface((W, H), pygame.SRCALPHA)
                flash_surf.fill((255, 255, 255, alpha))
                self.display.blit(flash_surf, (0, 0))

            msg = font_med.render(f"{old_name} is evolving!", True, (255, 245, 180))
            self.display.blit(msg, (W // 2 - msg.get_width() // 2, cy + 130))
            pygame.display.flip()

        # ── Phase 3: reveal result (wait for input) ────────────────────────
        waiting = True
        blink_t = 0.0
        while waiting and not self.quit_requested:
            dt = clock.tick(60) / 1000.0
            blink_t += dt
            for ev in pygame.event.get():
                if ev.type == pygame.QUIT:
                    self.quit_requested = True
                    waiting = False
                elif ev.type in (pygame.MOUSEBUTTONDOWN, pygame.KEYDOWN):
                    waiting = False

            _draw_base(blink_t + 3.8)
            _blit_sprite(new_sprite, cx, cy)

            title = font_lrg.render(f"{old_name} evolved into {new_name}!",
                                    True, (255, 220, 50))
            self.display.blit(title, (W // 2 - title.get_width() // 2, cy + 120))

            if int(blink_t * 2) % 2 == 0:
                hint = font_sml.render("Press any key to continue", True, (180, 190, 220))
                self.display.blit(hint, (W // 2 - hint.get_width() // 2, cy + 160))
            pygame.display.flip()

    def show_settings(self, player: Trainer, battles_won: int) -> str:
        """Show the settings screen. Returns 'return' or 'quit'."""
        screen = SettingsScreen(self.display, self.assets,
                                player.name, battles_won, player.money)
        result = screen.run()
        if result is None:
            self.quit_requested = True
            return "quit"
        return result if result else "return"  # "return", "main_menu", or "quit"

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

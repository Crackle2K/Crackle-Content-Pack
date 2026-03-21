"""Settings screen — Save & Return or Save & Quit."""

from __future__ import annotations
import pygame
from typing import Any, Optional

from src.ui import config
from src.ui.screens.base_screen import BaseScreen
from src.ui.components.button import Button
from src.ui.asset_manager import AssetManager


_HEADER_H = 75


class SettingsScreen(BaseScreen):
    """Simple settings screen with Save+Return and Save+Quit options."""

    def __init__(self, display: pygame.Surface, assets: AssetManager,
                 player_name: str, battles_won: int, money: int):
        super().__init__(display, assets)
        self.player_name = player_name
        self.battles_won = battles_won
        self.money       = money

        cx   = config.SCREEN_WIDTH  // 2
        mid  = config.SCREEN_HEIGHT // 2

        self.return_button = Button(cx - 170, mid - 10, 160, 50,
                                    "Save & Return",
                                    font=self.font_medium,
                                    color=config.COLOR_PRIMARY)
        self.quit_button   = Button(cx + 10,  mid - 10, 160, 50,
                                    "Save & Quit",
                                    font=self.font_medium,
                                    color=config.COLOR_ACCENT)
        self.save_label = ""
        self.save_timer = 0.0

    # ── Events ────────────────────────────────────────────────────────────────

    def handle_event(self, event: pygame.event.Event) -> Optional[Any]:
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            return "return"
        if self.return_button.handle_event(event):
            return "return"
        if self.quit_button.handle_event(event):
            return "quit"
        return None

    # ── Update ────────────────────────────────────────────────────────────────

    def update(self, dt: float):
        pos = pygame.mouse.get_pos()
        self.return_button.update(pos)
        self.quit_button.update(pos)
        if self.save_timer > 0:
            self.save_timer = max(0.0, self.save_timer - dt)

    # ── Render ────────────────────────────────────────────────────────────────

    def render(self):
        self.display.fill(config.COLOR_BG)

        # Header
        pygame.draw.rect(self.display, (55, 55, 72),
                         (0, 0, config.SCREEN_WIDTH, _HEADER_H))
        pygame.draw.rect(self.display, config.COLOR_SECONDARY,
                         (0, _HEADER_H - 3, config.SCREEN_WIDTH, 3))
        title = self.font_large.render("SETTINGS", True, config.COLOR_WHITE)
        self.display.blit(title, title.get_rect(
            centerx=config.SCREEN_WIDTH // 2, centery=36))

        # Player info card
        card_w, card_h = 360, 120
        card_x = (config.SCREEN_WIDTH - card_w) // 2
        card_y = _HEADER_H + 30
        pygame.draw.rect(self.display, config.COLOR_INFO_BOX,
                         (card_x, card_y, card_w, card_h), border_radius=10)
        pygame.draw.rect(self.display, config.COLOR_INFO_BOX_BORDER,
                         (card_x, card_y, card_w, card_h), width=1, border_radius=10)

        lines = [
            ("Trainer",   self.player_name),
            ("Battles",   str(self.battles_won)),
            ("Money",     f"${self.money}"),
        ]
        for i, (lbl, val) in enumerate(lines):
            y = card_y + 14 + i * 30
            ls = self.font_small.render(lbl, True, config.COLOR_GRAY)
            vs = self.font_medium.render(val, True, config.COLOR_BLACK)
            self.display.blit(ls, (card_x + 16, y))
            self.display.blit(vs, (card_x + card_w - vs.get_width() - 16, y))

        # Divider
        mid = config.SCREEN_HEIGHT // 2
        pygame.draw.line(self.display, config.COLOR_INFO_BOX_BORDER,
                         (40, mid - 30), (config.SCREEN_WIDTH - 40, mid - 30), 1)

        # Buttons
        self.return_button.render(self.display, self.font_medium)
        self.quit_button.render(self.display, self.font_medium)

        # ESC hint
        hint = self.font_small.render("ESC to return", True, config.COLOR_GRAY)
        self.display.blit(hint, hint.get_rect(
            centerx=config.SCREEN_WIDTH // 2,
            y=config.SCREEN_HEIGHT - 40))

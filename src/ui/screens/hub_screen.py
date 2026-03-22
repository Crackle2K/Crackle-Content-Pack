"""Hub screen — the main overworld menu with 4 quadrant options + settings footer."""

import math
import random
import pygame
from typing import Any, Optional

from src.ui import config
from src.ui.screens.base_screen import BaseScreen
from src.ui.asset_manager import AssetManager
from src.entities.trainer import Trainer


# (label, sub-label, result token, base color, hover color, icon tag)
_QUADRANTS = [
    ("BATTLE",    "Find opponent",  "battle",         (56,  88, 152),  (76,  108, 180), "sword"),
    ("SHOP",      "Buy items",      "shop",            (180, 140,  30), (210, 165,  45), "bag"),
    ("INVENTORY", "Use items",      "inventory",       (60,  140,  70), (80,  165,  90), "pack"),
    ("CENTER",    "Heal Pokemon",   "pokemon_center",  (170,  55, 100), (200,  75, 125), "cross"),
]

_FOOTER_H = 44  # height of the settings footer strip


class HubScreen(BaseScreen):
    """Main hub with Battle, Shop, Inventory, and Pokemon Center in four quadrants.
    A thin footer strip at the bottom holds the Save/Quit settings action.
    """

    def __init__(self, display: pygame.Surface, assets: AssetManager,
                 player: Trainer, battles_won: int):
        super().__init__(display, assets)
        self.player = player
        self.battles_won = battles_won

        # Stable star field
        rng = random.Random(99)
        self.stars = [
            (rng.randint(0, config.SCREEN_WIDTH),
             rng.randint(80, config.SCREEN_HEIGHT - _FOOTER_H),
             rng.randint(1, 2),
             rng.uniform(0, math.pi * 2))
            for _ in range(60)
        ]
        self.star_time = 0.0

        # Layout
        self._header_h = 80
        content_top = self._header_h
        content_bot = config.SCREEN_HEIGHT - _FOOTER_H
        content_h   = content_bot - content_top
        half_w = config.SCREEN_WIDTH  // 2
        half_h = content_h // 2

        self._quads = [
            pygame.Rect(0,       content_top,          half_w, half_h),
            pygame.Rect(half_w,  content_top,          half_w, half_h),
            pygame.Rect(0,       content_top + half_h, half_w, half_h),
            pygame.Rect(half_w,  content_top + half_h, half_w, half_h),
        ]
        self._footer_rect = pygame.Rect(0, content_bot, config.SCREEN_WIDTH, _FOOTER_H)

        self._hovered: Optional[int] = None   # 0-3 for quads
        self._footer_hovered  = False
        self._team_hovered    = False
        self._storage_hovered = False

        # Split footer: left = My Team, center = Storage, right = Settings
        w3 = config.SCREEN_WIDTH // 3
        self._team_rect     = pygame.Rect(0,      content_bot, w3,                         _FOOTER_H)
        self._storage_rect  = pygame.Rect(w3,     content_bot, w3,                         _FOOTER_H)
        self._footer_rect   = pygame.Rect(2 * w3, content_bot, config.SCREEN_WIDTH - 2 * w3, _FOOTER_H)

    # ------------------------------------------------------------------
    # Event / Update / Render
    # ------------------------------------------------------------------

    def handle_event(self, event: pygame.event.Event) -> Optional[Any]:
        if event.type == pygame.MOUSEMOTION:
            self._hovered          = self._quad_at(event.pos)
            self._footer_hovered   = self._footer_rect.collidepoint(event.pos)
            self._team_hovered     = self._team_rect.collidepoint(event.pos)
            self._storage_hovered  = self._storage_rect.collidepoint(event.pos)

        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self._team_rect.collidepoint(event.pos):
                return "pokemon"
            if self._storage_rect.collidepoint(event.pos):
                return "storage"
            if self._footer_rect.collidepoint(event.pos):
                return "settings"
            idx = self._quad_at(event.pos)
            if idx is not None:
                return _QUADRANTS[idx][2]

        elif event.type == pygame.KEYDOWN:
            key_map = {
                pygame.K_1: 0, pygame.K_KP1: 0,
                pygame.K_2: 1, pygame.K_KP2: 1,
                pygame.K_3: 2, pygame.K_KP3: 2,
                pygame.K_4: 3, pygame.K_KP4: 3,
            }
            if event.key in key_map:
                return _QUADRANTS[key_map[event.key]][2]
            if event.key in (pygame.K_5, pygame.K_KP5, pygame.K_t):
                return "pokemon"
            if event.key in (pygame.K_g, pygame.K_KP6):
                return "storage"
            if event.key == pygame.K_ESCAPE:
                return "settings"

        return None

    def update(self, dt: float):
        self.star_time += dt
        pos = pygame.mouse.get_pos()
        self._hovered          = self._quad_at(pos)
        self._footer_hovered   = self._footer_rect.collidepoint(pos)
        self._team_hovered     = self._team_rect.collidepoint(pos)
        self._storage_hovered  = self._storage_rect.collidepoint(pos)

    def render(self):
        self.display.fill(config.COLOR_MENU_BG)

        # Stars (clip above footer)
        for x, y, size, phase in self.stars:
            b = int(160 + 70 * math.sin(self.star_time * 1.2 + phase))
            pygame.draw.circle(self.display, (b, b, min(b + 20, 255)), (x, y), size)

        # Header bar
        pygame.draw.rect(self.display, config.COLOR_PRIMARY,
                         (0, 0, config.SCREEN_WIDTH, self._header_h))
        pygame.draw.rect(self.display, config.COLOR_SECONDARY,
                         (0, self._header_h - 3, config.SCREEN_WIDTH, 3))

        # Title
        title_surf = self.font_large.render("POKEMON  JUNO", True, config.COLOR_WHITE)
        self.display.blit(title_surf, (20, (self._header_h - title_surf.get_height()) // 2))

        # Player money
        money_surf = self.font_large.render(f"${self.player.money}", True, config.COLOR_SECONDARY)
        self.display.blit(money_surf,
                          (config.SCREEN_WIDTH - money_surf.get_width() - 20,
                           (self._header_h - money_surf.get_height()) // 2))

        # Battles won
        bw_surf = self.font_small.render(f"Battles: {self.battles_won}", True, (180, 200, 230))
        self.display.blit(bw_surf,
                          ((config.SCREEN_WIDTH - bw_surf.get_width()) // 2,
                           (self._header_h - bw_surf.get_height()) // 2))

        # Quadrants
        for i, (rect, quad) in enumerate(zip(self._quads, _QUADRANTS)):
            label, sublabel, _, base_col, hover_col, icon = quad
            is_hov = self._hovered == i
            color = hover_col if is_hov else base_col

            pygame.draw.rect(self.display, color, rect)

            if is_hov:
                hi_surf = pygame.Surface((rect.width, 6), pygame.SRCALPHA)
                hi_surf.fill((255, 255, 255, 30))
                self.display.blit(hi_surf, rect.topleft)

            # Divider lines
            pygame.draw.rect(self.display, config.COLOR_MENU_BG, rect, width=2)

            cx = rect.centerx
            cy = rect.centery - 22
            self._draw_icon(icon, cx, cy, is_hov)

            lbl_surf = self.font_large.render(label, True, config.COLOR_WHITE)
            self.display.blit(lbl_surf,
                              (rect.centerx - lbl_surf.get_width() // 2, cy + 30))

            sub_surf = self.font_small.render(sublabel, True, (200, 215, 230))
            self.display.blit(sub_surf,
                              (rect.centerx - sub_surf.get_width() // 2,
                               cy + 30 + lbl_surf.get_height() + 4))

            hint_surf = self.font_small.render(f"[{i + 1}]", True, (130, 145, 165))
            self.display.blit(hint_surf,
                              (rect.right - hint_surf.get_width() - 8,
                               rect.bottom - hint_surf.get_height() - 6))

        # Footer — left: My Team, center: Storage, right: Settings
        pygame.draw.line(self.display, (90, 90, 115),
                         (0, self._team_rect.top),
                         (config.SCREEN_WIDTH, self._team_rect.top), 1)

        # My Team tile
        team_col = (60, 90, 130) if self._team_hovered else (42, 65, 95)
        pygame.draw.rect(self.display, team_col, self._team_rect)
        pygame.draw.line(self.display, (90, 90, 115),
                         (self._team_rect.right, self._team_rect.top),
                         (self._team_rect.right, self._team_rect.bottom), 1)
        team_cx = self._team_rect.centerx - 30
        team_cy = self._team_rect.centery
        self._draw_icon("pack", team_cx, team_cy, self._team_hovered)
        team_surf = self.font_small.render(
            "MY TEAM  [T]", True,
            (210, 230, 255) if self._team_hovered else (150, 175, 215))
        self.display.blit(team_surf,
                          (team_cx + 22,
                           self._team_rect.centery - team_surf.get_height() // 2))

        # Storage tile
        stor_col = (50, 100, 80) if self._storage_hovered else (35, 72, 58)
        pygame.draw.rect(self.display, stor_col, self._storage_rect)
        pygame.draw.line(self.display, (90, 90, 115),
                         (self._storage_rect.right, self._storage_rect.top),
                         (self._storage_rect.right, self._storage_rect.bottom), 1)
        stor_cx = self._storage_rect.centerx - 35
        stor_cy = self._storage_rect.centery
        self._draw_icon("pack", stor_cx, stor_cy, self._storage_hovered)
        stor_surf = self.font_small.render(
            "PC STORAGE  [G]", True,
            (200, 235, 215) if self._storage_hovered else (140, 180, 160))
        self.display.blit(stor_surf,
                          (stor_cx + 22,
                           self._storage_rect.centery - stor_surf.get_height() // 2))

        # Settings tile
        footer_col = (75, 75, 95) if self._footer_hovered else (55, 55, 72)
        pygame.draw.rect(self.display, footer_col, self._footer_rect)
        gear_cx = self._footer_rect.centerx - 60
        gear_cy = self._footer_rect.centery
        self._draw_icon("gear", gear_cx, gear_cy, self._footer_hovered)
        settings_surf = self.font_small.render(
            "SETTINGS  /  SAVE & QUIT", True,
            (210, 215, 230) if self._footer_hovered else (160, 170, 190))
        self.display.blit(settings_surf,
                          (gear_cx + 22,
                           self._footer_rect.centery - settings_surf.get_height() // 2))

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _quad_at(self, pos) -> Optional[int]:
        for i, rect in enumerate(self._quads):
            if rect.collidepoint(pos):
                return i
        return None

    def _draw_icon(self, tag: str, cx: int, cy: int, bright: bool):
        col = (255, 255, 255) if bright else (200, 215, 230)
        if tag == "sword":
            pygame.draw.line(self.display, col, (cx - 14, cy + 14), (cx + 14, cy - 14), 3)
            pygame.draw.line(self.display, col, (cx - 8, cy - 8), (cx - 14, cy - 2), 2)
            pygame.draw.line(self.display, col, (cx - 8, cy - 8), (cx - 2, cy - 14), 2)
        elif tag == "bag":
            pygame.draw.rect(self.display, col, (cx - 12, cy - 6, 24, 20), width=2, border_radius=3)
            pygame.draw.arc(self.display, col,
                            pygame.Rect(cx - 8, cy - 14, 16, 14), 0, math.pi, 2)
        elif tag == "pack":
            pygame.draw.rect(self.display, col, (cx - 12, cy - 10, 24, 22), width=2, border_radius=4)
            pygame.draw.line(self.display, col, (cx - 5, cy - 10), (cx - 5, cy + 12), 2)
            pygame.draw.line(self.display, col, (cx + 5, cy - 10), (cx + 5, cy + 12), 2)
            pygame.draw.line(self.display, col, (cx - 5, cy), (cx + 5, cy), 2)
        elif tag == "cross":
            # Red cross / healing symbol
            bar_w, bar_h = 6, 18
            pygame.draw.rect(self.display, col,
                             (cx - bar_w // 2, cy - bar_h // 2, bar_w, bar_h),
                             border_radius=2)
            pygame.draw.rect(self.display, col,
                             (cx - bar_h // 2, cy - bar_w // 2, bar_h, bar_w),
                             border_radius=2)
        elif tag == "gear":
            pygame.draw.circle(self.display, col, (cx, cy), 8, 2)
            pygame.draw.circle(self.display, col, (cx, cy), 3, 2)
            for angle in range(0, 360, 45):
                rad = math.radians(angle)
                x1 = int(cx + 8  * math.cos(rad))
                y1 = int(cy + 8  * math.sin(rad))
                x2 = int(cx + 12 * math.cos(rad))
                y2 = int(cy + 12 * math.sin(rad))
                pygame.draw.line(self.display, col, (x1, y1), (x2, y2), 2)

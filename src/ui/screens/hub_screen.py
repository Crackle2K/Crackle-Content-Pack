"""Hub screen — the main overworld menu with 4 quadrant options."""

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
    ("BATTLE",    "Encounter",  "battle",    (56, 88, 152),   (76, 108, 180),  "sword"),
    ("SHOP",      "Buy items",  "shop",      (180, 140, 30),  (210, 165, 45),  "bag"),
    ("INVENTORY", "Use items",  "inventory", (60, 140, 70),   (80, 165, 90),   "pack"),
    ("SETTINGS",  "Save/Quit",  "settings",  (90, 90, 110),   (115, 115, 138), "gear"),
]


class HubScreen(BaseScreen):
    """Main hub with Battle, Shop, Inventory, and Settings in four quadrants."""

    def __init__(self, display: pygame.Surface, assets: AssetManager,
                 player: Trainer, battles_won: int):
        super().__init__(display, assets)
        self.player = player
        self.battles_won = battles_won

        # Stable star field
        rng = random.Random(99)
        self.stars = [
            (rng.randint(0, config.SCREEN_WIDTH),
             rng.randint(80, config.SCREEN_HEIGHT),
             rng.randint(1, 2),
             rng.uniform(0, math.pi * 2))
            for _ in range(60)
        ]
        self.star_time = 0.0

        # Quadrant rects
        self._header_h = 80
        content_w = config.SCREEN_WIDTH // 2
        content_h = (config.SCREEN_HEIGHT - self._header_h) // 2
        self._quads = [
            pygame.Rect(0,          self._header_h,              content_w, content_h),
            pygame.Rect(content_w,  self._header_h,              content_w, content_h),
            pygame.Rect(0,          self._header_h + content_h,  content_w, content_h),
            pygame.Rect(content_w,  self._header_h + content_h,  content_w, content_h),
        ]

        self._hovered: Optional[int] = None
        self._pending: Optional[str] = None

    # ------------------------------------------------------------------
    # Event / Update / Render
    # ------------------------------------------------------------------

    def handle_event(self, event: pygame.event.Event) -> Optional[Any]:
        if event.type == pygame.MOUSEMOTION:
            self._hovered = self._quad_at(event.pos)

        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
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

        return None

    def update(self, dt: float):
        self.star_time += dt
        self._hovered = self._quad_at(pygame.mouse.get_pos())

    def render(self):
        self.display.fill(config.COLOR_MENU_BG)

        # Stars
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

        # Player money (right side)
        money_text = f"${self.player.money}"
        money_surf = self.font_large.render(money_text, True, config.COLOR_SECONDARY)
        self.display.blit(money_surf,
                          (config.SCREEN_WIDTH - money_surf.get_width() - 20,
                           (self._header_h - money_surf.get_height()) // 2))

        # Battles won (center)
        bw_text = f"Battles: {self.battles_won}"
        bw_surf = self.font_small.render(bw_text, True, (180, 200, 230))
        self.display.blit(bw_surf,
                          ((config.SCREEN_WIDTH - bw_surf.get_width()) // 2,
                           (self._header_h - bw_surf.get_height()) // 2))

        # Quadrants
        for i, (rect, quad) in enumerate(zip(self._quads, _QUADRANTS)):
            label, sublabel, _, base_col, hover_col, icon = quad
            is_hov = self._hovered == i
            color = hover_col if is_hov else base_col

            # Fill
            pygame.draw.rect(self.display, color, rect)

            # Thin inner shadow at top
            if is_hov:
                hi_surf = pygame.Surface((rect.width, 6), pygame.SRCALPHA)
                hi_surf.fill((255, 255, 255, 30))
                self.display.blit(hi_surf, rect.topleft)

            # Divider lines
            pygame.draw.rect(self.display, config.COLOR_MENU_BG, rect, width=2)

            # Icon
            cx = rect.centerx
            cy = rect.centery - 20
            self._draw_icon(icon, cx, cy, is_hov)

            # Label
            lbl_surf = self.font_large.render(label, True, config.COLOR_WHITE)
            self.display.blit(lbl_surf,
                              (rect.centerx - lbl_surf.get_width() // 2,
                               cy + 32))

            # Sub-label
            sub_surf = self.font_small.render(sublabel, True, (200, 215, 230))
            self.display.blit(sub_surf,
                              (rect.centerx - sub_surf.get_width() // 2,
                               cy + 32 + lbl_surf.get_height() + 4))

            # Key hint
            hint = f"[{i + 1}]"
            hint_surf = self.font_small.render(hint, True, (130, 145, 165))
            self.display.blit(hint_surf,
                              (rect.right - hint_surf.get_width() - 8,
                               rect.bottom - hint_surf.get_height() - 6))

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
            # Simple sword shape
            pygame.draw.line(self.display, col, (cx - 14, cy + 14), (cx + 14, cy - 14), 3)
            pygame.draw.line(self.display, col, (cx - 8, cy - 8), (cx - 14, cy - 2), 2)
            pygame.draw.line(self.display, col, (cx - 8, cy - 8), (cx - 2, cy - 14), 2)
        elif tag == "bag":
            # Shopping bag
            pygame.draw.rect(self.display, col, (cx - 12, cy - 6, 24, 20), width=2, border_radius=3)
            pygame.draw.arc(self.display, col,
                            pygame.Rect(cx - 8, cy - 14, 16, 14), 0, math.pi, 2)
        elif tag == "pack":
            # Backpack
            pygame.draw.rect(self.display, col, (cx - 12, cy - 10, 24, 22), width=2, border_radius=4)
            pygame.draw.line(self.display, col, (cx - 5, cy - 10), (cx - 5, cy + 12), 2)
            pygame.draw.line(self.display, col, (cx + 5, cy - 10), (cx + 5, cy + 12), 2)
            pygame.draw.line(self.display, col, (cx - 5, cy), (cx + 5, cy), 2)
        elif tag == "gear":
            # Gear circle with spokes
            pygame.draw.circle(self.display, col, (cx, cy), 10, 2)
            pygame.draw.circle(self.display, col, (cx, cy), 4, 2)
            for angle in range(0, 360, 45):
                rad = math.radians(angle)
                x1 = int(cx + 10 * math.cos(rad))
                y1 = int(cy + 10 * math.sin(rad))
                x2 = int(cx + 14 * math.cos(rad))
                y2 = int(cy + 14 * math.sin(rad))
                pygame.draw.line(self.display, col, (x1, y1), (x2, y2), 3)

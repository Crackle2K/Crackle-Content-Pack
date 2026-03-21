"""Shop screen — Poke Mart displayed as a scrollable item grid."""

from __future__ import annotations
import json
import pygame
from pathlib import Path
from typing import Any, Optional

from src.ui import config
from src.ui.screens.base_screen import BaseScreen
from src.ui.components.button import Button
from src.ui.asset_manager import AssetManager
from src.entities.trainer import Trainer


# ── Fallback catalog ──────────────────────────────────────────────────────────
_FALLBACK_CATALOG = [
    {"slug": "poke-ball",    "display_name": "Poke Ball",    "category": "Pokeballs",
     "cost": 80,   "description": "Catches Pokemon.",      "effect": {"type": "pokeball"}},
    {"slug": "great-ball",   "display_name": "Great Ball",   "category": "Pokeballs",
     "cost": 250,  "description": "Better catch rate.",    "effect": {"type": "pokeball"}},
    {"slug": "ultra-ball",   "display_name": "Ultra Ball",   "category": "Pokeballs",
     "cost": 500,  "description": "High-grade Ball.",      "effect": {"type": "pokeball"}},
    {"slug": "potion",       "display_name": "Potion",       "category": "Medicine",
     "cost": 100,  "description": "Restores 20 HP.",       "effect": {"type": "heal", "amount": 20}},
    {"slug": "super-potion", "display_name": "Super Potion", "category": "Medicine",
     "cost": 250,  "description": "Restores 50 HP.",       "effect": {"type": "heal", "amount": 50}},
    {"slug": "hyper-potion", "display_name": "Hyper Potion", "category": "Medicine",
     "cost": 500,  "description": "Restores 200 HP.",      "effect": {"type": "heal", "amount": 200}},
    {"slug": "max-potion",   "display_name": "Max Potion",   "category": "Medicine",
     "cost": 900,  "description": "Fully restores HP.",    "effect": {"type": "heal", "amount": "full"}},
    {"slug": "revive",       "display_name": "Revive",       "category": "Medicine",
     "cost": 600,  "description": "Revives a fainted Pokemon.", "effect": {"type": "revive", "amount": "half"}},
    {"slug": "oran-berry",   "display_name": "Oran Berry",   "category": "Berries",
     "cost": 30,   "description": "Restores 10 HP.",       "effect": {"type": "heal", "amount": 10}},
    {"slug": "sitrus-berry", "display_name": "Sitrus Berry", "category": "Berries",
     "cost": 80,   "description": "Restores 25 HP.",       "effect": {"type": "heal", "amount": 25}},
    {"slug": "lum-berry",    "display_name": "Lum Berry",    "category": "Berries",
     "cost": 100,  "description": "Cures all status.",     "effect": {"type": "heal", "amount": 0}},
    {"slug": "leppa-berry",  "display_name": "Leppa Berry",  "category": "Berries",
     "cost": 60,   "description": "Restores 10 PP.",       "effect": {"type": "pp_restore", "amount": 10}},
]

_CATEGORY_COLORS = {
    "Pokeballs": (200, 50,  50),
    "Medicine":  (50,  130, 220),
    "Berries":   (80,  170, 60),
}

_ITEMS_FOLDER  = Path("assets/items")
_SPRITE_SIZE   = 40
_HEADER_H      = 75
_FOOTER_H      = 56
_COLS          = 3
_SECTION_H     = 28
_CELL_PAD      = 10
_CELL_INNER_H  = 100   # height of each item cell


class ShopScreen(BaseScreen):
    """Poke Mart — grid of item tiles, prices shown below each item."""

    def __init__(self, display: pygame.Surface, assets: AssetManager, player: Trainer):
        super().__init__(display, assets)
        self.player  = player
        self.message = ""
        self.message_timer = 0.0
        self.scroll  = 0

        self.catalog = self._load_catalog()
        self._sprites: dict[str, Optional[pygame.Surface]] = {}
        self._load_sprites()
        self._build_layout()

    # ── Init helpers ──────────────────────────────────────────────────────────

    def _load_catalog(self) -> list[dict]:
        p = _ITEMS_FOLDER / "catalog.json"
        if p.exists():
            try:
                return json.loads(p.read_text())
            except Exception:
                pass
        return _FALLBACK_CATALOG

    def _load_sprites(self):
        for item in self.catalog:
            slug = item["slug"]
            p    = _ITEMS_FOLDER / f"{slug}.png"
            if p.exists():
                try:
                    s = pygame.image.load(str(p)).convert_alpha()
                    self._sprites[slug] = pygame.transform.scale(s, (_SPRITE_SIZE, _SPRITE_SIZE))
                    continue
                except pygame.error:
                    pass
            self._sprites[slug] = None

    def _build_layout(self):
        """Pre-compute (y, rect, item_index) for every cell and section header."""
        visible_w   = config.SCREEN_WIDTH - 2 * _CELL_PAD
        cell_w      = (visible_w - (_COLS - 1) * _CELL_PAD) // _COLS

        self._cell_w = cell_w
        self._cell_h = _CELL_INNER_H

        # Group items by category (preserve catalog order of categories)
        seen_cats: list[str]   = []
        groups: dict[str, list] = {}
        for item in self.catalog:
            cat = item["category"]
            if cat not in groups:
                seen_cats.append(cat)
                groups[cat] = []
            groups[cat].append(item)

        self._sections: list[tuple[str, int]] = []   # (category, y)
        self._cells:    list[tuple[int, int, int, dict]] = []  # (col, row_y, item_idx, item)
        self._total_h   = 0

        y = 0
        idx = 0
        for cat in seen_cats:
            self._sections.append((cat, y))
            y += _SECTION_H
            items = groups[cat]
            # Lay items out in rows of _COLS
            for row_start in range(0, len(items), _COLS):
                row_items = items[row_start: row_start + _COLS]
                for col, item in enumerate(row_items):
                    x = _CELL_PAD + col * (cell_w + _CELL_PAD)
                    self._cells.append((x, y, idx + row_start + col - row_start, item))
                y += _CELL_INNER_H + _CELL_PAD
                idx += len(row_items)

        self._total_h   = y
        self._visible_h = config.SCREEN_HEIGHT - _HEADER_H - _FOOTER_H

        # Back button
        self.back_button = Button(
            (config.SCREEN_WIDTH - 160) // 2,
            config.SCREEN_HEIGHT - _FOOTER_H + (_FOOTER_H - 40) // 2,
            160, 40, "BACK",
            font=self.font_medium, color=config.COLOR_ACCENT)

    # ── Events ────────────────────────────────────────────────────────────────

    def handle_event(self, event: pygame.event.Event) -> Optional[Any]:
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                return "back"
            elif event.key in (pygame.K_DOWN, pygame.K_s):
                self._scroll(_CELL_INNER_H)
            elif event.key in (pygame.K_UP, pygame.K_w):
                self._scroll(-_CELL_INNER_H)

        elif event.type == pygame.MOUSEWHEEL:
            self._scroll(-event.y * 60)

        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mx, my = event.pos
            if my >= config.SCREEN_HEIGHT - _FOOTER_H:
                if self.back_button.handle_event(event):
                    return "back"
                return None
            # Check cell clicks (translate by scroll + header)
            content_y = my - _HEADER_H - self.scroll
            content_x = mx
            for x, y, _, item in self._cells:
                rect = pygame.Rect(x, y, self._cell_w, self._cell_h)
                if rect.collidepoint(content_x, content_y):
                    self._try_buy(item)
                    return None

        elif event.type in (pygame.MOUSEBUTTONUP, pygame.MOUSEMOTION):
            if self.back_button.handle_event(event):
                return "back"

        return None

    # ── Update ────────────────────────────────────────────────────────────────

    def update(self, dt: float):
        pos = pygame.mouse.get_pos()
        self.back_button.update(pos)
        if self.message_timer > 0:
            self.message_timer = max(0.0, self.message_timer - dt)
            if self.message_timer == 0:
                self.message = ""

    # ── Render ────────────────────────────────────────────────────────────────

    def render(self):
        self.display.fill(config.COLOR_BG)

        # Build content surface
        content_surf = pygame.Surface(
            (config.SCREEN_WIDTH, max(self._total_h, 1)), pygame.SRCALPHA)
        content_surf.fill((0, 0, 0, 0))

        # Section headers
        for cat, y in self._sections:
            col = _CATEGORY_COLORS.get(cat, config.COLOR_GRAY)
            pygame.draw.rect(content_surf, (*col, 40),
                             (0, y, config.SCREEN_WIDTH, _SECTION_H - 2))
            lbl = self.font_small.render(f"── {cat.upper()} ──", True, col)
            content_surf.blit(lbl, (14, y + (_SECTION_H - lbl.get_height()) // 2))

        # Item cells
        affordable_set = {item["slug"] for _, _, _, item in self._cells
                          if self.player.money >= item["cost"]}
        for x, y, _, item in self._cells:
            self._draw_cell(content_surf, item, x, y, item["slug"] in affordable_set)

        # Clip + blit with scroll
        clip_rect = pygame.Rect(0, _HEADER_H, config.SCREEN_WIDTH, self._visible_h)
        self.display.set_clip(clip_rect)
        self.display.blit(content_surf, (0, _HEADER_H + self.scroll))
        self.display.set_clip(None)

        # Fade edges
        self._draw_fade(_HEADER_H, True)
        self._draw_fade(config.SCREEN_HEIGHT - _FOOTER_H - 20, False)

        # Header (on top)
        self._draw_header()

        # Footer
        pygame.draw.rect(self.display, config.COLOR_BG,
                         (0, config.SCREEN_HEIGHT - _FOOTER_H,
                          config.SCREEN_WIDTH, _FOOTER_H))
        pygame.draw.line(self.display, config.COLOR_INFO_BOX_BORDER,
                         (0, config.SCREEN_HEIGHT - _FOOTER_H),
                         (config.SCREEN_WIDTH, config.SCREEN_HEIGHT - _FOOTER_H), 1)
        if self.message:
            ok = "Bought" in self.message
            ms = self.font_medium.render(
                self.message, True, (40, 160, 40) if ok else config.COLOR_ACCENT)
            self.display.blit(ms, ms.get_rect(
                centerx=config.SCREEN_WIDTH // 2,
                centery=config.SCREEN_HEIGHT - _FOOTER_H + 10))
        self.back_button.render(self.display, self.font_medium)

    def _draw_header(self):
        pygame.draw.rect(self.display, config.COLOR_PRIMARY,
                         (0, 0, config.SCREEN_WIDTH, _HEADER_H))
        pygame.draw.rect(self.display, config.COLOR_SECONDARY,
                         (0, _HEADER_H - 3, config.SCREEN_WIDTH, 3))
        t = self.font_large.render("POKE MART", True, config.COLOR_WHITE)
        self.display.blit(t, t.get_rect(centerx=config.SCREEN_WIDTH // 2, centery=36))
        m = self.font_small.render(f"${self.player.money}", True, config.COLOR_SECONDARY)
        self.display.blit(m, (config.SCREEN_WIDTH - m.get_width() - 14, 28))

    def _draw_cell(self, surf: pygame.Surface, item: dict, x: int, y: int, affordable: bool):
        cat     = item.get("category", "")
        cat_col = _CATEGORY_COLORS.get(cat, config.COLOR_GRAY)
        rect    = pygame.Rect(x, y, self._cell_w, self._cell_h)
        bg      = (250, 252, 255) if affordable else (235, 235, 240)

        pygame.draw.rect(surf, bg, rect, border_radius=8)
        pygame.draw.rect(surf, config.COLOR_INFO_BOX_BORDER, rect, width=1, border_radius=8)

        # Top colour accent bar
        pygame.draw.rect(surf, cat_col,
                         pygame.Rect(x, y, self._cell_w, 4), border_radius=8)

        # Sprite centered at top
        sprite = self._sprites.get(item["slug"])
        if sprite:
            sx = x + (self._cell_w - _SPRITE_SIZE) // 2
            surf.blit(sprite, (sx, y + 10))

        # Name
        name_col = config.COLOR_BLACK if affordable else config.COLOR_GRAY
        ns = self.font_small.render(item["display_name"], True, name_col)
        surf.blit(ns, (x + (self._cell_w - ns.get_width()) // 2, y + 10 + _SPRITE_SIZE + 4))

        # Price — green if affordable, red if not
        price_col = (40, 160, 40) if affordable else config.COLOR_ACCENT
        ps = self.font_small.render(f"${item['cost']}", True, price_col)
        surf.blit(ps, (x + (self._cell_w - ps.get_width()) // 2,
                        y + 10 + _SPRITE_SIZE + 4 + ns.get_height() + 3))

        # Owned badge (top-right corner)
        count = self.player.items.get(item["slug"], 0)
        if count:
            cs = self.font_small.render(f"x{count}", True, config.COLOR_DARK_GRAY)
            surf.blit(cs, (x + self._cell_w - cs.get_width() - 6, y + 8))

    def _draw_fade(self, y: int, fade_up: bool):
        h = 18
        for i in range(h):
            alpha = int(180 * (i / h if fade_up else (h - i) / h))
            s = pygame.Surface((config.SCREEN_WIDTH, 1), pygame.SRCALPHA)
            s.fill((248, 248, 250, alpha))
            self.display.blit(s, (0, y + i))

    # ── Logic ─────────────────────────────────────────────────────────────────

    def _scroll(self, delta: int):
        max_scroll = -(max(0, self._total_h - self._visible_h))
        self.scroll = max(max_scroll, min(0, self.scroll - delta))

    def _try_buy(self, item: dict):
        if self.player.spend_money(item["cost"]):
            self.player.add_item(item["slug"])
            self.message = f"Bought {item['display_name']}!"
        else:
            self.message = "Not enough money!"
        self.message_timer = 2.0

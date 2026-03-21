"""Shop screen — Poke Mart with PokeAPI-sourced catalog and item sprites."""

from __future__ import annotations
import json
import os
import pygame
from pathlib import Path
from typing import Any, Optional

from src.ui import config
from src.ui.screens.base_screen import BaseScreen
from src.ui.components.button import Button
from src.ui.asset_manager import AssetManager
from src.entities.trainer import Trainer

# Fallback catalog used when the downloaded catalog is unavailable
_FALLBACK_CATALOG = [
    {"slug": "poke-ball",    "display_name": "Poke Ball",    "category": "Pokeballs",
     "cost": 200,  "description": "Catches Pokemon.",              "has_sprite": False,
     "effect": {"type": "pokeball"}},
    {"slug": "great-ball",   "display_name": "Great Ball",   "category": "Pokeballs",
     "cost": 600,  "description": "Better catch rate.",           "has_sprite": False,
     "effect": {"type": "pokeball"}},
    {"slug": "ultra-ball",   "display_name": "Ultra Ball",   "category": "Pokeballs",
     "cost": 1200, "description": "High-grade Ball.",             "has_sprite": False,
     "effect": {"type": "pokeball"}},
    {"slug": "potion",       "display_name": "Potion",       "category": "Medicine",
     "cost": 300,  "description": "Restores 20 HP.",              "has_sprite": False,
     "effect": {"type": "heal", "amount": 20}},
    {"slug": "super-potion", "display_name": "Super Potion", "category": "Medicine",
     "cost": 700,  "description": "Restores 50 HP.",              "has_sprite": False,
     "effect": {"type": "heal", "amount": 50}},
    {"slug": "hyper-potion", "display_name": "Hyper Potion", "category": "Medicine",
     "cost": 1200, "description": "Restores 200 HP.",             "has_sprite": False,
     "effect": {"type": "heal", "amount": 200}},
    {"slug": "max-potion",   "display_name": "Max Potion",   "category": "Medicine",
     "cost": 2500, "description": "Fully restores HP.",           "has_sprite": False,
     "effect": {"type": "heal", "amount": "full"}},
    {"slug": "revive",       "display_name": "Revive",       "category": "Medicine",
     "cost": 1500, "description": "Revives a fainted Pokemon.",   "has_sprite": False,
     "effect": {"type": "revive", "amount": "half"}},
    {"slug": "oran-berry",   "display_name": "Oran Berry",   "category": "Berries",
     "cost": 80,   "description": "Restores 10 HP.",              "has_sprite": False,
     "effect": {"type": "heal", "amount": 10}},
    {"slug": "sitrus-berry", "display_name": "Sitrus Berry", "category": "Berries",
     "cost": 200,  "description": "Restores 25 HP.",              "has_sprite": False,
     "effect": {"type": "heal", "amount": 25}},
    {"slug": "lum-berry",    "display_name": "Lum Berry",    "category": "Berries",
     "cost": 250,  "description": "Cures all status conditions.", "has_sprite": False,
     "effect": {"type": "heal", "amount": 0, "note": "Cures status"}},
    {"slug": "leppa-berry",  "display_name": "Leppa Berry",  "category": "Berries",
     "cost": 150,  "description": "Restores 10 PP to one move.", "has_sprite": False,
     "effect": {"type": "pp_restore", "amount": 10}},
]

_CATEGORY_COLORS = {
    "Pokeballs": (200, 50,  50),
    "Medicine":  (50,  130, 220),
    "Berries":   (80,  170, 60),
}

_SPRITE_SIZE = 30   # display size for item sprites


class ShopScreen(BaseScreen):
    """Poke Mart — scrollable catalog loaded from assets/items/catalog.json."""

    _ITEMS_FOLDER = Path("assets/items")
    _ROW_H = 52
    _HEADER_H = 75
    _FOOTER_H = 56

    def __init__(self, display: pygame.Surface, assets: AssetManager, player: Trainer):
        super().__init__(display, assets)
        self.player = player
        self.message = ""
        self.message_timer = 0.0
        self.scroll = 0  # pixel offset (negative = scrolled down)

        self.catalog = self._load_catalog()
        self._sprites: dict[str, Optional[pygame.Surface]] = {}
        self._load_sprites()

        self._content_h = self._measure_content_height()
        self._visible_h = config.SCREEN_HEIGHT - self._HEADER_H - self._FOOTER_H

        self._build_buttons()

    # ── Init helpers ─────────────────────────────────────────────────────────

    def _load_catalog(self) -> list[dict]:
        path = self._ITEMS_FOLDER / "catalog.json"
        if path.exists():
            try:
                return json.loads(path.read_text())
            except Exception:
                pass
        return _FALLBACK_CATALOG

    def _load_sprites(self):
        for item in self.catalog:
            slug = item["slug"]
            sprite_path = self._ITEMS_FOLDER / f"{slug}.png"
            if sprite_path.exists():
                try:
                    surf = pygame.image.load(str(sprite_path)).convert_alpha()
                    surf = pygame.transform.scale(surf, (_SPRITE_SIZE, _SPRITE_SIZE))
                    self._sprites[slug] = surf
                    continue
                except pygame.error:
                    pass
            self._sprites[slug] = None

    def _measure_content_height(self) -> int:
        seen: set[str] = set()
        h = 0
        for item in self.catalog:
            cat = item["category"]
            if cat not in seen:
                seen.add(cat)
                h += 26  # section header height
            h += self._ROW_H
        return h

    def _build_buttons(self):
        """Create BUY buttons positioned in content space (pre-scroll)."""
        self._buy_buttons: list[tuple[int, Button]] = []  # (catalog_index, button)
        seen: set[str] = set()
        y = 0
        for i, item in enumerate(self.catalog):
            cat = item["category"]
            if cat not in seen:
                seen.add(cat)
                y += 26
            btn = Button(
                config.SCREEN_WIDTH - 130,
                y + (self._ROW_H - 36) // 2,
                110, 36,
                f"${item['cost']}",
                font=self.font_small,
                color=_CATEGORY_COLORS.get(cat, config.COLOR_GRAY),
            )
            self._buy_buttons.append((i, btn))
            y += self._ROW_H

        self.back_button = Button(
            (config.SCREEN_WIDTH - 160) // 2,
            config.SCREEN_HEIGHT - self._FOOTER_H + (self._FOOTER_H - 40) // 2,
            160, 40,
            "BACK",
            font=self.font_medium,
            color=config.COLOR_ACCENT,
        )

    # ── Event / Update / Render ───────────────────────────────────────────────

    def handle_event(self, event: pygame.event.Event) -> Optional[Any]:
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                return "back"
            elif event.key in (pygame.K_DOWN, pygame.K_s):
                self._scroll(self._ROW_H)
            elif event.key in (pygame.K_UP, pygame.K_w):
                self._scroll(-self._ROW_H)

        elif event.type == pygame.MOUSEWHEEL:
            self._scroll(-event.y * self._ROW_H)

        elif event.type in (pygame.MOUSEBUTTONDOWN, pygame.MOUSEBUTTONUP,
                             pygame.MOUSEMOTION):
            # Translate y by scroll offset before button hit-test
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if event.pos[1] >= config.SCREEN_HEIGHT - self._FOOTER_H:
                    # Back button area — let it fall through
                    if self.back_button.handle_event(event):
                        return "back"
                    return None

            # Offset event position for scrolled buttons
            fake_pos = (event.pos[0], event.pos[1] - self._HEADER_H - self.scroll)
            fake_event = pygame.event.Event(
                event.type,
                {**event.__dict__, "pos": fake_pos}
            )
            for idx, btn in self._buy_buttons:
                if btn.handle_event(fake_event):
                    self._try_buy(idx)
                    return None

            if self.back_button.handle_event(event):
                return "back"

        return None

    def update(self, dt: float):
        mouse_pos = pygame.mouse.get_pos()
        scroll_mouse = (mouse_pos[0], mouse_pos[1] - self._HEADER_H - self.scroll)

        affordable = {idx for idx, _ in self._buy_buttons
                      if self.player.money >= self.catalog[idx]["cost"]}
        for idx, btn in self._buy_buttons:
            btn.disabled = idx not in affordable
            btn.update(scroll_mouse)
        self.back_button.update(mouse_pos)

        if self.message_timer > 0:
            self.message_timer = max(0.0, self.message_timer - dt)
            if self.message_timer == 0:
                self.message = ""

    def render(self):
        self.display.fill(config.COLOR_BG)

        # Scrollable content area clip
        content_rect = pygame.Rect(0, self._HEADER_H,
                                   config.SCREEN_WIDTH, self._visible_h)
        content_surf = pygame.Surface((config.SCREEN_WIDTH, self._content_h),
                                      pygame.SRCALPHA)
        content_surf.fill((0, 0, 0, 0))

        seen: set[str] = set()
        y = 0
        for i, item in enumerate(self.catalog):
            cat = item["category"]
            if cat not in seen:
                seen.add(cat)
                self._draw_section_header(content_surf, cat, y)
                y += 26
            self._draw_row(content_surf, item, i, y)
            y += self._ROW_H

        # Blit with scroll
        self.display.blit(content_surf, (0, self._HEADER_H + self.scroll))

        # Draw buttons on top (at their scrolled positions)
        for idx, btn in self._buy_buttons:
            btn.rect.y  # already positioned
            blit_y = self._HEADER_H + self.scroll + btn.rect.y
            if self._HEADER_H <= blit_y <= config.SCREEN_HEIGHT - self._FOOTER_H - 10:
                btn.render(self.display, self.font_small)

        # Fade overlay at top and bottom of scroll area
        self._draw_fade(self._HEADER_H, fade_up=True)
        self._draw_fade(config.SCREEN_HEIGHT - self._FOOTER_H - 20, fade_up=False)

        # Header (on top of everything)
        self._draw_header()

        # Footer
        pygame.draw.rect(self.display, config.COLOR_BG,
                         (0, config.SCREEN_HEIGHT - self._FOOTER_H,
                          config.SCREEN_WIDTH, self._FOOTER_H))
        pygame.draw.line(self.display, config.COLOR_INFO_BOX_BORDER,
                         (0, config.SCREEN_HEIGHT - self._FOOTER_H),
                         (config.SCREEN_WIDTH, config.SCREEN_HEIGHT - self._FOOTER_H), 1)
        if self.message:
            ok = "Bought" in self.message
            msg_surf = self.font_medium.render(
                self.message, True,
                (40, 160, 40) if ok else config.COLOR_ACCENT
            )
            self.display.blit(
                msg_surf,
                msg_surf.get_rect(centerx=config.SCREEN_WIDTH // 2,
                                  centery=config.SCREEN_HEIGHT - self._FOOTER_H + 10)
            )
        self.back_button.render(self.display, self.font_medium)

    # ── Drawing helpers ───────────────────────────────────────────────────────

    def _draw_header(self):
        pygame.draw.rect(self.display, config.COLOR_PRIMARY,
                         (0, 0, config.SCREEN_WIDTH, self._HEADER_H))
        pygame.draw.rect(self.display, config.COLOR_SECONDARY,
                         (0, self._HEADER_H - 3, config.SCREEN_WIDTH, 3))
        t = self.font_large.render("POKE MART", True, config.COLOR_WHITE)
        self.display.blit(t, t.get_rect(centerx=config.SCREEN_WIDTH // 2, centery=36))
        m = self.font_small.render(f"${self.player.money}", True, config.COLOR_SECONDARY)
        self.display.blit(m, (config.SCREEN_WIDTH - m.get_width() - 14, 28))

    def _draw_section_header(self, surf: pygame.Surface, cat: str, y: int):
        col = _CATEGORY_COLORS.get(cat, config.COLOR_GRAY)
        pygame.draw.rect(surf, (*col, 40), (0, y, config.SCREEN_WIDTH, 24))
        lbl = self.font_small.render(f"── {cat.upper()} ──", True, col)
        surf.blit(lbl, (14, y + (24 - lbl.get_height()) // 2))

    def _draw_row(self, surf: pygame.Surface, item: dict, idx: int, y: int):
        row_rect = pygame.Rect(8, y + 2, config.SCREEN_WIDTH - 16, self._ROW_H - 4)
        affordable = self.player.money >= item["cost"]
        bg = (250, 252, 255) if affordable else (235, 235, 240)
        pygame.draw.rect(surf, bg, row_rect, border_radius=6)
        pygame.draw.rect(surf, config.COLOR_INFO_BOX_BORDER, row_rect,
                         width=1, border_radius=6)

        cat_col = _CATEGORY_COLORS.get(item["category"], config.COLOR_GRAY)
        pygame.draw.rect(surf, cat_col,
                         pygame.Rect(row_rect.x + 4, row_rect.y + 4, 4,
                                     row_rect.height - 8),
                         border_radius=2)

        # Sprite
        sprite = self._sprites.get(item["slug"])
        sx = row_rect.x + 14
        if sprite:
            surf.blit(sprite, (sx, y + (self._ROW_H - _SPRITE_SIZE) // 2))
        text_x = sx + _SPRITE_SIZE + 8

        name_col = config.COLOR_BLACK if affordable else config.COLOR_GRAY
        name_surf = self.font_medium.render(item["display_name"], True, name_col)
        surf.blit(name_surf, (text_x, y + 8))

        desc = item.get("description", "")
        if desc:
            desc_surf = self.font_small.render(
                desc[:55] + ("…" if len(desc) > 55 else ""),
                True, config.COLOR_GRAY
            )
            surf.blit(desc_surf, (text_x, y + 10 + name_surf.get_height()))

        # Owned count
        count = self.player.items.get(item["slug"], 0)
        if count:
            ct = self.font_small.render(f"x{count}", True, config.COLOR_DARK_GRAY)
            surf.blit(ct, (config.SCREEN_WIDTH - 150 - ct.get_width() - 6,
                           y + (self._ROW_H - ct.get_height()) // 2))

    def _draw_fade(self, y: int, fade_up: bool):
        h = 18
        for i in range(h):
            alpha = int(180 * (i / h if fade_up else (h - i) / h))
            line_y = y + i if fade_up else y + i
            s = pygame.Surface((config.SCREEN_WIDTH, 1), pygame.SRCALPHA)
            s.fill((248, 248, 250, alpha))
            self.display.blit(s, (0, line_y))

    # ── Logic ─────────────────────────────────────────────────────────────────

    def _scroll(self, delta: int):
        max_scroll = -(max(0, self._content_h - self._visible_h))
        self.scroll = max(max_scroll, min(0, self.scroll - delta))

    def _try_buy(self, item_index: int):
        item = self.catalog[item_index]
        if self.player.spend_money(item["cost"]):
            self.player.add_item(item["slug"])
            self.message = f"Bought {item['display_name']}!"
        else:
            self.message = "Not enough money!"
        self.message_timer = 2.0

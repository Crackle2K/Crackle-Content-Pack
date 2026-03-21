"""Inventory screen — view and use items on Pokemon."""

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
from src.entities.pokemon import Pokemon

_ITEMS_FOLDER = Path("assets/items")
_SPRITE_SIZE = 28

_CATEGORY_COLORS = {
    "Pokeballs": (200, 50,  50),
    "Medicine":  (50,  130, 220),
    "Berries":   (80,  170, 60),
}


def _load_catalog() -> dict[str, dict]:
    """Return slug → item-dict mapping."""
    path = _ITEMS_FOLDER / "catalog.json"
    if path.exists():
        try:
            return {it["slug"]: it for it in json.loads(path.read_text())}
        except Exception:
            pass
    return {}


class InventoryScreen(BaseScreen):
    """Shows the player's bag and lets them use items on their Pokemon."""

    STATE_ITEMS   = "items"
    STATE_TARGETS = "targets"

    _ROW_H    = 58
    _HEADER_H = 75

    def __init__(self, display: pygame.Surface, assets: AssetManager, player: Trainer):
        super().__init__(display, assets)
        self.player = player
        self.state = self.STATE_ITEMS
        self.selected_item: Optional[str] = None
        self.message = ""
        self.message_timer = 0.0
        self.scroll = 0

        self._catalog = _load_catalog()
        self._sprites: dict[str, Optional[pygame.Surface]] = {}
        self._preload_sprites()

        self._build_item_buttons()
        self._build_target_buttons()

        self.back_button = Button(
            (config.SCREEN_WIDTH - 160) // 2,
            config.SCREEN_HEIGHT - 52,
            160, 40,
            "BACK",
            font=self.font_medium,
            color=config.COLOR_ACCENT,
        )

    def _preload_sprites(self):
        for slug in self.player.items:
            if slug in self._sprites:
                continue
            path = _ITEMS_FOLDER / f"{slug}.png"
            if path.exists():
                try:
                    s = pygame.image.load(str(path)).convert_alpha()
                    self._sprites[slug] = pygame.transform.scale(
                        s, (_SPRITE_SIZE, _SPRITE_SIZE))
                    continue
                except pygame.error:
                    pass
            self._sprites[slug] = None

    # ── Events ────────────────────────────────────────────────────────────────

    def handle_event(self, event: pygame.event.Event) -> Optional[Any]:
        if self.state == self.STATE_ITEMS:
            if event.type == pygame.MOUSEWHEEL:
                self._scroll_by(-event.y * self._ROW_H)

            fake = self._fake_scroll_event(event)
            for slug, btn in self._item_buttons:
                if btn.handle_event(fake):
                    self._select_item(slug)
                    return None

            if self.back_button.handle_event(event):
                return "back"

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return "back"
                elif event.key in (pygame.K_DOWN, pygame.K_s):
                    self._scroll_by(self._ROW_H)
                elif event.key in (pygame.K_UP, pygame.K_w):
                    self._scroll_by(-self._ROW_H)

        elif self.state == self.STATE_TARGETS:
            for idx, btn in self._target_buttons:
                if btn.handle_event(event):
                    self._use_on(idx)
                    return None

            if self.back_button.handle_event(event):
                self.state = self.STATE_ITEMS
                return None

            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                self.state = self.STATE_ITEMS

        return None

    def _fake_scroll_event(self, event: pygame.event.Event) -> pygame.event.Event:
        if hasattr(event, "pos"):
            new_pos = (event.pos[0], event.pos[1] - self._HEADER_H - self.scroll)
            return pygame.event.Event(event.type, {**event.__dict__, "pos": new_pos})
        return event

    # ── Update ────────────────────────────────────────────────────────────────

    def update(self, dt: float):
        mouse_pos = pygame.mouse.get_pos()
        scroll_mouse = (mouse_pos[0], mouse_pos[1] - self._HEADER_H - self.scroll)

        if self.state == self.STATE_ITEMS:
            for _, btn in self._item_buttons:
                btn.update(scroll_mouse)
        else:
            for _, btn in self._target_buttons:
                btn.update(mouse_pos)
        self.back_button.update(mouse_pos)

        if self.message_timer > 0:
            self.message_timer = max(0.0, self.message_timer - dt)
            if self.message_timer == 0:
                self.message = ""
                if self.state == self.STATE_TARGETS:
                    self.state = self.STATE_ITEMS
                    self._build_item_buttons()
                    self._preload_sprites()

    # ── Render ────────────────────────────────────────────────────────────────

    def render(self):
        self.display.fill(config.COLOR_BG)
        self._draw_header()

        if self.state == self.STATE_ITEMS:
            self._render_items()
        else:
            self._render_targets()

        # Footer
        footer_y = config.SCREEN_HEIGHT - 56
        pygame.draw.rect(self.display, config.COLOR_BG,
                         (0, footer_y, config.SCREEN_WIDTH, 56))
        pygame.draw.line(self.display, config.COLOR_INFO_BOX_BORDER,
                         (0, footer_y), (config.SCREEN_WIDTH, footer_y), 1)
        if self.message:
            ok = any(w in self.message for w in ("restored", "revived", "Used"))
            c = (40, 160, 40) if ok else config.COLOR_ACCENT
            ms = self.font_medium.render(self.message, True, c)
            self.display.blit(ms, ms.get_rect(
                centerx=config.SCREEN_WIDTH // 2, centery=footer_y + 10))

        back_lbl = "BACK" if self.state == self.STATE_ITEMS else "CANCEL"
        self.back_button.set_text(back_lbl)
        self.back_button.render(self.display, self.font_medium)

    def _draw_header(self):
        pygame.draw.rect(self.display, (55, 120, 60),
                         (0, 0, config.SCREEN_WIDTH, self._HEADER_H))
        pygame.draw.rect(self.display, config.COLOR_SECONDARY,
                         (0, self._HEADER_H - 3, config.SCREEN_WIDTH, 3))
        t = self.font_large.render("ITEM BAG", True, config.COLOR_WHITE)
        self.display.blit(t, t.get_rect(centerx=config.SCREEN_WIDTH // 2, centery=36))

    def _render_items(self):
        items = [(slug, cnt) for slug, cnt in self.player.items.items() if cnt > 0]
        if not items:
            empty = self.font_medium.render("Your bag is empty.", True, config.COLOR_GRAY)
            self.display.blit(empty, empty.get_rect(
                center=(config.SCREEN_WIDTH // 2, 280)))
            return

        visible_h = config.SCREEN_HEIGHT - self._HEADER_H - 56
        total_h = len(items) * self._ROW_H
        content_surf = pygame.Surface((config.SCREEN_WIDTH, max(total_h, 1)), pygame.SRCALPHA)
        content_surf.fill((0, 0, 0, 0))

        for i, (slug, count) in enumerate(items):
            y = i * self._ROW_H
            self._draw_item_row(content_surf, slug, count, i, y)

        self.display.blit(content_surf, (0, self._HEADER_H + self.scroll))
        for _, btn in self._item_buttons:
            blit_y = self._HEADER_H + self.scroll + btn.rect.y
            if self._HEADER_H <= blit_y <= config.SCREEN_HEIGHT - 56 - 10:
                btn.render(self.display, self.font_small)

    def _draw_item_row(self, surf: pygame.Surface, slug: str,
                       count: int, idx: int, y: int):
        meta = self._catalog.get(slug, {})
        cat = meta.get("category", "")
        cat_col = _CATEGORY_COLORS.get(cat, config.COLOR_GRAY)

        row_rect = pygame.Rect(8, y + 2, config.SCREEN_WIDTH - 16, self._ROW_H - 4)
        pygame.draw.rect(surf, (250, 252, 255), row_rect, border_radius=6)
        pygame.draw.rect(surf, config.COLOR_INFO_BOX_BORDER,
                         row_rect, width=1, border_radius=6)
        pygame.draw.rect(surf, cat_col,
                         pygame.Rect(row_rect.x + 4, row_rect.y + 4, 4,
                                     row_rect.height - 8), border_radius=2)

        sprite = self._sprites.get(slug)
        sx = row_rect.x + 14
        if sprite:
            surf.blit(sprite, (sx, y + (self._ROW_H - _SPRITE_SIZE) // 2))
        tx = sx + _SPRITE_SIZE + 8

        display_name = meta.get("display_name", slug.replace("-", " ").title())
        name_surf = self.font_medium.render(display_name, True, config.COLOR_BLACK)
        surf.blit(name_surf, (tx, y + 8))

        ct_surf = self.font_small.render(f"x{count}", True, config.COLOR_DARK_GRAY)
        surf.blit(ct_surf, (tx, y + 10 + name_surf.get_height()))

    def _render_targets(self):
        prompt = f"Use {self._catalog.get(self.selected_item or '', {}).get('display_name', self.selected_item)} on?"
        ps = self.font_medium.render(prompt, True, config.COLOR_BLACK)
        self.display.blit(ps, ps.get_rect(centerx=config.SCREEN_WIDTH // 2, y=82))

        row_h = 68
        for i, (idx, btn) in enumerate(self._target_buttons):
            pk = self.player.team[idx]
            y = 116 + i * row_h
            row_rect = pygame.Rect(20, y, config.SCREEN_WIDTH - 40, row_h - 6)

            hp = pk.get_hp_percentage()
            if pk.is_fainted:
                bg = (245, 215, 215)
            elif hp > 50:
                bg = (225, 248, 225)
            elif hp > 20:
                bg = (250, 245, 210)
            else:
                bg = (252, 228, 225)

            pygame.draw.rect(self.display, bg, row_rect, border_radius=8)
            pygame.draw.rect(self.display, config.COLOR_INFO_BOX_BORDER,
                             row_rect, width=1, border_radius=8)

            status = "FAINTED" if pk.is_fainted else f"{pk.current_hp}/{pk.max_hp} HP"
            ns = self.font_medium.render(pk.get_display_name(), True, config.COLOR_BLACK)
            hs = self.font_small.render(status, True, config.COLOR_DARK_GRAY)
            ls = self.font_small.render(f"Lv.{pk.level}", True, config.COLOR_GRAY)

            self.display.blit(ns, (row_rect.x + 12, row_rect.y + 8))
            self.display.blit(hs, (row_rect.x + 12, row_rect.y + 10 + ns.get_height()))
            self.display.blit(ls, (row_rect.right - ls.get_width() - 130,
                                    row_rect.centery - ls.get_height() // 2))
            btn.render(self.display, self.font_small)

    # ── Button builders ───────────────────────────────────────────────────────

    def _build_item_buttons(self):
        self._item_buttons: list[tuple[str, Button]] = []
        items = [(s, c) for s, c in self.player.items.items() if c > 0]
        for i, (slug, _) in enumerate(items):
            meta = self._catalog.get(slug, {})
            cat = meta.get("category", "")
            col = _CATEGORY_COLORS.get(cat, config.COLOR_PRIMARY)
            btn = Button(
                config.SCREEN_WIDTH - 130,
                i * self._ROW_H + (self._ROW_H - 36) // 2,
                110, 36,
                "USE",
                font=self.font_small,
                color=col,
            )
            self._item_buttons.append((slug, btn))

    def _build_target_buttons(self):
        self._target_buttons: list[tuple[int, Button]] = []
        effect = {}
        if self.selected_item:
            meta = self._catalog.get(self.selected_item, {})
            effect = meta.get("effect", {})
        is_revive = effect.get("type") == "revive"

        row_h = 68
        for i, pk in enumerate(self.player.team):
            usable = (is_revive and pk.is_fainted) or \
                     (not is_revive and not pk.is_fainted)
            btn = Button(
                config.SCREEN_WIDTH - 130,
                116 + i * row_h + (row_h - 36) // 2,
                110, 36,
                "SELECT",
                font=self.font_small,
                color=config.COLOR_PRIMARY,
                disabled=not usable,
            )
            self._target_buttons.append((i, btn))

    # ── Logic ─────────────────────────────────────────────────────────────────

    def _scroll_by(self, delta: int):
        items = [s for s, c in self.player.items.items() if c > 0]
        total_h = len(items) * self._ROW_H
        visible_h = config.SCREEN_HEIGHT - self._HEADER_H - 56
        max_scroll = -(max(0, total_h - visible_h))
        self.scroll = max(max_scroll, min(0, self.scroll - delta))

    def _select_item(self, slug: str):
        self.selected_item = slug
        self._build_target_buttons()
        self.state = self.STATE_TARGETS

    def _use_on(self, pokemon_index: int):
        pk: Pokemon = self.player.team[pokemon_index]
        meta = self._catalog.get(self.selected_item or "", {})
        effect = meta.get("effect", {})
        etype = effect.get("type", "none")
        amount = effect.get("amount", 0)

        if etype == "pokeball":
            self.message = "Can't use that here!"
            self.message_timer = 1.5
            return

        if not self.player.use_item(self.selected_item):
            self.message = "No items left!"
            self.message_timer = 1.5
            return

        if etype == "heal":
            if isinstance(amount, int) and amount > 0:
                healed = pk.heal(amount)
                self.message = f"{pk.get_display_name()} +{healed} HP!"
            elif amount == "full":
                pk.full_restore()
                self.message = f"{pk.get_display_name()} fully restored!"
            else:
                note = effect.get("note", "Effect applied!")
                self.message = note

        elif etype == "revive":
            if not pk.is_fainted:
                self.player.add_item(self.selected_item)  # refund
                self.message = f"{pk.get_display_name()} is not fainted!"
                self.message_timer = 1.5
                return
            pk.current_hp = pk.max_hp // 2
            pk.is_fainted = False
            self.message = f"{pk.get_display_name()} was revived!"

        elif etype == "pp_restore":
            for move in pk.moves:
                move.current_pp = min(move.max_pp, move.current_pp + amount)
            self.message = f"{pk.get_display_name()} PP restored!"

        else:
            self.message = "Can't use that here."

        self.message_timer = 2.0
        self._build_item_buttons()
        self._preload_sprites()

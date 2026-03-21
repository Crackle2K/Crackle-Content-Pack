"""Inventory screen — view and use items on Pokemon."""

import pygame
from typing import Any, Optional, List, Tuple

from src.ui import config
from src.ui.screens.base_screen import BaseScreen
from src.ui.components.button import Button
from src.ui.asset_manager import AssetManager
from src.entities.trainer import Trainer
from src.entities.pokemon import Pokemon


# Effects for each item name
_ITEM_EFFECTS = {
    "Potion":        {"type": "heal",   "amount": 30},
    "Super Potion":  {"type": "heal",   "amount": 70},
    "Full Restore":  {"type": "heal",   "amount": "full"},
    "Revive":        {"type": "revive", "amount": "half"},
}

_ITEM_COLORS = {
    "Potion":       (60, 160, 240),
    "Super Potion": (50, 110, 220),
    "Full Restore": (200, 170, 40),
    "Revive":       (180, 80, 200),
}


class InventoryScreen(BaseScreen):
    """Shows the player's item bag and lets them use items on their Pokemon."""

    STATE_ITEMS   = "items"    # Browse items
    STATE_TARGETS = "targets"  # Choose a Pokemon to use item on

    def __init__(self, display: pygame.Surface, assets: AssetManager, player: Trainer):
        super().__init__(display, assets)
        self.player = player
        self.state = self.STATE_ITEMS
        self.selected_item: Optional[str] = None
        self.message = ""
        self.message_timer = 0.0

        self._build_item_buttons()
        self._build_target_buttons()

        self.back_button = Button(
            (config.SCREEN_WIDTH - 160) // 2, config.SCREEN_HEIGHT - 60,
            160, 44,
            "BACK",
            font=self.font_medium,
            color=config.COLOR_ACCENT,
        )

    # ------------------------------------------------------------------
    def handle_event(self, event: pygame.event.Event) -> Optional[Any]:
        if self.state == self.STATE_ITEMS:
            for name, btn in self._item_buttons:
                if btn.handle_event(event):
                    self._select_item(name)
                    return None

            if self.back_button.handle_event(event):
                return "back"

            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                return "back"

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

    def update(self, dt: float):
        mouse_pos = pygame.mouse.get_pos()
        for _, btn in (self._item_buttons if self.state == self.STATE_ITEMS
                       else self._target_buttons):
            btn.update(mouse_pos)
        self.back_button.update(mouse_pos)

        if self.message_timer > 0:
            self.message_timer -= dt
            if self.message_timer <= 0:
                self.message = ""
                if self.state == self.STATE_TARGETS:
                    self.state = self.STATE_ITEMS
                    self._build_item_buttons()

    def render(self):
        self.display.fill(config.COLOR_BG)

        # Header
        pygame.draw.rect(self.display, (55, 120, 60),
                         (0, 0, config.SCREEN_WIDTH, 72))
        pygame.draw.rect(self.display, config.COLOR_SECONDARY,
                         (0, 72, config.SCREEN_WIDTH, 3))
        title_surf = self.font_large.render("ITEM BAG", True, config.COLOR_WHITE)
        self.display.blit(title_surf,
                          title_surf.get_rect(centerx=config.SCREEN_WIDTH // 2, centery=36))

        if self.state == self.STATE_ITEMS:
            self._render_items()
        else:
            self._render_targets()

        # Feedback message
        if self.message:
            ok = any(w in self.message for w in ("Used", "restored", "revived"))
            msg_col = (40, 160, 40) if ok else config.COLOR_ACCENT
            msg_surf = self.font_medium.render(self.message, True, msg_col)
            self.display.blit(msg_surf,
                              msg_surf.get_rect(centerx=config.SCREEN_WIDTH // 2,
                                                y=config.SCREEN_HEIGHT - 110))

        back_label = "BACK" if self.state == self.STATE_ITEMS else "CANCEL"
        self.back_button.set_text(back_label)
        self.back_button.render(self.display, self.font_medium)

    # ------------------------------------------------------------------
    def _render_items(self):
        if not self._item_buttons:
            empty = self.font_medium.render("Your bag is empty.", True, config.COLOR_GRAY)
            self.display.blit(empty,
                              empty.get_rect(center=(config.SCREEN_WIDTH // 2, 280)))
            return

        row_h = 78
        for i, (name, btn) in enumerate(self._item_buttons):
            row_y = 90 + i * row_h
            row_rect = pygame.Rect(20, row_y, config.SCREEN_WIDTH - 40, row_h - 6)
            color = _ITEM_COLORS.get(name, config.COLOR_GRAY)

            pygame.draw.rect(self.display, (248, 250, 252), row_rect, border_radius=8)
            pygame.draw.rect(self.display, config.COLOR_INFO_BOX_BORDER,
                             row_rect, width=1, border_radius=8)

            swatch = pygame.Rect(row_rect.x + 10, row_rect.y + 10, 8, row_rect.height - 20)
            pygame.draw.rect(self.display, color, swatch, border_radius=4)

            name_surf = self.font_medium.render(name, True, config.COLOR_BLACK)
            self.display.blit(name_surf, (row_rect.x + 28, row_rect.y + 8))

            count = self.player.items.get(name, 0)
            ct_surf = self.font_small.render(f"x{count}", True, config.COLOR_DARK_GRAY)
            self.display.blit(ct_surf,
                              (row_rect.x + 28,
                               row_rect.y + 10 + name_surf.get_height()))

            btn.render(self.display, self.font_small)

    def _render_targets(self):
        prompt = f"Use {self.selected_item} on which Pokemon?"
        p_surf = self.font_medium.render(prompt, True, config.COLOR_BLACK)
        self.display.blit(p_surf, p_surf.get_rect(centerx=config.SCREEN_WIDTH // 2, y=86))

        row_h = 68
        for i, (idx, btn) in enumerate(self._target_buttons):
            pokemon = self.player.team[idx]
            row_y = 120 + i * row_h
            row_rect = pygame.Rect(20, row_y, config.SCREEN_WIDTH - 40, row_h - 6)

            hp_pct = pokemon.get_hp_percentage()
            if pokemon.is_fainted:
                bg = (240, 220, 220)
            elif hp_pct > 50:
                bg = (228, 248, 228)
            elif hp_pct > 20:
                bg = (250, 245, 215)
            else:
                bg = (250, 228, 228)

            pygame.draw.rect(self.display, bg, row_rect, border_radius=8)
            pygame.draw.rect(self.display, config.COLOR_INFO_BOX_BORDER,
                             row_rect, width=1, border_radius=8)

            status = "FAINTED" if pokemon.is_fainted else f"{pokemon.current_hp}/{pokemon.max_hp} HP"
            name_surf = self.font_medium.render(pokemon.get_display_name(), True, config.COLOR_BLACK)
            hp_surf = self.font_small.render(status, True, config.COLOR_DARK_GRAY)
            lvl_surf = self.font_small.render(f"Lv.{pokemon.level}", True, config.COLOR_GRAY)

            self.display.blit(name_surf, (row_rect.x + 12, row_rect.y + 8))
            self.display.blit(hp_surf, (row_rect.x + 12, row_rect.y + 10 + name_surf.get_height()))
            self.display.blit(lvl_surf, (row_rect.right - lvl_surf.get_width() - 130,
                                          row_rect.centery - lvl_surf.get_height() // 2))

            btn.render(self.display, self.font_small)

    # ------------------------------------------------------------------
    def _build_item_buttons(self):
        self._item_buttons: List[Tuple[str, Button]] = []
        row_h = 78
        for i, (name, count) in enumerate(self.player.items.items()):
            if count <= 0:
                continue
            color = _ITEM_COLORS.get(name, config.COLOR_GRAY)
            btn = Button(
                config.SCREEN_WIDTH - 130, 90 + i * row_h + (row_h - 40) // 2,
                110, 40,
                "USE",
                font=self.font_small,
                color=color,
            )
            self._item_buttons.append((name, btn))

    def _build_target_buttons(self):
        self._target_buttons: List[Tuple[int, Button]] = []
        effect = _ITEM_EFFECTS.get(self.selected_item or "", {})
        is_revive = effect.get("type") == "revive"

        row_h = 68
        for i, pokemon in enumerate(self.player.team):
            usable = (is_revive and pokemon.is_fainted) or \
                     (not is_revive and not pokemon.is_fainted)
            btn = Button(
                config.SCREEN_WIDTH - 130, 120 + i * row_h + (row_h - 36) // 2,
                110, 36,
                "SELECT",
                font=self.font_small,
                color=config.COLOR_PRIMARY,
                disabled=not usable,
            )
            self._target_buttons.append((i, btn))

    def _select_item(self, name: str):
        self.selected_item = name
        self._build_target_buttons()
        self.state = self.STATE_TARGETS

    def _use_on(self, pokemon_index: int):
        pokemon: Pokemon = self.player.team[pokemon_index]
        effect = _ITEM_EFFECTS.get(self.selected_item, {})
        etype = effect.get("type")
        amount = effect.get("amount")

        if etype == "heal":
            if not self.player.use_item(self.selected_item):
                self.message = "No items left!"
                self.message_timer = 1.5
                return
            if amount == "full":
                pokemon.full_restore()
                self.message = f"{pokemon.get_display_name()} fully restored!"
            else:
                healed = pokemon.heal(amount)
                self.message = f"{pokemon.get_display_name()} restored {healed} HP!"

        elif etype == "revive":
            if not pokemon.is_fainted:
                self.message = f"{pokemon.get_display_name()} is not fainted!"
                self.message_timer = 1.5
                return
            if not self.player.use_item(self.selected_item):
                self.message = "No items left!"
                self.message_timer = 1.5
                return
            pokemon.current_hp = pokemon.max_hp // 2
            pokemon.is_fainted = False
            self.message = f"{pokemon.get_display_name()} was revived!"

        else:
            self.message = "Can't use that here."

        self.message_timer = 2.0
        self._build_item_buttons()

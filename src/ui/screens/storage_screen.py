"""PC Storage screen — deposit/withdraw Pokemon between team and box."""

import pygame
from typing import Optional, List

from src.ui import config
from src.ui.screens.base_screen import BaseScreen
from src.ui.asset_manager import AssetManager
from src.entities.trainer import Trainer
from src.entities.pokemon import Pokemon

_HEADER_H = 60
_FOOTER_H = 44
_PANEL_W  = 395
_CONTENT_TOP = _HEADER_H + 6
_CONTENT_BOT = config.SCREEN_HEIGHT - _FOOTER_H
_ITEM_H  = 52
_ITEM_GAP = 4

_BG       = (20, 24, 40)
_PANEL_BG = (28, 33, 52)
_DIVIDER  = (60, 70, 100)
_SELECTED = config.COLOR_SECONDARY
_HINT_COL = (130, 150, 190)


class StorageScreen(BaseScreen):
    """Screen for managing Pokemon between active team and PC box."""

    SIDE_TEAM = "team"
    SIDE_BOX  = "box"

    def __init__(self, display: pygame.Surface, assets: AssetManager, player: Trainer):
        super().__init__(display, assets)
        self.player       = player
        self.selected_side: Optional[str] = None
        self.selected_idx: Optional[int]  = None
        self.box_scroll: int = 0
        self.message: str    = "Select a Pokemon to move it."
        self._team_hover: Optional[int] = None
        self._box_hover:  Optional[int] = None

    def _team_item_rect(self, i: int) -> pygame.Rect:
        y = _CONTENT_TOP + 26 + i * (_ITEM_H + _ITEM_GAP)
        return pygame.Rect(4, y, _PANEL_W - 8, _ITEM_H)

    def _box_item_rect(self, i: int) -> pygame.Rect:
        y = _CONTENT_TOP + 26 + i * (_ITEM_H + _ITEM_GAP) - self.box_scroll
        return pygame.Rect(_PANEL_W + 4, y, _PANEL_W - 8, _ITEM_H)

    def _box_visible(self) -> tuple:
        """Returns (first_visible_index, last_visible_index+1)."""
        capacity = _CONTENT_BOT - _CONTENT_TOP
        first = self.box_scroll // (_ITEM_H + _ITEM_GAP)
        last  = first + capacity // (_ITEM_H + _ITEM_GAP) + 2
        return first, min(last, len(self.player.box))

    def _clamp_box_scroll(self):
        max_scroll = max(0, len(self.player.box) * (_ITEM_H + _ITEM_GAP) - (_CONTENT_BOT - _CONTENT_TOP))
        self.box_scroll = max(0, min(self.box_scroll, max_scroll))

    def handle_event(self, event: pygame.event.Event) -> Optional[str]:
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                return "done"

        elif event.type == pygame.MOUSEWHEEL:
            self.box_scroll -= event.y * 30
            self._clamp_box_scroll()

        elif event.type == pygame.MOUSEMOTION:
            pos = event.pos
            self._team_hover = next(
                (i for i in range(len(self.player.team))
                 if self._team_item_rect(i).collidepoint(pos)
                 and _CONTENT_TOP <= self._team_item_rect(i).y <= _CONTENT_BOT), None)
            self._box_hover = next(
                (i for i in range(len(self.player.box))
                 if self._box_item_rect(i).collidepoint(pos)
                 and _CONTENT_TOP <= self._box_item_rect(i).y <= _CONTENT_BOT), None)

        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            pos = event.pos
            # Done button
            done_rect = pygame.Rect(config.SCREEN_WIDTH // 2 - 70, _CONTENT_BOT + 6, 140, 32)
            if done_rect.collidepoint(pos):
                return "done"

            # Team side click
            for i in range(len(self.player.team)):
                rect = self._team_item_rect(i)
                if rect.collidepoint(pos) and rect.y >= _CONTENT_TOP and rect.bottom <= _CONTENT_BOT + _ITEM_H:
                    self._handle_team_click(i)
                    return None

            # Box side click
            for i in range(len(self.player.box)):
                rect = self._box_item_rect(i)
                if rect.collidepoint(pos) and rect.y >= _CONTENT_TOP and rect.bottom <= _CONTENT_BOT + _ITEM_H:
                    self._handle_box_click(i)
                    return None

        return None

    def _handle_team_click(self, idx: int):
        pk = self.player.team[idx]
        if self.selected_side == self.SIDE_TEAM and self.selected_idx == idx:
            # Deselect
            self.selected_side = None
            self.selected_idx  = None
            self.message = "Deselected."
        elif self.selected_side == self.SIDE_BOX and self.selected_idx is not None:
            # Swap: withdraw selected box pokemon, deposit team[idx]
            if len(self.player.team) >= self.player.MAX_TEAM_SIZE:
                # Can't add more, need to swap
                box_pk = self.player.box[self.selected_idx]
                team_pk = self.player.team[idx]
                self.player.team[idx] = box_pk
                self.player.box[self.selected_idx] = team_pk
                self.message = f"Swapped {team_pk.get_display_name()} with {box_pk.get_display_name()}!"
            else:
                # Just withdraw (team not full)
                self.player.withdraw_from_box(self.selected_idx)
                self.message = f"{self.player.team[-1].get_display_name()} joined the team!"
            self.selected_side = None
            self.selected_idx  = None
        else:
            # Select for deposit
            if len(self.player.team) <= 1:
                self.message = "Can't deposit — team must have at least 1 Pokemon!"
                return
            self.selected_side = self.SIDE_TEAM
            self.selected_idx  = idx
            self.message = f"Selected {pk.get_display_name()} — click box to deposit, or click again to deselect."

    def _handle_box_click(self, idx: int):
        pk = self.player.box[idx]
        if self.selected_side == self.SIDE_BOX and self.selected_idx == idx:
            self.selected_side = None
            self.selected_idx  = None
            self.message = "Deselected."
        elif self.selected_side == self.SIDE_TEAM and self.selected_idx is not None:
            # Swap: deposit team pokemon to box, withdraw this box pokemon
            team_pk = self.player.team[self.selected_idx]
            self.player.box[idx] = team_pk
            self.player.team[self.selected_idx] = pk
            self.message = f"Swapped {team_pk.get_display_name()} with {pk.get_display_name()}!"
            # Fix active index
            if self.player.active_pokemon_index >= len(self.player.team):
                self.player.active_pokemon_index = 0
            self.selected_side = None
            self.selected_idx  = None
        else:
            if len(self.player.team) >= self.player.MAX_TEAM_SIZE:
                self.selected_side = self.SIDE_BOX
                self.selected_idx  = idx
                self.message = f"Team is full. Select a team Pokemon to swap with {pk.get_display_name()}."
            else:
                # Just withdraw
                self.player.withdraw_from_box(idx)
                self.message = f"{pk.get_display_name()} joined the team!"
                self.selected_side = None
                self.selected_idx  = None

    def update(self, dt: float):
        pos = pygame.mouse.get_pos()
        self._team_hover = next(
            (i for i in range(len(self.player.team))
             if self._team_item_rect(i).collidepoint(pos)
             and _CONTENT_TOP <= self._team_item_rect(i).y <= _CONTENT_BOT + _ITEM_H), None)
        self._box_hover = next(
            (i for i in range(len(self.player.box))
             if self._box_item_rect(i).collidepoint(pos)
             and _CONTENT_TOP <= self._box_item_rect(i).y <= _CONTENT_BOT + _ITEM_H), None)

    def render(self):
        self.display.fill(_BG)
        self._render_header()
        self._render_team_panel()
        self._render_box_panel()
        self._render_divider()
        self._render_footer()

    def _render_header(self):
        pygame.draw.rect(self.display, config.COLOR_PRIMARY,
                         (0, 0, config.SCREEN_WIDTH, _HEADER_H))
        ts = self.font_large.render("PC STORAGE", True, config.COLOR_WHITE)
        self.display.blit(ts, (20, (_HEADER_H - ts.get_height()) // 2))
        sub = self.font_small.render(f"Team: {len(self.player.team)}/6   Box: {len(self.player.box)}",
                                      True, (200, 220, 255))
        self.display.blit(sub, (config.SCREEN_WIDTH - sub.get_width() - 20,
                                 (_HEADER_H - sub.get_height()) // 2))

    def _render_divider(self):
        pygame.draw.line(self.display, _DIVIDER,
                         (_PANEL_W, _HEADER_H), (_PANEL_W, config.SCREEN_HEIGHT), 2)

    def _render_team_panel(self):
        lbl = self.font_medium.render("TEAM", True, (180, 210, 255))
        self.display.blit(lbl, (8, _HEADER_H + 2))

        clip = pygame.Rect(0, _CONTENT_TOP + 24, _PANEL_W, _CONTENT_BOT - _CONTENT_TOP - 24)
        self.display.set_clip(clip)
        for i, pk in enumerate(self.player.team):
            rect = self._team_item_rect(i)
            self._render_item(rect, pk, i, self.SIDE_TEAM, self._team_hover)
        self.display.set_clip(None)

    def _render_box_panel(self):
        lbl = self.font_medium.render("PC BOX", True, (180, 210, 255))
        self.display.blit(lbl, (_PANEL_W + 8, _HEADER_H + 2))

        clip = pygame.Rect(_PANEL_W, _CONTENT_TOP + 24, _PANEL_W, _CONTENT_BOT - _CONTENT_TOP - 24)
        self.display.set_clip(clip)
        for i, pk in enumerate(self.player.box):
            rect = self._box_item_rect(i)
            if rect.bottom < _CONTENT_TOP + 24 or rect.top > _CONTENT_BOT:
                continue
            self._render_item(rect, pk, i, self.SIDE_BOX, self._box_hover)
        self.display.set_clip(None)

        if not self.player.box:
            hint = self.font_small.render("Box is empty", True, _HINT_COL)
            self.display.blit(hint, (_PANEL_W + 12, _CONTENT_TOP + 30))

    def _render_item(self, rect: pygame.Rect, pk: Pokemon,
                     idx: int, side: str, hover_idx: Optional[int]):
        is_sel = (self.selected_side == side and self.selected_idx == idx)
        is_hov = (hover_idx == idx)

        hp_pct = pk.get_hp_percentage()
        base_col = (config.COLOR_HP_GREEN  if hp_pct > 50
                    else config.COLOR_HP_YELLOW if hp_pct > 20
                    else config.COLOR_HP_RED)
        if pk.is_fainted:
            base_col = (80, 80, 80)

        if is_sel:
            glow = rect.inflate(6, 6)
            pygame.draw.rect(self.display, _SELECTED, glow, border_radius=10)
        col = tuple(min(255, c + 30) for c in base_col) if is_hov else base_col
        pygame.draw.rect(self.display, col, rect, border_radius=8)

        name_s = self.font_small.render(
            f"{pk.get_display_name()}  Lv.{pk.level}", True, config.COLOR_WHITE)
        hp_s   = self.font_small.render(
            f"HP {pk.current_hp}/{pk.max_hp}  {'(fainted)' if pk.is_fainted else ''}",
            True, (230, 245, 255))
        self.display.blit(name_s, (rect.x + 8, rect.y + 6))
        self.display.blit(hp_s,   (rect.x + 8, rect.y + 6 + name_s.get_height() + 2))

    def _render_footer(self):
        foot_y = _CONTENT_BOT
        pygame.draw.rect(self.display, (35, 40, 60),
                         (0, foot_y, config.SCREEN_WIDTH, _FOOTER_H))
        pygame.draw.line(self.display, _DIVIDER,
                         (0, foot_y), (config.SCREEN_WIDTH, foot_y), 1)

        msg_s = self.font_small.render(self.message, True, (200, 215, 240))
        self.display.blit(msg_s, (10, foot_y + (_FOOTER_H - msg_s.get_height()) // 2))

        done_rect = pygame.Rect(config.SCREEN_WIDTH // 2 - 70, foot_y + 6, 140, 32)
        pygame.draw.rect(self.display, (60, 70, 110), done_rect, border_radius=6)
        done_s = self.font_small.render("Done [ESC]", True, config.COLOR_WHITE)
        self.display.blit(done_s, (done_rect.centerx - done_s.get_width() // 2,
                                    done_rect.centery - done_s.get_height() // 2))

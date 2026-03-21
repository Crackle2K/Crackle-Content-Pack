"""Pokemon party screen — view your Pokemon's stats and manage their moves."""

import pygame
from typing import Optional, List

from src.ui import config
from src.ui.screens.base_screen import BaseScreen
from src.ui.asset_manager import AssetManager
from src.entities.trainer import Trainer
from src.entities.pokemon import Pokemon
from src.entities.move import Move

# ── Layout constants ──────────────────────────────────────────────────────────
_PANEL_W   = 218   # left panel width
_HEADER_H  = 60    # header bar height
_DX        = _PANEL_W + 12   # right panel x start
_DW        = config.SCREEN_WIDTH - _DX - 10  # right panel width

# Detail view row y-positions
_NAME_Y      = _HEADER_H + 10
_TYPES_Y     = _NAME_Y + 38
_XP_LBL_Y   = _TYPES_Y + 24
_XP_BAR_Y   = _XP_LBL_Y + 22
_STATS_Y     = _XP_BAR_Y + 18
_DIV_Y       = _STATS_Y + 54   # after 2 rows × 27px of stats
_MOVES_LBL_Y = _DIV_Y + 10
_MOVES_Y     = _MOVES_LBL_Y + 24

_MOVE_H  = 40
_MOVE_GAP = 5

# Swap list
_SWAP_HDR_Y   = _HEADER_H + 10
_SWAP_LIST_Y  = _SWAP_HDR_Y + 28
_SWAP_ITEM_H  = 34
_SWAP_ITEM_GAP = 3
_SWAP_CLIP_TOP = _SWAP_LIST_Y - 4
_SWAP_CLIP_BOT = config.SCREEN_HEIGHT - 8

# Colours
_BG         = (22, 26, 42)
_PANEL_BG   = (30, 35, 54)
_DIVIDER    = (60, 70, 100)
_SEL_GLOW   = config.COLOR_SECONDARY
_XP_FILL    = (100, 160, 255)
_XP_BG      = (45, 50, 80)
_STAT_LBL   = (150, 170, 210)
_STAT_VAL   = config.COLOR_WHITE
_HINT_COL   = (120, 140, 180)
_MOVE_HINT  = (180, 200, 240)
_SWAP_HDR   = (255, 220, 100)
_CURRENT_MV = (200, 200, 80)


class PokemonPartyScreen(BaseScreen):
    """View all team Pokemon stats/XP and manage their moves."""

    STATE_LIST   = "list"
    STATE_DETAIL = "detail"
    STATE_SWAP   = "swap"

    def __init__(self, display: pygame.Surface, assets: AssetManager, player: Trainer):
        super().__init__(display, assets)
        self.player = player
        self.state  = self.STATE_LIST

        self.selected_idx: Optional[int] = None  # index into player.team
        self.swap_slot:    Optional[int] = None  # move slot being replaced (0-3)
        self.swap_scroll:  int = 0               # pixel scroll offset for swap list

        self._team_rects: List[pygame.Rect] = self._build_team_rects()
        self._team_hover: Optional[int] = None

    # ── Layout helpers ────────────────────────────────────────────────────────

    def _build_team_rects(self) -> List[pygame.Rect]:
        rects = []
        bw = _PANEL_W - 16
        bh = 52
        for i in range(len(self.player.team)):
            rects.append(pygame.Rect(8, _HEADER_H + 8 + i * (bh + 6), bw, bh))
        return rects

    def _move_rect(self, slot: int) -> pygame.Rect:
        return pygame.Rect(_DX, _MOVES_Y + slot * (_MOVE_H + _MOVE_GAP), _DW, _MOVE_H)

    def _swap_item_rect(self, index: int) -> pygame.Rect:
        y = _SWAP_LIST_Y + index * (_SWAP_ITEM_H + _SWAP_ITEM_GAP) - self.swap_scroll
        return pygame.Rect(_DX, y, _DW, _SWAP_ITEM_H)

    def _back_rect(self) -> pygame.Rect:
        return pygame.Rect(config.SCREEN_WIDTH - 108, 12, 96, 36)

    # ── Event handling ────────────────────────────────────────────────────────

    def handle_event(self, event: pygame.event.Event) -> Optional[str]:
        if event.type == pygame.MOUSEMOTION:
            pos = event.pos
            self._team_hover = next(
                (i for i, r in enumerate(self._team_rects) if r.collidepoint(pos)), None)

        elif event.type == pygame.MOUSEWHEEL:
            if self.state == self.STATE_SWAP:
                pk = self.player.team[self.selected_idx]
                available = pk.get_available_moves()
                max_scroll = max(0, len(available) * (_SWAP_ITEM_H + _SWAP_ITEM_GAP)
                                 - (_SWAP_CLIP_BOT - _SWAP_LIST_Y))
                self.swap_scroll = max(0, min(max_scroll, self.swap_scroll - event.y * 30))

        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                return self._go_back()

        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            return self._handle_click(event.pos)

        return None

    def _go_back(self) -> Optional[str]:
        if self.state == self.STATE_SWAP:
            self.state = self.STATE_DETAIL
            self.swap_slot = None
            return None
        if self.state == self.STATE_DETAIL:
            self.state = self.STATE_LIST
            self.selected_idx = None
            return None
        return "done"

    def _handle_click(self, pos) -> Optional[str]:
        # Back button
        if self._back_rect().collidepoint(pos):
            return self._go_back()

        # Team list (left panel)
        for i, rect in enumerate(self._team_rects):
            if rect.collidepoint(pos):
                self.selected_idx = i
                self.swap_slot    = None
                self.swap_scroll  = 0
                self.state        = self.STATE_DETAIL
                return None

        # Right panel actions
        if pos[0] < _PANEL_W:
            return None

        if self.state == self.STATE_DETAIL and self.selected_idx is not None:
            pk = self.player.team[self.selected_idx]
            for slot in range(len(pk.moves)):
                if self._move_rect(slot).collidepoint(pos):
                    self.swap_slot   = slot
                    self.swap_scroll = 0
                    self.state       = self.STATE_SWAP
                    return None

        elif self.state == self.STATE_SWAP and self.selected_idx is not None:
            pk        = self.player.team[self.selected_idx]
            available = pk.get_available_moves()
            for i, move_name in enumerate(available):
                rect = self._swap_item_rect(i)
                if (rect.collidepoint(pos)
                        and _SWAP_CLIP_TOP <= rect.y
                        and rect.bottom <= _SWAP_CLIP_BOT):
                    pk.learn_move(move_name, slot=self.swap_slot)
                    self.state     = self.STATE_DETAIL
                    self.swap_slot = None
                    return None

        return None

    # ── Update ───────────────────────────────────────────────────────────────

    def update(self, dt: float):
        pos = pygame.mouse.get_pos()
        self._team_hover = next(
            (i for i, r in enumerate(self._team_rects) if r.collidepoint(pos)), None)

    # ── Render ───────────────────────────────────────────────────────────────

    def render(self):
        self.display.fill(_BG)
        self._render_header()
        self._render_left_panel()
        pygame.draw.line(self.display, _DIVIDER,
                         (_PANEL_W, _HEADER_H), (_PANEL_W, config.SCREEN_HEIGHT), 2)
        self._render_right_panel()

    def _render_header(self):
        pygame.draw.rect(self.display, config.COLOR_PRIMARY,
                         (0, 0, config.SCREEN_WIDTH, _HEADER_H))
        ts = self.font_large.render("POKEMON TEAM", True, config.COLOR_WHITE)
        self.display.blit(ts, (20, (_HEADER_H - ts.get_height()) // 2))

        br = self._back_rect()
        pygame.draw.rect(self.display, (70, 80, 110), br, border_radius=6)
        pygame.draw.rect(self.display, _DIVIDER, br, width=1, border_radius=6)
        bs = self.font_small.render("Back [ESC]", True, config.COLOR_WHITE)
        self.display.blit(bs, (br.centerx - bs.get_width() // 2,
                               br.centery - bs.get_height() // 2))

    def _render_left_panel(self):
        pygame.draw.rect(self.display, _PANEL_BG,
                         (0, _HEADER_H, _PANEL_W, config.SCREEN_HEIGHT - _HEADER_H))

        for i, (rect, pk) in enumerate(zip(self._team_rects, self.player.team)):
            is_sel = (i == self.selected_idx)
            is_hov = (i == self._team_hover)

            hp_pct = pk.get_hp_percentage()
            col = (config.COLOR_HP_GREEN  if hp_pct > 50
                   else config.COLOR_HP_YELLOW if hp_pct > 20
                   else config.COLOR_HP_RED)

            if is_sel:
                glow = rect.inflate(6, 6)
                pygame.draw.rect(self.display, _SEL_GLOW, glow, border_radius=10)
            bg = tuple(min(255, c + 30) for c in col) if is_hov else col
            pygame.draw.rect(self.display, bg, rect, border_radius=8)

            name_s = self.font_small.render(
                f"{pk.get_display_name()}  Lv.{pk.level}", True, config.COLOR_WHITE)
            hp_s   = self.font_small.render(
                f"HP {pk.current_hp}/{pk.max_hp}", True, (220, 235, 255))
            self.display.blit(name_s, (rect.x + 8, rect.y + 6))
            self.display.blit(hp_s,   (rect.x + 8, rect.y + 6 + name_s.get_height() + 2))

        if not self.player.team:
            hint = self.font_small.render("No Pokemon!", True, _HINT_COL)
            self.display.blit(hint, (10, _HEADER_H + 20))

    def _render_right_panel(self):
        if self.state == self.STATE_LIST or self.selected_idx is None:
            hint = self.font_medium.render("Select a Pokemon →", True, _HINT_COL)
            self.display.blit(hint, (_DX, config.SCREEN_HEIGHT // 2 - hint.get_height() // 2))
            return

        pk = self.player.team[self.selected_idx]
        if self.state == self.STATE_DETAIL:
            self._render_detail(pk)
        elif self.state == self.STATE_SWAP:
            self._render_swap(pk)

    def _render_detail(self, pk: Pokemon):
        # Name + level
        name_s = self.font_large.render(
            f"{pk.get_display_name()}  Lv.{pk.level}", True, config.COLOR_WHITE)
        self.display.blit(name_s, (_DX, _NAME_Y))

        # Types
        types_s = self.font_small.render(
            "  ".join(t.value.title() for t in pk.types), True, (180, 200, 230))
        self.display.blit(types_s, (_DX, _TYPES_Y))

        # XP bar
        xp_needed = pk.level * 100
        xp_ratio  = min(1.0, pk.experience_points / max(1, xp_needed))
        xp_lbl = self.font_small.render(
            f"EXP  {pk.experience_points} / {xp_needed}  → Lv.{pk.level + 1}",
            True, (170, 200, 255))
        self.display.blit(xp_lbl, (_DX, _XP_LBL_Y))

        pygame.draw.rect(self.display, _XP_BG,
                         (_DX, _XP_BAR_Y, _DW, 12), border_radius=6)
        if xp_ratio > 0:
            pygame.draw.rect(self.display, _XP_FILL,
                             (_DX, _XP_BAR_Y, int(_DW * xp_ratio), 12), border_radius=6)
        pygame.draw.rect(self.display, _DIVIDER,
                         (_DX, _XP_BAR_Y, _DW, 12), width=1, border_radius=6)

        # Stats (2 rows × 3 cols)
        stats = [
            ("HP",      f"{pk.current_hp}/{pk.max_hp}"),
            ("Attack",  str(pk.attack)),
            ("Defense", str(pk.defense)),
            ("Sp.Atk",  str(pk.sp_attack)),
            ("Sp.Def",  str(pk.sp_defense)),
            ("Speed",   str(pk.speed)),
        ]
        col_w = _DW // 3
        for i, (label, val) in enumerate(stats):
            col = i % 3
            row = i // 3
            sx = _DX + col * col_w
            sy = _STATS_Y + row * 27
            lbl_s = self.font_small.render(f"{label}:", True, _STAT_LBL)
            val_s = self.font_small.render(val, True, _STAT_VAL)
            self.display.blit(lbl_s, (sx, sy))
            self.display.blit(val_s, (sx + lbl_s.get_width() + 4, sy))

        # Divider
        pygame.draw.line(self.display, _DIVIDER,
                         (_DX, _DIV_Y), (config.SCREEN_WIDTH - 10, _DIV_Y), 1)

        # Moves section
        hint_s = self.font_small.render("Moves  (click a move to swap it):", True, _MOVE_HINT)
        self.display.blit(hint_s, (_DX, _MOVES_LBL_Y))

        mouse_pos = pygame.mouse.get_pos()
        for slot, move in enumerate(pk.moves):
            rect = self._move_rect(slot)
            tc   = config.TYPE_COLORS.get(move.type, config.COLOR_GRAY)
            is_hov = rect.collidepoint(mouse_pos)
            if move.current_pp <= 0:
                bg = (70, 70, 80)
            elif is_hov:
                bg = tuple(min(255, c + 40) for c in tc)
            else:
                bg = tc
            pygame.draw.rect(self.display, bg, rect, border_radius=7)
            pygame.draw.rect(self.display, (0, 0, 0, 0), rect, width=1, border_radius=7)

            move_txt = (f"{move.display_name}"
                        f"  [{move.type.value.title()}]"
                        f"  PP {move.current_pp}/{move.max_pp}")
            mt = self.font_small.render(move_txt, True, config.COLOR_WHITE)
            self.display.blit(mt, (rect.x + 10, rect.centery - mt.get_height() // 2))

        if len(pk.moves) == 0:
            no_s = self.font_small.render("No moves!", True, _HINT_COL)
            self.display.blit(no_s, (_DX, _MOVES_Y))

    def _render_swap(self, pk: Pokemon):
        slot     = self.swap_slot
        old_name = pk.moves[slot].display_name if slot < len(pk.moves) else "?"

        hdr_s = self.font_small.render(
            f"Replacing: {old_name}  —  choose a move:", True, _SWAP_HDR)
        self.display.blit(hdr_s, (_DX, _SWAP_HDR_Y))

        scroll_hint = self.font_small.render("Scroll to see more", True, _HINT_COL)
        self.display.blit(scroll_hint,
                          (config.SCREEN_WIDTH - scroll_hint.get_width() - 12,
                           _SWAP_HDR_Y))

        available    = pk.get_available_moves()
        current_set  = {m.name for m in pk.moves}
        mouse_pos    = pygame.mouse.get_pos()

        # Clip region
        clip_rect = pygame.Rect(_DX, _SWAP_CLIP_TOP,
                                 _DW + 10, _SWAP_CLIP_BOT - _SWAP_CLIP_TOP)
        self.display.set_clip(clip_rect)

        for i, move_name in enumerate(available):
            rect = self._swap_item_rect(i)
            if rect.bottom < _SWAP_CLIP_TOP or rect.top > _SWAP_CLIP_BOT:
                continue

            is_cur = move_name in current_set
            is_hov = rect.collidepoint(mouse_pos) and _SWAP_CLIP_TOP <= rect.y

            try:
                m  = Move(move_name)
                tc = config.TYPE_COLORS.get(m.type, config.COLOR_GRAY)
            except Exception:
                m  = None
                tc = config.COLOR_GRAY

            if is_cur:
                bg = _CURRENT_MV
            elif is_hov:
                bg = tuple(min(255, c + 60) for c in tc)
            else:
                bg = tuple(c // 2 + 20 for c in tc)

            pygame.draw.rect(self.display, bg, rect, border_radius=5)

            disp = move_name.replace("_", " ").title()
            if m:
                disp += f"  [{m.type.value.title()}]  PP:{m.max_pp}"
            if is_cur:
                disp += "  ✓ equipped"
            ms = self.font_small.render(disp, True, config.COLOR_WHITE)
            self.display.blit(ms, (rect.x + 8, rect.centery - ms.get_height() // 2))

        self.display.set_clip(None)

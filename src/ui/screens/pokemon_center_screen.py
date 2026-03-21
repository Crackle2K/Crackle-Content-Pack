"""Pokemon Center screen — free healing with a timed animation."""

from __future__ import annotations
import math
import pygame
from typing import Any, Optional

from src.ui import config
from src.ui.screens.base_screen import BaseScreen
from src.ui.asset_manager import AssetManager
from src.entities.trainer import Trainer


_HEAL_DURATION = 3.0   # seconds the progress bar takes to fill
_HEADER_H      = 75
_BAR_W         = 320
_BAR_H         = 22


class PokemonCenterScreen(BaseScreen):
    """Animates a healing timer, then fully restores the player's team."""

    STATE_HEALING = "healing"
    STATE_DONE    = "done"

    def __init__(self, display: pygame.Surface, assets: AssetManager, player: Trainer):
        super().__init__(display, assets)
        self.player  = player
        self.state   = self.STATE_HEALING
        self.elapsed = 0.0
        self._healed = False          # whether we've already called heal_team()
        self._flash  = 0.0            # brief white-flash timer after heal

    # ── Events ────────────────────────────────────────────────────────────────

    def handle_event(self, event: pygame.event.Event) -> Optional[Any]:
        if self.state == self.STATE_DONE:
            if event.type in (pygame.KEYDOWN, pygame.MOUSEBUTTONDOWN):
                return "back"
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            # Allow bailing out early (team is healed immediately)
            if not self._healed:
                self.player.heal_team()
                self._healed = True
            return "back"
        return None

    # ── Update ────────────────────────────────────────────────────────────────

    def update(self, dt: float):
        if self.state == self.STATE_HEALING:
            self.elapsed += dt
            if self.elapsed >= _HEAL_DURATION and not self._healed:
                self.player.heal_team()
                self._healed = True
                self._flash  = 0.35
                self.state   = self.STATE_DONE

        if self._flash > 0:
            self._flash = max(0.0, self._flash - dt)

    # ── Render ────────────────────────────────────────────────────────────────

    def render(self):
        self.display.fill(config.COLOR_BG)
        self._draw_header()
        self._draw_team()
        self._draw_bar()
        self._draw_status_message()

        # Flash overlay when healing completes
        if self._flash > 0:
            alpha = int(180 * (self._flash / 0.35))
            flash_surf = pygame.Surface(
                (config.SCREEN_WIDTH, config.SCREEN_HEIGHT), pygame.SRCALPHA)
            flash_surf.fill((255, 255, 255, alpha))
            self.display.blit(flash_surf, (0, 0))

    def _draw_header(self):
        pygame.draw.rect(self.display, (185, 55, 105),
                         (0, 0, config.SCREEN_WIDTH, _HEADER_H))
        pygame.draw.rect(self.display, config.COLOR_SECONDARY,
                         (0, _HEADER_H - 3, config.SCREEN_WIDTH, 3))
        t = self.font_large.render("POKEMON CENTER", True, config.COLOR_WHITE)
        self.display.blit(t, t.get_rect(centerx=config.SCREEN_WIDTH // 2, centery=36))

    def _draw_team(self):
        """Render each Pokemon's name and HP, greyed-out until healed."""
        row_h = 48
        start_y = _HEADER_H + 18
        for i, pk in enumerate(self.player.team):
            y = start_y + i * row_h
            healed_now = self._healed

            bg = (225, 248, 225) if healed_now else (238, 238, 245)
            row_rect = pygame.Rect(20, y, config.SCREEN_WIDTH - 40, row_h - 6)
            pygame.draw.rect(self.display, bg, row_rect, border_radius=6)
            pygame.draw.rect(self.display, config.COLOR_INFO_BOX_BORDER,
                             row_rect, width=1, border_radius=6)

            name_col = config.COLOR_BLACK if healed_now else config.COLOR_GRAY
            ns = self.font_medium.render(pk.get_display_name(), True, name_col)
            self.display.blit(ns, (row_rect.x + 12, row_rect.y + 8))

            if healed_now:
                status_txt = f"{pk.current_hp}/{pk.max_hp} HP  ✓"
                status_col = (40, 160, 40)
            else:
                old_hp = pk.current_hp
                status_txt = f"{old_hp}/{pk.max_hp} HP"
                status_col = config.COLOR_DARK_GRAY
            hs = self.font_small.render(status_txt, True, status_col)
            self.display.blit(hs, (row_rect.x + 12, row_rect.y + 10 + ns.get_height()))

            lv = self.font_small.render(f"Lv.{pk.level}", True, config.COLOR_GRAY)
            self.display.blit(lv, (row_rect.right - lv.get_width() - 12,
                                    row_rect.centery - lv.get_height() // 2))

    def _draw_bar(self):
        """Progress bar beneath the team list."""
        team_rows = len(self.player.team)
        row_h  = 48
        bar_top = _HEADER_H + 18 + team_rows * row_h + 14

        label = self.font_small.render("Healing…", True, config.COLOR_DARK_GRAY)
        self.display.blit(label,
                          (config.SCREEN_WIDTH // 2 - label.get_width() // 2,
                           bar_top - label.get_height() - 4))

        bar_x = (config.SCREEN_WIDTH - _BAR_W) // 2
        bar_rect = pygame.Rect(bar_x, bar_top, _BAR_W, _BAR_H)
        pygame.draw.rect(self.display, (210, 210, 220), bar_rect, border_radius=_BAR_H // 2)
        pygame.draw.rect(self.display, config.COLOR_INFO_BOX_BORDER,
                         bar_rect, width=1, border_radius=_BAR_H // 2)

        if self.state == self.STATE_HEALING:
            progress = min(1.0, self.elapsed / _HEAL_DURATION)
        else:
            progress = 1.0

        if progress > 0:
            fill_w = max(_BAR_H, int(_BAR_W * progress))
            # Colour shifts green→bright-green as it fills
            r = int(80  + (0   - 80)  * progress)
            g = int(160 + (210 - 160) * progress)
            b = int(80  + (80  - 80)  * progress)
            fill_rect = pygame.Rect(bar_x, bar_top, fill_w, _BAR_H)
            pygame.draw.rect(self.display, (r, g, b), fill_rect,
                             border_radius=_BAR_H // 2)

        # Animated sparkle dot on the fill edge (healing state only)
        if self.state == self.STATE_HEALING and 0 < progress < 1:
            dot_x = bar_x + int(_BAR_W * progress)
            dot_y = bar_top + _BAR_H // 2
            pulse = 0.5 + 0.5 * math.sin(self.elapsed * 8)
            dot_r = int(5 + 3 * pulse)
            pygame.draw.circle(self.display, config.COLOR_WHITE, (dot_x, dot_y), dot_r)

    def _draw_status_message(self):
        footer_y = config.SCREEN_HEIGHT - 56
        pygame.draw.rect(self.display, config.COLOR_BG,
                         (0, footer_y, config.SCREEN_WIDTH, 56))
        pygame.draw.line(self.display, config.COLOR_INFO_BOX_BORDER,
                         (0, footer_y), (config.SCREEN_WIDTH, footer_y), 1)

        if self.state == self.STATE_DONE:
            msg  = "All Pokemon restored!"
            hint = "Press any key to continue"
            ms = self.font_medium.render(msg,  True, (40, 160, 40))
            hs = self.font_small.render(hint,  True, config.COLOR_GRAY)
            self.display.blit(ms, ms.get_rect(centerx=config.SCREEN_WIDTH // 2,
                                               centery=footer_y + 12))
            self.display.blit(hs, hs.get_rect(centerx=config.SCREEN_WIDTH // 2,
                                               centery=footer_y + 12 + ms.get_height() + 4))
        else:
            hint = "ESC to skip"
            hs = self.font_small.render(hint, True, config.COLOR_GRAY)
            self.display.blit(hs, hs.get_rect(centerx=config.SCREEN_WIDTH // 2,
                                               centery=footer_y + 20))

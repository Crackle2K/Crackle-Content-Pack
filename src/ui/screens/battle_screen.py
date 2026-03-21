"""Battle screen for Pokemon battles."""

import json
from pathlib import Path
import pygame
from typing import Any, Optional, List, Tuple

from src.ui import config
from src.ui.screens.base_screen import BaseScreen
from src.ui.components.button import Button
from src.ui.components.hp_bar import HPBar
from src.ui.components.message_box import MessageBox
from src.ui.asset_manager import AssetManager
from src.battle.battle import Battle, BattleEvent


# Load item catalog once for in-battle item use
def _load_catalog() -> dict:
    p = Path("assets/items/catalog.json")
    try:
        return {it["slug"]: it for it in json.loads(p.read_text())} if p.exists() else {}
    except Exception:
        return {}

_CATALOG: dict = {}


class BattleScreen(BaseScreen):
    """Screen for Pokemon battles."""

    STATE_MAIN   = "main"
    STATE_MOVE   = "move"
    STATE_SWITCH = "switch"
    STATE_ITEM   = "item"
    STATE_MESSAGE = "message"
    STATE_RESULT  = "result"

    # Pokeball slugs in priority order
    BALL_PRIORITY = ["ultra-ball", "great-ball", "poke-ball"]

    def __init__(self, display: pygame.Surface, assets: AssetManager, battle: Battle):
        super().__init__(display, assets)

        global _CATALOG
        if not _CATALOG:
            _CATALOG = _load_catalog()

        self.battle   = battle
        self.state    = self.STATE_MESSAGE
        self.player   = battle.player
        self.opponent = battle.opponent

        self.player_sprite   = None
        self.opponent_sprite = None
        self._load_sprites()

        self.opponent_hp_bar = HPBar(86,  62,  230, 18, show_text=True)
        self.player_hp_bar   = HPBar(536, 316, 216, 18, show_text=True)
        self._update_hp_bars(animate=False)

        self.battle_bg = self._create_battle_bg()

        self.message_box = MessageBox(
            20, config.SCREEN_HEIGHT - 180,
            config.SCREEN_WIDTH - 40, 80,
            font=self.font_medium
        )

        self._create_buttons()

        self.event_queue: List[BattleEvent] = []
        self.current_event = None
        self.action_result: Optional[Tuple[str, Any]] = None

    # ── Background / sprites ──────────────────────────────────────────────────

    def _create_battle_bg(self) -> pygame.Surface:
        battle_h  = config.SCREEN_HEIGHT - 180
        surface   = pygame.Surface((config.SCREEN_WIDTH, battle_h))
        horizon   = 230
        sky_top   = config.COLOR_SKY_TOP
        sky_bot   = config.COLOR_SKY_BOTTOM
        grass_top = config.COLOR_GRASS_TOP
        grass_bot = config.COLOR_GRASS_BOTTOM
        for y in range(battle_h):
            if y < horizon:
                t    = y / horizon
                top  = sky_top
                bot  = sky_bot
            else:
                t    = (y - horizon) / max(1, battle_h - horizon)
                top  = grass_top
                bot  = grass_bot
            r = int(top[0] + (bot[0] - top[0]) * t)
            g = int(top[1] + (bot[1] - top[1]) * t)
            b = int(top[2] + (bot[2] - top[2]) * t)
            pygame.draw.line(surface, (r, g, b), (0, y), (config.SCREEN_WIDTH, y))
        return surface

    def _draw_platforms(self):
        opp_cx = config.OPPONENT_SPRITE_POS[0] + 144
        opp_cy = 305
        pygame.draw.ellipse(self.display, config.COLOR_PLATFORM_EDGE,
                            pygame.Rect(opp_cx - 112, opp_cy - 20, 224, 40))
        pygame.draw.ellipse(self.display, config.COLOR_PLATFORM_FILL,
                            pygame.Rect(opp_cx - 108, opp_cy - 15, 216, 30))
        pl_cx = config.PLAYER_SPRITE_POS[0] + 144
        pl_cy = 398
        pygame.draw.ellipse(self.display, config.COLOR_PLATFORM_EDGE,
                            pygame.Rect(pl_cx - 112, pl_cy - 20, 224, 40))
        pygame.draw.ellipse(self.display, config.COLOR_PLATFORM_FILL,
                            pygame.Rect(pl_cx - 108, pl_cy - 15, 216, 30))

    def _load_sprites(self):
        player_pokemon   = self.player.get_active_pokemon()
        opponent_pokemon = self.opponent.get_active_pokemon()
        if player_pokemon:
            self.player_sprite = self.assets.get_sprite_from_pokemon(
                player_pokemon, scale=config.SPRITE_SCALE)
        if opponent_pokemon:
            self.opponent_sprite = self.assets.get_sprite_from_pokemon(
                opponent_pokemon, scale=config.SPRITE_SCALE)

    def _update_hp_bars(self, animate: bool = True):
        player_pokemon   = self.player.get_active_pokemon()
        opponent_pokemon = self.opponent.get_active_pokemon()
        if player_pokemon:
            self.player_hp_bar.set_hp(player_pokemon.current_hp,
                                      player_pokemon.max_hp, animate=animate)
        if opponent_pokemon:
            self.opponent_hp_bar.set_hp(opponent_pokemon.current_hp,
                                        opponent_pokemon.max_hp, animate=animate)

    # ── Button creation ───────────────────────────────────────────────────────

    def _create_buttons(self):
        bw   = 118
        bh   = 45
        by   = config.SCREEN_HEIGHT - 80
        gap  = 10
        # Five main battle actions
        self.main_buttons = [
            Button(30,                by, bw, bh, "Attack",
                   font=self.font_medium, color=config.COLOR_PRIMARY),
            Button(30 +   (bw+gap),  by, bw, bh, "Switch",
                   font=self.font_medium, color=(100, 70, 170)),
            Button(30 + 2*(bw+gap),  by, bw, bh, "Items",
                   font=self.font_medium, color=(60, 140, 70)),
            Button(30 + 3*(bw+gap),  by, bw, bh, "Catch",
                   font=self.font_medium, color=(170, 55, 100)),
            Button(30 + 4*(bw+gap),  by, bw, bh, "Run",
                   font=self.font_medium, color=config.COLOR_ACCENT),
        ]
        self.move_buttons   = []
        self.switch_buttons = []
        self.item_buttons: list[tuple[str, Button]] = []  # (slug, btn)
        self.back_button = Button(
            config.SCREEN_WIDTH - 120, by, 100, bh, "Back",
            font=self.font_medium, color=config.COLOR_GRAY)

    def _update_move_buttons(self):
        self.move_buttons = []
        pokemon = self.player.get_active_pokemon()
        if not pokemon:
            return
        bw, bh = 170, 40
        sx     = 30
        sy     = config.SCREEN_HEIGHT - 85
        for i, move in enumerate(pokemon.moves):
            x = sx + (i % 2) * (bw + 10)
            y = sy + (i // 2) * (bh + 5)
            tc = config.TYPE_COLORS.get(move.type, config.COLOR_GRAY)
            self.move_buttons.append(Button(
                x, y, bw, bh,
                f"{move.display_name}  {move.current_pp}/{move.max_pp}",
                font=self.font_small, color=tc,
                disabled=(move.current_pp <= 0)
            ))

    def _update_switch_buttons(self):
        self.switch_buttons = []
        bw, bh = 200, 40
        sx     = 30
        sy     = config.SCREEN_HEIGHT - 85
        for i, (idx, pk) in enumerate(self.player.get_available_pokemon()):
            if idx == self.player.active_pokemon_index:
                continue
            x = sx + (i % 3) * (bw + 10)
            y = sy + (i // 3) * (bh + 5)
            hp = pk.get_hp_percentage()
            col = (config.COLOR_HP_GREEN if hp > 50
                   else config.COLOR_HP_YELLOW if hp > 20
                   else config.COLOR_HP_RED)
            btn = Button(x, y, bw, bh,
                         f"{pk.name}  {pk.current_hp}/{pk.max_hp}",
                         font=self.font_small, color=col)
            btn.pokemon_index = idx
            self.switch_buttons.append(btn)

    def _update_item_buttons(self):
        """Build buttons for healing/usable items (excludes Pokeballs for use panel)."""
        self.item_buttons = []
        bw, bh = 200, 40
        sx     = 30
        sy     = config.SCREEN_HEIGHT - 85
        usable_slugs = [
            slug for slug, cnt in self.player.items.items()
            if cnt > 0 and _CATALOG.get(slug, {}).get("effect", {}).get("type") not in ("pokeball", "none", None)
        ]
        for i, slug in enumerate(usable_slugs):
            x   = sx + (i % 3) * (bw + 10)
            y   = sy + (i // 3) * (bh + 5)
            meta = _CATALOG.get(slug, {})
            name = meta.get("display_name", slug.replace("-", " ").title())
            cnt  = self.player.items.get(slug, 0)
            btn  = Button(x, y, bw, bh, f"{name}  x{cnt}",
                          font=self.font_small, color=(50, 130, 220))
            self.item_buttons.append((slug, btn))

    # ── Event display ─────────────────────────────────────────────────────────

    def show_events(self, events: List[BattleEvent]):
        self.event_queue = events.copy()
        self.state = self.STATE_MESSAGE
        self._next_event()

    def _next_event(self):
        if self.event_queue:
            self.current_event = self.event_queue.pop(0)
            self.message_box.set_message(self.current_event.message)
            if self.current_event.event_type in ("damage", "faint"):
                self._update_hp_bars()
            if self.current_event.event_type in ("switch", "send_out"):
                self._load_sprites()
                self._update_hp_bars(animate=False)
        else:
            self.current_event = None
            if not self.battle.is_over:
                if self.battle.player_must_switch():
                    self.state = self.STATE_SWITCH
                    self._update_switch_buttons()
                else:
                    self.state = self.STATE_MAIN
            else:
                self.state = self.STATE_RESULT

    # ── Action selection loop ─────────────────────────────────────────────────

    def get_action(self) -> Optional[Tuple[str, Any]]:
        """Run until the player chooses an action. Returns (action, data) or None."""
        self.state = self.STATE_MAIN
        self.action_result = None

        while self.running and self.action_result is None:
            dt = self.clock.tick(config.FPS) / 1000.0
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return ("quit", 0)
                self._handle_action_event(event)
            self.update(dt)
            self.render()
            pygame.display.flip()

        return self.action_result

    def get_forced_switch(self) -> Optional[int]:
        self.state = self.STATE_SWITCH
        self._update_switch_buttons()
        self.action_result = None
        self.message_box.set_message("Choose a Pokemon to send out!")

        while self.running and self.action_result is None:
            dt = self.clock.tick(config.FPS) / 1000.0
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return None
                self._handle_switch_event(event)
            self.update(dt)
            self.render()
            pygame.display.flip()

        if self.action_result:
            return self.action_result[1]
        return None

    # ── Event handling ────────────────────────────────────────────────────────

    def _handle_action_event(self, event: pygame.event.Event):
        if self.state == self.STATE_MAIN:
            for i, btn in enumerate(self.main_buttons):
                if btn.handle_event(event):
                    if i == 0:   # Attack
                        self.state = self.STATE_MOVE
                        self._update_move_buttons()
                    elif i == 1: # Switch
                        self._update_switch_buttons()
                        if self.switch_buttons:
                            self.state = self.STATE_SWITCH
                        # else no other pokemon — stay in main
                    elif i == 2: # Items
                        self._update_item_buttons()
                        if self.item_buttons:
                            self.state = self.STATE_ITEM
                        # else no items — stay in main (button visually disabled)
                    elif i == 3: # Catch
                        # Find best ball in inventory
                        ball = next(
                            (s for s in self.BALL_PRIORITY
                             if self.player.items.get(s, 0) > 0),
                            None)
                        self.action_result = ("catch", ball)
                    elif i == 4: # Run
                        self.action_result = ("run", 0)

        elif self.state == self.STATE_MOVE:
            for i, btn in enumerate(self.move_buttons):
                if btn.handle_event(event):
                    self.action_result = ("move", i)
            if self.back_button.handle_event(event):
                self.state = self.STATE_MAIN

        elif self.state == self.STATE_ITEM:
            for slug, btn in self.item_buttons:
                if btn.handle_event(event):
                    self.action_result = ("item", slug)
            if self.back_button.handle_event(event):
                self.state = self.STATE_MAIN

        elif self.state == self.STATE_SWITCH:
            for btn in self.switch_buttons:
                if btn.handle_event(event):
                    self.action_result = ("switch", btn.pokemon_index)
            if self.back_button.handle_event(event):
                self.state = self.STATE_MAIN

    def _handle_switch_event(self, event: pygame.event.Event):
        for btn in self.switch_buttons:
            if btn.handle_event(event):
                self.action_result = ("switch", btn.pokemon_index)

    def handle_event(self, event: pygame.event.Event) -> Optional[Any]:
        if self.state == self.STATE_MESSAGE:
            if event.type == pygame.MOUSEBUTTONDOWN or (
                event.type == pygame.KEYDOWN and event.key in (pygame.K_RETURN, pygame.K_SPACE)
            ):
                if self.message_box.advance():
                    self._next_event()
        elif self.state == self.STATE_RESULT:
            if event.type == pygame.MOUSEBUTTONDOWN or (
                event.type == pygame.KEYDOWN and event.key in (pygame.K_RETURN, pygame.K_SPACE)
            ):
                return "done"
        return None

    # ── Update / Render ───────────────────────────────────────────────────────

    def update(self, dt: float):
        self.player_hp_bar.update(dt)
        self.opponent_hp_bar.update(dt)
        self.message_box.update(dt)

        mouse_pos = pygame.mouse.get_pos()
        if self.state == self.STATE_MAIN:
            for btn in self.main_buttons:
                btn.update(mouse_pos)
        elif self.state == self.STATE_MOVE:
            for btn in self.move_buttons:
                btn.update(mouse_pos)
            self.back_button.update(mouse_pos)
        elif self.state == self.STATE_ITEM:
            for _, btn in self.item_buttons:
                btn.update(mouse_pos)
            self.back_button.update(mouse_pos)
        elif self.state == self.STATE_SWITCH:
            for btn in self.switch_buttons:
                btn.update(mouse_pos)
            self.back_button.update(mouse_pos)

    def render(self):
        self.display.blit(self.battle_bg, (0, 0))
        self._draw_platforms()

        panel_y = config.SCREEN_HEIGHT - 180
        pygame.draw.rect(self.display, (160, 170, 175),
                         (0, panel_y - 4, config.SCREEN_WIDTH, 4))
        pygame.draw.rect(self.display, config.COLOR_WHITE,
                         (0, panel_y, config.SCREEN_WIDTH, 180))
        pygame.draw.line(self.display, config.COLOR_INFO_BOX_BORDER,
                         (0, panel_y), (config.SCREEN_WIDTH, panel_y), 2)

        self._render_opponent()
        self._render_player()

        if self.state in (self.STATE_MESSAGE, self.STATE_RESULT):
            self.message_box.render(self.display, self.font_medium)

        if self.state == self.STATE_MAIN:
            has_ball = any(self.player.items.get(s, 0) > 0 for s in self.BALL_PRIORITY)
            has_other = any(
                idx != self.player.active_pokemon_index and not pk.is_fainted
                for idx, pk in enumerate(self.player.team)
            )
            self.main_buttons[1].disabled = not has_other   # Switch
            self.main_buttons[3].disabled = not has_ball    # Catch
            for btn in self.main_buttons:
                btn.render(self.display, self.font_medium)

        elif self.state == self.STATE_MOVE:
            # Sub-header
            self._draw_panel_label("Choose a move:")
            for btn in self.move_buttons:
                btn.render(self.display, self.font_small)
            self.back_button.render(self.display, self.font_medium)

        elif self.state == self.STATE_ITEM:
            self._draw_panel_label("Use which item?")
            for _, btn in self.item_buttons:
                btn.render(self.display, self.font_small)
            self.back_button.render(self.display, self.font_medium)

        elif self.state == self.STATE_SWITCH:
            self._draw_panel_label("Send out which Pokemon?")
            for btn in self.switch_buttons:
                btn.render(self.display, self.font_small)
            if not self.battle.player_must_switch():
                self.back_button.render(self.display, self.font_medium)

        if self.state == self.STATE_RESULT:
            self._render_result()

    def _draw_panel_label(self, text: str):
        lbl = self.font_small.render(text, True, config.COLOR_DARK_GRAY)
        self.display.blit(lbl, (30, config.SCREEN_HEIGHT - 180 + 8))

    # ── Info-box drawing ──────────────────────────────────────────────────────

    def _draw_info_box(self, box_x, box_y, box_w, box_h, pokemon, hp_bar, name_right=False):
        shadow = pygame.Surface((box_w, box_h), pygame.SRCALPHA)
        pygame.draw.rect(shadow, (0, 0, 0, 45), shadow.get_rect(), border_radius=10)
        self.display.blit(shadow, (box_x + 4, box_y + 4))

        pygame.draw.rect(self.display, config.COLOR_INFO_BOX,
                         (box_x, box_y, box_w, box_h), border_radius=10)
        pygame.draw.rect(self.display, config.COLOR_INFO_BOX_BORDER,
                         (box_x, box_y, box_w, box_h), width=2, border_radius=10)

        name_surf = self.font_medium.render(pokemon.get_display_name(), True, config.COLOR_BLACK)
        lvl_surf  = self.font_small.render(f"Lv.{pokemon.level}", True, config.COLOR_DARK_GRAY)

        if name_right:
            self.display.blit(name_surf, (box_x + box_w - name_surf.get_width() - 10, box_y + 8))
            self.display.blit(lvl_surf,  (box_x + 10, box_y + 12))
        else:
            self.display.blit(name_surf, (box_x + 10, box_y + 8))
            self.display.blit(lvl_surf,  (box_x + box_w - lvl_surf.get_width() - 10, box_y + 12))

        hp_label = self.font_small.render("HP", True, config.COLOR_DARK_GRAY)
        self.display.blit(hp_label, (box_x + 10, hp_bar.rect.y + 1))
        hp_bar.render(self.display, self.font_small)

    def _render_opponent(self):
        opp = self.opponent.get_active_pokemon()
        if not opp:
            return
        self._draw_info_box(48, 14, 300, 82, opp, self.opponent_hp_bar)
        if self.opponent_sprite:
            self.display.blit(self.opponent_sprite, config.OPPONENT_SPRITE_POS)

    def _render_player(self):
        pl = self.player.get_active_pokemon()
        if not pl:
            return
        if self.player_sprite:
            self.display.blit(self.player_sprite, config.PLAYER_SPRITE_POS)
        self._draw_info_box(498, 256, 272, 88, pl, self.player_hp_bar)

    def _render_result(self):
        overlay = pygame.Surface((config.SCREEN_WIDTH, config.SCREEN_HEIGHT))
        overlay.fill(config.COLOR_BLACK)
        overlay.set_alpha(128)
        self.display.blit(overlay, (0, 0))

        if self.battle.winner == self.battle.player:
            text, color = "VICTORY!", config.COLOR_HP_GREEN
        else:
            text, color = "DEFEAT...", config.COLOR_HP_RED

        ts = self.font_title.render(text, True, color)
        self.display.blit(ts, ts.get_rect(center=(config.SCREEN_WIDTH // 2,
                                                   config.SCREEN_HEIGHT // 2 - 50)))
        ps = self.font_medium.render("Press any key to continue", True, config.COLOR_WHITE)
        self.display.blit(ps, ps.get_rect(center=(config.SCREEN_WIDTH // 2,
                                                   config.SCREEN_HEIGHT // 2 + 50)))

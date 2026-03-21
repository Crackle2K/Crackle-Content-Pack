"""Battle screen for Pokemon battles."""

import pygame
from typing import Any, Optional, List, Tuple

from src.ui import config
from src.ui.screens.base_screen import BaseScreen
from src.ui.components.button import Button
from src.ui.components.hp_bar import HPBar
from src.ui.components.message_box import MessageBox
from src.ui.components.pokemon_card import PokemonCard
from src.ui.asset_manager import AssetManager
from src.battle.battle import Battle, BattleEvent


class BattleScreen(BaseScreen):
    """Screen for Pokemon battles."""

    # Battle menu states
    STATE_MAIN = "main"
    STATE_MOVE = "move"
    STATE_SWITCH = "switch"
    STATE_MESSAGE = "message"
    STATE_RESULT = "result"

    def __init__(
        self,
        display: pygame.Surface,
        assets: AssetManager,
        battle: Battle
    ):
        """
        Initialize the battle screen.

        Args:
            display: The pygame display surface
            assets: The asset manager
            battle: The Battle object
        """
        super().__init__(display, assets)

        self.battle = battle
        self.state = self.STATE_MESSAGE
        self.selected_index = 0

        # Player and opponent data
        self.player = battle.player
        self.opponent = battle.opponent

        # Load sprites
        self.player_sprite = None
        self.opponent_sprite = None
        self._load_sprites()

        # HP bars — positioned inside styled info boxes
        # Opponent info box: top-left area (x=48, y=14, w=300, h=82)
        self.opponent_hp_bar = HPBar(
            86, 62,
            230, 18, show_text=True
        )
        # Player info box: right side (x=500, y=258, w=270, h=88)
        self.player_hp_bar = HPBar(
            536, 316,
            216, 18, show_text=True
        )
        self._update_hp_bars(animate=False)

        # Pre-render gradient battle background
        self.battle_bg = self._create_battle_bg()

        # Message box
        self.message_box = MessageBox(
            20, config.SCREEN_HEIGHT - 180,
            config.SCREEN_WIDTH - 40, 80,
            font=self.font_medium
        )

        # Action buttons
        self._create_buttons()

        # Event queue
        self.event_queue: List[BattleEvent] = []
        self.current_event = None

        # Result tracking
        self.action_result: Optional[Tuple[str, int]] = None

    def _create_battle_bg(self) -> pygame.Surface:
        """Pre-render a sky-to-grass gradient for the battle area."""
        battle_h = config.SCREEN_HEIGHT - 180
        surface = pygame.Surface((config.SCREEN_WIDTH, battle_h))
        horizon = 230

        sky_top = config.COLOR_SKY_TOP
        sky_bot = config.COLOR_SKY_BOTTOM
        grass_top = config.COLOR_GRASS_TOP
        grass_bot = config.COLOR_GRASS_BOTTOM

        for y in range(battle_h):
            if y < horizon:
                t = y / horizon
                r = int(sky_top[0] + (sky_bot[0] - sky_top[0]) * t)
                g = int(sky_top[1] + (sky_bot[1] - sky_top[1]) * t)
                b = int(sky_top[2] + (sky_bot[2] - sky_top[2]) * t)
            else:
                t = (y - horizon) / (battle_h - horizon)
                r = int(grass_top[0] + (grass_bot[0] - grass_top[0]) * t)
                g = int(grass_top[1] + (grass_bot[1] - grass_top[1]) * t)
                b = int(grass_top[2] + (grass_bot[2] - grass_top[2]) * t)
            pygame.draw.line(surface, (r, g, b), (0, y), (config.SCREEN_WIDTH, y))

        return surface

    def _draw_platforms(self):
        """Draw oval grass platforms under each Pokemon."""
        # Opponent platform (upper-left quadrant)
        opp_cx = config.OPPONENT_SPRITE_POS[0] + 144
        opp_cy = 305
        opp_outer = pygame.Rect(opp_cx - 112, opp_cy - 20, 224, 40)
        opp_inner = pygame.Rect(opp_cx - 108, opp_cy - 15, 216, 30)
        pygame.draw.ellipse(self.display, config.COLOR_PLATFORM_EDGE, opp_outer)
        pygame.draw.ellipse(self.display, config.COLOR_PLATFORM_FILL, opp_inner)

        # Player platform (lower-right quadrant)
        pl_cx = config.PLAYER_SPRITE_POS[0] + 144
        pl_cy = 398
        pl_outer = pygame.Rect(pl_cx - 112, pl_cy - 20, 224, 40)
        pl_inner = pygame.Rect(pl_cx - 108, pl_cy - 15, 216, 30)
        pygame.draw.ellipse(self.display, config.COLOR_PLATFORM_EDGE, pl_outer)
        pygame.draw.ellipse(self.display, config.COLOR_PLATFORM_FILL, pl_inner)

    def _load_sprites(self):
        """Load Pokemon sprites."""
        player_pokemon = self.player.get_active_pokemon()
        opponent_pokemon = self.opponent.get_active_pokemon()

        if player_pokemon:
            self.player_sprite = self.assets.get_sprite_from_pokemon(
                player_pokemon, scale=config.SPRITE_SCALE
            )
        if opponent_pokemon:
            self.opponent_sprite = self.assets.get_sprite_from_pokemon(
                opponent_pokemon, scale=config.SPRITE_SCALE
            )

    def _update_hp_bars(self, animate: bool = True):
        """Update HP bars with current Pokemon HP."""
        player_pokemon = self.player.get_active_pokemon()
        opponent_pokemon = self.opponent.get_active_pokemon()

        if player_pokemon:
            self.player_hp_bar.set_hp(
                player_pokemon.current_hp,
                player_pokemon.max_hp,
                animate=animate
            )
        if opponent_pokemon:
            self.opponent_hp_bar.set_hp(
                opponent_pokemon.current_hp,
                opponent_pokemon.max_hp,
                animate=animate
            )

    def _create_buttons(self):
        """Create action buttons."""
        button_width = 150
        button_height = 45
        button_y = config.SCREEN_HEIGHT - 80

        # Main action buttons
        self.main_buttons = [
            Button(40, button_y, button_width, button_height, "Fight",
                   font=self.font_medium, color=config.COLOR_PRIMARY),
            Button(200, button_y, button_width, button_height, "Pokemon",
                   font=self.font_medium, color=config.COLOR_HP_GREEN),
            Button(360, button_y, button_width, button_height, "Run",
                   font=self.font_medium, color=config.COLOR_ACCENT),
        ]

        # Move buttons (will be updated dynamically)
        self.move_buttons = []

        # Switch buttons (will be updated dynamically)
        self.switch_buttons = []

        # Back button
        self.back_button = Button(
            config.SCREEN_WIDTH - 120, button_y,
            100, button_height, "Back",
            font=self.font_medium, color=config.COLOR_GRAY
        )

    def _update_move_buttons(self):
        """Update move buttons based on active Pokemon."""
        self.move_buttons = []
        pokemon = self.player.get_active_pokemon()

        if not pokemon:
            return

        button_width = 170
        button_height = 40
        start_x = 30
        start_y = config.SCREEN_HEIGHT - 85

        for i, move in enumerate(pokemon.moves):
            x = start_x + (i % 2) * (button_width + 10)
            y = start_y + (i // 2) * (button_height + 5)

            type_color = config.TYPE_COLORS.get(move.type, config.COLOR_GRAY)
            disabled = move.current_pp <= 0

            button = Button(
                x, y, button_width, button_height,
                f"{move.display_name} {move.current_pp}/{move.max_pp}",
                font=self.font_small,
                color=type_color,
                disabled=disabled
            )
            self.move_buttons.append(button)

    def _update_switch_buttons(self):
        """Update switch buttons based on available Pokemon."""
        self.switch_buttons = []
        available = self.player.get_available_pokemon()

        button_width = 200
        button_height = 40
        start_x = 30
        start_y = config.SCREEN_HEIGHT - 85

        for i, (idx, pokemon) in enumerate(available):
            if idx == self.player.active_pokemon_index:
                continue  # Skip active Pokemon

            x = start_x + (i % 3) * (button_width + 10)
            y = start_y + (i // 3) * (button_height + 5)

            hp_percent = pokemon.get_hp_percentage()
            if hp_percent > 50:
                color = config.COLOR_HP_GREEN
            elif hp_percent > 20:
                color = config.COLOR_HP_YELLOW
            else:
                color = config.COLOR_HP_RED

            button = Button(
                x, y, button_width, button_height,
                f"{pokemon.name} {pokemon.current_hp}/{pokemon.max_hp}",
                font=self.font_small,
                color=color
            )
            button.pokemon_index = idx  # Store the actual index
            self.switch_buttons.append(button)

    def show_events(self, events: List[BattleEvent]):
        """Queue battle events to display."""
        self.event_queue = events.copy()
        self.state = self.STATE_MESSAGE
        self._next_event()

    def _next_event(self):
        """Move to the next event in the queue."""
        if self.event_queue:
            self.current_event = self.event_queue.pop(0)
            self.message_box.set_message(self.current_event.message)

            # Update HP bars on damage events
            if self.current_event.event_type in ("damage", "faint"):
                self._update_hp_bars()

            # Update sprites on switch/send_out events
            if self.current_event.event_type in ("switch", "send_out"):
                self._load_sprites()
                self._update_hp_bars(animate=False)
        else:
            self.current_event = None
            # Return to main menu if battle not over
            if not self.battle.is_over:
                if self.battle.player_must_switch():
                    self.state = self.STATE_SWITCH
                    self._update_switch_buttons()
                else:
                    self.state = self.STATE_MAIN
            else:
                self.state = self.STATE_RESULT

    def get_action(self) -> Optional[Tuple[str, int]]:
        """
        Run until the player selects an action.

        Returns:
            Tuple of (action_type, index) or None if window closed
        """
        self.state = self.STATE_MAIN
        self.action_result = None

        while self.running and self.action_result is None:
            dt = self.clock.tick(config.FPS) / 1000.0

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return None
                self._handle_action_event(event)

            self.update(dt)
            self.render()
            pygame.display.flip()

        return self.action_result

    def get_forced_switch(self) -> Optional[int]:
        """
        Run until the player selects a Pokemon to switch to.

        Returns:
            Index of Pokemon to switch to, or None if window closed
        """
        self.state = self.STATE_SWITCH
        self._update_switch_buttons()
        self.action_result = None

        # Show forced switch message
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
            return self.action_result[1]  # Return just the index
        return None

    def _handle_action_event(self, event: pygame.event.Event):
        """Handle events during action selection."""
        if self.state == self.STATE_MAIN:
            for i, button in enumerate(self.main_buttons):
                if button.handle_event(event):
                    if i == 0:  # Fight
                        self.state = self.STATE_MOVE
                        self._update_move_buttons()
                    elif i == 1:  # Pokemon
                        self.state = self.STATE_SWITCH
                        self._update_switch_buttons()
                    elif i == 2:  # Run
                        self.action_result = ("run", 0)

        elif self.state == self.STATE_MOVE:
            for i, button in enumerate(self.move_buttons):
                if button.handle_event(event):
                    self.action_result = ("move", i)

            if self.back_button.handle_event(event):
                self.state = self.STATE_MAIN

        elif self.state == self.STATE_SWITCH:
            for button in self.switch_buttons:
                if button.handle_event(event):
                    self.action_result = ("switch", button.pokemon_index)

            if self.back_button.handle_event(event):
                self.state = self.STATE_MAIN

    def _handle_switch_event(self, event: pygame.event.Event):
        """Handle events during forced switch."""
        for button in self.switch_buttons:
            if button.handle_event(event):
                self.action_result = ("switch", button.pokemon_index)

    def handle_event(self, event: pygame.event.Event) -> Optional[Any]:
        """Handle pygame events."""
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

    def update(self, dt: float):
        """Update the battle screen."""
        # Update HP bars
        self.player_hp_bar.update(dt)
        self.opponent_hp_bar.update(dt)

        # Update message box
        self.message_box.update(dt)

        # Update buttons
        mouse_pos = pygame.mouse.get_pos()

        if self.state == self.STATE_MAIN:
            for button in self.main_buttons:
                button.update(mouse_pos)
        elif self.state == self.STATE_MOVE:
            for button in self.move_buttons:
                button.update(mouse_pos)
            self.back_button.update(mouse_pos)
        elif self.state == self.STATE_SWITCH:
            for button in self.switch_buttons:
                button.update(mouse_pos)
            self.back_button.update(mouse_pos)

    def render(self):
        """Render the battle screen."""
        # Draw gradient battle background
        self.display.blit(self.battle_bg, (0, 0))

        # Draw grass platforms under sprites
        self._draw_platforms()

        # Draw action panel
        panel_y = config.SCREEN_HEIGHT - 180
        # Subtle top shadow strip
        pygame.draw.rect(
            self.display,
            (160, 170, 175),
            (0, panel_y - 4, config.SCREEN_WIDTH, 4)
        )
        # Panel fill
        pygame.draw.rect(
            self.display,
            config.COLOR_WHITE,
            (0, panel_y, config.SCREEN_WIDTH, 180)
        )
        # Panel top border
        pygame.draw.line(
            self.display,
            config.COLOR_INFO_BOX_BORDER,
            (0, panel_y),
            (config.SCREEN_WIDTH, panel_y),
            2
        )

        # Draw opponent Pokemon
        self._render_opponent()

        # Draw player Pokemon
        self._render_player()

        # Draw message box (always visible during message state)
        if self.state == self.STATE_MESSAGE or self.state == self.STATE_RESULT:
            self.message_box.render(self.display, self.font_medium)

        # Draw action buttons
        if self.state == self.STATE_MAIN:
            for button in self.main_buttons:
                button.render(self.display, self.font_medium)
        elif self.state == self.STATE_MOVE:
            for button in self.move_buttons:
                button.render(self.display, self.font_small)
            self.back_button.render(self.display, self.font_medium)
        elif self.state == self.STATE_SWITCH:
            for button in self.switch_buttons:
                button.render(self.display, self.font_small)
            # Only show back button if not forced switch
            if not self.battle.player_must_switch():
                self.back_button.render(self.display, self.font_medium)

        # Draw result overlay
        if self.state == self.STATE_RESULT:
            self._render_result()

    def _draw_info_box(self, box_x: int, box_y: int, box_w: int, box_h: int,
                       pokemon, hp_bar: 'HPBar', name_right: bool = False):
        """Draw a styled Pokemon info box (name, level, HP)."""
        # Drop shadow
        shadow_surf = pygame.Surface((box_w, box_h), pygame.SRCALPHA)
        pygame.draw.rect(shadow_surf, (0, 0, 0, 45), shadow_surf.get_rect(), border_radius=10)
        self.display.blit(shadow_surf, (box_x + 4, box_y + 4))

        # Box background
        pygame.draw.rect(
            self.display, config.COLOR_INFO_BOX,
            (box_x, box_y, box_w, box_h), border_radius=10
        )
        # Box border
        pygame.draw.rect(
            self.display, config.COLOR_INFO_BOX_BORDER,
            (box_x, box_y, box_w, box_h), width=2, border_radius=10
        )

        # Pokemon name
        name_surf = self.font_medium.render(pokemon.get_display_name(), True, config.COLOR_BLACK)
        # Level label (right-aligned)
        lvl_surf = self.font_small.render(f"Lv.{pokemon.level}", True, config.COLOR_DARK_GRAY)

        if name_right:
            # Name right-aligned, level to left
            self.display.blit(name_surf, (box_x + box_w - name_surf.get_width() - 10, box_y + 8))
            self.display.blit(lvl_surf, (box_x + 10, box_y + 12))
        else:
            self.display.blit(name_surf, (box_x + 10, box_y + 8))
            self.display.blit(lvl_surf, (box_x + box_w - lvl_surf.get_width() - 10, box_y + 12))

        # "HP" label
        hp_label = self.font_small.render("HP", True, config.COLOR_DARK_GRAY)
        self.display.blit(hp_label, (box_x + 10, hp_bar.rect.y + 1))

        # HP bar
        hp_bar.render(self.display, self.font_small)

    def _render_opponent(self):
        """Render opponent Pokemon area."""
        opponent_pokemon = self.opponent.get_active_pokemon()
        if not opponent_pokemon:
            return

        # Styled info box (top-left area)
        self._draw_info_box(48, 14, 300, 82, opponent_pokemon, self.opponent_hp_bar)

        # Draw sprite on top (transparent areas let the box show through)
        if self.opponent_sprite:
            self.display.blit(self.opponent_sprite, config.OPPONENT_SPRITE_POS)

    def _render_player(self):
        """Render player Pokemon area."""
        player_pokemon = self.player.get_active_pokemon()
        if not player_pokemon:
            return

        # Draw sprite first, then info box on top
        if self.player_sprite:
            self.display.blit(self.player_sprite, config.PLAYER_SPRITE_POS)

        # Styled info box (bottom-right area)
        self._draw_info_box(498, 256, 272, 88, player_pokemon, self.player_hp_bar, name_right=False)

    def _render_result(self):
        """Render battle result overlay."""
        # Semi-transparent overlay
        overlay = pygame.Surface((config.SCREEN_WIDTH, config.SCREEN_HEIGHT))
        overlay.fill(config.COLOR_BLACK)
        overlay.set_alpha(128)
        self.display.blit(overlay, (0, 0))

        # Result text
        if self.battle.winner == self.battle.player:
            text = "VICTORY!"
            color = config.COLOR_HP_GREEN
        else:
            text = "DEFEAT..."
            color = config.COLOR_HP_RED

        text_surface = self.font_title.render(text, True, color)
        text_rect = text_surface.get_rect(center=(config.SCREEN_WIDTH // 2, config.SCREEN_HEIGHT // 2 - 50))
        self.display.blit(text_surface, text_rect)

        # Continue prompt
        prompt = "Press any key to continue"
        prompt_surface = self.font_medium.render(prompt, True, config.COLOR_WHITE)
        prompt_rect = prompt_surface.get_rect(center=(config.SCREEN_WIDTH // 2, config.SCREEN_HEIGHT // 2 + 50))
        self.display.blit(prompt_surface, prompt_rect)

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

        # HP bars
        self.player_hp_bar = HPBar(
            config.SCREEN_WIDTH - 280, 320,
            200, 25, show_text=True
        )
        self.opponent_hp_bar = HPBar(
            80, 80,
            200, 25, show_text=True
        )
        self._update_hp_bars(animate=False)

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
        # Draw background
        self.fill_background(config.COLOR_BATTLE_BG)

        # Draw battle area separator
        pygame.draw.rect(
            self.display,
            config.COLOR_WHITE,
            (0, config.SCREEN_HEIGHT - 180, config.SCREEN_WIDTH, 180)
        )
        pygame.draw.line(
            self.display,
            config.COLOR_BLACK,
            (0, config.SCREEN_HEIGHT - 180),
            (config.SCREEN_WIDTH, config.SCREEN_HEIGHT - 180),
            3
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

    def _render_opponent(self):
        """Render opponent Pokemon area."""
        opponent_pokemon = self.opponent.get_active_pokemon()
        if not opponent_pokemon:
            return

        # Draw sprite
        if self.opponent_sprite:
            self.display.blit(self.opponent_sprite, config.OPPONENT_SPRITE_POS)

        # Draw info box
        info_x = 80
        info_y = 20

        # Name and level
        name_text = f"{opponent_pokemon.get_display_name()}  Lv.{opponent_pokemon.level}"
        name_surface = self.font_medium.render(name_text, True, config.COLOR_BLACK)
        self.display.blit(name_surface, (info_x, info_y))

        # HP bar
        self.opponent_hp_bar.render(self.display, self.font_small)

    def _render_player(self):
        """Render player Pokemon area."""
        player_pokemon = self.player.get_active_pokemon()
        if not player_pokemon:
            return

        # Draw sprite
        if self.player_sprite:
            self.display.blit(self.player_sprite, config.PLAYER_SPRITE_POS)

        # Draw info box
        info_x = config.SCREEN_WIDTH - 280
        info_y = 260

        # Name and level
        name_text = f"{player_pokemon.get_display_name()}  Lv.{player_pokemon.level}"
        name_surface = self.font_medium.render(name_text, True, config.COLOR_BLACK)
        self.display.blit(name_surface, (info_x, info_y))

        # HP bar is rendered separately

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

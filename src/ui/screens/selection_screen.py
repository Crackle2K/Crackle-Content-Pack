"""Pokemon selection screen."""

import pygame
from typing import Any, Optional, List

from src.ui import config
from src.ui.screens.base_screen import BaseScreen
from src.ui.components.button import Button
from src.ui.components.pokemon_card import PokemonCard
from src.ui.components.text_input import TextInput
from src.ui.asset_manager import AssetManager


class SelectionScreen(BaseScreen):
    """Screen for selecting Pokemon from a list."""

    def __init__(
        self,
        display: pygame.Surface,
        assets: AssetManager,
        pokemon_list: List,
        title: str = "Choose your Pokemon:"
    ):
        """
        Initialize the selection screen.

        Args:
            display: The pygame display surface
            assets: The asset manager
            pokemon_list: List of Pokemon to choose from
            title: Title to display
        """
        super().__init__(display, assets)

        self.title = title
        self.pokemon_list = pokemon_list
        self.selected_index = 0

        # Create Pokemon cards
        self.cards = []
        card_width = 160
        card_height = 200
        cards_per_row = min(4, len(pokemon_list))
        total_width = cards_per_row * (card_width + 20) - 20
        start_x = (config.SCREEN_WIDTH - total_width) // 2

        for i, pokemon in enumerate(pokemon_list):
            row = i // cards_per_row
            col = i % cards_per_row
            x = start_x + col * (card_width + 20)
            y = 120 + row * (card_height + 20)

            card = PokemonCard(x, y, card_width, card_height, show_stats=True)
            card.set_pokemon(pokemon, assets, sprite_scale=1.5)
            self.cards.append(card)

        if self.cards:
            self.cards[0].set_selected(True)

        # Select button
        self.select_button = Button(
            (config.SCREEN_WIDTH - 200) // 2,
            config.SCREEN_HEIGHT - 70,
            200, 50,
            "Select",
            font=self.font_large,
            on_click=self._confirm_selection
        )

        self._pending_result = None

    def _confirm_selection(self):
        """Confirm the current selection."""
        self._pending_result = self.selected_index

    def handle_event(self, event: pygame.event.Event) -> Optional[Any]:
        """Handle pygame events."""
        # Handle card clicks
        for i, card in enumerate(self.cards):
            if card.handle_event(event):
                # Update selection
                self.cards[self.selected_index].set_selected(False)
                self.selected_index = i
                self.cards[self.selected_index].set_selected(True)

        # Handle button click
        if self.select_button.handle_event(event):
            return self._pending_result

        # Keyboard navigation
        if event.type == pygame.KEYDOWN:
            cards_per_row = min(4, len(self.pokemon_list))

            if event.key == pygame.K_LEFT:
                self._move_selection(-1)
            elif event.key == pygame.K_RIGHT:
                self._move_selection(1)
            elif event.key == pygame.K_UP:
                self._move_selection(-cards_per_row)
            elif event.key == pygame.K_DOWN:
                self._move_selection(cards_per_row)
            elif event.key == pygame.K_RETURN:
                self._confirm_selection()
                return self._pending_result

        return None

    def _move_selection(self, delta: int):
        """Move the selection by delta."""
        new_index = self.selected_index + delta
        if 0 <= new_index < len(self.cards):
            self.cards[self.selected_index].set_selected(False)
            self.selected_index = new_index
            self.cards[self.selected_index].set_selected(True)

    def update(self, dt: float):
        """Update the selection screen."""
        mouse_pos = pygame.mouse.get_pos()

        for card in self.cards:
            card.update(mouse_pos)

        self.select_button.update(mouse_pos)

    def render(self):
        """Render the selection screen."""
        self.fill_background(config.COLOR_BG)

        # Draw title
        self.draw_text_centered(self.title, 30, self.font_large)

        # Draw separator
        pygame.draw.line(
            self.display,
            config.COLOR_GRAY,
            (50, 80),
            (config.SCREEN_WIDTH - 50, 80),
            2
        )

        # Draw cards
        for card in self.cards:
            card.render(self.display, self.font_medium, self.font_small)

        # Draw select button
        self.select_button.render(self.display, self.font_large)

        # Draw instructions
        instructions = "Arrow Keys to navigate, Enter to select"
        inst_surface = self.font_small.render(instructions, True, config.COLOR_GRAY)
        inst_rect = inst_surface.get_rect(centerx=config.SCREEN_WIDTH // 2, bottom=config.SCREEN_HEIGHT - 10)
        self.display.blit(inst_surface, inst_rect)


class NameInputScreen(BaseScreen):
    """Screen for entering player name."""

    def __init__(self, display: pygame.Surface, assets: AssetManager):
        """
        Initialize the name input screen.

        Args:
            display: The pygame display surface
            assets: The asset manager
        """
        super().__init__(display, assets)

        # Create text input
        input_width = 300
        input_height = 50
        self.text_input = TextInput(
            (config.SCREEN_WIDTH - input_width) // 2,
            250,
            input_width,
            input_height,
            font=self.font_large,
            max_length=15,
            placeholder="Enter name..."
        )
        self.text_input.focus()

        # Confirm button
        self.confirm_button = Button(
            (config.SCREEN_WIDTH - 200) // 2,
            350,
            200, 50,
            "Confirm",
            font=self.font_large,
            on_click=self._confirm
        )

        self._pending_result = None

    def _confirm(self):
        """Confirm the entered name."""
        name = self.text_input.get_text().strip()
        self._pending_result = name if name else "Trainer"

    def handle_event(self, event: pygame.event.Event) -> Optional[Any]:
        """Handle pygame events."""
        # Handle text input
        if self.text_input.handle_event(event):
            self._confirm()
            return self._pending_result

        # Handle button click
        if self.confirm_button.handle_event(event):
            return self._pending_result

        return None

    def update(self, dt: float):
        """Update the name input screen."""
        self.text_input.update(dt)
        mouse_pos = pygame.mouse.get_pos()
        self.confirm_button.update(mouse_pos)

    def render(self):
        """Render the name input screen."""
        self.fill_background(config.COLOR_BG)

        # Draw title
        self.draw_text_centered("What is your name, trainer?", 150, self.font_large)

        # Draw text input
        self.text_input.render(self.display, self.font_large)

        # Draw confirm button
        self.confirm_button.render(self.display, self.font_large)

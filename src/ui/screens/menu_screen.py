"""Main menu screen."""

import pygame
from typing import Any, Optional

from src.ui import config
from src.ui.screens.base_screen import BaseScreen
from src.ui.components.button import Button
from src.ui.asset_manager import AssetManager


class MenuScreen(BaseScreen):
    """Main menu screen with game options."""

    def __init__(self, display: pygame.Surface, assets: AssetManager):
        """
        Initialize the menu screen.

        Args:
            display: The pygame display surface
            assets: The asset manager
        """
        super().__init__(display, assets)

        # Create menu buttons
        button_width = 250
        button_height = 50
        button_x = (config.SCREEN_WIDTH - button_width) // 2
        button_y_start = 280
        button_spacing = 70

        self.buttons = [
            Button(
                button_x, button_y_start,
                button_width, button_height,
                "New Game",
                font=self.font_large,
                on_click=lambda: self._set_result("new_game")
            ),
            Button(
                button_x, button_y_start + button_spacing,
                button_width, button_height,
                "Quick Battle",
                font=self.font_large,
                on_click=lambda: self._set_result("quick_battle")
            ),
            Button(
                button_x, button_y_start + button_spacing * 2,
                button_width, button_height,
                "Exit",
                font=self.font_large,
                color=config.COLOR_ACCENT,
                hover_color=(220, 80, 80),
                on_click=lambda: self._set_result("exit")
            ),
        ]

        self.selected_index = 0
        self._pending_result = None

    def _set_result(self, result: str):
        """Set the pending result."""
        self._pending_result = result

    def handle_event(self, event: pygame.event.Event) -> Optional[Any]:
        """Handle pygame events."""
        # Handle button clicks
        for button in self.buttons:
            if button.handle_event(event):
                return self._pending_result

        # Keyboard navigation
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                self.selected_index = (self.selected_index - 1) % len(self.buttons)
            elif event.key == pygame.K_DOWN:
                self.selected_index = (self.selected_index + 1) % len(self.buttons)
            elif event.key == pygame.K_RETURN:
                # Trigger the selected button
                self.buttons[self.selected_index].on_click()
                return self._pending_result

        return None

    def update(self, dt: float):
        """Update the menu screen."""
        mouse_pos = pygame.mouse.get_pos()
        for i, button in enumerate(self.buttons):
            button.update(mouse_pos)
            # Update selection based on hover
            if button.is_hovered:
                self.selected_index = i

    def render(self):
        """Render the menu screen."""
        self.fill_background(config.COLOR_MENU_BG)

        # Draw title
        title_lines = [
            "POKEMON",
            "JUNO"
        ]

        y = 60
        for line in title_lines:
            surface = self.font_title.render(line, True, config.COLOR_SECONDARY)
            rect = surface.get_rect(centerx=config.SCREEN_WIDTH // 2, y=y)
            self.display.blit(surface, rect)
            y += 70

        # Draw subtitle
        subtitle = "A Pokemon Battle Simulator"
        subtitle_surface = self.font_small.render(subtitle, True, config.COLOR_WHITE)
        subtitle_rect = subtitle_surface.get_rect(centerx=config.SCREEN_WIDTH // 2, y=220)
        self.display.blit(subtitle_surface, subtitle_rect)

        # Draw buttons
        for i, button in enumerate(self.buttons):
            # Highlight selected button
            if i == self.selected_index:
                button.is_hovered = True
            button.render(self.display, self.font_large)

        # Draw instructions
        instructions = "Use Arrow Keys and Enter, or Click"
        inst_surface = self.font_small.render(instructions, True, config.COLOR_GRAY)
        inst_rect = inst_surface.get_rect(centerx=config.SCREEN_WIDTH // 2, bottom=config.SCREEN_HEIGHT - 20)
        self.display.blit(inst_surface, inst_rect)

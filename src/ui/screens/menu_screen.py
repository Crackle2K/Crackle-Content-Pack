"""Main menu screen."""

import math
import random
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
                "Exit",
                font=self.font_large,
                color=config.COLOR_ACCENT,
                hover_color=(220, 80, 80),
                on_click=lambda: self._set_result("exit")
            ),
        ]

        self.selected_index = 0
        self._pending_result = None

        # Star field for background animation
        rng = random.Random(42)
        self.stars = [
            (rng.randint(0, config.SCREEN_WIDTH),
             rng.randint(0, config.SCREEN_HEIGHT),
             rng.randint(1, 2),
             rng.uniform(0, math.pi * 2))
            for _ in range(80)
        ]
        self.star_time = 0.0

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
        self.star_time += dt
        mouse_pos = pygame.mouse.get_pos()
        for i, button in enumerate(self.buttons):
            button.update(mouse_pos)
            # Update selection based on hover
            if button.is_hovered:
                self.selected_index = i

    def _draw_pokeball_deco(self, cx: int, cy: int, r: int):
        """Draw a subtle Pokeball decoration blended into the dark background."""
        # Top half (dark red tint)
        pygame.draw.circle(self.display, (75, 28, 28), (cx, cy), r)
        # Bottom half (dark blue-gray blending into bg)
        pygame.draw.rect(self.display, (48, 53, 70), (cx - r, cy, r * 2, r + 1))
        # Horizontal center stripe
        pygame.draw.rect(self.display, (36, 41, 56), (cx - r, cy - 7, r * 2, 14))
        # Center circle outer
        pygame.draw.circle(self.display, (36, 41, 56), (cx, cy), r // 4 + 2)
        # Center circle inner highlight
        pygame.draw.circle(self.display, (58, 63, 80), (cx, cy), r // 4 - 2)
        # Outer ring outline
        pygame.draw.circle(self.display, (50, 55, 72), (cx, cy), r, width=2)

    def render(self):
        """Render the menu screen."""
        self.fill_background(config.COLOR_MENU_BG)

        # Draw twinkling star field
        for x, y, size, phase in self.stars:
            brightness = int(170 + 65 * math.sin(self.star_time * 1.3 + phase))
            pygame.draw.circle(
                self.display,
                (brightness, brightness, min(brightness + 25, 255)),
                (x, y), size
            )

        # Draw decorative Pokeball in the top-right corner (partially cropped)
        self._draw_pokeball_deco(700, 80, 105)

        # Draw title with shadow effect
        title_lines = [
            "POKEMON",
            "JUNO"
        ]

        y = 60
        for line in title_lines:
            # Shadow
            shadow_surface = self.font_title.render(line, True, config.COLOR_BLACK)
            shadow_rect = shadow_surface.get_rect(centerx=config.SCREEN_WIDTH // 2 + 3, y=y + 3)
            self.display.blit(shadow_surface, shadow_rect)
            # Main text
            surface = self.font_title.render(line, True, config.COLOR_SECONDARY)
            rect = surface.get_rect(centerx=config.SCREEN_WIDTH // 2, y=y)
            self.display.blit(surface, rect)
            y += 70

        # Draw subtitle
        subtitle = "A Pokemon Battle Simulator"
        subtitle_surface = self.font_small.render(subtitle, True, config.COLOR_LIGHT_GRAY)
        subtitle_rect = subtitle_surface.get_rect(centerx=config.SCREEN_WIDTH // 2, y=220)
        self.display.blit(subtitle_surface, subtitle_rect)

        # Decorative divider under subtitle
        div_y = 252
        div_cx = config.SCREEN_WIDTH // 2
        pygame.draw.line(self.display, (60, 70, 100), (div_cx - 120, div_y), (div_cx - 10, div_y), 1)
        pygame.draw.circle(self.display, config.COLOR_SECONDARY, (div_cx, div_y), 4)
        pygame.draw.line(self.display, (60, 70, 100), (div_cx + 10, div_y), (div_cx + 120, div_y), 1)

        # Draw buttons
        for i, button in enumerate(self.buttons):
            # Highlight selected button
            if i == self.selected_index:
                button.is_hovered = True
            button.render(self.display, self.font_large)

        # Draw instructions
        instructions = "Use Arrow Keys and Enter, or Click"
        inst_surface = self.font_small.render(instructions, True, config.COLOR_LIGHT_GRAY)
        inst_rect = inst_surface.get_rect(centerx=config.SCREEN_WIDTH // 2, bottom=config.SCREEN_HEIGHT - 20)
        self.display.blit(inst_surface, inst_rect)

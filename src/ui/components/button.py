"""Button component for Pygame UI."""

import pygame
from typing import Optional, Callable, Tuple

from src.ui import config


class Button:
    """A clickable button with hover and pressed states."""

    def __init__(
        self,
        x: int,
        y: int,
        width: int,
        height: int,
        text: str,
        font: pygame.font.Font = None,
        color: Tuple[int, int, int] = None,
        hover_color: Tuple[int, int, int] = None,
        text_color: Tuple[int, int, int] = None,
        disabled: bool = False,
        on_click: Callable = None
    ):
        """
        Initialize a button.

        Args:
            x, y: Position of the button
            width, height: Size of the button
            text: Text to display on the button
            font: Font to use (if None, uses default)
            color: Button background color
            hover_color: Color when hovered
            text_color: Color of the text
            disabled: Whether button is disabled
            on_click: Callback function when clicked
        """
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.font = font
        self.color = color or config.COLOR_BUTTON
        self.hover_color = hover_color or config.COLOR_BUTTON_HOVER
        self.text_color = text_color or config.COLOR_BUTTON_TEXT
        self.disabled = disabled
        self.on_click = on_click

        self.is_hovered = False
        self.is_pressed = False

    def handle_event(self, event: pygame.event.Event) -> bool:
        """
        Handle a pygame event.

        Args:
            event: The pygame event

        Returns:
            True if the button was clicked
        """
        if self.disabled:
            return False

        if event.type == pygame.MOUSEMOTION:
            self.is_hovered = self.rect.collidepoint(event.pos)

        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1 and self.rect.collidepoint(event.pos):
                self.is_pressed = True

        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1 and self.is_pressed:
                self.is_pressed = False
                if self.rect.collidepoint(event.pos):
                    if self.on_click:
                        self.on_click()
                    return True

        return False

    def update(self, mouse_pos: Tuple[int, int]):
        """Update button state based on mouse position."""
        if not self.disabled:
            self.is_hovered = self.rect.collidepoint(mouse_pos)

    def render(self, surface: pygame.Surface, font: pygame.font.Font = None):
        """
        Render the button to a surface.

        Args:
            surface: The surface to render to
            font: Font to use (overrides self.font)
        """
        # Determine color based on state
        if self.disabled:
            color = config.COLOR_BUTTON_DISABLED
        elif self.is_pressed:
            color = config.COLOR_BUTTON_PRESSED
        elif self.is_hovered:
            color = self.hover_color
        else:
            color = self.color

        # Draw button background with rounded corners
        pygame.draw.rect(surface, color, self.rect, border_radius=8)

        # Inner top highlight (subtle gloss effect)
        if not self.disabled and not self.is_pressed:
            highlight_h = max(self.rect.height // 3, 6)
            highlight_surf = pygame.Surface(
                (self.rect.width - 6, highlight_h), pygame.SRCALPHA
            )
            highlight_surf.fill((255, 255, 255, 38))
            surface.blit(highlight_surf, (self.rect.x + 3, self.rect.y + 3))

        # Draw border
        border_color = config.COLOR_DARK_GRAY if self.disabled else config.COLOR_BLACK
        pygame.draw.rect(surface, border_color, self.rect, width=2, border_radius=8)

        # Draw text
        use_font = font or self.font
        if use_font:
            text_color = config.COLOR_GRAY if self.disabled else self.text_color
            text_surface = use_font.render(self.text, True, text_color)
            text_rect = text_surface.get_rect(center=self.rect.center)
            surface.blit(text_surface, text_rect)

    def set_position(self, x: int, y: int):
        """Set the button position."""
        self.rect.x = x
        self.rect.y = y

    def set_text(self, text: str):
        """Set the button text."""
        self.text = text

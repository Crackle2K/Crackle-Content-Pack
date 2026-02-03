"""Text input component for Pygame UI."""

import pygame
from typing import Tuple

from src.ui import config


class TextInput:
    """A text input field for entering text."""

    def __init__(
        self,
        x: int,
        y: int,
        width: int,
        height: int,
        font: pygame.font.Font = None,
        max_length: int = 20,
        placeholder: str = "",
        initial_text: str = ""
    ):
        """
        Initialize a text input.

        Args:
            x, y: Position of the input field
            width, height: Size of the input field
            font: Font to use for text
            max_length: Maximum number of characters
            placeholder: Placeholder text when empty
            initial_text: Initial text value
        """
        self.rect = pygame.Rect(x, y, width, height)
        self.font = font
        self.max_length = max_length
        self.placeholder = placeholder
        self.text = initial_text
        self.active = False
        self.cursor_visible = True
        self.cursor_timer = 0

    def handle_event(self, event: pygame.event.Event) -> bool:
        """
        Handle a pygame event.

        Args:
            event: The pygame event

        Returns:
            True if Enter was pressed and text is not empty
        """
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                self.active = self.rect.collidepoint(event.pos)

        elif event.type == pygame.KEYDOWN and self.active:
            if event.key == pygame.K_RETURN:
                if self.text:
                    return True

            elif event.key == pygame.K_BACKSPACE:
                self.text = self.text[:-1]

            elif event.key == pygame.K_DELETE:
                self.text = ""

            elif event.unicode and len(self.text) < self.max_length:
                # Only allow printable characters
                if event.unicode.isprintable():
                    self.text += event.unicode

        return False

    def update(self, dt: float):
        """
        Update the text input.

        Args:
            dt: Delta time in seconds
        """
        # Blink cursor
        self.cursor_timer += dt
        if self.cursor_timer >= 0.5:
            self.cursor_timer = 0
            self.cursor_visible = not self.cursor_visible

    def render(self, surface: pygame.Surface, font: pygame.font.Font = None):
        """
        Render the text input to a surface.

        Args:
            surface: The surface to render to
            font: Font to use (overrides self.font)
        """
        use_font = font or self.font

        # Draw background
        bg_color = config.COLOR_WHITE
        pygame.draw.rect(surface, bg_color, self.rect, border_radius=4)

        # Draw border (highlighted when active)
        border_color = config.COLOR_PRIMARY if self.active else config.COLOR_GRAY
        pygame.draw.rect(surface, border_color, self.rect, width=2, border_radius=4)

        if use_font:
            # Draw text or placeholder
            if self.text:
                text_color = config.COLOR_BLACK
                display_text = self.text
            else:
                text_color = config.COLOR_GRAY
                display_text = self.placeholder

            text_surface = use_font.render(display_text, True, text_color)
            text_rect = text_surface.get_rect(midleft=(self.rect.x + 10, self.rect.centery))
            surface.blit(text_surface, text_rect)

            # Draw cursor
            if self.active and self.cursor_visible and self.text:
                cursor_x = text_rect.right + 2
                cursor_y1 = self.rect.y + 8
                cursor_y2 = self.rect.bottom - 8
                pygame.draw.line(surface, config.COLOR_BLACK, (cursor_x, cursor_y1), (cursor_x, cursor_y2), 2)
            elif self.active and self.cursor_visible and not self.text:
                cursor_x = self.rect.x + 12
                cursor_y1 = self.rect.y + 8
                cursor_y2 = self.rect.bottom - 8
                pygame.draw.line(surface, config.COLOR_BLACK, (cursor_x, cursor_y1), (cursor_x, cursor_y2), 2)

    def get_text(self) -> str:
        """Get the current text."""
        return self.text

    def set_text(self, text: str):
        """Set the text."""
        self.text = text[:self.max_length]

    def clear(self):
        """Clear the text."""
        self.text = ""

    def focus(self):
        """Give focus to this input."""
        self.active = True

    def unfocus(self):
        """Remove focus from this input."""
        self.active = False

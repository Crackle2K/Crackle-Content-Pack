"""Message box component for Pygame UI."""

import pygame
from typing import List, Optional

from src.ui import config


class MessageBox:
    """A message box for displaying battle text with typewriter effect."""

    def __init__(
        self,
        x: int,
        y: int,
        width: int,
        height: int,
        font: pygame.font.Font = None
    ):
        """
        Initialize a message box.

        Args:
            x, y: Position of the message box
            width, height: Size of the message box
            font: Font for text
        """
        self.rect = pygame.Rect(x, y, width, height)
        self.font = font

        self.messages: List[str] = []
        self.current_message = ""
        self.displayed_chars = 0
        self.char_timer = 0
        self.chars_per_second = 30
        self.is_complete = True
        self.waiting_for_input = False

    def set_message(self, message: str):
        """
        Set a single message to display.

        Args:
            message: The message to display
        """
        self.messages = [message]
        self.current_message = message
        self.displayed_chars = 0
        self.is_complete = False
        self.waiting_for_input = False

    def set_messages(self, messages: List[str]):
        """
        Set multiple messages to display in sequence.

        Args:
            messages: List of messages
        """
        self.messages = messages.copy()
        if self.messages:
            self.current_message = self.messages[0]
            self.displayed_chars = 0
            self.is_complete = False
            self.waiting_for_input = False
        else:
            self.is_complete = True

    def advance(self) -> bool:
        """
        Advance to the next message or complete current one.

        Returns:
            True if all messages are done
        """
        if not self.is_complete:
            # Complete current message instantly
            self.displayed_chars = len(self.current_message)
            self.is_complete = True
            self.waiting_for_input = True
            return False

        if self.waiting_for_input:
            # Move to next message
            if len(self.messages) > 1:
                self.messages.pop(0)
                self.current_message = self.messages[0]
                self.displayed_chars = 0
                self.is_complete = False
                self.waiting_for_input = False
                return False
            else:
                # All done
                self.messages = []
                self.current_message = ""
                return True

        return True

    def update(self, dt: float):
        """
        Update the typewriter effect.

        Args:
            dt: Delta time in seconds
        """
        if not self.is_complete and self.current_message:
            self.char_timer += dt
            chars_to_add = int(self.char_timer * self.chars_per_second)

            if chars_to_add > 0:
                self.char_timer = 0
                self.displayed_chars = min(
                    self.displayed_chars + chars_to_add,
                    len(self.current_message)
                )

                if self.displayed_chars >= len(self.current_message):
                    self.is_complete = True
                    self.waiting_for_input = True

    def render(self, surface: pygame.Surface, font: pygame.font.Font = None):
        """
        Render the message box to a surface.

        Args:
            surface: The surface to render to
            font: Font to use (overrides self.font)
        """
        use_font = font or self.font

        # Draw background
        pygame.draw.rect(surface, config.COLOR_WHITE, self.rect, border_radius=8)

        # Draw border
        pygame.draw.rect(surface, config.COLOR_BLACK, self.rect, width=3, border_radius=8)

        # Draw text
        if use_font and self.current_message:
            display_text = self.current_message[:self.displayed_chars]

            # Word wrap
            words = display_text.split(' ')
            lines = []
            current_line = ""
            max_width = self.rect.width - 40

            for word in words:
                test_line = current_line + (" " if current_line else "") + word
                if use_font.size(test_line)[0] < max_width:
                    current_line = test_line
                else:
                    if current_line:
                        lines.append(current_line)
                    current_line = word

            if current_line:
                lines.append(current_line)

            # Render lines
            y_offset = 15
            for line in lines:
                text_surface = use_font.render(line, True, config.COLOR_BLACK)
                surface.blit(text_surface, (self.rect.x + 20, self.rect.y + y_offset))
                y_offset += use_font.get_height() + 5

        # Draw continue indicator
        if self.waiting_for_input:
            indicator_x = self.rect.right - 30
            indicator_y = self.rect.bottom - 25
            pygame.draw.polygon(
                surface,
                config.COLOR_BLACK,
                [(indicator_x, indicator_y), (indicator_x + 10, indicator_y), (indicator_x + 5, indicator_y + 8)]
            )

    def has_messages(self) -> bool:
        """Check if there are messages to display."""
        return bool(self.messages) or bool(self.current_message)

    def is_waiting(self) -> bool:
        """Check if waiting for user input."""
        return self.waiting_for_input

"""HP bar component for Pygame UI."""

import pygame
from typing import Tuple

from src.ui import config


class HPBar:
    """An animated HP bar for displaying Pokemon health."""

    def __init__(
        self,
        x: int,
        y: int,
        width: int = config.HP_BAR_WIDTH,
        height: int = config.HP_BAR_HEIGHT,
        show_text: bool = True
    ):
        """
        Initialize an HP bar.

        Args:
            x, y: Position of the HP bar
            width, height: Size of the HP bar
            show_text: Whether to show HP text
        """
        self.rect = pygame.Rect(x, y, width, height)
        self.show_text = show_text

        self.current_hp = 100
        self.max_hp = 100
        self.display_hp = 100  # For animation
        self.target_hp = 100

        self.animation_speed = 100  # HP per second

    def set_hp(self, current: int, maximum: int, animate: bool = True):
        """
        Set the HP values.

        Args:
            current: Current HP
            maximum: Maximum HP
            animate: Whether to animate the change
        """
        self.current_hp = current
        self.max_hp = maximum
        self.target_hp = current

        if not animate:
            self.display_hp = current

    def update(self, dt: float):
        """
        Update the HP bar animation.

        Args:
            dt: Delta time in seconds
        """
        if self.display_hp != self.target_hp:
            diff = self.target_hp - self.display_hp
            change = self.animation_speed * dt

            if abs(diff) < change:
                self.display_hp = self.target_hp
            elif diff > 0:
                self.display_hp += change
            else:
                self.display_hp -= change

    def render(self, surface: pygame.Surface, font: pygame.font.Font = None):
        """
        Render the HP bar to a surface.

        Args:
            surface: The surface to render to
            font: Font for HP text
        """
        # Draw background
        pygame.draw.rect(surface, config.COLOR_HP_BG, self.rect, border_radius=4)

        # Calculate fill width
        if self.max_hp > 0:
            hp_percent = self.display_hp / self.max_hp
        else:
            hp_percent = 0

        fill_width = int((self.rect.width - 4) * hp_percent)

        # Determine color based on HP percentage
        if hp_percent > 0.5:
            fill_color = config.COLOR_HP_GREEN
        elif hp_percent > 0.2:
            fill_color = config.COLOR_HP_YELLOW
        else:
            fill_color = config.COLOR_HP_RED

        # Draw fill
        if fill_width > 0:
            fill_rect = pygame.Rect(
                self.rect.x + 2,
                self.rect.y + 2,
                fill_width,
                self.rect.height - 4
            )
            pygame.draw.rect(surface, fill_color, fill_rect, border_radius=2)

        # Draw border
        pygame.draw.rect(surface, config.COLOR_BLACK, self.rect, width=2, border_radius=4)

        # Draw HP text
        if self.show_text and font:
            hp_text = f"{int(self.display_hp)}/{self.max_hp}"
            text_surface = font.render(hp_text, True, config.COLOR_WHITE)
            text_rect = text_surface.get_rect(center=self.rect.center)
            surface.blit(text_surface, text_rect)

    def get_percentage(self) -> float:
        """Get the current HP percentage."""
        if self.max_hp > 0:
            return self.current_hp / self.max_hp
        return 0

    def is_animating(self) -> bool:
        """Check if the HP bar is currently animating."""
        return abs(self.display_hp - self.target_hp) > 0.5

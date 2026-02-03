"""Base screen class for Pygame UI."""

import pygame
from abc import ABC, abstractmethod
from typing import Any, Optional

from src.ui import config
from src.ui.asset_manager import AssetManager


class BaseScreen(ABC):
    """Abstract base class for all game screens."""

    def __init__(self, display: pygame.Surface, assets: AssetManager):
        """
        Initialize the base screen.

        Args:
            display: The pygame display surface
            assets: The asset manager
        """
        self.display = display
        self.assets = assets
        self.clock = pygame.time.Clock()
        self.running = True
        self.result = None

        # Fonts
        self.font_title = assets.get_font(config.FONT_SIZE_TITLE, bold=True)
        self.font_large = assets.get_font(config.FONT_SIZE_LARGE)
        self.font_medium = assets.get_font(config.FONT_SIZE_MEDIUM)
        self.font_small = assets.get_font(config.FONT_SIZE_SMALL)

    @abstractmethod
    def handle_event(self, event: pygame.event.Event) -> Optional[Any]:
        """
        Handle a pygame event.

        Args:
            event: The pygame event

        Returns:
            Result value if screen should exit, None otherwise
        """
        pass

    @abstractmethod
    def update(self, dt: float):
        """
        Update the screen state.

        Args:
            dt: Delta time in seconds
        """
        pass

    @abstractmethod
    def render(self):
        """Render the screen to the display."""
        pass

    def run(self) -> Any:
        """
        Run the screen's event loop.

        Returns:
            The result value when the screen exits
        """
        self.running = True
        self.result = None

        while self.running:
            dt = self.clock.tick(config.FPS) / 1000.0

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                    self.result = None
                    return None

                result = self.handle_event(event)
                if result is not None:
                    self.running = False
                    self.result = result

            self.update(dt)
            self.render()
            pygame.display.flip()

        return self.result

    def draw_text_centered(self, text: str, y: int, font: pygame.font.Font = None,
                           color: tuple = config.COLOR_BLACK):
        """Draw text centered horizontally."""
        use_font = font or self.font_medium
        surface = use_font.render(text, True, color)
        rect = surface.get_rect(centerx=config.SCREEN_WIDTH // 2, y=y)
        self.display.blit(surface, rect)

    def fill_background(self, color: tuple = config.COLOR_BG):
        """Fill the display with a background color."""
        self.display.fill(color)

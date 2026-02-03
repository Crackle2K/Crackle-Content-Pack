"""Pokemon card component for displaying Pokemon info."""

import pygame
from typing import Optional, Tuple

from src.ui import config
from src.ui.asset_manager import AssetManager


class PokemonCard:
    """A card displaying Pokemon sprite and basic info."""

    def __init__(
        self,
        x: int,
        y: int,
        width: int = 180,
        height: int = 220,
        show_stats: bool = True
    ):
        """
        Initialize a Pokemon card.

        Args:
            x, y: Position of the card
            width, height: Size of the card
            show_stats: Whether to show detailed stats
        """
        self.rect = pygame.Rect(x, y, width, height)
        self.show_stats = show_stats
        self.pokemon = None
        self.sprite = None
        self.selected = False
        self.hovered = False

    def set_pokemon(self, pokemon, asset_manager: AssetManager, sprite_scale: float = 1.5):
        """
        Set the Pokemon to display.

        Args:
            pokemon: The Pokemon object
            asset_manager: Asset manager for loading sprites
            sprite_scale: Scale for the sprite
        """
        self.pokemon = pokemon
        if pokemon:
            self.sprite = asset_manager.get_sprite_from_pokemon(pokemon, sprite_scale)
        else:
            self.sprite = None

    def handle_event(self, event: pygame.event.Event) -> bool:
        """
        Handle a pygame event.

        Args:
            event: The pygame event

        Returns:
            True if the card was clicked
        """
        if event.type == pygame.MOUSEMOTION:
            self.hovered = self.rect.collidepoint(event.pos)

        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1 and self.rect.collidepoint(event.pos):
                return True

        return False

    def update(self, mouse_pos: Tuple[int, int]):
        """Update card state based on mouse position."""
        self.hovered = self.rect.collidepoint(mouse_pos)

    def render(self, surface: pygame.Surface, font_large: pygame.font.Font, font_small: pygame.font.Font):
        """
        Render the Pokemon card to a surface.

        Args:
            surface: The surface to render to
            font_large: Font for Pokemon name
            font_small: Font for stats
        """
        # Draw background
        if self.selected:
            bg_color = config.COLOR_SECONDARY
        elif self.hovered:
            bg_color = config.COLOR_LIGHT_GRAY
        else:
            bg_color = config.COLOR_WHITE

        pygame.draw.rect(surface, bg_color, self.rect, border_radius=10)

        # Draw border
        border_color = config.COLOR_PRIMARY if self.selected else config.COLOR_DARK_GRAY
        border_width = 3 if self.selected or self.hovered else 2
        pygame.draw.rect(surface, border_color, self.rect, width=border_width, border_radius=10)

        if not self.pokemon:
            return

        y_offset = self.rect.y + 10

        # Draw sprite
        if self.sprite:
            sprite_x = self.rect.centerx - self.sprite.get_width() // 2
            surface.blit(self.sprite, (sprite_x, y_offset))
            y_offset += self.sprite.get_height() + 5
        else:
            y_offset += 70

        # Draw name
        name_text = f"{self.pokemon.name}"
        name_surface = font_large.render(name_text, True, config.COLOR_BLACK)
        name_rect = name_surface.get_rect(centerx=self.rect.centerx, top=y_offset)
        surface.blit(name_surface, name_rect)
        y_offset += name_surface.get_height() + 2

        # Draw level
        level_text = f"Lv. {self.pokemon.level}"
        level_surface = font_small.render(level_text, True, config.COLOR_DARK_GRAY)
        level_rect = level_surface.get_rect(centerx=self.rect.centerx, top=y_offset)
        surface.blit(level_surface, level_rect)
        y_offset += level_surface.get_height() + 5

        # Draw types
        type_x = self.rect.centerx
        for i, ptype in enumerate(self.pokemon.types):
            type_color = config.TYPE_COLORS.get(ptype, config.COLOR_GRAY)
            type_text = ptype.value.upper()
            type_surface = font_small.render(type_text, True, config.COLOR_WHITE)

            badge_width = type_surface.get_width() + 10
            badge_height = type_surface.get_height() + 4
            badge_x = type_x - badge_width // 2 + (i * (badge_width + 5)) - ((len(self.pokemon.types) - 1) * (badge_width + 5) // 2)

            badge_rect = pygame.Rect(badge_x, y_offset, badge_width, badge_height)
            pygame.draw.rect(surface, type_color, badge_rect, border_radius=4)
            surface.blit(type_surface, (badge_x + 5, y_offset + 2))

        y_offset += badge_height + 8

        # Draw stats if enabled
        if self.show_stats and y_offset < self.rect.bottom - 30:
            stats_text = f"HP:{self.pokemon.max_hp} ATK:{self.pokemon.attack} DEF:{self.pokemon.defense}"
            stats_surface = font_small.render(stats_text, True, config.COLOR_DARK_GRAY)
            stats_rect = stats_surface.get_rect(centerx=self.rect.centerx, top=y_offset)

            # Ensure it fits
            if stats_rect.bottom < self.rect.bottom - 5:
                surface.blit(stats_surface, stats_rect)

    def set_selected(self, selected: bool):
        """Set the selected state."""
        self.selected = selected

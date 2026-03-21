"""Asset manager for loading and caching sprites and fonts."""

import os
import pygame
from typing import Dict, Optional


class AssetManager:
    """Manages loading and caching of game assets."""

    def __init__(self, assets_path: str = "assets"):
        """
        Initialize the asset manager.

        Args:
            assets_path: Base path to assets folder
        """
        self.assets_path = assets_path
        self.sprites_path = os.path.join(assets_path, "sprites")
        self._sprite_cache: Dict[str, pygame.Surface] = {}
        self._font_cache: Dict[tuple, pygame.font.Font] = {}

    def get_sprite(self, pokemon_id: int, pokemon_name: str, scale: float = 1.0) -> Optional[pygame.Surface]:
        """
        Load and cache a Pokemon sprite.

        Args:
            pokemon_id: The Pokemon's Pokedex number
            pokemon_name: The Pokemon's name
            scale: Scale factor for the sprite

        Returns:
            The loaded sprite surface, or None if not found
        """
        cache_key = f"{pokemon_id}_{scale}"

        if cache_key in self._sprite_cache:
            return self._sprite_cache[cache_key]

        filename = f"{pokemon_id:03d}_{pokemon_name.lower()}.png"
        filepath = os.path.join(self.sprites_path, filename)

        if not os.path.exists(filepath):
            return None

        try:
            sprite = pygame.image.load(filepath).convert_alpha()

            if scale != 1.0:
                new_size = (int(sprite.get_width() * scale), int(sprite.get_height() * scale))
                sprite = pygame.transform.scale(sprite, new_size)

            self._sprite_cache[cache_key] = sprite
            return sprite

        except pygame.error:
            return None

    def get_sprite_from_pokemon(self, pokemon, scale: float = 1.0) -> Optional[pygame.Surface]:
        """
        Load sprite for a Pokemon object.

        Args:
            pokemon: Pokemon instance
            scale: Scale factor

        Returns:
            The loaded sprite surface, or None if not found
        """
        return self.get_sprite(pokemon.id, pokemon.name, scale)

    def get_font(self, size: int, bold: bool = False) -> pygame.font.Font:
        """
        Get a font of the specified size.

        Args:
            size: Font size in points
            bold: Whether to use bold font

        Returns:
            The font object
        """
        cache_key = (size, bold)

        if cache_key in self._font_cache:
            return self._font_cache[cache_key]

        # Try the pixel font (Press Start 2P) first — halve size so it fits existing layouts
        pixel_font_path = os.path.join(self.assets_path, "fonts", "PressStart2P-Regular.ttf")
        if os.path.exists(pixel_font_path):
            try:
                adjusted = max(8, size // 2)
                font = pygame.font.Font(pixel_font_path, adjusted)
                self._font_cache[cache_key] = font
                return font
            except pygame.error:
                pass

        # Fall back to system fonts
        font_names = ["Segoe UI", "Roboto", "SF Pro Display", "Inter", "Open Sans", "Helvetica Neue", "arial"]

        font = None
        for name in font_names:
            try:
                font = pygame.font.SysFont(name, size, bold=bold)
                break
            except Exception:
                continue

        if font is None:
            font = pygame.font.Font(None, size)

        self._font_cache[cache_key] = font
        return font

    def preload_sprites(self, pokemon_ids: list, scale: float = 1.0):
        """
        Preload sprites for multiple Pokemon.

        Args:
            pokemon_ids: List of Pokemon IDs to preload
            scale: Scale factor for sprites
        """
        from src.core.pokemon_data import get_pokemon_data, is_pokemon_available

        for pid in pokemon_ids:
            if is_pokemon_available(pid):
                data = get_pokemon_data(pid)
                self.get_sprite(pid, data["name"], scale)

    def clear_cache(self):
        """Clear all cached assets."""
        self._sprite_cache.clear()
        self._font_cache.clear()

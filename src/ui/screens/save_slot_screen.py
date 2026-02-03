"""Save slot selection screen."""

import pygame
import json
from pathlib import Path
from typing import Any, Optional, Dict

from src.ui import config
from src.ui.screens.base_screen import BaseScreen
from src.ui.components.button import Button
from src.ui.asset_manager import AssetManager


class SaveSlotScreen(BaseScreen):
    """Screen for selecting a save slot."""

    def __init__(self, display: pygame.Surface, assets: AssetManager):
        """
        Initialize the save slot screen.

        Args:
            display: The pygame display surface
            assets: The asset manager
        """
        super().__init__(display, assets)
        
        self.save_folder = Path("saves")
        self.save_folder.mkdir(exist_ok=True)
        
        # Create 4 save slot buttons
        self.slot_buttons = []
        self.save_data = {}
        
        slot_width = 600
        slot_height = 80
        slot_x = (config.SCREEN_WIDTH - slot_width) // 2
        slot_y_start = 150
        slot_spacing = 95
        
        for i in range(4):
            slot_num = i + 1
            save_file = self.save_folder / f"save_{slot_num}.json"
            
            # Load save data if exists
            if save_file.exists():
                try:
                    with open(save_file, 'r') as f:
                        self.save_data[slot_num] = json.load(f)
                except:
                    self.save_data[slot_num] = None
            else:
                self.save_data[slot_num] = None
            
            button = Button(
                slot_x, slot_y_start + i * slot_spacing,
                slot_width, slot_height,
                self._get_slot_text(slot_num),
                font=self.font_medium,
                on_click=lambda s=slot_num: self._select_slot(s)
            )
            self.slot_buttons.append(button)
        
        # Back button
        self.back_button = Button(
            (config.SCREEN_WIDTH - 200) // 2, 550,
            200, 40,
            "Back",
            font=self.font_small,
            color=config.COLOR_BUTTON_DISABLED,
            on_click=lambda: self._set_result(None)
        )
        
        self.selected_index = 0
        self._pending_result = None

    def _get_slot_text(self, slot_num: int) -> str:
        """Get display text for a save slot."""
        save_data = self.save_data.get(slot_num)
        if save_data:
            player_name = save_data.get('player_name', 'Unknown')
            pokemon_count = save_data.get('pokemon_count', 0)
            return f"Slot {slot_num}: {player_name} - {pokemon_count} Pokemon"
        else:
            return f"Slot {slot_num}: Empty"

    def _select_slot(self, slot_num: int):
        """Select a save slot."""
        self._pending_result = slot_num
        self.running = False

    def _set_result(self, result):
        """Set the pending result."""
        self._pending_result = result
        self.running = False

    def handle_event(self, event: pygame.event.Event) -> Optional[Any]:
        """Handle pygame events."""
        # Handle button clicks
        for button in self.slot_buttons:
            if button.handle_event(event):
                return self._pending_result
        
        if self.back_button.handle_event(event):
            return self._pending_result

        # Keyboard navigation
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                self.selected_index = (self.selected_index - 1) % (len(self.slot_buttons) + 1)
            elif event.key == pygame.K_DOWN:
                self.selected_index = (self.selected_index + 1) % (len(self.slot_buttons) + 1)
            elif event.key == pygame.K_RETURN:
                if self.selected_index < len(self.slot_buttons):
                    self.slot_buttons[self.selected_index].on_click()
                else:
                    self.back_button.on_click()
                return self._pending_result
            elif event.key == pygame.K_ESCAPE:
                self._set_result(None)
                return self._pending_result

        return None

    def update(self, dt: float):
        """Update the save slot screen."""
        mouse_pos = pygame.mouse.get_pos()
        
        for i, button in enumerate(self.slot_buttons):
            button.update(mouse_pos)
            if button.is_hovered:
                self.selected_index = i
        
        self.back_button.update(mouse_pos)
        if self.back_button.is_hovered:
            self.selected_index = len(self.slot_buttons)

    def render(self):
        """Render the save slot screen."""
        self.fill_background(config.COLOR_MENU_BG)

        # Draw title with shadow
        title = "Select Save Slot"
        # Shadow
        shadow_surface = self.font_large.render(title, True, config.COLOR_BLACK)
        shadow_rect = shadow_surface.get_rect(centerx=config.SCREEN_WIDTH // 2 + 2, y=62)
        self.display.blit(shadow_surface, shadow_rect)
        # Main title
        title_surface = self.font_large.render(title, True, config.COLOR_SECONDARY)
        title_rect = title_surface.get_rect(centerx=config.SCREEN_WIDTH // 2, y=60)
        self.display.blit(title_surface, title_rect)

        # Draw save slot buttons
        for i, button in enumerate(self.slot_buttons):
            if i == self.selected_index:
                button.is_hovered = True
            
            # Draw button background
            button.render(self.display, self.font_medium)
            
            # Draw additional info for existing saves
            slot_num = i + 1
            save_data = self.save_data.get(slot_num)
            if save_data:
                # Draw a checkmark/indicator with glow
                indicator_color = config.COLOR_HP_GREEN
                indicator_pos = (button.rect.right - 30, button.rect.centery)
                # Glow effect
                pygame.draw.circle(self.display, (*indicator_color, 100), 
                                 indicator_pos, 12)
                # Main indicator
                pygame.draw.circle(self.display, indicator_color, 
                                 indicator_pos, 8)
                # Inner highlight
                pygame.draw.circle(self.display, config.COLOR_WHITE, 
                                 (indicator_pos[0] - 2, indicator_pos[1] - 2), 3)

        # Draw back button
        if self.selected_index == len(self.slot_buttons):
            self.back_button.is_hovered = True
        self.back_button.render(self.display, self.font_small)

        # Draw instructions with better styling
        instructions = "Select a slot to start your journey"
        inst_surface = self.font_small.render(instructions, True, config.COLOR_LIGHT_GRAY)
        inst_rect = inst_surface.get_rect(centerx=config.SCREEN_WIDTH // 2, y=110)
        self.display.blit(inst_surface, inst_rect)

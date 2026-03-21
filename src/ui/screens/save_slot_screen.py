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
        super().__init__(display, assets)

        self.save_folder = Path("saves")
        self.save_folder.mkdir(exist_ok=True)

        self.save_data = {}
        self.slot_buttons = []
        self.delete_buttons = []

        # Confirmation state: slot number being confirmed for deletion, or None
        self._confirm_delete_slot: Optional[int] = None
        self._confirm_yes_btn: Optional[Button] = None
        self._confirm_no_btn: Optional[Button] = None

        slot_width = 520
        slot_height = 80
        slot_x = (config.SCREEN_WIDTH - slot_width) // 2 - 40
        slot_y_start = 150
        slot_spacing = 95
        delete_btn_w = 70
        delete_btn_gap = 10

        for i in range(4):
            slot_num = i + 1
            save_file = self.save_folder / f"save_{slot_num}.json"

            if save_file.exists():
                try:
                    with open(save_file, 'r') as f:
                        self.save_data[slot_num] = json.load(f)
                except Exception:
                    self.save_data[slot_num] = None
            else:
                self.save_data[slot_num] = None

            slot_btn = Button(
                slot_x, slot_y_start + i * slot_spacing,
                slot_width, slot_height,
                self._get_slot_text(slot_num),
                font=self.font_medium,
                on_click=lambda s=slot_num: self._select_slot(s)
            )
            self.slot_buttons.append(slot_btn)

            delete_x = slot_x + slot_width + delete_btn_gap
            delete_y = slot_y_start + i * slot_spacing + (slot_height - slot_height // 2) // 2
            del_btn = Button(
                delete_x, delete_y,
                delete_btn_w, slot_height // 2,
                "Del",
                font=self.font_small,
                color=config.COLOR_ACCENT,
                hover_color=(220, 80, 80),
                disabled=(self.save_data[slot_num] is None),
                on_click=lambda s=slot_num: self._ask_delete(s)
            )
            self.delete_buttons.append(del_btn)

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
        save_data = self.save_data.get(slot_num)
        if save_data:
            player_name = save_data.get('player_name', 'Unknown')
            pokemon_count = save_data.get('pokemon_count', 0)
            return f"Slot {slot_num}: {player_name} - {pokemon_count} Pokemon"
        return f"Slot {slot_num}: Empty"

    def _select_slot(self, slot_num: int):
        if self._confirm_delete_slot is not None:
            return
        self._pending_result = slot_num
        self.running = False

    def _set_result(self, result):
        self._pending_result = result
        self.running = False

    def _ask_delete(self, slot_num: int):
        """Enter confirmation mode for deleting a save."""
        self._confirm_delete_slot = slot_num
        cx = config.SCREEN_WIDTH // 2
        cy = config.SCREEN_HEIGHT // 2
        self._confirm_yes_btn = Button(
            cx - 120, cy + 30, 100, 40,
            "Delete",
            font=self.font_small,
            color=config.COLOR_ACCENT,
            hover_color=(220, 80, 80),
            on_click=lambda: self._do_delete(slot_num)
        )
        self._confirm_no_btn = Button(
            cx + 20, cy + 30, 100, 40,
            "Cancel",
            font=self.font_small,
            color=config.COLOR_BUTTON_DISABLED,
            on_click=self._cancel_delete
        )

    def _do_delete(self, slot_num: int):
        """Delete the save file and refresh the slot."""
        save_file = self.save_folder / f"save_{slot_num}.json"
        try:
            save_file.unlink(missing_ok=True)
        except Exception:
            pass
        self.save_data[slot_num] = None
        idx = slot_num - 1
        self.slot_buttons[idx].text = self._get_slot_text(slot_num)
        self.delete_buttons[idx].disabled = True
        self._cancel_delete()

    def _cancel_delete(self):
        self._confirm_delete_slot = None
        self._confirm_yes_btn = None
        self._confirm_no_btn = None

    # ── Event handling ─────────────────────────────────────────────────────────

    def handle_event(self, event: pygame.event.Event) -> Optional[Any]:
        # Confirmation dialog takes priority
        if self._confirm_delete_slot is not None:
            if self._confirm_yes_btn and self._confirm_yes_btn.handle_event(event):
                return None
            if self._confirm_no_btn and self._confirm_no_btn.handle_event(event):
                return None
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                self._cancel_delete()
            return None

        for button in self.slot_buttons:
            if button.handle_event(event):
                return self._pending_result

        for button in self.delete_buttons:
            button.handle_event(event)

        if self.back_button.handle_event(event):
            return self._pending_result

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
        mouse_pos = pygame.mouse.get_pos()

        if self._confirm_delete_slot is not None:
            if self._confirm_yes_btn:
                self._confirm_yes_btn.update(mouse_pos)
            if self._confirm_no_btn:
                self._confirm_no_btn.update(mouse_pos)
            return

        for i, button in enumerate(self.slot_buttons):
            button.update(mouse_pos)
            if button.is_hovered:
                self.selected_index = i

        for button in self.delete_buttons:
            button.update(mouse_pos)

        self.back_button.update(mouse_pos)
        if self.back_button.is_hovered:
            self.selected_index = len(self.slot_buttons)

    def render(self):
        self.fill_background(config.COLOR_MENU_BG)

        # Title
        title = "Select Save Slot"
        shadow_surface = self.font_large.render(title, True, config.COLOR_BLACK)
        shadow_rect = shadow_surface.get_rect(centerx=config.SCREEN_WIDTH // 2 + 2, y=62)
        self.display.blit(shadow_surface, shadow_rect)
        title_surface = self.font_large.render(title, True, config.COLOR_SECONDARY)
        title_rect = title_surface.get_rect(centerx=config.SCREEN_WIDTH // 2, y=60)
        self.display.blit(title_surface, title_rect)

        # Save slot buttons + delete buttons
        for i, button in enumerate(self.slot_buttons):
            if i == self.selected_index:
                button.is_hovered = True
            button.render(self.display, self.font_medium)

            slot_num = i + 1
            save_data = self.save_data.get(slot_num)
            if save_data:
                indicator_color = config.COLOR_HP_GREEN
                indicator_pos = (button.rect.right - 30, button.rect.centery)
                pygame.draw.circle(self.display, indicator_color, indicator_pos, 8)
                pygame.draw.circle(self.display, config.COLOR_WHITE,
                                   (indicator_pos[0] - 2, indicator_pos[1] - 2), 3)

            self.delete_buttons[i].render(self.display, self.font_small)

        # Back button
        if self.selected_index == len(self.slot_buttons):
            self.back_button.is_hovered = True
        self.back_button.render(self.display, self.font_small)

        # Instructions
        instructions = "Select a slot to continue  |  Del to delete a save"
        inst_surface = self.font_small.render(instructions, True, config.COLOR_LIGHT_GRAY)
        inst_rect = inst_surface.get_rect(centerx=config.SCREEN_WIDTH // 2, y=110)
        self.display.blit(inst_surface, inst_rect)

        # Confirmation dialog overlay
        if self._confirm_delete_slot is not None:
            self._render_confirm_dialog()

    def _render_confirm_dialog(self):
        """Draw a centered confirmation popup."""
        overlay = pygame.Surface((config.SCREEN_WIDTH, config.SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 160))
        self.display.blit(overlay, (0, 0))

        box_w, box_h = 360, 140
        bx = (config.SCREEN_WIDTH - box_w) // 2
        by = (config.SCREEN_HEIGHT - box_h) // 2
        pygame.draw.rect(self.display, config.COLOR_DARK_GRAY, (bx, by, box_w, box_h), border_radius=10)
        pygame.draw.rect(self.display, config.COLOR_ACCENT, (bx, by, box_w, box_h), width=2, border_radius=10)

        msg = f"Delete Slot {self._confirm_delete_slot}?"
        msg_surf = self.font_medium.render(msg, True, config.COLOR_WHITE)
        msg_rect = msg_surf.get_rect(centerx=config.SCREEN_WIDTH // 2, y=by + 20)
        self.display.blit(msg_surf, msg_rect)

        sub = self.font_small.render("This cannot be undone.", True, config.COLOR_LIGHT_GRAY)
        sub_rect = sub.get_rect(centerx=config.SCREEN_WIDTH // 2, y=by + 52)
        self.display.blit(sub, sub_rect)

        if self._confirm_yes_btn:
            self._confirm_yes_btn.render(self.display, self.font_small)
        if self._confirm_no_btn:
            self._confirm_no_btn.render(self.display, self.font_small)

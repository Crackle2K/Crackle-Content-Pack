"""Shop screen — buy items with money earned from battles."""

import pygame
from typing import Any, Optional

from src.ui import config
from src.ui.screens.base_screen import BaseScreen
from src.ui.components.button import Button
from src.ui.asset_manager import AssetManager
from src.entities.trainer import Trainer


SHOP_CATALOG = [
    {
        "name": "Potion",
        "price": 100,
        "description": "Restores 30 HP to one Pokemon",
        "color": (60, 160, 240),
    },
    {
        "name": "Super Potion",
        "price": 250,
        "description": "Restores 70 HP to one Pokemon",
        "color": (50, 110, 220),
    },
    {
        "name": "Full Restore",
        "price": 500,
        "description": "Fully heals one Pokemon",
        "color": (200, 170, 40),
    },
    {
        "name": "Revive",
        "price": 300,
        "description": "Revives one fainted Pokemon to half HP",
        "color": (180, 80, 200),
    },
]


class ShopScreen(BaseScreen):
    """Shop where the player can spend money on items."""

    def __init__(self, display: pygame.Surface, assets: AssetManager, player: Trainer):
        super().__init__(display, assets)
        self.player = player
        self.message = ""
        self.message_timer = 0.0

        # Build buy buttons for each item
        row_h = 90
        start_y = 120
        self.buy_buttons: list[Button] = []

        for i, item in enumerate(SHOP_CATALOG):
            btn = Button(
                config.SCREEN_WIDTH - 130, start_y + i * row_h + (row_h - 40) // 2,
                110, 40,
                f"BUY ${item['price']}",
                font=self.font_small,
                color=item["color"],
            )
            self.buy_buttons.append(btn)

        self.back_button = Button(
            (config.SCREEN_WIDTH - 160) // 2, config.SCREEN_HEIGHT - 60,
            160, 44,
            "BACK",
            font=self.font_medium,
            color=config.COLOR_ACCENT,
        )

    def handle_event(self, event: pygame.event.Event) -> Optional[Any]:
        for i, btn in enumerate(self.buy_buttons):
            if btn.handle_event(event):
                self._try_buy(i)
                return None

        if self.back_button.handle_event(event):
            return "back"

        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            return "back"

        return None

    def update(self, dt: float):
        mouse_pos = pygame.mouse.get_pos()
        for btn in self.buy_buttons:
            btn.update(mouse_pos)
        self.back_button.update(mouse_pos)

        if self.message_timer > 0:
            self.message_timer -= dt
            if self.message_timer <= 0:
                self.message = ""

    def render(self):
        self.display.fill(config.COLOR_BG)

        # Header
        pygame.draw.rect(self.display, config.COLOR_PRIMARY,
                         (0, 0, config.SCREEN_WIDTH, 72))
        pygame.draw.rect(self.display, config.COLOR_SECONDARY,
                         (0, 72, config.SCREEN_WIDTH, 3))
        title_surf = self.font_large.render("POKE MART", True, config.COLOR_WHITE)
        self.display.blit(title_surf,
                          title_surf.get_rect(centerx=config.SCREEN_WIDTH // 2, centery=36))

        # Player money (right of header)
        money_surf = self.font_small.render(f"${self.player.money}", True, config.COLOR_SECONDARY)
        self.display.blit(money_surf,
                          (config.SCREEN_WIDTH - money_surf.get_width() - 16, 28))

        # Item rows
        row_h = 90
        start_y = 120
        for i, item in enumerate(SHOP_CATALOG):
            row_rect = pygame.Rect(20, start_y + i * row_h, config.SCREEN_WIDTH - 40, row_h - 6)

            # Row background
            affordable = self.player.money >= item["price"]
            bg = (248, 250, 252) if affordable else (230, 230, 235)
            pygame.draw.rect(self.display, bg, row_rect, border_radius=8)
            pygame.draw.rect(self.display, config.COLOR_INFO_BOX_BORDER,
                             row_rect, width=1, border_radius=8)

            # Color swatch
            swatch = pygame.Rect(row_rect.x + 10, row_rect.y + 10,
                                 8, row_rect.height - 20)
            pygame.draw.rect(self.display, item["color"], swatch, border_radius=4)

            # Name
            name_col = config.COLOR_BLACK if affordable else config.COLOR_GRAY
            name_surf = self.font_medium.render(item["name"], True, name_col)
            self.display.blit(name_surf, (row_rect.x + 28, row_rect.y + 10))

            # Description
            desc_surf = self.font_small.render(item["description"], True, config.COLOR_GRAY)
            self.display.blit(desc_surf,
                              (row_rect.x + 28, row_rect.y + 14 + name_surf.get_height()))

            # Count owned
            count = self.player.items.get(item["name"], 0)
            if count:
                count_surf = self.font_small.render(f"x{count}", True, config.COLOR_DARK_GRAY)
                self.display.blit(count_surf,
                                  (config.SCREEN_WIDTH - 150 - count_surf.get_width() - 8,
                                   row_rect.centery - count_surf.get_height() // 2))

            # Disable button if can't afford
            self.buy_buttons[i].disabled = not affordable
            self.buy_buttons[i].render(self.display, self.font_small)

        # Feedback message
        if self.message:
            msg_col = (40, 160, 40) if "Bought" in self.message else config.COLOR_ACCENT
            msg_surf = self.font_medium.render(self.message, True, msg_col)
            self.display.blit(msg_surf,
                              msg_surf.get_rect(centerx=config.SCREEN_WIDTH // 2,
                                                y=config.SCREEN_HEIGHT - 110))

        self.back_button.render(self.display, self.font_medium)

    def _try_buy(self, item_index: int):
        item = SHOP_CATALOG[item_index]
        if self.player.spend_money(item["price"]):
            self.player.add_item(item["name"])
            self.message = f"Bought {item['name']}!"
        else:
            self.message = "Not enough money!"
        self.message_timer = 2.0

"""
Pokemon Game - Main Entry Point
A Pokemon-style game with starter selection, battles, and overworld exploration.
All assets fetched from PokeAPI in real-time.
"""

import pygame
import sys
import random
from enum import Enum

# Import from our modules
from src.api.api_client import PokeAPIClient
from src.models.pokemon import Pokemon
from src.models.player import Player
from src.game.battle_system import BattleSystem
from src.utils.colors import *
from src.utils.constants import *

class GameState(Enum):
    """Game states"""
    LOADING = 0
    STARTER_SELECT = 1
    OVERWORLD = 2
    BATTLE = 3
    GAME_OVER = 4

class Game:
    """Main game class"""
    
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Pokemon Game")
        self.clock = pygame.time.Clock()
        self.running = True
        
        # API client
        self.api_client = PokeAPIClient()
        
        # Game state
        self.state = GameState.LOADING
        self.loading_message = "Loading..."
        
        # Fonts
        self.font_large = pygame.font.Font(None, 72)
        self.font_medium = pygame.font.Font(None, 48)
        self.font_small = pygame.font.Font(None, 32)
        self.font_tiny = pygame.font.Font(None, 24)
        
        # Starter selection
        self.starters = []
        self.starter_data = []
        self.selected_starter = 0
        
        # Player
        self.player = None
        self.player_pokemon = None
        
        # Battle
        self.battle_system = None
        self.selected_move = 0
        self.enemy_pokemon = None
        
        # Overworld
        self.encounter_cooldown = 0
        
        # Initialize
        self.load_starters()
    
    def load_starters(self):
        """Load starter Pokemon from API"""
        self.loading_message = "Loading starter Pokemon..."
        
        # Classic starters: Bulbasaur, Charmander, Squirtle
        starter_ids = [1, 4, 7]
        
        for pokemon_id in starter_ids:
            data = self.api_client.get_pokemon_data(pokemon_id)
            if data:
                self.starter_data.append(data)
        
        if len(self.starter_data) == 3:
            self.state = GameState.STARTER_SELECT
        else:
            self.loading_message = "Error loading starters!"
    
    def choose_starter(self, index):
        """Choose a starter Pokemon"""
        if 0 <= index < len(self.starter_data):
            self.player_pokemon = Pokemon(self.starter_data[index], self.api_client, level=5)
            self.player = Player(WORLD_WIDTH // 2, WORLD_HEIGHT // 2)
            self.state = GameState.OVERWORLD
    
    def start_wild_encounter(self):
        """Start a random wild Pokemon encounter"""
        # Random Pokemon from Gen 1 (1-151)
        wild_id = random.randint(1, 151)
        wild_data = self.api_client.get_pokemon_data(wild_id)
        
        if wild_data:
            wild_level = random.randint(3, 7)
            self.enemy_pokemon = Pokemon(wild_data, self.api_client, level=wild_level)
            self.battle_system = BattleSystem(self.player_pokemon, self.enemy_pokemon)
            self.selected_move = 0
            self.state = GameState.BATTLE
    
    def handle_events(self):
        """Handle input events"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            
            elif event.type == pygame.KEYDOWN:
                if self.state == GameState.STARTER_SELECT:
                    self.handle_starter_input(event.key)
                elif self.state == GameState.OVERWORLD:
                    self.handle_overworld_input(event.key)
                elif self.state == GameState.BATTLE:
                    self.handle_battle_input(event.key)
                elif self.state == GameState.GAME_OVER:
                    if event.key == pygame.K_RETURN:
                        self.reset_game()
    
    def handle_starter_input(self, key):
        """Handle starter selection input"""
        if key == pygame.K_LEFT:
            self.selected_starter = (self.selected_starter - 1) % 3
        elif key == pygame.K_RIGHT:
            self.selected_starter = (self.selected_starter + 1) % 3
        elif key == pygame.K_RETURN:
            self.choose_starter(self.selected_starter)
    
    def handle_overworld_input(self, key):
        """Handle overworld movement input"""
        if key == pygame.K_ESCAPE:
            self.running = False
    
    def handle_battle_input(self, key):
        """Handle battle menu input"""
        if not self.battle_system or not self.battle_system.battle_active:
            # Battle ended, return to overworld
            if key == pygame.K_RETURN:
                if self.player_pokemon.is_fainted():
                    self.state = GameState.GAME_OVER
                else:
                    self.state = GameState.OVERWORLD
                    self.encounter_cooldown = ENCOUNTER_COOLDOWN
            return
        
        if self.battle_system.turn != "player":
            return
        
        if key == pygame.K_LEFT:
            self.selected_move = (self.selected_move - 1) % len(self.player_pokemon.moves)
        elif key == pygame.K_RIGHT:
            self.selected_move = (self.selected_move + 1) % len(self.player_pokemon.moves)
        elif key == pygame.K_RETURN:
            self.battle_system.player_attack(self.selected_move)
        elif key == pygame.K_r:
            self.battle_system.run_away()
    
    def update(self):
        """Update game logic"""
        if self.state == GameState.OVERWORLD:
            self.update_overworld()
        elif self.state == GameState.BATTLE:
            self.update_battle()
    
    def update_overworld(self):
        """Update overworld logic"""
        # Handle movement
        keys = pygame.key.get_pressed()
        dx = keys[pygame.K_RIGHT] - keys[pygame.K_LEFT]
        dy = keys[pygame.K_DOWN] - keys[pygame.K_UP]
        
        if dx != 0 or dy != 0:
            self.player.move(dx, dy, (WORLD_WIDTH, WORLD_HEIGHT))
            
            # Random encounters
            if self.encounter_cooldown <= 0:
                if random.random() < ENCOUNTER_RATE:
                    self.start_wild_encounter()
            else:
                self.encounter_cooldown -= 1
    
    def update_battle(self):
        """Update battle logic"""
        if not self.battle_system:
            return
        
        # Enemy turn
        if self.battle_system.turn == "enemy" and self.battle_system.battle_active:
            pygame.time.wait(1000)  # Delay before enemy attack
            self.battle_system.enemy_attack()
    
    def draw(self):
        """Draw current game state"""
        self.screen.fill(WHITE)
        
        if self.state == GameState.LOADING:
            self.draw_loading()
        elif self.state == GameState.STARTER_SELECT:
            self.draw_starter_select()
        elif self.state == GameState.OVERWORLD:
            self.draw_overworld()
        elif self.state == GameState.BATTLE:
            self.draw_battle()
        elif self.state == GameState.GAME_OVER:
            self.draw_game_over()
        
        pygame.display.flip()
    
    def draw_loading(self):
        """Draw loading screen"""
        text = self.font_medium.render(self.loading_message, True, BLACK)
        rect = text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
        self.screen.blit(text, rect)
    
    def draw_starter_select(self):
        """Draw starter selection screen"""
        # Title
        title = self.font_large.render("Choose Your Starter!", True, BLUE)
        title_rect = title.get_rect(center=(SCREEN_WIDTH // 2, 80))
        self.screen.blit(title, title_rect)
        
        # Draw starters
        spacing = 300
        start_x = (SCREEN_WIDTH - spacing * 2) // 2
        
        for i, data in enumerate(self.starter_data):
            x = start_x + i * spacing
            y = 250
            
            # Sprite
            sprite = self.api_client.get_pokemon_sprite(data, 'front_default', (192, 192))
            sprite_rect = sprite.get_rect(center=(x, y))
            self.screen.blit(sprite, sprite_rect)
            
            # Name
            name = self.font_medium.render(data['name'].capitalize(), True, BLACK)
            name_rect = name.get_rect(center=(x, y + 150))
            self.screen.blit(name, name_rect)
            
            # Selection indicator
            if i == self.selected_starter:
                pygame.draw.circle(self.screen, YELLOW, (x, y + 200), 15)
        
        # Instructions
        instructions = self.font_small.render("Arrow Keys to Select | Enter to Choose", True, DARK_GRAY)
        inst_rect = instructions.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 50))
        self.screen.blit(instructions, inst_rect)
    
    def draw_overworld(self):
        """Draw overworld"""
        # Background
        self.screen.fill(GREEN)
        
        # Grid
        for x in range(0, SCREEN_WIDTH, TILE_SIZE):
            for y in range(0, SCREEN_HEIGHT, TILE_SIZE):
                pygame.draw.rect(self.screen, DARK_GRAY, (x, y, TILE_SIZE, TILE_SIZE), 1)
        
        # Player
        center_x = SCREEN_WIDTH // 2
        center_y = SCREEN_HEIGHT // 2
        self.screen.blit(self.player.sprite, (center_x - TILE_SIZE // 2, center_y - TILE_SIZE // 2))
        
        # UI
        self.draw_overworld_ui()
    
    def draw_overworld_ui(self):
        """Draw overworld UI"""
        # Pokemon info box
        box_rect = pygame.Rect(20, 20, 300, 120)
        pygame.draw.rect(self.screen, WHITE, box_rect)
        pygame.draw.rect(self.screen, BLACK, box_rect, 3)
        
        # Pokemon name and level
        name_text = self.font_medium.render(f"{self.player_pokemon.name}", True, BLACK)
        self.screen.blit(name_text, (30, 30))
        
        level_text = self.font_small.render(f"Lv. {self.player_pokemon.level}", True, DARK_GRAY)
        self.screen.blit(level_text, (30, 70))
        
        # HP bar
        hp_ratio = self.player_pokemon.hp / self.player_pokemon.max_hp
        hp_color = HP_GREEN if hp_ratio > 0.5 else (HP_YELLOW if hp_ratio > 0.25 else HP_RED)
        
        pygame.draw.rect(self.screen, DARK_GRAY, (30, 100, 260, 20))
        pygame.draw.rect(self.screen, hp_color, (30, 100, int(260 * hp_ratio), 20))
        
        hp_text = self.font_tiny.render(f"{self.player_pokemon.hp}/{self.player_pokemon.max_hp}", True, BLACK)
        self.screen.blit(hp_text, (35, 102))
        
        # Instructions
        inst_text = self.font_small.render("Arrow Keys to Move | ESC to Quit", True, WHITE)
        inst_rect = inst_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 30))
        
        # Background for text
        bg_rect = inst_rect.inflate(20, 10)
        pygame.draw.rect(self.screen, BLACK, bg_rect)
        self.screen.blit(inst_text, inst_rect)
    
    def draw_battle(self):
        """Draw battle screen"""
        # Background
        self.screen.fill(LIGHT_BLUE)
        
        # Battle platform
        pygame.draw.ellipse(self.screen, DARK_GRAY, (100, 400, 250, 80))
        pygame.draw.ellipse(self.screen, DARK_GRAY, (650, 200, 250, 80))
        
        # Pokemon sprites
        if self.player_pokemon:
            player_sprite = self.player_pokemon.get_sprite_back((192, 192))
            self.screen.blit(player_sprite, (150, 320))
        
        if self.enemy_pokemon:
            enemy_sprite = self.enemy_pokemon.get_sprite_front((192, 192))
            self.screen.blit(enemy_sprite, (700, 120))
        
        # Info boxes
        self.draw_battle_ui()
    
    def draw_battle_ui(self):
        """Draw battle UI"""
        # Player Pokemon info
        player_box = pygame.Rect(550, 450, 450, 100)
        pygame.draw.rect(self.screen, WHITE, player_box)
        pygame.draw.rect(self.screen, BLACK, player_box, 3)
        
        name = self.font_medium.render(f"{self.player_pokemon.name} Lv.{self.player_pokemon.level}", True, BLACK)
        self.screen.blit(name, (560, 460))
        
        hp_ratio = self.player_pokemon.hp / self.player_pokemon.max_hp
        hp_color = HP_GREEN if hp_ratio > 0.5 else (HP_YELLOW if hp_ratio > 0.25 else HP_RED)
        
        pygame.draw.rect(self.screen, DARK_GRAY, (560, 505, 420, 25))
        pygame.draw.rect(self.screen, hp_color, (560, 505, int(420 * hp_ratio), 25))
        
        hp_text = self.font_small.render(f"HP: {self.player_pokemon.hp}/{self.player_pokemon.max_hp}", True, BLACK)
        self.screen.blit(hp_text, (565, 507))
        
        # Enemy Pokemon info
        enemy_box = pygame.Rect(20, 50, 350, 80)
        pygame.draw.rect(self.screen, WHITE, enemy_box)
        pygame.draw.rect(self.screen, BLACK, enemy_box, 3)
        
        enemy_name = self.font_medium.render(f"{self.enemy_pokemon.name} Lv.{self.enemy_pokemon.level}", True, BLACK)
        self.screen.blit(enemy_name, (30, 60))
        
        enemy_hp_ratio = self.enemy_pokemon.hp / self.enemy_pokemon.max_hp
        enemy_hp_color = HP_GREEN if enemy_hp_ratio > 0.5 else (HP_YELLOW if enemy_hp_ratio > 0.25 else HP_RED)
        
        pygame.draw.rect(self.screen, DARK_GRAY, (30, 100, 320, 20))
        pygame.draw.rect(self.screen, enemy_hp_color, (30, 100, int(320 * enemy_hp_ratio), 20))
        
        # Message box
        msg_box = pygame.Rect(20, 580, 650, 150)
        pygame.draw.rect(self.screen, WHITE, msg_box)
        pygame.draw.rect(self.screen, BLACK, msg_box, 3)
        
        # Word wrap message
        words = self.battle_system.message.split(' ')
        lines = []
        current_line = ""
        
        for word in words:
            test_line = current_line + word + " "
            if self.font_small.render(test_line, True, BLACK).get_width() < 620:
                current_line = test_line
            else:
                lines.append(current_line)
                current_line = word + " "
        lines.append(current_line)
        
        for i, line in enumerate(lines[:4]):  # Max 4 lines
            text = self.font_small.render(line, True, BLACK)
            self.screen.blit(text, (30, 595 + i * 35))
        
        # Move selection
        if self.battle_system.battle_active and self.battle_system.turn == "player":
            move_box = pygame.Rect(680, 580, 330, 150)
            pygame.draw.rect(self.screen, WHITE, move_box)
            pygame.draw.rect(self.screen, BLACK, move_box, 3)
            
            for i, move in enumerate(self.player_pokemon.moves):
                y = 595 + (i % 2) * 70
                x = 690 + (i // 2) * 170
                
                # Highlight selected move
                if i == self.selected_move:
                    highlight = pygame.Rect(x - 5, y - 5, 160, 60)
                    pygame.draw.rect(self.screen, YELLOW, highlight, 3)
                
                move_name = self.font_small.render(move['name'].capitalize(), True, BLACK)
                self.screen.blit(move_name, (x, y))
                
                move_pp = self.font_tiny.render(f"PP: {move['pp']}", True, DARK_GRAY)
                self.screen.blit(move_pp, (x, y + 30))
            
            # Instructions
            inst = self.font_tiny.render("Arrows: Select | Enter: Attack | R: Run", True, BLACK)
            self.screen.blit(inst, (690, 720))
        elif not self.battle_system.battle_active:
            # Battle ended
            cont_text = self.font_small.render("Press Enter to Continue", True, BLACK)
            cont_rect = cont_text.get_rect(center=(SCREEN_WIDTH // 2, 680))
            self.screen.blit(cont_text, cont_rect)
    
    def draw_game_over(self):
        """Draw game over screen"""
        self.screen.fill(BLACK)
        
        game_over_text = self.font_large.render("GAME OVER", True, RED)
        game_over_rect = game_over_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 50))
        self.screen.blit(game_over_text, game_over_rect)
        
        continue_text = self.font_medium.render("Press Enter to Restart", True, WHITE)
        continue_rect = continue_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 50))
        self.screen.blit(continue_text, continue_rect)
    
    def reset_game(self):
        """Reset the game"""
        self.state = GameState.LOADING
        self.player_pokemon = None
        self.player = None
        self.battle_system = None
        self.enemy_pokemon = None
        self.selected_starter = 0
        self.load_starters()
    
    def run(self):
        """Main game loop"""
        while self.running:
            self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(FPS)
        
        pygame.quit()
        sys.exit()

def main():
    """Entry point"""
    game = Game()
    game.run()

if __name__ == "__main__":
    main()
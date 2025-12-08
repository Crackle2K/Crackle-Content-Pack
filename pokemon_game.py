"""
Pokemon Game - Main Game Module
A complete Pokemon game with starter selection, battles, and movement
"""

import pygame
import sys
import json
import random
from pathlib import Path
from enum import Enum

# Initialize Pygame
pygame.init()

# Constants
SCREEN_WIDTH = 1024
SCREEN_HEIGHT = 768
FPS = 60
TILE_SIZE = 48

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BLUE = (61, 125, 202)
DARK_BLUE = (46, 95, 163)
LIGHT_BLUE = (227, 242, 253)
YELLOW = (255, 203, 5)
GOLD = (255, 215, 0)
GRAY = (200, 200, 200)
DARK_GRAY = (100, 100, 100)
GREEN = (76, 175, 80)
RED = (244, 67, 54)
HP_GREEN = (102, 204, 102)
HP_YELLOW = (255, 204, 51)
HP_RED = (255, 102, 102)

# Game States
class GameState(Enum):
    INTRO = 1
    STARTER_SELECTION = 2
    OVERWORLD = 3
    BATTLE = 4
    MENU = 5

class Pokemon:
    """Pokemon class to store Pokemon data and battle stats"""
    def __init__(self, data_file):
        with open(data_file, 'r') as f:
            data = json.load(f)
        
        self.name = data['name'].capitalize()
        self.types = data['types']
        self.level = 5
        self.max_hp = data['stats']['hp'] + self.level * 2
        self.hp = self.max_hp
        self.attack = data['stats']['attack']
        self.defense = data['stats']['defense']
        self.speed = data['stats']['speed']
        self.moves = data['moves'][:4]  # Max 4 moves
        self.exp = 0
        self.max_exp = 100
        
        # Load sprites
        sprite_dir = Path("game_assets/sprites") / self.name.lower()
        self.sprite_front = self.load_sprite(sprite_dir / "front.png")
        self.sprite_back = self.load_sprite(sprite_dir / "back.png")
    
    def load_sprite(self, path):
        """Load and scale a sprite"""
        try:
            sprite = pygame.image.load(str(path))
            return pygame.transform.scale(sprite, (192, 192))
        except:
            # Create placeholder if sprite not found
            surf = pygame.Surface((192, 192))
            surf.fill(GRAY)
            return surf
    
    def take_damage(self, damage):
        """Apply damage to Pokemon"""
        self.hp = max(0, self.hp - damage)
    
    def heal(self, amount):
        """Heal Pokemon"""
        self.hp = min(self.max_hp, self.hp + amount)
    
    def is_fainted(self):
        """Check if Pokemon has fainted"""
        return self.hp <= 0
    
    def gain_exp(self, amount):
        """Gain experience points"""
        self.exp += amount
        if self.exp >= self.max_exp:
            self.level_up()
    
    def level_up(self):
        """Level up the Pokemon"""
        self.level += 1
        self.exp = 0
        self.max_exp = int(self.max_exp * 1.2)
        
        # Stat increases
        self.max_hp += 5
        self.hp = self.max_hp
        self.attack += 2
        self.defense += 2
        self.speed += 2

class Player:
    """Player character for overworld movement"""
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.speed = 4
        self.rect = pygame.Rect(x, y, TILE_SIZE, TILE_SIZE)
        
        # Create simple player sprite
        self.sprite = pygame.Surface((TILE_SIZE, TILE_SIZE))
        self.sprite.fill(RED)
        
    def move(self, dx, dy, world_bounds):
        """Move player with collision detection"""
        new_x = self.x + dx * self.speed
        new_y = self.y + dy * self.speed
        
        # Keep player within bounds
        if 0 <= new_x < world_bounds[0] - TILE_SIZE:
            self.x = new_x
            self.rect.x = new_x
        
        if 0 <= new_y < world_bounds[1] - TILE_SIZE:
            self.y = new_y
            self.rect.y = new_y
    
    def draw(self, surface, camera_offset=(0, 0)):
        """Draw the player"""
        surface.blit(self.sprite, (self.x - camera_offset[0], self.y - camera_offset[1]))

class BattleSystem:
    """Handles Pokemon battle logic"""
    def __init__(self, player_pokemon, enemy_pokemon):
        self.player = player_pokemon
        self.enemy = enemy_pokemon
        self.turn = "player"
        self.message = f"Wild {self.enemy.name} appeared!"
        self.battle_active = True
        self.winner = None
        
    def calculate_damage(self, attacker, defender, move):
        """Calculate damage based on stats and move"""
        if move.get('damage_class') == 'status':
            return 0
        
        power = move.get('power', 40)
        level = attacker.level
        attack = attacker.attack
        defense = defender.defense
        
        # Basic damage formula
        damage = ((2 * level / 5 + 2) * power * attack / defense / 50) + 2
        
        # Random factor
        damage *= random.uniform(0.85, 1.0)
        
        # Type effectiveness (simplified)
        effectiveness = self.get_type_effectiveness(move['type'], defender.types)
        damage *= effectiveness
        
        return int(damage)
    
    def get_type_effectiveness(self, move_type, defender_types):
        """Get type effectiveness multiplier (simplified)"""
        effectiveness_chart = {
            'fire': {'grass': 2.0, 'water': 0.5},
            'water': {'fire': 2.0, 'grass': 0.5},
            'grass': {'water': 2.0, 'fire': 0.5},
            'electric': {'water': 2.0},
            'normal': {}
        }
        
        multiplier = 1.0
        chart = effectiveness_chart.get(move_type, {})
        
        for def_type in defender_types:
            if def_type in chart:
                multiplier *= chart[def_type]
        
        return multiplier
    
    def player_attack(self, move_index):
        """Player attacks with selected move"""
        if move_index >= len(self.player.moves):
            return
        
        move = self.player.moves[move_index]
        
        # Check accuracy
        if random.randint(1, 100) > move.get('accuracy', 100):
            self.message = f"{self.player.name}'s attack missed!"
            self.turn = "enemy"
            return
        
        damage = self.calculate_damage(self.player, self.enemy, move)
        self.enemy.take_damage(damage)
        
        effectiveness = self.get_type_effectiveness(move['type'], self.enemy.types)
        eff_text = ""
        if effectiveness > 1:
            eff_text = " It's super effective!"
        elif effectiveness < 1:
            eff_text = " It's not very effective..."
        
        self.message = f"{self.player.name} used {move['name']}! Dealt {damage} damage.{eff_text}"
        
        if self.enemy.is_fainted():
            self.battle_active = False
            self.winner = "player"
            self.message = f"Wild {self.enemy.name} fainted! You won!"
            self.player.gain_exp(50)
        else:
            self.turn = "enemy"
    
    def enemy_attack(self):
        """Enemy attacks with random move"""
        if not self.enemy.moves:
            self.turn = "player"
            return
        
        move = random.choice(self.enemy.moves)
        
        # Check accuracy
        if random.randint(1, 100) > move.get('accuracy', 100):
            self.message = f"Wild {self.enemy.name}'s attack missed!"
            self.turn = "player"
            return
        
        damage = self.calculate_damage(self.enemy, self.player, move)
        self.player.take_damage(damage)
        
        self.message = f"Wild {self.enemy.name} used {move['name']}! Dealt {damage} damage."
        
        if self.player.is_fainted():
            self.battle_active = False
            self.winner = "enemy"
            self.message = f"{self.player.name} fainted! You lost!"
        else:
            self.turn = "player"
    
    def run_away(self):
        """Attempt to run from battle"""
        if random.random() < 0.5:
            self.battle_active = False
            self.message = "Got away safely!"
            return True
        else:
            self.message = "Couldn't escape!"
            self.turn = "enemy"
            return False

class Game:
    """Main game class"""
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Pokemon Adventure")
        self.clock = pygame.time.Clock()
        
        # Fonts
        self.title_font = pygame.font.Font(None, 72)
        self.large_font = pygame.font.Font(None, 48)
        self.medium_font = pygame.font.Font(None, 36)
        self.small_font = pygame.font.Font(None, 24)
        
        # Game state
        self.state = GameState.INTRO
        self.running = True
        
        # Player data
        self.player_pokemon = None
        self.player = None
        
        # Battle data
        self.battle = None
        self.battle_message_timer = 0
        self.auto_progress = False
        
        # Overworld
        self.world_width = 1920
        self.world_height = 1440
        self.camera_x = 0
        self.camera_y = 0
        
        # Grass tiles for random encounters
        self.grass_tiles = []
        self.generate_grass()
        
        self.encounter_cooldown = 0
        
    def generate_grass(self):
        """Generate random grass patches"""
        for _ in range(100):
            x = random.randint(0, self.world_width - TILE_SIZE)
            y = random.randint(0, self.world_height - TILE_SIZE)
            self.grass_tiles.append(pygame.Rect(x, y, TILE_SIZE, TILE_SIZE))
    
    def check_encounter(self):
        """Check for wild Pokemon encounter in grass"""
        if self.encounter_cooldown > 0:
            return False
        
        player_rect = pygame.Rect(self.player.x, self.player.y, TILE_SIZE, TILE_SIZE)
        
        for grass in self.grass_tiles:
            if player_rect.colliderect(grass):
                if random.random() < 0.05:  # 5% encounter rate
                    self.encounter_cooldown = 120  # Cooldown frames
                    return True
        
        return False
    
    def start_battle(self):
        """Start a wild Pokemon battle"""
        wild_pokemon_files = [
            "game_assets/data/pidgey.json",
            "game_assets/data/rattata.json",
            "game_assets/data/caterpie.json",
            "game_assets/data/weedle.json",
        ]
        
        # Check if files exist, otherwise use pikachu
        available_files = [f for f in wild_pokemon_files if Path(f).exists()]
        
        if available_files:
            wild_data = random.choice(available_files)
        else:
            wild_data = "game_assets/data/pikachu.json"
        
        wild_pokemon = Pokemon(wild_data)
        wild_pokemon.level = random.randint(3, 7)
        wild_pokemon.hp = wild_pokemon.max_hp
        
        self.battle = BattleSystem(self.player_pokemon, wild_pokemon)
        self.state = GameState.BATTLE
        self.battle_message_timer = 120
    
    def update_camera(self):
        """Update camera to follow player"""
        self.camera_x = self.player.x - SCREEN_WIDTH // 2 + TILE_SIZE // 2
        self.camera_y = self.player.y - SCREEN_HEIGHT // 2 + TILE_SIZE // 2
        
        # Clamp camera
        self.camera_x = max(0, min(self.camera_x, self.world_width - SCREEN_WIDTH))
        self.camera_y = max(0, min(self.camera_y, self.world_height - SCREEN_HEIGHT))
    
    def draw_intro(self):
        """Draw intro screen"""
        self.screen.fill(DARK_BLUE)
        
        # Title
        title = self.title_font.render("Pokemon Adventure", True, YELLOW)
        title_shadow = self.title_font.render("Pokemon Adventure", True, BLACK)
        title_rect = title.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 3))
        self.screen.blit(title_shadow, (title_rect.x + 3, title_rect.y + 3))
        self.screen.blit(title, title_rect)
        
        # Instructions
        inst = self.medium_font.render("Press SPACE to Start", True, WHITE)
        inst_rect = inst.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
        self.screen.blit(inst, inst_rect)
        
        # Credits
        credit = self.small_font.render("Created with PokeAPI", True, GRAY)
        credit_rect = credit.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 50))
        self.screen.blit(credit, credit_rect)
    
    def draw_starter_selection(self):
        """Draw starter Pokemon selection screen"""
        self.screen.fill(LIGHT_BLUE)
        
        # Title
        title = self.large_font.render("Choose Your Starter Pokemon!", True, DARK_BLUE)
        title_rect = title.get_rect(center=(SCREEN_WIDTH // 2, 80))
        self.screen.blit(title, title_rect)
        
        # Load starters
        starters = [
            ("game_assets/data/bulbasaur.json", "Bulbasaur", "Grass"),
            ("game_assets/data/charmander.json", "Charmander", "Fire"),
            ("game_assets/data/squirtle.json", "Squirtle", "Water"),
        ]
        
        slot_width = 250
        slot_height = 350
        spacing = 50
        total_width = len(starters) * slot_width + (len(starters) - 1) * spacing
        start_x = (SCREEN_WIDTH - total_width) // 2
        
        mouse_pos = pygame.mouse.get_pos()
        
        for i, (data_file, name, ptype) in enumerate(starters):
            x = start_x + i * (slot_width + spacing)
            y = 180
            
            rect = pygame.Rect(x, y, slot_width, slot_height)
            
            # Check hover
            is_hovered = rect.collidepoint(mouse_pos)
            
            # Draw slot
            bg_color = GOLD if is_hovered else WHITE
            pygame.draw.rect(self.screen, bg_color, rect)
            pygame.draw.rect(self.screen, DARK_BLUE, rect, 4)
            
            # Draw sprite
            try:
                pokemon = Pokemon(data_file)
                sprite_rect = pokemon.sprite_front.get_rect(center=(x + slot_width // 2, y + 120))
                self.screen.blit(pokemon.sprite_front, sprite_rect)
            except:
                pass
            
            # Draw name
            name_text = self.medium_font.render(name, True, DARK_BLUE)
            name_rect = name_text.get_rect(center=(x + slot_width // 2, y + 250))
            self.screen.blit(name_text, name_rect)
            
            # Draw type
            type_text = self.small_font.render(f"Type: {ptype}", True, DARK_GRAY)
            type_rect = type_text.get_rect(center=(x + slot_width // 2, y + 290))
            self.screen.blit(type_text, type_rect)
            
            # Draw instruction
            if is_hovered:
                click_text = self.small_font.render("Click to Select", True, RED)
                click_rect = click_text.get_rect(center=(x + slot_width // 2, y + 320))
                self.screen.blit(click_text, click_rect)
            
            # Store rect for click detection
            if not hasattr(self, 'starter_rects'):
                self.starter_rects = []
            if len(self.starter_rects) <= i:
                self.starter_rects.append((rect, data_file))
            else:
                self.starter_rects[i] = (rect, data_file)
    
    def draw_overworld(self):
        """Draw overworld with player movement"""
        self.screen.fill(GREEN)
        
        # Draw grass tiles
        for grass in self.grass_tiles:
            grass_x = grass.x - self.camera_x
            grass_y = grass.y - self.camera_y
            
            # Only draw if on screen
            if -TILE_SIZE < grass_x < SCREEN_WIDTH and -TILE_SIZE < grass_y < SCREEN_HEIGHT:
                pygame.draw.rect(self.screen, (34, 139, 34), 
                               pygame.Rect(grass_x, grass_y, TILE_SIZE, TILE_SIZE))
        
        # Draw player
        self.player.draw(self.screen, (self.camera_x, self.camera_y))
        
        # Draw UI
        self.draw_overworld_ui()
    
    def draw_overworld_ui(self):
        """Draw overworld UI elements"""
        # Pokemon info panel
        panel_rect = pygame.Rect(10, 10, 300, 120)
        pygame.draw.rect(self.screen, WHITE, panel_rect)
        pygame.draw.rect(self.screen, BLACK, panel_rect, 3)
        
        # Pokemon name
        name_text = self.medium_font.render(self.player_pokemon.name, True, BLACK)
        self.screen.blit(name_text, (20, 20))
        
        # Level
        level_text = self.small_font.render(f"Lv. {self.player_pokemon.level}", True, DARK_GRAY)
        self.screen.blit(level_text, (20, 55))
        
        # HP bar
        hp_bar_width = 280
        hp_bar_height = 20
        hp_percentage = self.player_pokemon.hp / self.player_pokemon.max_hp
        
        pygame.draw.rect(self.screen, GRAY, pygame.Rect(20, 85, hp_bar_width, hp_bar_height))
        
        if hp_percentage > 0.5:
            hp_color = HP_GREEN
        elif hp_percentage > 0.2:
            hp_color = HP_YELLOW
        else:
            hp_color = HP_RED
        
        pygame.draw.rect(self.screen, hp_color, 
                        pygame.Rect(20, 85, int(hp_bar_width * hp_percentage), hp_bar_height))
        
        # HP text
        hp_text = self.small_font.render(f"HP: {self.player_pokemon.hp}/{self.player_pokemon.max_hp}", True, BLACK)
        self.screen.blit(hp_text, (25, 87))
        
        # Instructions
        inst_rect = pygame.Rect(10, SCREEN_HEIGHT - 80, 400, 70)
        pygame.draw.rect(self.screen, WHITE, inst_rect)
        pygame.draw.rect(self.screen, BLACK, inst_rect, 2)
        
        inst1 = self.small_font.render("Arrow Keys: Move", True, BLACK)
        inst2 = self.small_font.render("Walk in grass for wild encounters!", True, DARK_GRAY)
        self.screen.blit(inst1, (20, SCREEN_HEIGHT - 70))
        self.screen.blit(inst2, (20, SCREEN_HEIGHT - 45))
    
    def draw_battle(self):
        """Draw battle screen"""
        self.screen.fill(LIGHT_BLUE)
        
        # Battle background
        battle_bg = pygame.Rect(50, 50, SCREEN_WIDTH - 100, 400)
        pygame.draw.rect(self.screen, WHITE, battle_bg)
        pygame.draw.rect(self.screen, BLACK, battle_bg, 3)
        
        # Enemy Pokemon
        enemy_x = SCREEN_WIDTH - 350
        enemy_y = 100
        self.screen.blit(self.battle.enemy.sprite_front, (enemy_x, enemy_y))
        
        # Enemy info
        self.draw_pokemon_info(self.battle.enemy, enemy_x - 50, enemy_y - 50, False)
        
        # Player Pokemon
        player_x = 150
        player_y = 250
        self.screen.blit(self.battle.player.sprite_back, (player_x, player_y))
        
        # Player info
        self.draw_pokemon_info(self.battle.player, player_x + 200, player_y + 150, True)
        
        # Message box
        msg_rect = pygame.Rect(50, 470, SCREEN_WIDTH - 100, 100)
        pygame.draw.rect(self.screen, WHITE, msg_rect)
        pygame.draw.rect(self.screen, BLACK, msg_rect, 3)
        
        # Wrap message text
        self.draw_wrapped_text(self.battle.message, msg_rect, self.medium_font, BLACK)
        
        # Action buttons (only show during player's turn)
        if self.battle.battle_active and self.battle.turn == "player" and self.battle_message_timer <= 0:
            self.draw_battle_menu()
    
    def draw_pokemon_info(self, pokemon, x, y, show_exp=False):
        """Draw Pokemon info panel"""
        panel_width = 250
        panel_height = 100 if show_exp else 80
        
        panel_rect = pygame.Rect(x, y, panel_width, panel_height)
        pygame.draw.rect(self.screen, WHITE, panel_rect)
        pygame.draw.rect(self.screen, BLACK, panel_rect, 2)
        
        # Name and level
        name_text = self.medium_font.render(f"{pokemon.name} Lv.{pokemon.level}", True, BLACK)
        self.screen.blit(name_text, (x + 10, y + 10))
        
        # HP bar
        hp_bar_width = 230
        hp_bar_height = 20
        hp_percentage = pokemon.hp / pokemon.max_hp
        
        pygame.draw.rect(self.screen, GRAY, pygame.Rect(x + 10, y + 45, hp_bar_width, hp_bar_height))
        
        if hp_percentage > 0.5:
            hp_color = HP_GREEN
        elif hp_percentage > 0.2:
            hp_color = HP_YELLOW
        else:
            hp_color = HP_RED
        
        pygame.draw.rect(self.screen, hp_color,
                        pygame.Rect(x + 10, y + 45, int(hp_bar_width * hp_percentage), hp_bar_height))
        
        # HP text
        hp_text = self.small_font.render(f"{pokemon.hp}/{pokemon.max_hp}", True, BLACK)
        self.screen.blit(hp_text, (x + 15, y + 47))
        
        # Experience bar (only for player)
        if show_exp:
            exp_percentage = pokemon.exp / pokemon.max_exp
            pygame.draw.rect(self.screen, GRAY, pygame.Rect(x + 10, y + 75, hp_bar_width, 10))
            pygame.draw.rect(self.screen, BLUE,
                           pygame.Rect(x + 10, y + 75, int(hp_bar_width * exp_percentage), 10))
    
    def draw_battle_menu(self):
        """Draw battle action menu"""
        menu_rect = pygame.Rect(50, 590, SCREEN_WIDTH - 100, 160)
        pygame.draw.rect(self.screen, WHITE, menu_rect)
        pygame.draw.rect(self.screen, BLACK, menu_rect, 3)
        
        # Title
        title = self.small_font.render("Choose an action:", True, BLACK)
        self.screen.blit(title, (70, 605))
        
        # Move buttons
        if not hasattr(self, 'move_buttons'):
            self.move_buttons = []
        
        self.move_buttons.clear()
        
        button_width = 220
        button_height = 45
        start_x = 70
        start_y = 640
        spacing = 15
        
        mouse_pos = pygame.mouse.get_pos()
        
        # Draw moves (2x2 grid)
        for i, move in enumerate(self.battle.player.moves):
            row = i // 2
            col = i % 2
            x = start_x + col * (button_width + spacing)
            y = start_y + row * (button_height + spacing)
            
            button_rect = pygame.Rect(x, y, button_width, button_height)
            is_hovered = button_rect.collidepoint(mouse_pos)
            
            # Draw button
            btn_color = YELLOW if is_hovered else BLUE
            pygame.draw.rect(self.screen, btn_color, button_rect)
            pygame.draw.rect(self.screen, BLACK, button_rect, 2)
            
            # Move name
            move_text = self.small_font.render(move['name'].capitalize(), True, BLACK if is_hovered else WHITE)
            text_rect = move_text.get_rect(center=(x + button_width // 2, y + button_height // 2))
            self.screen.blit(move_text, text_rect)
            
            self.move_buttons.append((button_rect, i))
        
        # Run button
        run_x = start_x + 2 * (button_width + spacing)
        run_y = start_y
        run_rect = pygame.Rect(run_x, run_y, button_width, button_height)
        is_run_hovered = run_rect.collidepoint(mouse_pos)
        
        run_color = YELLOW if is_run_hovered else RED
        pygame.draw.rect(self.screen, run_color, run_rect)
        pygame.draw.rect(self.screen, BLACK, run_rect, 2)
        
        run_text = self.small_font.render("Run Away", True, BLACK if is_run_hovered else WHITE)
        run_text_rect = run_text.get_rect(center=(run_x + button_width // 2, run_y + button_height // 2))
        self.screen.blit(run_text, run_text_rect)
        
        self.move_buttons.append((run_rect, "run"))
    
    def draw_wrapped_text(self, text, rect, font, color):
        """Draw text wrapped within a rectangle"""
        words = text.split(' ')
        lines = []
        current_line = []
        
        for word in words:
            test_line = ' '.join(current_line + [word])
            if font.size(test_line)[0] <= rect.width - 20:
                current_line.append(word)
            else:
                if current_line:
                    lines.append(' '.join(current_line))
                current_line = [word]
        
        if current_line:
            lines.append(' '.join(current_line))
        
        y_offset = rect.y + 15
        for line in lines[:3]:  # Max 3 lines
            text_surf = font.render(line, True, color)
            self.screen.blit(text_surf, (rect.x + 15, y_offset))
            y_offset += font.get_height() + 5
    
    def handle_events(self):
        """Handle pygame events"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            
            if event.type == pygame.KEYDOWN:
                if self.state == GameState.INTRO:
                    if event.key == pygame.K_SPACE:
                        self.state = GameState.STARTER_SELECTION
                
                elif self.state == GameState.BATTLE:
                    if event.key == pygame.K_ESCAPE and not self.battle.battle_active:
                        self.state = GameState.OVERWORLD
                        self.battle = None
            
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mouse_pos = pygame.mouse.get_pos()
                
                if self.state == GameState.STARTER_SELECTION:
                    self.handle_starter_click(mouse_pos)
                
                elif self.state == GameState.BATTLE:
                    self.handle_battle_click(mouse_pos)
    
    def handle_starter_click(self, mouse_pos):
        """Handle clicks on starter selection"""
        if hasattr(self, 'starter_rects'):
            for rect, data_file in self.starter_rects:
                if rect.collidepoint(mouse_pos):
                    self.player_pokemon = Pokemon(data_file)
                    self.player = Player(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
                    self.state = GameState.OVERWORLD
                    break
    
    def handle_battle_click(self, mouse_pos):
        """Handle clicks during battle"""
        if not self.battle.battle_active:
            return
        
        if self.battle.turn != "player" or self.battle_message_timer > 0:
            return
        
        if hasattr(self, 'move_buttons'):
            for button_rect, action in self.move_buttons:
                if button_rect.collidepoint(mouse_pos):
                    if action == "run":
                        if self.battle.run_away():
                            self.battle_message_timer = 120
                        else:
                            self.battle_message_timer = 60
                            self.auto_progress = True
                    else:
                        self.battle.player_attack(action)
                        self.battle_message_timer = 120
                        self.auto_progress = True
                    break
    
    def update(self):
        """Update game state"""
        if self.state == GameState.OVERWORLD:
            self.update_overworld()
        
        elif self.state == GameState.BATTLE:
            self.update_battle()
        
        if self.encounter_cooldown > 0:
            self.encounter_cooldown -= 1
    
    def update_overworld(self):
        """Update overworld state"""
        keys = pygame.key.get_pressed()
        
        dx = 0
        dy = 0
        
        if keys[pygame.K_LEFT]:
            dx = -1
        elif keys[pygame.K_RIGHT]:
            dx = 1
        
        if keys[pygame.K_UP]:
            dy = -1
        elif keys[pygame.K_DOWN]:
            dy = 1
        
        if dx != 0 or dy != 0:
            self.player.move(dx, dy, (self.world_width, self.world_height))
            self.update_camera()
            
            # Check for encounters
            if self.check_encounter():
                self.start_battle()
    
    def update_battle(self):
        """Update battle state"""
        if self.battle_message_timer > 0:
            self.battle_message_timer -= 1
        
        # Auto-progress to enemy turn
        if self.auto_progress and self.battle_message_timer <= 0:
            if self.battle.turn == "enemy" and self.battle.battle_active:
                self.battle.enemy_attack()
                self.battle_message_timer = 120
            else:
                self.auto_progress = False
    
    def run(self):
        """Main game loop"""
        while self.running:
            self.clock.tick(FPS)
            
            self.handle_events()
            self.update()
            
            # Draw based on state
            if self.state == GameState.INTRO:
                self.draw_intro()
            elif self.state == GameState.STARTER_SELECTION:
                self.draw_starter_selection()
            elif self.state == GameState.OVERWORLD:
                self.draw_overworld()
            elif self.state == GameState.BATTLE:
                self.draw_battle()
            
            pygame.display.flip()
        
        pygame.quit()
        sys.exit()

def main():
    """Entry point"""
    # Check if assets exist
    if not Path("game_assets/data").exists():
        print("=" * 60)
        print("ERROR: Game assets not found!")
        print("Please run 'python download_assets.py' first to download")
        print("all Pokemon data and sprites from PokeAPI.")
        print("=" * 60)
        return
    
    game = Game()
    game.run()

if __name__ == "__main__":
    main()

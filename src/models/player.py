"""
Player character for overworld movement
"""

import pygame

TILE_SIZE = 48

class Player:
    """Player character for overworld movement"""
    
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.speed = 4
        self.rect = pygame.Rect(x, y, TILE_SIZE, TILE_SIZE)
        
        # Create simple player sprite
        self.sprite = pygame.Surface((TILE_SIZE, TILE_SIZE))
        self.sprite.fill((244, 67, 54))  # RED
    
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

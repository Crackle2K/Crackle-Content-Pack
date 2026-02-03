"""UI configuration constants."""

from src.core.type_chart import PokemonType

# Window settings
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60
TITLE = "Pokemon Juno"

# Colors
COLOR_WHITE = (255, 255, 255)
COLOR_BLACK = (0, 0, 0)
COLOR_GRAY = (128, 128, 128)
COLOR_LIGHT_GRAY = (200, 200, 200)
COLOR_DARK_GRAY = (64, 64, 64)

# Pokemon-themed colors
COLOR_PRIMARY = (56, 88, 152)       # Pokemon blue
COLOR_SECONDARY = (232, 208, 48)    # Pokemon yellow
COLOR_ACCENT = (200, 64, 64)        # Pokemon red

# HP bar colors
COLOR_HP_GREEN = (104, 208, 80)
COLOR_HP_YELLOW = (248, 208, 48)
COLOR_HP_RED = (240, 64, 64)
COLOR_HP_BG = (64, 64, 64)

# Background colors
COLOR_BG = (248, 248, 248)
COLOR_BATTLE_BG = (200, 224, 200)
COLOR_MENU_BG = (40, 40, 80)

# Button colors
COLOR_BUTTON = (80, 120, 200)
COLOR_BUTTON_HOVER = (100, 140, 220)
COLOR_BUTTON_PRESSED = (60, 100, 180)
COLOR_BUTTON_DISABLED = (128, 128, 128)
COLOR_BUTTON_TEXT = (255, 255, 255)

# Type colors for move buttons and badges
TYPE_COLORS = {
    PokemonType.NORMAL: (168, 168, 120),
    PokemonType.FIRE: (240, 128, 48),
    PokemonType.WATER: (104, 144, 240),
    PokemonType.ELECTRIC: (248, 208, 48),
    PokemonType.GRASS: (120, 200, 80),
    PokemonType.ICE: (152, 216, 216),
    PokemonType.FIGHTING: (192, 48, 40),
    PokemonType.POISON: (160, 64, 160),
    PokemonType.GROUND: (224, 192, 104),
    PokemonType.FLYING: (168, 144, 240),
    PokemonType.PSYCHIC: (248, 88, 136),
    PokemonType.BUG: (168, 184, 32),
    PokemonType.ROCK: (184, 160, 56),
    PokemonType.GHOST: (112, 88, 152),
    PokemonType.DRAGON: (112, 56, 248),
}

# Font sizes
FONT_SIZE_TITLE = 48
FONT_SIZE_LARGE = 32
FONT_SIZE_MEDIUM = 24
FONT_SIZE_SMALL = 18
FONT_SIZE_TINY = 14

# Timing
MESSAGE_DELAY = 1.5  # seconds
ANIMATION_SPEED = 0.3  # seconds

# Layout constants
PADDING = 20
BUTTON_HEIGHT = 50
BUTTON_WIDTH = 200
HP_BAR_WIDTH = 200
HP_BAR_HEIGHT = 20

# Battle screen layout
OPPONENT_SPRITE_POS = (100, 50)
PLAYER_SPRITE_POS = (500, 250)
SPRITE_SCALE = 3.0  # Pokemon sprites are 96x96, scale up
MESSAGE_BOX_HEIGHT = 100
ACTION_MENU_HEIGHT = 150

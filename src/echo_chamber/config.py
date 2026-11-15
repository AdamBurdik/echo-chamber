import pygame


# Copy from utils.py, cause python is shit and cant resolve circular imports....
def argb_int_to_rgba(value):
    a = (value >> 24) & 0xFF
    r = (value >> 16) & 0xFF
    g = (value >> 8) & 0xFF
    b = value & 0xFF
    return r, g, b, a


def load_image(path: str) -> pygame.Surface:
    return pygame.image.load(path).convert_alpha()


DEBUG__SCALE = True
DEBUG__DRAW_TILEMAP_INDICES = False

DISPLAY_WIDTH = 1920
DISPLAY_HEIGHT = 1080
RENDER_SCALE = 5  # low-res -> hi-res factor
SCREEN_WIDTH = DISPLAY_WIDTH // RENDER_SCALE  # ints, so Surface() accepts them
SCREEN_HEIGHT = DISPLAY_HEIGHT // RENDER_SCALE

TILE_SIZE = 16

MAIN_MENU_BACKGROUND_COLOR = argb_int_to_rgba(0xff2e2a4f)

BOARD_GRID_WIDTH = 17
BOARD_GRID_HEIGHT = 17
BOARD_RENDER_MARGIN = 2  # extra tiles so jumps never expose the background

BACKDROP_PATH = "assets/backdrop.png"
BACKDROP_INTENSITY = 1.0  # strength of the animated edge warp
BACKDROP_SPEED = 0.5  # animation speed multiplier

VERTEX_SHADER_PATH = "assets/shaders/vertex.glsl"
FRAGMENT_SHADER_PATH = "assets/shaders/fragment.glsl"

PLAYER_WIDTH = 8
PLAYER_HEIGHT = 16

PLAYER_MAX_HEALTH = 100
PLAYER_ENEMY_COLLISION_DAMAGE = 10

DAMAGE_LOG_DURATION = 1.0
DAMAGE_LOG_HOLD = 0.3
DAMAGE_LOG_RISE = 10
DAMAGE_LOG_DRIFT = 2.5
DAMAGE_LOG_FLASH_DURATION = 0.08
DAMAGE_LOG_COLOR = (255, 80, 80)
HEAL_LOG_COLOR = (105, 255, 140)
DAMAGE_LOG_FLASH_COLOR = (255, 255, 255)
DAMAGE_LOG_OFFSET_Y = -4

INSTANT_HEAL_AMOUNT = 25
REGENERATION_TICK_AMOUNT = 2
REGENERATION_TICK_INTERVAL = 0.5
REGENERATION_DURATION = 3.0

PLAYER_SCREEN_POS = (SCREEN_WIDTH // 4 + TILE_SIZE, SCREEN_HEIGHT // 2)

GOBLIN_KILL_EXPERIENCE_GAIN = 10

GOBLIN_WIDTH = 10
GOBLIN_HEIGHT = 10
GOBLIN_MAX_HEALTH = 2
GOBLIN_ATTACK_DAMAGE = 5

HUD_HEALTH_RECT = (8, 5, 82, 18)
HUD_EXPERIENCE_RECT = (90, 5, 150, 18)
HUD_XP_GROW_DURATION = 0.2  # easing time for XP fill growth

HUD_HP_WAVE_SPEED = 0.70  # HP fill edge wave speed
HUD_HP_WAVE_AMPLITUDE = 1.0  # HP fill edge wave strength
HUD_XP_WAVE_SPEED = 1.5  # XP fill edge idle wave speed
HUD_XP_WAVE_AMPLITUDE = 0.5  # XP fill edge idle wave strength
HUD_EDGE_WIDTH = 2.0  # width of the shaded right edge in low-res pixels

CARD_WIDTH = 50
CARD_HEIGHT = 16
CARD_QUEUE_BACKGROUND_COLOR = argb_int_to_rgba(0x2e2a4f)
CARD_BACKGROUND_COLOR = argb_int_to_rgba(0xff60556e)
ECHO_CARD_BACKGROUND_COLOR = argb_int_to_rgba(0x287699)
CARD_TEXT_COLOR = argb_int_to_rgba(0xffcdd4a5)
CARD_ICON_COLOR = argb_int_to_rgba(0xffc7786f)
ECHO_CARD_ICON_COLOR = argb_int_to_rgba(0xff0ce6f2)
CARD_ICON_PADDING = 2

CARD_QUEUE_PADDING = 5
CARD_QUEUE_WIDTH = CARD_WIDTH + CARD_QUEUE_PADDING * 2
CARD_QUEUE_HEIGHT = SCREEN_HEIGHT - 38  # SCREEN_HEIGHT - CONFIRM_BUTTON_HEIGHT
CARD_QUEUE_GAP = 1  # Gap between each card pair
CARD_QUEUE_SELECTED_GAP = 10  # Gap between selected ones and the rest
CARD_QUEUE_MAX_SELECTED = 7

CONFIRM_BUTTON_WIDTH = 144
CONFIRM_BUTTON_HEIGHT = 27

CARD_REGISTRY = {
    "move-forward-1": {
        "type": "move-forward-1",
        "icon": "icons/arrow.png",
        "color": argb_int_to_rgba(0xffff0000),
        "lines": [
            "Move 1 tile",
            "forward",
        ],
        "selected": False,
        "actions": [
            {
                "move": {
                    "amount": 1,
                    "direction": "up"
                }
            }
        ],
        "echo": True
    },
    "move-forward-2": {
        "type": "move-forward-2",
        "icon": "icons/arrow.png",
        "color": argb_int_to_rgba(0xff00ff00),
        "lines": [
            "Move 2 tiles",
            "forward",
        ],
        "selected": False,
        "actions": [
            {
                "move": {
                    "amount": 2,
                    "direction": "up"
                }
            }
        ],
        "echo": False
    },
    "move-down-1": {
        "type": "move-down-1",
        "icon": "icons/arrow.png",
        "icon_rotation": 180,
        "color": argb_int_to_rgba(0xff0000ff),
        "lines": [
            "Move 1 tile",
            "down",
        ],
        "selected": False,
        "actions": [
            {
                "move": {
                    "amount": 1,
                    "direction": "down"
                }
            }
        ],
        "echo": False
    },
    "move-left-1": {
        "type": "move-left-1",
        "icon": "icons/arrow.png",
        "icon_rotation": 90,
        "color": argb_int_to_rgba(0xff0000ff),
        "lines": [
            "Move 1 tile",
            "left",
        ],
        "selected": False,
        "actions": [
            {
                "move": {
                    "amount": 1,
                    "direction": "left"
                }
            }
        ],
        "echo": False
    },
    "move-right-1": {
        "type": "move-right-1",
        "icon": "icons/arrow.png",
        "icon_rotation": -90,
        "color": argb_int_to_rgba(0xff0000ff),
        "lines": [
            "Move 1 tile",
            "right",
        ],
        "selected": False,
        "actions": [
            {
                "move": {
                    "amount": 1,
                    "direction": "right"
                }
            }
        ],
        "echo": False
    },
    "do-nothing": {
        "type": "do-nothing",
        "icon": "icons/plus.png",
        "color": argb_int_to_rgba(0xff0000ff),
        "lines": [
            "Do nothing"
        ],
        "selected": False,
        "actions": [],
        "echo": False
    },
    "attack-forward": {
        "type": "attack-forward",
        "icon": "icons/sword.png",
        "color": argb_int_to_rgba(0xffff00ff),
        "lines": [
            "Attacks forward",
            "Damage: 1"
        ],
        "selected": False,
        "actions": [
            {
                "attack_forward": {
                    "damage": 1
                }
            }
        ],
        "echo": False
    },
    "spin-attack": {
        "type": "spin-attack",
        "icon": "icons/clockwise.png",
        "color": argb_int_to_rgba(0xffff8800),
        "lines": [
            "Spin attack",
            "Damage: 1"
        ],
        "selected": False,
        "actions": [
            {
                "spin_attack": {
                    "damage": 1
                }
            }
        ],
        "echo": False
    },
    "rotate-left": {
        "type": "rotate-left",
        "icon": "icons/anti_clockwise.png",
        "color": argb_int_to_rgba(0xff00ffff),
        "lines": [
            "Rotate left"
        ],
        "selected": False,
        "actions": [
            {
                "rotate": {
                    "direction": "left"
                }
            }
        ],
        "echo": False
    },
    "rotate-right": {
        "type": "rotate-right",
        "icon": "icons/clockwise.png",
        "color": argb_int_to_rgba(0xffffff00),
        "lines": [
            "Rotate right"
        ],
        "selected": False,
        "actions": [
            {
                "rotate": {
                    "direction": "right"
                }
            }
        ],
        "echo": False
    },
    "instant-heal": {
        "type": "instant-heal",
        "icon": "icons/heart.png",
        "color": argb_int_to_rgba(0xff66ff88),
        "lines": [
            "Instant heal",
            f"{INSTANT_HEAL_AMOUNT} HP"
        ],
        "selected": False,
        "actions": [
            {
                "heal": {
                    "amount": INSTANT_HEAL_AMOUNT
                }
            }
        ],
        "echo": False
    },
    "regeneration": {
        "type": "regeneration",
        "icon": "icons/plus.png",
        "color": argb_int_to_rgba(0xff66ff88),
        "lines": [
            "Regeneration",
            f"{int(REGENERATION_TICK_AMOUNT * REGENERATION_DURATION / REGENERATION_TICK_INTERVAL)} HP / {REGENERATION_DURATION:g}s"
        ],
        "selected": False,
        "actions": [
            {
                "regenerate": {
                    "amount": REGENERATION_TICK_AMOUNT,
                    "duration": REGENERATION_DURATION
                }
            }
        ],
        "echo": False
    }
}

TILE_REGISTRY = {}


def load_tile_textures() -> None:
    def register(tile_id, image):
        TILE_REGISTRY[tile_id] = {
            "image": load_image(image)
        }

    register("empty", "assets/tiles/empty.png")
    register("hole", "assets/tiles/hole.png")
    register("square_pattern", "assets/tiles/square_pattern.png")
    register("lines", "assets/tiles/lines.png")


FONT_PATH = "./assets/fonts/at01.ttf"
FONT_BASE_SIZE = 12
TEXT_SCALE = 0.67

SIMULATION_DELAY = 120 * 1  # = second

EXPERIENCE_LEVELS = {
    1: 50,
    2: 74,
    3: 112,
    4: 162,
    5: 226,
    6: 304,
    7: 397,
    8: 504,
    9: 627,
    10: 766,
    11: 917,
    12: 1081,
    13: 1258,
    14: 1447,
    15: 1648,
    16: 1860,
    17: 2083,
    18: 2317,
    19: 2561,
    20: 2815,
    21: 3084,
    22: 3367,
    23: 3662,
    24: 3971,
    25: 4293,
    26: 4627,
    27: 4974,
    28: 5333,
    29: 5705,
    30: 6089,
    31: 6490,
    32: 6906,
    33: 7335,
    34: 7777,
    35: 8233,
    36: 8702,
    37: 9183,
    38: 9677,
    39: 10183,
    40: 10702,
    41: 11237,
    42: 11786,
    43: 12349,
    44: 12925,
    45: 13514,
    46: 14115,
    47: 14729,
    48: 15000,
    49: 15000,
    50: 15000
}

EXPERIENCE_MULTIPLIERS = {
    1: 1.0,
    2: 1.1,
    3: 1.22,
    4: 1.36,
    5: 1.52,
    6: 1.70,
    7: 1.90,
    8: 2.12,
    9: 2.30,
    10: 2.50,
    11: 3.12,
    12: 3.90,
    13: 4.88,
    14: 6.09,
    15: 7.61,
    16: 9.51,
    17: 11.89,
    18: 14.86,
    19: 18.57,
    20: 23.22,
    21: 25.80,
    22: 28.67,
    23: 31.86,
    24: 35.40,
    25: 39.33,
    26: 43.70,
    27: 48.56,
    28: 53.95,
    29: 59.95,
    30: 66.61,
    31: 71.39,
    32: 76.51,
    33: 81.99,
    34: 87.87,
    35: 94.17,
    36: 100.0,
    37: 100.0,
    38: 100.0,
    39: 100.0,
    40: 100.0,
    41: 100.0,
    42: 100.0,
    43: 100.0,
    44: 100.0,
    45: 100.0,
    46: 100.0,
    47: 100.0,
    48: 100.0,
    49: 100.0,
    50: 100.0
}
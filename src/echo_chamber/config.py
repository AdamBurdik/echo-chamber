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

TILE_GENERATION_SEED = 2227
TILE_PATCH_SCALE = 6.0
TILE_DETAIL_SCALE = 2.0
TRAP_SPAWN_CHANCE = 0.01
TRAP_SPAWN_SAFE_RADIUS = 3

ENEMY_SPAWN_CHANCE = 0.015
ENEMY_SPAWN_SAFE_RADIUS = 4
STARTING_ENEMY_COUNT_MIN = 2
STARTING_ENEMY_COUNT_MAX = 3
STARTING_ENEMY_SPAWN_RADIUS = 8
STARTING_ENEMY_MIN_DISTANCE = 5
ENEMY_CAP_BASE = 3
ENEMY_CAP_PER_LEVEL = 1
CULTIST_CAP_BASE = 1
CULTIST_CAP_LEVEL_INTERVAL = 3

BACKDROP_PATH = "assets/backdrop.png"
BACKDROP_INTENSITY = 1.0  # strength of the animated edge warp
BACKDROP_SPEED = 0.5  # animation speed multiplier

VERTEX_SHADER_PATH = "assets/shaders/vertex.glsl"
FRAGMENT_SHADER_PATH = "assets/shaders/fragment.glsl"

PLAYER_WIDTH = 8
PLAYER_HEIGHT = 16

PLAYER_MAX_HEALTH = 100
PLAYER_ENEMY_COLLISION_DAMAGE = 10

TRAP_PATH = "assets/traps/spikes.png"
TRAP_ICON_PATH = "assets/icons/spikes.png"
TRAP_PLAYER_DAMAGE = 15
TRAP_ENEMY_DAMAGE = 1

SUMMON_LOG_DURATION = 5.0
SUMMON_LOG_HOLD = 0.3
SUMMON_LOG_RISE = 4
SUMMON_LOG_DRIFT = 0.2
SUMMON_LOG_FLASH_DURATION = 0.08
SUMMON_LOG_COLOR = (180, 80, 255)
SUMMON_LOG_FLASH_COLOR = (255, 255, 255)
SUMMON_LOG_OFFSET_Y = -8

DAMAGE_LOG_DURATION = 1.0
DAMAGE_LOG_HOLD = 0.3
DAMAGE_LOG_RISE = 10
DAMAGE_LOG_DRIFT = 2.5
DAMAGE_LOG_FLASH_DURATION = 0.08
DAMAGE_LOG_COLOR = (255, 80, 80)
HEAL_LOG_COLOR = (105, 255, 140)
BLOCK_LOG_COLOR = (120, 200, 255)
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

SLIME_WIDTH = 11
SLIME_HEIGHT = 10
FULL_SLIME_MAX_HEALTH = 3
HALF_SLIME_MAX_HEALTH = 2
QUARTER_SLIME_MAX_HEALTH = 1
FULL_SLIME_ATTACK_DAMAGE = 8
HALF_SLIME_ATTACK_DAMAGE = 4
QUARTER_SLIME_ATTACK_DAMAGE = 2
SLIME_SPLIT_RADIUS = 2
SLIME_SPLIT_COUNT = 2
SLIME_SPLIT_JUMP_STAGGER = 0.08

CULTIST_WIDTH = 8
CULTIST_HEIGHT = 16
CULTIST_MAX_HEALTH = 5
CULTIST_ATTACK_DAMAGE = 5
CULTIST_IDEAL_DISTANCE_PX = 80
CULTIST_DISTANCE_TOLERANCE_PX = 8
CULTIST_KILL_EXPERIENCE_GAIN = 25
CULTIST_SUMMON_COOLDOWN_TURNS = 10
CULTIST_SUMMON_RETREAT_TURNS = 3

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
CARD_QUEUE_BACKGROUND_COLOR = argb_int_to_rgba(0xff2e2a4f)
CARD_BACKGROUND_COLOR = argb_int_to_rgba(0xff60556e)
ECHO_CARD_BACKGROUND_COLOR = argb_int_to_rgba(0x287699)
ECHO_CARD_BORDER_DARK_COLOR = argb_int_to_rgba(0xff0098db)
ECHO_CARD_BORDER_LIGHT_COLOR = argb_int_to_rgba(0xff0ce6f2)
CURSE_CARD_BACKGROUND_COLOR = argb_int_to_rgba(0xff3d2666)
CURSE_CARD_BORDER_DARK_COLOR = argb_int_to_rgba(0xff6a2fa0)
CURSE_CARD_BORDER_LIGHT_COLOR = argb_int_to_rgba(0xffb56cff)
CARD_TEXT_COLOR = argb_int_to_rgba(0xffcdd4a5)
CURSE_CARD_TEXT_COLOR = argb_int_to_rgba(0xffe6d4ff)
CARD_ICON_COLOR = argb_int_to_rgba(0xffc7786f)
ECHO_CARD_ICON_COLOR = argb_int_to_rgba(0xff0ce6f2)
CURSE_CARD_ICON_COLOR = argb_int_to_rgba(0xffc77dff)
CARD_ICON_PADDING = 2

CARD_QUEUE_PADDING = 5
CARD_QUEUE_WIDTH = CARD_WIDTH + CARD_QUEUE_PADDING * 2
CARD_QUEUE_HEIGHT = SCREEN_HEIGHT - 40  # SCREEN_HEIGHT - CONFIRM_BUTTON_HEIGHT
CARD_QUEUE_GAP = 1  # Gap between each card pair
ECHO_COUNTDOWN_DEFAULT = 3  # Fallback for cards without a per-card echo countdown
ECHO_OVERFLOW_DIVISOR = 3  # Fraction of chamber cards auto-played on overflow
CARD_QUEUE_SELECTED_GAP = 10  # Gap between selected ones and the rest
CARD_QUEUE_MAX_SELECTED = 7

ACTION_QUEUE_CAPACITY = 10

CARD_GEN_MIN_PER_TURN = 1
CARD_GEN_MAX_PER_TURN = 2
CARD_GEN_THREAT_RADIUS = 3
CARD_GEN_THREAT_MEDIUM_COUNT = 2
CARD_GEN_THREAT_HIGH_COUNT = 3
CARD_GEN_LOW_HEALTH_RATIO = 0.4
CARD_GEN_MAX_HEAL_PER_BATCH = 1
CARD_GEN_MAX_HEAL_IN_INVENTORY = 2
CARD_GEN_DUPLICATE_TYPE_PENALTY = 2.0
CARD_GEN_DUPLICATE_CATEGORY_PENALTY = 0.25
CARD_GEN_CALM_WEIGHTS = {
    "movement": 6.0,
    "rotation": 4.5,
    "combat": 1.5,
    "defense": 1.5,
    "heal": 0.8,
}
CARD_GEN_MEDIUM_WEIGHTS = {
    "movement": 5.0,
    "rotation": 3.5,
    "combat": 3.0,
    "defense": 3.0,
    "heal": 0.8,
}
CARD_GEN_THREAT_WEIGHTS = {
    "movement": 4.0,
    "rotation": 2.5,
    "combat": 5.0,
    "defense": 4.5,
    "heal": 0.8,
}
CARD_GEN_LOW_HEALTH_HEAL_WEIGHT = 8.0

ECHO_QUEUE_CAPACITY = 8

ENERGY_SPIKE_DAMAGE = 15
ENERGY_SPIKE_RADIUS_TILES = 3
ENERGY_SPIKE_FRAME_DURATION = 0.08
ENERGY_SPIKE_SHAKE_DURATION = 0.35
ENERGY_SPIKE_SHAKE_INTENSITY = 3.0  # low-res pixels
ENERGY_SPIKE_FLASH_DURATION = 0.12
ENERGY_SPIKE_FLASH_COLOR = (180, 240, 255)
ENERGY_SPIKE_FLASH_ALPHA = 150

CONFIRM_BUTTON_WIDTH = 144
CONFIRM_BUTTON_HEIGHT = 27

CARD_REGISTRY = {
    "move-forward": {
        "type": "move-forward",
        "icon": "assets/icons/arrow.png",
        "color": argb_int_to_rgba(0xffff0000),
        "lines": [
            "Move 1 tile",
            "forward",
        ],
        "selected": False,
        "actions": [
            {
                "move_relative": {
                    "amount": 1,
                    "direction": "forward"
                }
            }
        ],
        "echo": True,
        "echo_countdown": 3
    },
    "do-nothing": {
        "type": "do-nothing",
        "icon": "assets/icons/plus.png",
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
        "icon": "assets/icons/sword.png",
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
        "icon": "assets/icons/clockwise.png",
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
        "icon": "assets/icons/anti_clockwise.png",
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
        "icon": "assets/icons/clockwise.png",
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
        "icon": "assets/icons/heart.png",
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
        "icon": "assets/icons/plus.png",
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
    },
    "spawn-trap": {
        "type": "spawn-trap",
        "icon": TRAP_ICON_PATH,
        "color": argb_int_to_rgba(0xffcc6633),
        "lines": [
            "Spawn trap",
            "In front"
        ],
        "selected": False,
        "actions": [
            {
                "spawn_trap": {}
            }
        ],
        "echo": False
    },
    "block-one": {
        "type": "block-one",
        "icon": "assets/icons/shield.png",
        "color": argb_int_to_rgba(0xff3399ff),
        "lines": [
            "Block 1",
            "adjacent attack"
        ],
        "selected": False,
        "actions": [
            {
                "block": {
                    "charges": 1
                }
            }
        ],
        "echo": False
    },
    "block-all": {
        "type": "block-all",
        "icon": "assets/icons/shield.png",
        "color": argb_int_to_rgba(0xff66ccff),
        "lines": [
            "Block all",
            "adjacent attacks"
        ],
        "selected": False,
        "actions": [
            {
                "block": {
                    "all_surrounding": True
                }
            }
        ],
        "echo": False
    },
    "dead-weight": {
        "type": "dead-weight",
        "icon": "assets/icons/curse.png",
        "lines": [
            "Dead weight",
            "Unplayable"
        ],
        "selected": False,
        "actions": [],
        "echo": False,
        "playable": False,
        "curse": True,
        "curse_effect": "dead_weight",
        "curse_targets": ["action", "echo"],
        "echo_countdown": 3
    },
    "uncontrolled-step": {
        "type": "uncontrolled-step",
        "icon": "assets/icons/curse.png",
        "lines": [
            "Uncontrolled",
            "Random step"
        ],
        "selected": False,
        "actions": [
            {
                "random_step": {}
            }
        ],
        "echo": False,
        "curse": True,
        "curse_effect": "uncontrolled_step",
        "curse_targets": ["action", "echo"],
        "echo_countdown": 3
    },
    "parasite": {
        "type": "parasite",
        "icon": "assets/icons/curse.png",
        "lines": [
            "Parasite",
            "Corrupts"
        ],
        "selected": False,
        "actions": [],
        "echo": False,
        "curse": True,
        "curse_effect": "parasite",
        "curse_targets": ["action"]
    },
    "dummy": {
        "type": "dummy",
        "lines": [
            "Dud"
        ],
        "selected": False,
        "actions": [],
        "echo": False,
        "random_spawn": False
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
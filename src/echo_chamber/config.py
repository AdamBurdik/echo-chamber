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

BOARD_GRID_WIDTH = 15
BOARD_GRID_HEIGHT = 15

PLAYER_WIDTH = 8
PLAYER_HEIGHT = 16

PLAYER_SCREEN_POS = (SCREEN_WIDTH // 4 + TILE_SIZE, SCREEN_HEIGHT // 2)

GOBLIN_WIDTH = 10
GOBLIN_HEIGHT = 10

CARD_WIDTH = 50
CARD_HEIGHT = 20

CARD_QUEUE_PADDING = 5
CARD_QUEUE_WIDTH = CARD_WIDTH + CARD_QUEUE_PADDING * 2
CARD_QUEUE_HEIGHT = SCREEN_HEIGHT - 32  # SCREEN_HEIGHT - CONFIRM_BUTTON_HEIGHT
CARD_QUEUE_GAP = 1  # Gap between each card pair
CARD_QUEUE_SELECTED_GAP = 20  # Gap between selected ones and the rest

CONFIRM_BUTTON_WIDTH = CARD_WIDTH + CARD_QUEUE_PADDING * 2
CONFIRM_BUTTON_HEIGHT = 32

CARD_REGISTRY = {
    "dummy": {
        "type": "dummy",
        "color": argb_int_to_rgba(0x9a6278),
        "lines": [
            "Lorem ipsum",
            "dolor sit amet",
        ],
        "selected": False,
        "actions": [
        ]
    },
    "move-forward-1": {
        "type": "move-forward-1",
        "color": argb_int_to_rgba(0xff0000),
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
        ]
    },
    "move-forward-2": {
        "type": "move-forward-2",
        "color": argb_int_to_rgba(0x00ff00),
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
        ]
    }
}

TILE_REGISTRY = {}

def load_tile_textures() -> None:
    def register(tile_id, image):
        TILE_REGISTRY[tile_id] = {
            "image": load_image(image)
        }
    
    register("empty", "assets/tiles/empty.png")


FONT_PATH = "./assets/fonts/at01.ttf"
FONT_BASE_SIZE = 12
TEXT_SCALE = 0.67

SIMULATION_DELAY = 120 * 1 # = second
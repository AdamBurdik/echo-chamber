import copy
import random

import pygame

from echo_chamber.config import RENDER_SCALE, SCALE, CARD_REGISTRY


def argb_int_to_rgba(value):
    a = (value >> 24) & 0xFF
    r = (value >> 16) & 0xFF
    g = (value >> 8) & 0xFF
    b = value & 0xFF
    return (r, g, b, a)

# Returns mouse position but projected to rendering size
def get_mouse_position() -> tuple[int, int]:
    mouse_x, mouse_y = pygame.mouse.get_pos()

    if SCALE:
        return mouse_x // RENDER_SCALE, mouse_y // RENDER_SCALE

    return mouse_x, mouse_y

def generate_card() -> dict:
    random_card = random.choice(list(CARD_REGISTRY.values()))
    random_card = copy.deepcopy(random_card)
    # Id ensures that each card has unique hash  
    random_card["_id"] = random.randint(0, 99999999)
    return random_card


def load_image(path: str) -> pygame.Surface:
    return pygame.image.load(path).convert_alpha()
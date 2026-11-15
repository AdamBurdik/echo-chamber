import copy
import random

import pygame

from echo_chamber.config import RENDER_SCALE, DEBUG__SCALE, CARD_REGISTRY


def argb_int_to_rgba(value):
    a = (value >> 24) & 0xFF
    r = (value >> 16) & 0xFF
    g = (value >> 8) & 0xFF
    b = value & 0xFF
    return r, g, b, a

# Returns mouse position but projected to rendering size
def get_mouse_position() -> tuple[int, int]:
    mouse_x, mouse_y = pygame.mouse.get_pos()

    if DEBUG__SCALE:
        return mouse_x // RENDER_SCALE, mouse_y // RENDER_SCALE

    return mouse_x, mouse_y

def create_card(card_type: str) -> dict:
    card = copy.deepcopy(CARD_REGISTRY[card_type])
    # Id ensures that each card has unique hash
    card["_id"] = random.randint(0, 99999999)
    return card


def generate_card() -> dict:
    spawnable_cards = [
        card for card in CARD_REGISTRY.values()
        if card.get("random_spawn", True) and not card.get("curse", False)
    ]
    random_card = random.choice(spawnable_cards)
    return create_card(random_card["type"])


def load_image(path: str) -> pygame.Surface:
    return pygame.image.load(path).convert_alpha()
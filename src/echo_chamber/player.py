import pygame

from echo_chamber.config import *
from echo_chamber.layer import TextLayer
from echo_chamber.utils import load_image


class Player:
    def __init__(self) -> None:
        board_width = TILE_SIZE * BOARD_GRID_WIDTH
        board_height = TILE_SIZE * BOARD_GRID_HEIGHT
        board_origin = (
            (SCREEN_WIDTH - board_width) / 6,
            (SCREEN_HEIGHT - board_height) / 2
        )
        
        self.origin = (
            board_origin[0] + (board_width - PLAYER_WIDTH) / 2,
            board_origin[1] + (board_height - PLAYER_HEIGHT) / 2,
        )
        
        self.textures = {
            "idle": {
                "front": load_image("assets/player/idle/front.png"),
                "back": load_image("assets/player/idle/back.png"),
                "left": load_image("assets/player/idle/left.png"),
                "right": load_image("assets/player/idle/right.png"),
                
            }
        }
        
        self.direction = "front"
        self.state = "idle"
    
    def render(self, surface: pygame.Surface, text_layer: TextLayer) -> None:
        texture = self.textures[self.state][self.direction]
        surface.blit(texture, self.origin)
        
    
    def handle_input(self, event: pygame.Event) -> None:
        ...
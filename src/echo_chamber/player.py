from unittest import case

from echo_chamber.config import *
from echo_chamber.layer import TextLayer
from echo_chamber.utils import load_image


class Player:
    def __init__(self) -> None:
        self.origin = PLAYER_SCREEN_POS
        
        self.textures = {
            "idle": {
                "up": load_image("assets/player/idle/front.png"),
                "down": load_image("assets/player/idle/back.png"),
                "left": load_image("assets/player/idle/left.png"),
                "right": load_image("assets/player/idle/right.png"),
                
            }
        }
        
        self.direction = "up"
        self.state = "idle"
        
    def get_direction_vector(self) -> tuple[int, int]:
        match self.direction:
            case "up": return 0, -1
            case "down": return 0, 1
            case "right": return 1, 0
            case "left": return 1, 1
        raise Exception(f"Invalid direction: {self.direction}")

    def render(self, surface: pygame.Surface, text_layer: TextLayer) -> None:
        texture = self.textures[self.state][self.direction]
        surface.blit(texture, self.origin)
        
    
    def handle_input(self, event: pygame.Event) -> None:
        ...
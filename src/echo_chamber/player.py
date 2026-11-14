import math

from echo_chamber.config import *
from echo_chamber.easing import ease_in_out_cubic
from echo_chamber.utils import load_image



JUMP_DURATION = 0.4   # seconds
JUMP_HEIGHT = 8 # pixels

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
        
        self.animation = "jump_up"
        self.animation_state = 0
        self.offset: list[int] = [0, 0]

        self.jumping = False
        self.jump_t = 0.0
        self.jump_start_offset = (0, 0)
        self.hop_y = 0.0
        
    def get_direction_vector(self) -> tuple[int, int]:
        match self.direction:
            case "up": return 0, -1
            case "down": return 0, 1
            case "right": return 1, 0
            case "left": return -1, 0
        raise Exception(f"Invalid direction: {self.direction}")

    def jump_up(self, board) -> None:
        self.jump(board, self.direction)

    def jump(self, board, direction: str) -> None:
        if self.jumping:
            return 

        self.direction = direction
        dx, dy = self.get_direction_vector()

        board.move_player((dx, dy), 1)  # logical move happens instantly

        # The logical move is instant, so offset the board back by exactly one
        # tile to keep the old frame on screen. It then eases back to zero.
        self.jump_start_offset = (dx * TILE_SIZE, dy * TILE_SIZE)
        board.camera_offset[0], board.camera_offset[1] = self.jump_start_offset

        self.jumping = True
        self.jump_t = 0.0

    def update(self, dt, board) -> None:
        if not self.jumping:
            return

        self.jump_t = min(1.0, self.jump_t + dt / JUMP_DURATION)
        t = self.jump_t

        # Board eases from the old frame to the new one without overshoot
        remaining = 1.0 - ease_in_out_cubic(t)
        board.camera_offset[0] = self.jump_start_offset[0] * remaining
        board.camera_offset[1] = self.jump_start_offset[1] * remaining

        # Player hops in an arc (0 -> peak -> 0)
        self.hop_y = -math.sin(math.pi * t) * JUMP_HEIGHT

        if t >= 1.0:
            self.jumping = False
            board.camera_offset[0] = board.camera_offset[1] = 0.0
            self.hop_y = 0.0

    def render(self, surface, text_layer) -> None:
        texture = self.textures[self.state][self.direction]
        surface.blit(texture, (self.origin[0], self.origin[1] + self.hop_y))
    
    def handle_input(self, event: pygame.Event) -> None:
        ...
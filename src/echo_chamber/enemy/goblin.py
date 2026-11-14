import random
from typing import TYPE_CHECKING

from echo_chamber.config import *
from echo_chamber.enemy.enemy import AbstractEnemy
from echo_chamber.layer import TextLayer

if TYPE_CHECKING:
    from echo_chamber.main import Game


class Goblin(AbstractEnemy):
    def __init__(self, game: "Game", grid_pos: tuple[int, int]) -> None:
        super().__init__(game, grid_pos)

        self.textures = {
            "idle": {
                "up": load_image("assets/goblin/idle/front.png"),
                "down": load_image("assets/goblin/idle/back.png"),
                "left": load_image("assets/goblin/idle/left.png"),
                "right": load_image("assets/goblin/idle/right.png"),

            }
        }

        self.direction = "up"
        self.state = "idle"

        self.origin = (
            PLAYER_SCREEN_POS[0] - PLAYER_WIDTH / 2,
            PLAYER_SCREEN_POS[1] + PLAYER_HEIGHT / 4,
        )

    def update(self) -> None:
        pass

    def render(self, surface: pygame.Surface, text_layer: TextLayer) -> None:
        x, y = self.game.board.grid_to_screen(self.grid_pos[0], self.grid_pos[1])
        
        x += (TILE_SIZE - GOBLIN_WIDTH) / 2
        y += (TILE_SIZE - GOBLIN_HEIGHT) / 2
        
        texture = self.textures[self.state][self.direction]
        surface.blit(texture, (x, y))

    def simulation_step(self) -> None:
        path: list[tuple[int, int]] = self.game.board.find_path_to_player(self.grid_pos)
        if len(path) <= 1:
            return 
        
        if random.randint(0, 2) == 0:
            return
        
        self.grid_pos = path[1]
        print("Moved closer")

import pygame

from echo_chamber.config import *
from echo_chamber.utils import load_image


class Board:
    def __init__(self) -> None:
        self.tile_texture = load_image("assets/tiles/tile1.png")
        self.board_width = TILE_SIZE * BOARD_GRID_WIDTH
        self.board_height = TILE_SIZE * BOARD_GRID_HEIGHT
        self.origin = (
            (SCREEN_WIDTH - self.board_width) / 6,
            (SCREEN_HEIGHT - self.board_height) / 2
        )

    def render(self, surface: pygame.Surface) -> None:
        for grid_y in range(BOARD_GRID_HEIGHT):
            for grid_x in range(BOARD_GRID_WIDTH):
                x = grid_x * TILE_SIZE + self.origin[0]
                y = grid_y * TILE_SIZE + self.origin[1]
                surface.blit(self.tile_texture, (x, y))

    def update(self) -> None:
        ...
from echo_chamber.config import *
from echo_chamber.layer import TextLayer
import pygame


class Board:
    def __init__(self) -> None:
        # Center origin to the middle of the screen
        self.origin = (
            PLAYER_SCREEN_POS[0] - PLAYER_WIDTH / 2,
            PLAYER_SCREEN_POS[1] + PLAYER_HEIGHT / 4,
        )

        self.tile_map = {}
        self.generate_initial_tilemap()

        # Use a list so coordinates can be updated in place
        self.player_position = [0, 0]

    def generate_initial_tilemap(self) -> None:
        for grid_y in range(BOARD_GRID_HEIGHT):
            for grid_x in range(BOARD_GRID_WIDTH):
                if grid_y not in self.tile_map:
                    self.tile_map[grid_y] = {}

                self.tile_map[grid_y][grid_x] = "empty"

    def get_tiles_around(self, grid_x: int, grid_y: int, radius: int) -> list[tuple[int, int]]:
        tiles: list[tuple[int, int]] = []

        for dy in range(-radius, radius + 1):
            for dx in range(-radius, radius + 1):
                tiles.append((grid_x + dx, grid_y + dy))

        return tiles

    def render(self, surface: pygame.Surface, text_layer: TextLayer) -> None:
        for (grid_x, grid_y) in self.get_tiles_around(self.player_position[0], self.player_position[1], (BOARD_GRID_WIDTH - 1) // 2):
            row = self.tile_map.get(grid_y)
            if row is None:
                row = {}
                self.tile_map[grid_y] = row

            tile_id = row.get(grid_x)
            if tile_id is None:
                # TODO Proper generation
                tile_id = "empty"
                row[grid_x] = tile_id

            tile = TILE_REGISTRY.get(tile_id)
            if tile is None:
                tile = TILE_REGISTRY["empty"]

            image = tile["image"]

            rel_x = grid_x - self.player_position[0]
            rel_y = grid_y - self.player_position[1]

            x = (rel_x * TILE_SIZE) + self.origin[0]
            y = (rel_y * TILE_SIZE) + self.origin[1]

            surface.blit(image, (x, y))

            if DEBUG__DRAW_TILEMAP_INDICES:
                text_layer.draw_text(f"{grid_x}; {grid_y}", (x, y))

    def move_player(self, direction: tuple[int, int]) -> None:
        self.player_position[0] += direction[0]
        self.player_position[1] += direction[1]

    def update(self) -> None:
        ...
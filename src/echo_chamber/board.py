import random
from collections import deque
from typing import TYPE_CHECKING

import pygame

from echo_chamber.config import *
from echo_chamber.layer import TextLayer

if TYPE_CHECKING:
    from echo_chamber.main import Game


class Board:
    def __init__(self, game: "Game") -> None:
        self.game: Game = game

        # Center origin to the middle of the screen
        self.origin = (
            PLAYER_SCREEN_POS[0] - PLAYER_WIDTH / 2,
            PLAYER_SCREEN_POS[1] + PLAYER_HEIGHT / 4,
        )

        self.tile_map = {}
        self.generate_initial_tilemap()

        # Use a list so coordinates can be updated in place
        self.player_position = [0, 0]
        self.camera_offset = [0.0, 0.0]
        
        self.backdrop: pygame.Surface = load_image("assets/backdrop.png")

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
        for (grid_x, grid_y) in self.get_tiles_around(self.player_position[0], self.player_position[1],
                                                      (BOARD_GRID_WIDTH - 1) // 2):
            row = self.tile_map.get(grid_y)
            if row is None:
                row = {}
                self.tile_map[grid_y] = row

            tile_id = row.get(grid_x)
            if tile_id is None:
                # TODO Proper generation\

                if random.randint(0, 10) == 0:
                    self.game.spawn_goblin(grid_x, grid_y)

                tile_id = "empty"
                row[grid_x] = tile_id

            tile = TILE_REGISTRY.get(tile_id)
            if tile is None:
                tile = TILE_REGISTRY["empty"]

            image = tile["image"]

            rel_x = grid_x - self.player_position[0]
            rel_y = grid_y - self.player_position[1]

            x = (rel_x * TILE_SIZE) + self.origin[0] + self.camera_offset[0]
            y = (rel_y * TILE_SIZE) + self.origin[1] + self.camera_offset[1]

            surface.blit(image, (x, y))

            if DEBUG__DRAW_TILEMAP_INDICES:
                text_layer.draw_text(f"{grid_x}; {grid_y}", (x, y))

        surface.blit(self.backdrop, (0, 0))

    def move_player(self, direction: tuple[int, int], amount: int) -> None:
        self.player_position[0] += direction[0] * amount
        self.player_position[1] += direction[1] * amount

    def move_player_relative(self, direction: str, amount: int) -> None:
        idk = {
            "up": (0, -1),
            "down": (0, 1),
            "left": (-1, 0),
            "right": (1, 0),
        }
        self.move_player(idk[direction], amount)

    def update(self) -> None:
        ...

    def grid_to_screen(self, grid_x: int, grid_y: int) -> tuple[float, float]:
        rel_x = grid_x - self.player_position[0]
        rel_y = grid_y - self.player_position[1]

        x = (rel_x * TILE_SIZE) + self.origin[0] + self.camera_offset[0]
        y = (rel_y * TILE_SIZE) + self.origin[1] + self.camera_offset[1]
        return x, y


    def find_path_to_player(self, start: tuple[int, int]) -> list[tuple[int, int]]:
        target = (self.player_position[0], self.player_position[1])
    
        if start == target:
            return [start]
    
        queue = deque([(start, [start])])
        visited = {start}
    
        # (up, down, left, right)
        directions = [(0, -1), (0, 1), (-1, 0), (1, 0)]
    
        while queue:
            current, path = queue.popleft()
    
            for dx, dy in directions:
                next_pos = (current[0] + dx, current[1] + dy)
    
                if next_pos == target:
                    return path + [next_pos]
    
                if next_pos not in visited:
                    row = self.tile_map.get(next_pos[1])
                    tile_id = row.get(next_pos[0]) if row else "empty"
                    tile = TILE_REGISTRY.get(tile_id, TILE_REGISTRY["empty"])
    
                    is_walkable = tile.get("walkable", True)
    
                    if is_walkable:
                        visited.add(next_pos)
                        queue.append((next_pos, path + [next_pos]))
    
        return []

import math
from collections import deque
from typing import TYPE_CHECKING

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
        self.traps: set[tuple[int, int]] = set()

        self.player_position = [0, 0]
        self.camera_offset = [0.0, 0.0]

        self.generate_initial_tilemap()
        self.trap_image = load_image(TRAP_PATH)

    def generate_initial_tilemap(self) -> None:
        half_width = (BOARD_GRID_WIDTH - 1) // 2
        half_height = (BOARD_GRID_HEIGHT - 1) // 2

        for grid_y in range(-half_height, half_height + 1):
            for grid_x in range(-half_width, half_width + 1):
                self._ensure_tile(grid_x, grid_y)

    def _hash01(self, x: int, y: int, salt: int) -> float:
        mask = 0xFFFFFFFFFFFFFFFF
        value = (
            x * 0x9E3779B97F4A7C15
            + y * 0xC2B2AE3D27D4EB4F
            + salt * 0x165667B19E3779F9
        ) & mask
        value = ((value ^ (value >> 30)) * 0xBF58476D1CE4E5B9) & mask
        value = ((value ^ (value >> 27)) * 0x94D049BB133111EB) & mask
        value ^= value >> 31
        return value / mask

    def _value_noise(self, x: float, y: float, scale: float, salt: int) -> float:
        grid_x = x / scale
        grid_y = y / scale
        x0 = math.floor(grid_x)
        y0 = math.floor(grid_y)
        tx = grid_x - x0
        ty = grid_y - y0
        sx = tx * tx * (3 - 2 * tx)
        sy = ty * ty * (3 - 2 * ty)

        n00 = self._hash01(x0, y0, salt)
        n10 = self._hash01(x0 + 1, y0, salt)
        n01 = self._hash01(x0, y0 + 1, salt)
        n11 = self._hash01(x0 + 1, y0 + 1, salt)

        nx0 = n00 + (n10 - n00) * sx
        nx1 = n01 + (n11 - n01) * sx
        return nx0 + (nx1 - nx0) * sy

    def _tile_noise(self, x: int, y: int, scale: float, salt: int) -> float:
        return (
            self._value_noise(x, y, scale, salt) * 0.7
            + self._value_noise(x, y, scale / 2, salt + 17) * 0.3
        )

    def _generate_tile_id(self, grid_x: int, grid_y: int) -> str:
        patch = self._tile_noise(
            grid_x, grid_y, TILE_PATCH_SCALE, TILE_GENERATION_SEED
        )
        detail = self._tile_noise(
            grid_x, grid_y, TILE_DETAIL_SCALE, TILE_GENERATION_SEED + 1
        )

        if patch < 0.48:
            return "empty"
        if patch < 0.58:
            return "hole"
        if patch < 0.70:
            return "lines" if detail < 0.5 else "square_pattern"
        return "square_pattern" if detail < 0.55 else "lines"

    def _should_place_trap(self, grid_x: int, grid_y: int) -> bool:
        player_x, player_y = self.player_position
        if max(abs(grid_x - player_x), abs(grid_y - player_y)) <= TRAP_SPAWN_SAFE_RADIUS:
            return False

        chance = self._hash01(grid_x, grid_y, TILE_GENERATION_SEED + 2)
        return chance < TRAP_SPAWN_CHANCE

    def _ensure_tile(self, grid_x: int, grid_y: int, allow_spawns: bool = False) -> str:
        row = self.tile_map.get(grid_y)
        if row is None:
            row = {}
            self.tile_map[grid_y] = row

        tile_id = row.get(grid_x)
        if tile_id is not None:
            return tile_id

        tile_id = self._generate_tile_id(grid_x, grid_y)
        row[grid_x] = tile_id

        if self._should_place_trap(grid_x, grid_y):
            self.traps.add((grid_x, grid_y))
        elif allow_spawns and (grid_x, grid_y) not in self.traps:
            self.game.maybe_spawn_enemy(grid_x, grid_y)

        return tile_id

    def get_tiles_around(self, grid_x: int, grid_y: int, radius: int) -> list[tuple[int, int]]:
        tiles: list[tuple[int, int]] = []

        for dy in range(-radius, radius + 1):
            for dx in range(-radius, radius + 1):
                tiles.append((grid_x + dx, grid_y + dy))

        return tiles

    def render(self, surface: pygame.Surface, text_layer: TextLayer) -> None:
        camera_x = round(self.camera_offset[0])
        camera_y = round(self.camera_offset[1])
        origin_x = round(self.origin[0])
        origin_y = round(self.origin[1])
        radius = (BOARD_GRID_WIDTH - 1) // 2 + BOARD_RENDER_MARGIN

        for (grid_x, grid_y) in self.get_tiles_around(self.player_position[0], self.player_position[1],
                                                      radius):
            tile_id = self._ensure_tile(grid_x, grid_y, allow_spawns=True)
            tile = TILE_REGISTRY.get(tile_id, TILE_REGISTRY["empty"])
            image = tile["image"]

            rel_x = grid_x - self.player_position[0]
            rel_y = grid_y - self.player_position[1]

            x = (rel_x * TILE_SIZE) + origin_x + camera_x
            y = (rel_y * TILE_SIZE) + origin_y + camera_y

            surface.blit(image, (x, y))

            if (grid_x, grid_y) in self.traps:
                surface.blit(self.trap_image, (x, y))

            if DEBUG__DRAW_TILEMAP_INDICES:
                text_layer.draw_text(f"{grid_x}; {grid_y}", (x, y))

    def place_trap(self, grid_pos: tuple[int, int]) -> None:
        self.traps.add(tuple(grid_pos))

    def trigger_trap(self, grid_pos: tuple[int, int]) -> bool:
        grid_pos = tuple(grid_pos)
        if grid_pos not in self.traps:
            return False

        self.traps.remove(grid_pos)
        return True

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

    def grid_to_screen(self, grid_x: int, grid_y: int) -> tuple[float, float]:
        rel_x = grid_x - self.player_position[0]
        rel_y = grid_y - self.player_position[1]

        x = (rel_x * TILE_SIZE) + round(self.origin[0]) + round(self.camera_offset[0])
        y = (rel_y * TILE_SIZE) + round(self.origin[1]) + round(self.camera_offset[1])
        return x, y


    def is_walkable(self, grid_pos: tuple[int, int]) -> bool:
        row = self.tile_map.get(grid_pos[1])
        tile_id = row.get(grid_pos[0]) if row else "empty"
        tile = TILE_REGISTRY.get(tile_id, TILE_REGISTRY["empty"])
        return tile.get("walkable", True)

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
    
                if next_pos not in visited and self.is_walkable(next_pos):
                    visited.add(next_pos)
                    queue.append((next_pos, path + [next_pos]))
    
        return []

import abc
import math
from typing import TYPE_CHECKING

import pygame

from echo_chamber.config import TRAP_ENEMY_DAMAGE
from echo_chamber.easing import ease_in_out_cubic
from echo_chamber.layer import TextLayer

if TYPE_CHECKING:
    from echo_chamber.main import Game


class AbstractEnemy(abc.ABC):
    JUMP_DURATION = 0.4
    JUMP_HEIGHT = 8
    BOUNCE_DURATION = 0.2
    BOUNCE_DISTANCE = 3.0

    def __init__(self, game: "Game", grid_pos: tuple[int, int]) -> None:
        self.game: Game = game
        self.grid_pos: tuple[int, int] = grid_pos
        self.direction = "down"

        self.jumping = False
        self.jump_t = 0.0
        self.jump_from = grid_pos

        self.bouncing = False
        self.bounce_t = 0.0
        self.bounce_dx = 0.0
        self.bounce_dy = 0.0

    def update(self, dt: float) -> None:
        if self.jumping:
            self.jump_t = min(1.0, self.jump_t + dt / self.JUMP_DURATION)

            if self.jump_t >= 1.0:
                self.jumping = False
                self.jump_t = 0.0
            return

        if not self.bouncing:
            return

        self.bounce_t = min(1.0, self.bounce_t + dt / self.BOUNCE_DURATION)

        if self.bounce_t >= 1.0:
            self.bouncing = False
            self.bounce_t = 0.0

    def is_tile_occupied(self, grid_pos: tuple[int, int]) -> bool:
        if grid_pos == tuple(self.game.board.player_position):
            return True

        return any(
            enemy is not self and enemy.grid_pos == grid_pos
            for enemy in self.game.enemies
        )

    def lunge_towards(self, dx: int, dy: int) -> None:
        length = math.hypot(dx, dy)
        if length == 0:
            return

        self.bounce_dx = dx / length
        self.bounce_dy = dy / length
        self.bouncing = True
        self.bounce_t = 0.0

    def bounce_back(self, dx: int, dy: int) -> None:
        self.lunge_towards(-dx, -dy)

    def jump_to(self, grid_pos: tuple[int, int]) -> bool:
        if self.jumping or self.bouncing or grid_pos == self.grid_pos:
            return False

        dx = grid_pos[0] - self.grid_pos[0]
        dy = grid_pos[1] - self.grid_pos[1]

        if self.is_tile_occupied(grid_pos):
            self.direction = self.direction_from_delta(dx, dy)
            self.bounce_back(dx, dy)
            return False

        self.jump_from = self.grid_pos
        self.grid_pos = grid_pos
        self.direction = self.direction_from_delta(dx, dy)
        self.jumping = True
        self.jump_t = 0.0

        if self.game.board.trigger_trap(grid_pos):
            self.take_damage(TRAP_ENEMY_DAMAGE)

        return True

    @staticmethod
    def direction_from_delta(dx: int, dy: int) -> str:
        if abs(dx) >= abs(dy):
            return "right" if dx > 0 else "left"
        return "down" if dy > 0 else "up"

    def get_render_position(self) -> tuple[float, float]:
        board = self.game.board
        if self.jumping:
            start_x, start_y = board.grid_to_screen(*self.jump_from)
            end_x, end_y = board.grid_to_screen(*self.grid_pos)
            t = ease_in_out_cubic(self.jump_t)

            x = start_x + (end_x - start_x) * t
            y = start_y + (end_y - start_y) * t
            y -= math.sin(math.pi * self.jump_t) * self.JUMP_HEIGHT
            return x, y

        x, y = board.grid_to_screen(*self.grid_pos)

        if self.bouncing:
            offset = math.sin(math.pi * self.bounce_t) * self.BOUNCE_DISTANCE
            x += self.bounce_dx * offset
            y += self.bounce_dy * offset

        return x, y

    @abc.abstractmethod
    def render(self, surface: pygame.Surface, text_layer: TextLayer) -> None:
        pass

    @abc.abstractmethod
    def simulation_step(self) -> None:
        ...

    @abc.abstractmethod
    def take_damage(self, damage: int) -> None:
        ...
import random
from typing import TYPE_CHECKING

import pygame

from echo_chamber.config import *
from echo_chamber.enemy.enemy import AbstractEnemy
from echo_chamber.layer import TextLayer
from echo_chamber.utils import load_image

if TYPE_CHECKING:
    from echo_chamber.main import Game


class Slime(AbstractEnemy):
    SPLIT_STATES = {
        "full": "half",
        "half": "quarter",
    }

    def __init__(
        self,
        game: "Game",
        grid_pos: tuple[int, int],
        state: str = "full",
    ) -> None:
        super().__init__(game, grid_pos)

        self.textures = {
            "full": {
                "up": load_image("assets/slime/full/back.png"),
                "down": load_image("assets/slime/full/front.png"),
                "left": load_image("assets/slime/full/left.png"),
                "right": load_image("assets/slime/full/right.png"),
            },
            "half": {
                "up": load_image("assets/slime/half/back.png"),
                "down": load_image("assets/slime/half/front.png"),
                "left": load_image("assets/slime/half/left.png"),
                "right": load_image("assets/slime/half/right.png"),
            },
            "quarter": {
                "up": load_image("assets/slime/quarter/back.png"),
                "down": load_image("assets/slime/quarter/front.png"),
                "left": load_image("assets/slime/quarter/left.png"),
                "right": load_image("assets/slime/quarter/right.png"),
            },
        }

        if state not in self.textures:
            raise ValueError(f"Invalid state: {state}")

        self.state = state
        self.direction = random.choice(["up", "down", "left", "right"])

        self.health = self.max_health
        self.dead = False
        self.spawn_jumping = False
        self.spawn_jump_delay = 0.0

    def render(self, surface: pygame.Surface, text_layer: TextLayer) -> None:
        x, y = self.get_render_position()

        x += (TILE_SIZE - SLIME_WIDTH) / 2
        y += (TILE_SIZE - SLIME_HEIGHT) / 2

        texture = self.textures[self.state][self.direction]
        surface.blit(texture, (x, y))

    @property
    def attack_damage(self) -> int:
        if self.state == "full":
            return FULL_SLIME_ATTACK_DAMAGE
        if self.state == "half":
            return HALF_SLIME_ATTACK_DAMAGE
        if self.state == "quarter":
            return QUARTER_SLIME_ATTACK_DAMAGE
        raise ValueError("Invalid state")

    @property
    def max_health(self) -> int:
        if self.state == "full":
            return FULL_SLIME_MAX_HEALTH
        if self.state == "half":
            return HALF_SLIME_MAX_HEALTH
        if self.state == "quarter":
            return QUARTER_SLIME_MAX_HEALTH
        raise ValueError("Invalid state")

    def update(self, dt: float) -> None:
        if self.spawn_jump_delay > 0:
            self.spawn_jump_delay -= dt
            if self.spawn_jump_delay > 0:
                return
            dt = -self.spawn_jump_delay
            self.spawn_jump_delay = 0.0

        super().update(dt)

        if self.spawn_jumping and not self.jumping:
            self.spawn_jumping = False

    def attack(self) -> None:
        player_x, player_y = self.game.board.player_position
        dx = player_x - self.grid_pos[0]
        dy = player_y - self.grid_pos[1]

        self.direction = self.direction_from_delta(dx, dy)
        self.lunge_towards(dx, dy)
        self.game.player.take_damage(self.attack_damage, self.grid_pos)

    def take_damage(self, damage: int) -> None:
        if self.dead:
            return

        self.health -= damage
        if self.health > 0:
            return

        self.dead = True
        self.game.enemies.remove(self)
        self.game.player.experience += GOBLIN_KILL_EXPERIENCE_GAIN
        self.split()

    def split(self) -> None:
        child_state = self.SPLIT_STATES.get(self.state)
        if child_state is None:
            return

        available_slots = max(0, self.game.enemy_cap - len(self.game.enemies))
        child_count = min(SLIME_SPLIT_COUNT, available_slots)
        if child_count <= 0:
            return

        targets = self.split_targets()
        children = [
            Slime(self.game, self.grid_pos, child_state)
            for _ in range(child_count)
        ]

        for child in children:
            self.game.enemies.append(child)

        for index, (child, target) in enumerate(zip(children, targets)):
            child.spawn_jump_delay = index * SLIME_SPLIT_JUMP_STAGGER
            if target != child.grid_pos:
                child.spawn_jumping = child.jump_to(target)

    def split_targets(self) -> list[tuple[int, int]]:
        death_pos = self.grid_pos
        player_pos = tuple(self.game.board.player_position)
        occupied = {enemy.grid_pos for enemy in self.game.enemies}

        candidates = [
            pos
            for pos in self.game.board.get_tiles_around(
                death_pos[0], death_pos[1], SLIME_SPLIT_RADIUS
            )
            if pos != death_pos and pos != player_pos and pos not in occupied
        ]
        random.shuffle(candidates)

        targets = candidates[:SLIME_SPLIT_COUNT]
        while len(targets) < SLIME_SPLIT_COUNT:
            targets.append(death_pos)

        return targets

    def simulation_step(self) -> None:
        if self.spawn_jumping or self.spawn_jump_delay > 0:
            return

        path: list[tuple[int, int]] = self.game.board.find_path_to_player(self.grid_pos)
        if len(path) == 2:
            self.attack()
            return

        if len(path) <= 1:
            return

        if random.randint(0, 2) == 0:
            return

        self.jump_to(path[1])

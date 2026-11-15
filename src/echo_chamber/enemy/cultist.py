import math
import random
from typing import TYPE_CHECKING

import pygame

from echo_chamber.config import *
from echo_chamber.enemy.enemy import AbstractEnemy
from echo_chamber.layer import TextLayer
from echo_chamber.utils import load_image

if TYPE_CHECKING:
    from echo_chamber.main import Game


class Cultist(AbstractEnemy):
    def __init__(self, game: "Game", grid_pos: tuple[int, int]) -> None:
        super().__init__(game, grid_pos)

        self.textures = {
            "idle": {
                "up": load_image("assets/cultist/idle/back.png"),
                "down": load_image("assets/cultist/idle/front.png"),
                "left": load_image("assets/cultist/idle/left.png"),
                "right": load_image("assets/cultist/idle/right.png"),
            },
            "summon": {
                "up": load_image("assets/cultist/summon/back.png"),
                "down": load_image("assets/cultist/summon/front.png"),
                "left": load_image("assets/cultist/summon/left.png"),
                "right": load_image("assets/cultist/summon/right.png"),
            },
        }

        self.state = "idle"
        self.direction = random.choice(["up", "down", "left", "right"])

        self.health = self.max_health
        self.dead = False
        self.summon_log = []
        self.summon_cooldown_turns = 0
        self.retreat_turns_remaining = 0

    def update(self, dt: float) -> None:
        super().update(dt)

        for entry in self.summon_log:
            entry["t"] += dt

        self.summon_log = [
            entry for entry in self.summon_log
            if entry["t"] < SUMMON_LOG_DURATION
        ]

    def render(self, surface: pygame.Surface, text_layer: TextLayer) -> None:
        x, y = self.get_render_position()

        texture = self.textures[self.state][self.direction]
        x += (TILE_SIZE - texture.get_width()) / 2
        y += (TILE_SIZE - texture.get_height()) / 2

        surface.blit(texture, (x, y))

        for entry in self.summon_log:
            t = entry["t"]
            progress = min(1.0, t / SUMMON_LOG_DURATION)
            eased = 1.0 - (1.0 - progress) ** 3

            rise = SUMMON_LOG_RISE * eased
            drift = entry["drift"] * eased

            alpha = 255
            if t > SUMMON_LOG_HOLD:
                fade = (t - SUMMON_LOG_HOLD) / (SUMMON_LOG_DURATION - SUMMON_LOG_HOLD)
                alpha = int(255 * max(0.0, 1.0 - fade))

            flash = max(0.0, 1.0 - t / SUMMON_LOG_FLASH_DURATION)
            color = (
                round(SUMMON_LOG_FLASH_COLOR[0] * flash + SUMMON_LOG_COLOR[0] * (1.0 - flash)),
                round(SUMMON_LOG_FLASH_COLOR[1] * flash + SUMMON_LOG_COLOR[1] * (1.0 - flash)),
                round(SUMMON_LOG_FLASH_COLOR[2] * flash + SUMMON_LOG_COLOR[2] * (1.0 - flash)),
            )

            text = "Cursed"
            text_width, _ = text_layer.text_size(text)
            text_layer.draw_text(
                text,
                (entry["x"] - text_width / 2 + drift, entry["y"] - rise),
                color,
                alpha=alpha,
            )

    @property
    def attack_damage(self) -> int:
        return CULTIST_ATTACK_DAMAGE

    @property
    def max_health(self) -> int:
        return CULTIST_MAX_HEALTH

    @property
    def distance_to_player_px(self) -> float:
        player_x, player_y = self.game.board.player_position
        return math.hypot(
            player_x - self.grid_pos[0],
            player_y - self.grid_pos[1],
        ) * TILE_SIZE

    def face_player(self) -> None:
        player_x, player_y = self.game.board.player_position
        self.direction = self.direction_from_delta(
            player_x - self.grid_pos[0],
            player_y - self.grid_pos[1],
        )

    def summon(self) -> None:
        if self.state == "summon" or self.summon_cooldown_turns > 0:
            return

        self.state = "summon"
        self.summon_cooldown_turns = CULTIST_SUMMON_COOLDOWN_TURNS
        self.retreat_turns_remaining = CULTIST_SUMMON_RETREAT_TURNS

        x, y = self.get_render_position()
        self.summon_log.append({
            "t": 0.0,
            "x": x + TILE_SIZE / 2,
            "y": y + SUMMON_LOG_OFFSET_Y,
            "drift": random.uniform(-SUMMON_LOG_DRIFT, SUMMON_LOG_DRIFT),
        })

        self.place_curse()

    def place_curse(self) -> None:
        curse_type = random.choice(("dead-weight", "uncontrolled-step", "parasite"))
        target = random.choice(CARD_REGISTRY[curse_type]["curse_targets"])
        self.game.add_curse(curse_type, to_echo=target == "echo")

    def approach_player(self) -> None:
        path = self.game.board.find_path_to_player(self.grid_pos)
        if len(path) > 1:
            self.jump_to(path[1])

    def retreat_from_player(self) -> None:
        player_x, player_y = self.game.board.player_position
        current_distance = self.distance_to_player_px
        candidates: list[tuple[float, tuple[int, int]]] = []

        for dx, dy in ((0, -1), (0, 1), (-1, 0), (1, 0)):
            grid_pos = (self.grid_pos[0] + dx, self.grid_pos[1] + dy)
            if not self.game.board.is_walkable(grid_pos):
                continue
            if self.is_tile_occupied(grid_pos):
                continue

            distance = math.hypot(
                player_x - grid_pos[0],
                player_y - grid_pos[1],
            ) * TILE_SIZE
            if distance > current_distance:
                candidates.append((distance, grid_pos))

        if not candidates:
            return

        best_distance = max(distance for distance, _ in candidates)
        best_positions = [
            grid_pos
            for distance, grid_pos in candidates
            if distance == best_distance
        ]
        self.jump_to(random.choice(best_positions))

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
        self.game.player.experience += CULTIST_KILL_EXPERIENCE_GAIN

    def simulation_step(self) -> None:
        if self.summon_cooldown_turns > 0:
            self.summon_cooldown_turns -= 1

            if not (self.jumping or self.bouncing):
                self.state = "idle"
                if self.retreat_turns_remaining > 0:
                    self.retreat_turns_remaining -= 1
                    self.retreat_from_player()
            return

        if self.jumping or self.bouncing:
            return

        distance = self.distance_to_player_px
        if abs(distance - CULTIST_IDEAL_DISTANCE_PX) <= CULTIST_DISTANCE_TOLERANCE_PX:
            self.summon()
            self.face_player()
            return

        self.state = "idle"
        if distance > CULTIST_IDEAL_DISTANCE_PX:
            self.approach_player()
        else:
            self.retreat_from_player()

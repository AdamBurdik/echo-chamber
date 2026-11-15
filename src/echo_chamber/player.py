import math
import random
from typing import TYPE_CHECKING

import pygame

from echo_chamber.config import *
from echo_chamber.easing import ease_in_out_cubic
from echo_chamber.layer import TextLayer
from echo_chamber.utils import load_image

if TYPE_CHECKING:
    from echo_chamber.main import Game


JUMP_DURATION = 0.4   # seconds
JUMP_HEIGHT = 8 # pixels
BOUNCE_DURATION = 0.2  # seconds
BOUNCE_DISTANCE = 3  # pixels
SLASH_FRAME_DURATION = 0.05  # seconds per slash frame
SPIN_SLASH_STAGGER = 0.06  # seconds between spin slash directions
CARDINAL_DIRECTIONS = ("up", "right", "down", "left")

class Player:
    def __init__(self, game: "Game") -> None:
        self.game: Game = game
        self.origin = PLAYER_SCREEN_POS
        
        self.textures = {
            "idle": {
                "up": load_image("assets/player/idle/back.png"),
                "down": load_image("assets/player/idle/front.png"),
                "left": load_image("assets/player/idle/left.png"),
                "right": load_image("assets/player/idle/right.png"),
                
            }
        }

        slash_frames = [
            load_image(f"assets/effects/slash/{i}.png")
            for i in range(1, 8)
        ]
        self.slash_frames = {
            "up": slash_frames,
            "right": [pygame.transform.rotate(frame, -90) for frame in slash_frames],
            "down": [pygame.transform.rotate(frame, 180) for frame in slash_frames],
            "left": [pygame.transform.rotate(frame, 90) for frame in slash_frames],
        }
        self.slash_frame_count = len(slash_frames)
        
        self.direction = "down"
        self.state = "idle"
        
        self.animation = "jump_up"
        self.animation_state = 0
        self.offset: list[int] = [0, 0]

        self.jumping = False
        self.jump_t = 0.0
        self.jump_start_offset = (0, 0)
        self.hop_y = 0.0

        self.bouncing = False
        self.bounce_t = 0.0
        self.bounce_dx = 0.0
        self.bounce_dy = 0.0

        self.slash_effects: list[dict] = []

        self.health = PLAYER_MAX_HEALTH
        self.experience = 5
        self.experience_level = 0

        self.health_log = []

        self.regeneration_amount = 0
        self.regeneration_time = 0.0
        self.regeneration_tick_timer = 0.0
        
    def get_direction_vector(self) -> tuple[int, int]:
        match self.direction:
            case "up": return 0, -1
            case "down": return 0, 1
            case "right": return 1, 0
            case "left": return -1, 0
        raise Exception(f"Invalid direction: {self.direction}")

    def jump_up(self, board, amount: int = 1) -> None:
        self.jump(board, "up", amount)

    def jump_down(self, board, amount: int = 1) -> None:
        self.jump(board, "down", amount)

    def jump_left(self, board, amount: int = 1) -> None:
        self.jump(board, "left", amount)

    def jump_right(self, board, amount: int = 1) -> None:
        self.jump(board, "right", amount)

    def _add_health_log(self, amount: float, kind: str) -> None:
        x, y = self.get_render_position()
        self.health_log.append({
            "amount": amount,
            "kind": kind,
            "t": 0.0,
            "x": x + PLAYER_WIDTH / 2,
            "y": y + DAMAGE_LOG_OFFSET_Y,
            "drift": random.uniform(-DAMAGE_LOG_DRIFT, DAMAGE_LOG_DRIFT),
        })

    def take_damage(self, amount: int) -> None:
        self.health -= amount
        self._add_health_log(amount, "damage")

    def heal(self, amount: int) -> None:
        healed = min(amount, PLAYER_MAX_HEALTH - self.health)
        if healed <= 0:
            return

        self.health += healed
        self._add_health_log(healed, "heal")

    def start_regeneration(self, amount: int, duration: float) -> None:
        if amount <= 0 or duration <= 0:
            return

        self.regeneration_amount = max(self.regeneration_amount, amount)
        self.regeneration_time = max(self.regeneration_time, duration)
        self.regeneration_tick_timer = min(
            self.regeneration_tick_timer,
            REGENERATION_TICK_INTERVAL,
        )

    def update_regeneration(self, dt: float) -> None:
        if self.regeneration_time <= 0:
            return

        active_dt = min(dt, self.regeneration_time)
        self.regeneration_time -= active_dt
        self.regeneration_tick_timer += active_dt

        while self.regeneration_tick_timer >= REGENERATION_TICK_INTERVAL:
            self.regeneration_tick_timer -= REGENERATION_TICK_INTERVAL
            self.heal(self.regeneration_amount)

        if self.regeneration_time <= 0:
            self.regeneration_amount = 0
            self.regeneration_tick_timer = 0.0

    def is_tile_occupied_by_enemy(self, board, grid_pos: tuple[int, int]) -> bool:
        return any(enemy.grid_pos == grid_pos for enemy in board.game.enemies)

    def bounce_back(self, dx: int, dy: int) -> None:
        length = math.hypot(dx, dy)
        if length == 0:
            return

        self.bounce_dx = -dx / length
        self.bounce_dy = -dy / length
        self.bouncing = True
        self.bounce_t = 0.0

    def jump(self, board, direction: str, amount: int = 1) -> None:
        if self.jumping or self.bouncing:
            return

        self.direction = direction
        dx, dy = self.get_direction_vector()

        target = (
            board.player_position[0] + dx * amount,
            board.player_position[1] + dy * amount,
        )
        if self.is_tile_occupied_by_enemy(board, target):
            self.bounce_back(dx, dy)
            self.take_damage(PLAYER_ENEMY_COLLISION_DAMAGE)
            return

        board.move_player((dx, dy), amount)  # logical move happens instantly

        # The logical move is instant, so offset the board back by the whole
        # move to keep the old frame on screen. It then eases back to zero.
        self.jump_start_offset = (dx * TILE_SIZE * amount, dy * TILE_SIZE * amount)
        board.camera_offset[0], board.camera_offset[1] = self.jump_start_offset

        self.jumping = True
        self.jump_t = 0.0
        self.experience += amount

    def rotate(self, direction: str) -> None:
        if direction not in CARDINAL_DIRECTIONS:
            raise ValueError(f"Invalid direction: {direction}")
        self.direction = direction

    def add_slash_effect(self, direction: str, delay: float = 0.0) -> None:
        self.slash_effects.append({
            "direction": direction,
            "t": 0.0,
            "delay": delay,
        })

    def attack_forward(self, damage: int) -> None:
        self.add_slash_effect(self.direction)

        dx, dy = self.get_direction_vector()
        player_x, player_y = self.game.board.player_position

        forward = (player_x + dx, player_y + dy)
        forward_left = (forward[0] + dy, forward[1] - dx)
        forward_right = (forward[0] - dy, forward[1] + dx)

        attack_tiles = {forward, forward_left, forward_right}
        for enemy in list(self.game.enemies):
            if enemy.grid_pos in attack_tiles:
                enemy.take_damage(damage)

    def spin_attack(self, damage: int) -> None:
        start = CARDINAL_DIRECTIONS.index(self.direction)
        for i in range(len(CARDINAL_DIRECTIONS)):
            direction = CARDINAL_DIRECTIONS[(start + i) % len(CARDINAL_DIRECTIONS)]
            self.add_slash_effect(direction, delay=i * SPIN_SLASH_STAGGER)

        player_x, player_y = self.game.board.player_position
        for enemy in list(self.game.enemies):
            dx = enemy.grid_pos[0] - player_x
            dy = enemy.grid_pos[1] - player_y
            if max(abs(dx), abs(dy)) == 1:
                enemy.take_damage(damage)

    def update(self, dt, board) -> None:
        for entry in self.health_log:
            entry["t"] += dt

        self.health_log = [
            entry for entry in self.health_log
            if entry["t"] < DAMAGE_LOG_DURATION
        ]

        self.update_regeneration(dt)

        for effect in self.slash_effects:
            effect["t"] += dt

        self.slash_effects = [
            effect for effect in self.slash_effects
            if effect["t"] < effect["delay"] + SLASH_FRAME_DURATION * self.slash_frame_count
        ]

        if self.jumping:
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
            return

        if not self.bouncing:
            return

        self.bounce_t = min(1.0, self.bounce_t + dt / BOUNCE_DURATION)

        if self.bounce_t >= 1.0:
            self.bouncing = False
            self.bounce_t = 0.0

    def get_render_position(self) -> tuple[float, float]:
        offset = 0.0
        if self.bouncing:
            offset = math.sin(math.pi * self.bounce_t) * BOUNCE_DISTANCE

        return (
            self.origin[0] + self.bounce_dx * offset,
            self.origin[1] + self.hop_y + self.bounce_dy * offset,
        )

    def render(self, surface: pygame.Surface, text_layer: TextLayer) -> None:
        x, y = self.get_render_position()

        texture = self.textures[self.state][self.direction]
        surface.blit(texture, (x, y))

        for entry in self.health_log:
            t = entry["t"]
            progress = min(1.0, t / DAMAGE_LOG_DURATION)
            eased = 1.0 - (1.0 - progress) ** 3

            rise = DAMAGE_LOG_RISE * eased
            drift = entry["drift"] * eased

            alpha = 255
            if t > DAMAGE_LOG_HOLD:
                fade = (t - DAMAGE_LOG_HOLD) / (DAMAGE_LOG_DURATION - DAMAGE_LOG_HOLD)
                alpha = int(255 * max(0.0, 1.0 - fade))

            flash = max(0.0, 1.0 - t / DAMAGE_LOG_FLASH_DURATION)
            base_color = HEAL_LOG_COLOR if entry["kind"] == "heal" else DAMAGE_LOG_COLOR
            color = (
                round(DAMAGE_LOG_FLASH_COLOR[0] * flash + base_color[0] * (1.0 - flash)),
                round(DAMAGE_LOG_FLASH_COLOR[1] * flash + base_color[1] * (1.0 - flash)),
                round(DAMAGE_LOG_FLASH_COLOR[2] * flash + base_color[2] * (1.0 - flash)),
            )

            prefix = "+" if entry["kind"] == "heal" else "-"
            text = f"{prefix}{entry['amount']:g} HP"
            text_width, _ = text_layer.text_size(text)
            text_layer.draw_text(
                text,
                (entry["x"] - text_width / 2 + drift, entry["y"] - rise),
                color,
                alpha=alpha,
            )

    def render_effects(self, surface: pygame.Surface) -> None:
        for effect in self.slash_effects:
            t = effect["t"] - effect["delay"]
            if t < 0:
                continue

            frame_index = min(
                int(t / SLASH_FRAME_DURATION),
                self.slash_frame_count - 1,
            )
            self.render_slash(surface, effect["direction"], frame_index)

    def render_slash(self, surface: pygame.Surface, direction: str, frame_index: int) -> None:
        frame = self.slash_frames[direction][frame_index]
        frame_w, frame_h = frame.get_size()

        x, y = self.get_render_position()
        center_x = x + PLAYER_WIDTH / 2
        center_y = y + PLAYER_HEIGHT / 2

        if direction == "right":
            pos = (x + PLAYER_WIDTH, center_y - frame_h / 2)
        elif direction == "left":
            pos = (x - frame_w, center_y - frame_h / 2)
        elif direction == "up":
            pos = (center_x - frame_w / 2, y - frame_h)
        else:
            pos = (center_x - frame_w / 2, y + PLAYER_HEIGHT)

        surface.blit(frame, (round(pos[0]), round(pos[1])))

    def simulation_step(self) -> None:
        ...

    def handle_input(self, event: pygame.Event) -> None:
        ...
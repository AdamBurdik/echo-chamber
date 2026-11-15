from functools import lru_cache
from typing import TYPE_CHECKING

import pygame

from echo_chamber.config import (
    ENERGY_SPIKE_FRAME_DURATION,
    PLAYER_HEIGHT,
    PLAYER_WIDTH,
)
from echo_chamber.utils import load_image

if TYPE_CHECKING:
    from echo_chamber.main import Game


@lru_cache(maxsize=1)
def _load_frames() -> tuple[pygame.Surface, ...]:
    return tuple(
        load_image(f"assets/energy_spike/{i}.png")
        for i in range(1, 5)
    )


class EnergySpikeEffect:
    def __init__(self, game: "Game") -> None:
        self.frames = _load_frames()
        self.frame_duration = ENERGY_SPIKE_FRAME_DURATION
        self.duration = self.frame_duration * len(self.frames)
        self.t = 0.0

        x, y = game.player.get_render_position()
        self.x = x + PLAYER_WIDTH / 2
        self.y = y + PLAYER_HEIGHT / 2

    def update(self, dt: float) -> bool:
        self.t += dt
        return self.t < self.duration

    def render(self, surface: pygame.Surface) -> None:
        frame_index = min(
            int(self.t / self.frame_duration),
            len(self.frames) - 1,
        )
        frame = self.frames[frame_index]
        surface.blit(
            frame,
            (
                round(self.x - frame.get_width() / 2),
                round(self.y - frame.get_height() / 2),
            ),
        )

from typing import TYPE_CHECKING

from echo_chamber.config import *

if TYPE_CHECKING:
    from echo_chamber.main import Game


class HUD:
    def __init__(self, game: "Game") -> None:
        self.game: Game = game

        self.health_pct = 1.0
        self.experience_pct = 0.0
        self.display_experience_pct = 0.0

        self.update(0.0)

    def update(self, dt: float) -> None:
        player = self.game.player

        self.health_pct = max(0.0, min(1.0, player.health / PLAYER_MAX_HEALTH))

        next_level = EXPERIENCE_LEVELS.get(player.experience_level + 1)
        if next_level is None or next_level <= 0:
            self.experience_pct = 1.0
        else:
            self.experience_pct = max(0.0, min(1.0, player.experience / next_level))

        if dt <= 0 or HUD_XP_GROW_DURATION <= 0:
            self.display_experience_pct = self.experience_pct
        elif self.experience_pct > self.display_experience_pct:
            growth = min(1.0, dt / HUD_XP_GROW_DURATION)
            self.display_experience_pct += (
                self.experience_pct - self.display_experience_pct
            ) * growth
        else:
            self.display_experience_pct = self.experience_pct

from typing import TYPE_CHECKING

import pygame

from echo_chamber.config import *
from echo_chamber.layer import TextLayer

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

    def render(self, surface: pygame.Surface, text_layer: TextLayer) -> None:
        # Stack header
        rect = pygame.Rect(240, 5.5, 62, 16)
        pygame.draw.rect(surface, CARD_QUEUE_BACKGROUND_COLOR, rect)
        
        text_size = text_layer.text_size("STACK", text_scale=1)
        text_layer.draw_text("STACK", (
            rect.x + (rect.width - text_size[0]) / 2,
            rect.y + (rect.height - text_size[1]) / 2,
        ), (255, 255, 255), text_scale=1)
        
        # Echo header
        rect = pygame.Rect(306.5, 5.5, 62, 16)
        pygame.draw.rect(surface, CARD_QUEUE_BACKGROUND_COLOR, rect)
    
        text_size = text_layer.text_size("ECHO", text_scale=1)
        text_layer.draw_text("ECHO", (
            rect.x + (rect.width - text_size[0]) / 2,
            rect.y + (rect.height - text_size[1]) / 2,
        ), (255, 255, 255), text_scale=1)
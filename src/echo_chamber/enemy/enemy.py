import abc
from typing import TYPE_CHECKING

import pygame

from echo_chamber.layer import TextLayer

if TYPE_CHECKING:
    from echo_chamber.main import Game


class AbstractEnemy(abc.ABC):
    def __init__(self, game: "Game", grid_pos: tuple[int, int]) -> None:
        self.game: Game = game
        self.grid_pos: tuple[int, int] = grid_pos

    @abc.abstractmethod
    def update(self) -> None:
        pass

    @abc.abstractmethod
    def render(self, surface: pygame.Surface, text_layer: TextLayer) -> None:
        pass
    
    @abc.abstractmethod
    def simulation_step(self) -> None:
        ...

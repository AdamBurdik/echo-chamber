from typing import TYPE_CHECKING


from echo_chamber.config import *

if TYPE_CHECKING:
    from echo_chamber.main import Game


class MainMenu:
    def __init__(self, game: "Game") -> None:
        self.game: Game = game
        self.surface = pygame.Surface((DISPLAY_WIDTH, DISPLAY_HEIGHT))

    def update(self) -> None:
        pass

    def handle_input(self, event: pygame.event.Event) -> None:
        ...

    def render(self) -> None:
        self.surface.fill(MAIN_MENU_BACKGROUND_COLOR)
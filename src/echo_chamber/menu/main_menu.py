from typing import TYPE_CHECKING

import pygame

from echo_chamber.config import *

if TYPE_CHECKING:
    from echo_chamber.main import Game


def create_button(
        surface: pygame.Surface,
        rect: pygame.Rect,
        text: str,
        font: pygame.font.Font,
        button_color: tuple[int, int, int],
        text_color: tuple[int, int, int] = (255, 255, 255)
) -> None:
    """Draws a button rectangle with centered text onto the given surface."""
    text_surface = font.render(text, False, text_color)
    text_rect = text_surface.get_rect(center=rect.center)
    surface.blit(text_surface, text_rect)


class MainMenu:
    def __init__(self, game: "Game") -> None:
        self.game: Game = game
        self.surface = pygame.Surface((DISPLAY_WIDTH, DISPLAY_HEIGHT))

        self.title_font = pygame.font.Font(FONT_PATH, 300)
        self.button_font = pygame.font.Font(FONT_PATH, 128)

        play_button_size = (300, 100)
        self.play_rect = pygame.Rect(
            play_button_size[0],
            (DISPLAY_HEIGHT - play_button_size[1]) / 1.5,
            play_button_size[0],
            play_button_size[1]
        )
        
        self.main_colr = argb_int_to_rgba(0xffc7786f)
        
        def load_texture(path: str) -> pygame.Surface:
            raw = pygame.image.load(path)
            return pygame.transform.scale(raw, (raw.width * 10, raw.height * 10))
        
        self.character_texture = load_texture("assets/player/idle/front.png")

    def update(self) -> None:
        pass

    def handle_input(self, event: pygame.event.Event) -> None:
        if event.type == pygame.MOUSEBUTTONDOWN:
            # Check for left mouse click
            if event.button == 1:
                # Check if the click position is inside the play button rectangle
                mouse_pos = self.game.ui_to_surface_position(event.pos)
                if self.play_rect.collidepoint(mouse_pos):
                    print("Play button clicked!")
                    self.game.start_game()

    def render(self) -> None:
        self.surface.fill(MAIN_MENU_BACKGROUND_COLOR)

        title = self.title_font.render("Echo Chamber", False, self.main_colr)
        title_width, title_height = self.title_font.size("Echo Chamber")

        self.surface.blit(title, (
            (DISPLAY_WIDTH - title_width) / 2,
            (DISPLAY_HEIGHT - title_height) / 4,
        ))

        create_button(
            surface=self.surface,
            rect=self.play_rect,
            text="Play",
            font=self.button_font,
            button_color=(255, 0, 0),
            text_color=self.main_colr
        )
        
        self.surface.blit(
            self.character_texture,
            (1200, 920)
        )

import pygame

from echo_chamber.config import *
from echo_chamber.layer import TextLayer
from echo_chamber.utils import get_mouse_position


class ConfirmButton:
    def __init__(self):
        diff = SCREEN_WIDTH - CARD_QUEUE_WIDTH

        self.origin = (
            diff / 2 + diff / 4,
            SCREEN_HEIGHT - CONFIRM_BUTTON_HEIGHT
        )
    
    def render(self, surface: pygame.Surface, text_layer: TextLayer) -> None:
        rect = pygame.Rect(self.origin[0], self.origin[1], CONFIRM_BUTTON_WIDTH, CONFIRM_BUTTON_HEIGHT)
        pygame.draw.rect(surface, (0, 0, 0), rect)
        
        text_size = text_layer.text_size("BEGIN TURN", text_scale=2)
        text_layer.draw_text(
            "BEGIN_RUN",
            (
                rect.x + (CONFIRM_BUTTON_WIDTH - text_size[0]) / 2,
                rect.y + (CONFIRM_BUTTON_HEIGHT - text_size[1]) / 2
            ),
            (255, 255, 255),
            text_scale=2
        )
    
    def handle_input(self, event: pygame.event.Event) -> None:
        if event.type == pygame.MOUSEBUTTONDOWN:
            mouse_x, mouse_y = get_mouse_position()
            
            rect = pygame.Rect(self.origin[0], self.origin[1], CONFIRM_BUTTON_WIDTH, CONFIRM_BUTTON_HEIGHT)
            if rect.collidepoint(mouse_x, mouse_y):
                print("BEGIN RUN")
                return
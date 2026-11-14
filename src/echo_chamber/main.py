import sys

import pygame
pygame.init()

from echo_chamber.board import Board
from echo_chamber.config import *
from echo_chamber.confirm_button import ConfirmButton
from echo_chamber.layer import  TextLayer
from echo_chamber.player import Player
from echo_chamber.queue.action import ActionQueue
from echo_chamber.utils import generate_card

 
            
        


def main() -> None:
    pygame.display.set_caption("Echo Chamber")

    screen = pygame.display.set_mode((DISPLAY_WIDTH, DISPLAY_HEIGHT), pygame.FULLSCREEN)
    clock = pygame.time.Clock()
    
    load_tile_textures()

    board: Board = Board()
    action_queue: ActionQueue = ActionQueue()
    player: Player = Player()
    
    confirm_button: ConfirmButton = ConfirmButton()

    for i in range(5):
        action_queue.push_card(generate_card())

    rendering_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))

    # When SCALE is off the low-res surface is shown 1:1, so text uses scale 1
    text_scale = RENDER_SCALE if DEBUG__SCALE else 1
    text_layer = TextLayer(SCREEN_WIDTH, SCREEN_HEIGHT, text_scale,
                           FONT_PATH, FONT_BASE_SIZE, TEXT_SCALE)

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()
            else:
                action_queue.handle_input(event)
                confirm_button.handle_input(event)
                player.handle_input(event)

        # Rendering
        screen.fill((0, 0, 0))
        rendering_surface.fill((255, 255, 255))
        text_layer.clear()

        board.render(rendering_surface, text_layer)
        player.render(rendering_surface, text_layer)
        
        action_queue.render(rendering_surface, text_layer)
        confirm_button.render(rendering_surface, text_layer)

        # Scale low-res surface, then draw hi-res text on top
        if DEBUG__SCALE:
            scaled = pygame.transform.scale(rendering_surface, (DISPLAY_WIDTH, DISPLAY_HEIGHT))
        else:
            scaled = rendering_surface
        screen.blit(scaled, (0, 0))
        screen.blit(text_layer.surface, (0, 0))

        clock.tick(120)
        pygame.display.flip()


if __name__ == "__main__":
    main()
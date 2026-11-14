import os
import sys

import pygame
from pygame.time import Clock

from echo_chamber.enemy.enemy import AbstractEnemy
from echo_chamber.enemy.goblin import Goblin
from echo_chamber.simulation import Simulation

# Tiling Wayland compositors can ignore SDL's fullscreen request. XWayland
# honors it, so prefer X11 when both backends are available.
if os.environ.get("WAYLAND_DISPLAY") and os.environ.get("DISPLAY"):
    os.environ["SDL_VIDEODRIVER"] = "x11"

pygame.init()

from echo_chamber.board import Board
from echo_chamber.config import *
from echo_chamber.confirm_button import ConfirmButton
from echo_chamber.layer import TextLayer
from echo_chamber.player import Player
from echo_chamber.queue.action import ActionQueue
from echo_chamber.renderer import Renderer
from echo_chamber.utils import generate_card


class Game:
    def __init__(self) -> None:
        pygame.display.set_caption("Echo Chamber")

        # Tiling Wayland compositors ignore FULLSCREEN and tile the window instead.
        # A borderless window at the desktop size reliably covers the screen.
        flags = pygame.OPENGL | pygame.DOUBLEBUF
        if pygame.display.get_driver() == "wayland":
            flags |= pygame.NOFRAME
        else:
            flags |= pygame.FULLSCREEN

        self.screen = pygame.display.set_mode((DISPLAY_WIDTH, DISPLAY_HEIGHT), flags)
        self.clock = pygame.time.Clock()
        self.dt = 0
    
        load_tile_textures()

        self.player: Player = Player()
        self.board: Board = Board(self)
        self.action_queue: ActionQueue = ActionQueue(self)

        self.simulation: Simulation = Simulation(self)
        self.confirm_button: ConfirmButton = ConfirmButton(self.simulation, self.action_queue)
    
        for i in range(10):
            self.action_queue.push_card(generate_card())

        self.rendering_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        self.overlay_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
    
        # When SCALE is off the low-res surface is shown 1:1, so text uses scale 1
        self.text_scale = RENDER_SCALE if DEBUG__SCALE else 1
        self.text_layer = TextLayer(SCREEN_WIDTH, SCREEN_HEIGHT, self.text_scale,
                               FONT_PATH, FONT_BASE_SIZE, TEXT_SCALE)

        self.renderer = Renderer(
            (SCREEN_WIDTH, SCREEN_HEIGHT),
            self.text_layer.surface.get_size(),
        )
        
        self.enemies: list[AbstractEnemy] = []
        
    def spawn_goblin(self, grid_x: int, grid_y: int) -> None:
        self.enemies.append(Goblin(self, (grid_x, grid_y)))

    def handle_input(self, event: pygame.Event) -> None:
        self.action_queue.handle_input(event)
        self.confirm_button.handle_input(event)
        # self.player.handle_input(event)
    
    def update(self) -> None:
        self.simulation.update()
        self.player.update(self.dt, self.board)
        self.renderer.update(self.dt)
    
    def render(self) -> None:
        self.board.render(self.rendering_surface, self.text_layer)
        self.player.render(self.rendering_surface, self.text_layer)
        for enemy in self.enemies:
            enemy.render(self.rendering_surface, self.text_layer)

        self.action_queue.render(self.rendering_surface, self.text_layer)
        self.confirm_button.render(self.rendering_surface, self.text_layer)


    def run(self) -> None:
        while True:
            self.update()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        pygame.quit()
                        sys.exit()
                else:
                    self.handle_input(event)
    
            # Rendering
            self.rendering_surface.fill((255, 255, 255))
            self.overlay_surface.fill((0, 0, 0, 0))
            self.text_layer.clear()
    
            self.render()
            self.renderer.render(
                self.rendering_surface,
                self.overlay_surface,
                self.text_layer.surface,
                self.text_layer.behind_surface,
            )

            self.dt = self.clock.tick(120) / 1000
            pygame.display.flip()



def main() -> None:
    game: Game = Game()
    game.run()


if __name__ == "__main__":
    main()

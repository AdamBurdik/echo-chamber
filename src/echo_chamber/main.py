import os
import sys
import random

from echo_chamber.hud import HUD
from echo_chamber.menu.main_menu import MainMenu
from echo_chamber.queue.echo import EchoQueue

random.seed(5)

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
    def _create_display(self, opengl: bool) -> pygame.Surface:
        flags = 0
        if opengl:
            flags |= pygame.OPENGL | pygame.DOUBLEBUF

        # Tiling Wayland compositors ignore FULLSCREEN and tile the window instead.
        # A borderless window at the desktop size reliably covers the screen.
        if pygame.display.get_driver() == "wayland":
            flags |= pygame.NOFRAME
        else:
            flags |= pygame.FULLSCREEN

        return pygame.display.set_mode(
            (DISPLAY_WIDTH, DISPLAY_HEIGHT), flags
        )

    def __init__(self) -> None:
        pygame.display.set_caption("Echo Chamber")

        self.screen = self._create_display(opengl=False)
        self.clock = pygame.time.Clock()
        self.dt = 0

        load_tile_textures()

        self.player: Player = Player(self)
        self.board: Board = Board(self)
        self.action_queue: ActionQueue = ActionQueue(self)
        self.echo_queue: EchoQueue = EchoQueue(self)

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

        self.renderer: Renderer | None = None

        self.enemies: list[AbstractEnemy] = []

        self.hud: HUD = HUD(self)

        self.main_menu: MainMenu = MainMenu(self)

        self.menu = "main"

    def start_game(self) -> None:
        if self.renderer is None:
            self.screen = self._create_display(opengl=True)
            self.renderer = Renderer(
                (SCREEN_WIDTH, SCREEN_HEIGHT),
                self.text_layer.surface.get_size(),
            )
        self.menu = "game"

    def spawn_goblin(self, grid_x: int, grid_y: int) -> None:
        if (grid_x, grid_y) == tuple(self.board.player_position):
            return

        self.enemies.append(Goblin(self, (grid_x, grid_y)))

    def handle_input(self, event: pygame.Event) -> None:
        if self.menu == "main":
            self.main_menu.handle_input(event)
        elif self.menu == "game":
            self.action_queue.handle_input(event)
            self.confirm_button.handle_input(event)
            # self.player.handle_input(event)
    
    def update(self) -> None:
        if self.menu == "main":
            self.main_menu.update()
        elif self.menu == "game":
            self.simulation.update()
            self.player.update(self.dt, self.board)
            for enemy in self.enemies:
                enemy.update(self.dt)
            self.hud.update(self.dt)
            if self.renderer is not None:
                self.renderer.update(self.dt)

    def render(self) -> None:
        self.board.render(self.rendering_surface, self.text_layer)
        self.player.render(self.rendering_surface, self.text_layer)
        for enemy in self.enemies:
            enemy.render(self.rendering_surface, self.text_layer)

        self.player.render_effects(self.rendering_surface)

        self.action_queue.render(self.rendering_surface, self.text_layer)
        self.echo_queue.render(self.rendering_surface, self.text_layer)
        self.confirm_button.render(self.rendering_surface, self.text_layer)

    def run(self) -> None:
        while True:
            self.update()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()
                else:
                    self.handle_input(event)

            if self.menu == "main":
                self.main_menu.render()
                self.screen.blit(self.main_menu.surface, (0, 0))
            else:
                self.rendering_surface.fill((255, 255, 255))
                self.overlay_surface.fill((0, 0, 0, 0))
                self.text_layer.clear()

                self.render()
                if self.renderer is None:
                    raise RuntimeError("Game renderer was not initialized")
                self.renderer.render(
                    self.rendering_surface,
                    self.overlay_surface,
                    self.text_layer.surface,
                    self.text_layer.behind_surface,
                    self.hud.health_pct,
                    self.hud.display_experience_pct,
                )

            self.dt = self.clock.tick(120) / 1000
            pygame.display.flip()



def main() -> None:
    game: Game = Game()
    game.run()


if __name__ == "__main__":
    main()

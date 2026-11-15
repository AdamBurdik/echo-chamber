import math
import os
import sys
import random

if getattr(sys, "frozen", False):
    os.chdir(getattr(sys, "_MEIPASS", os.path.dirname(sys.executable)))

from echo_chamber.enemy.cultist import Cultist
from echo_chamber.enemy.slime import Slime
from echo_chamber.energy_spike import EnergySpikeEffect
from echo_chamber.hud import HUD
from echo_chamber.menu.dead_screen import DeadScreen
from echo_chamber.menu.main_menu import MainMenu
from echo_chamber.queue.echo import EchoQueue

# random.seed(10)

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
from echo_chamber.utils import create_card, generate_card


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
        self.confirm_button: ConfirmButton = ConfirmButton(self)
    
        for i in range(10):
            self.action_queue.push_card(generate_card())

        self.rendering_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        self.hud_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        self.overlay_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
    
        # When SCALE is off the low-res surface is shown 1:1, so text uses scale 1
        self.text_scale = RENDER_SCALE if DEBUG__SCALE else 1
        self.text_layer = TextLayer(SCREEN_WIDTH, SCREEN_HEIGHT, self.text_scale,
                               FONT_PATH, FONT_BASE_SIZE, TEXT_SCALE)

        self.renderer: Renderer | None = None

        self.enemies: list[AbstractEnemy] = []
        self.effects: list[EnergySpikeEffect] = []

        self.spawn_starting_enemies()

        self.shake_rng = random.Random()
        self.screen_shake_time = 0.0
        self.screen_shake_duration = 0.0
        self.screen_shake_intensity = 0.0
        self.screen_flash_time = 0.0
        self.screen_flash_duration = 0.0
        self.screen_flash_color = ENERGY_SPIKE_FLASH_COLOR

        self.hud: HUD = HUD(self)

        self.main_menu: MainMenu = MainMenu(self)
        self.dead_menu: DeadScreen = DeadScreen(self)

        self.menu = "main"

    def start_game(self) -> None:
        if self.renderer is None:
            self.screen = self._create_display(opengl=True)
            self.renderer = Renderer(
                (SCREEN_WIDTH, SCREEN_HEIGHT),
                self.text_layer.surface.get_size(),
            )
        self.menu = "game"
        
    def end_game(self) -> None:
        self.renderer = None
        self.screen = self._create_display(opengl=False)

    @property
    def enemy_cap(self) -> int:
        return ENEMY_CAP_BASE + (self.player.level - 1) * ENEMY_CAP_PER_LEVEL

    @property
    def cultist_cap(self) -> int:
        return (
            CULTIST_CAP_BASE
            + (self.player.level - 1) // CULTIST_CAP_LEVEL_INTERVAL
        )

    @property
    def cultist_count(self) -> int:
        return sum(isinstance(enemy, Cultist) for enemy in self.enemies)

    def can_spawn_enemy(self, enemy_type: type[AbstractEnemy] | None = None) -> bool:
        if len(self.enemies) >= self.enemy_cap:
            return False
        if enemy_type is Cultist and self.cultist_count >= self.cultist_cap:
            return False
        return True

    def spawn_random_enemy(self, grid_x: int, grid_y: int) -> None:
        if not self.can_spawn_enemy():
            return

        spawn_options = [Goblin, Goblin, Slime, Slime]
        if self.cultist_count < self.cultist_cap:
            spawn_options.append(Cultist)

        spawners = {
            Goblin: self.spawn_goblin,
            Slime: self.spawn_slime,
            Cultist: self.spawn_cultist,
        }
        spawners[random.choice(spawn_options)](grid_x, grid_y)

    def maybe_spawn_enemy(self, grid_x: int, grid_y: int) -> None:
        if random.random() >= ENEMY_SPAWN_CHANCE:
            return

        player_x, player_y = self.board.player_position
        if max(abs(grid_x - player_x), abs(grid_y - player_y)) <= ENEMY_SPAWN_SAFE_RADIUS:
            return

        self.spawn_random_enemy(grid_x, grid_y)

    def spawn_starting_enemies(self) -> None:
        desired_count = random.randint(
            STARTING_ENEMY_COUNT_MIN,
            STARTING_ENEMY_COUNT_MAX,
        )
        if desired_count <= 0:
            return

        candidates = []
        for pos in self.board.get_tiles_around(
            0, 0, STARTING_ENEMY_SPAWN_RADIUS
        ):
            if pos == (0, 0) or pos in self.board.traps:
                continue
            if max(abs(pos[0]), abs(pos[1])) < STARTING_ENEMY_MIN_DISTANCE:
                continue

            screen_x, screen_y = self.board.grid_to_screen(pos[0], pos[1])
            if not (
                0 <= screen_x <= SCREEN_WIDTH - TILE_SIZE
                and 0 <= screen_y <= SCREEN_HEIGHT - TILE_SIZE
            ):
                continue

            candidates.append(pos)

        random.shuffle(candidates)

        for grid_x, grid_y in candidates[:desired_count]:
            self.spawn_random_enemy(grid_x, grid_y)

    def spawn_goblin(self, grid_x: int, grid_y: int) -> None:
        if (grid_x, grid_y) == tuple(self.board.player_position):
            return
        if not self.can_spawn_enemy(Goblin):
            return

        self.enemies.append(Goblin(self, (grid_x, grid_y)))

    def spawn_slime(self, grid_x: int, grid_y: int) -> None:
        if (grid_x, grid_y) == tuple(self.board.player_position):
            return
        if not self.can_spawn_enemy(Slime):
            return

        self.enemies.append(Slime(self, (grid_x, grid_y)))

    def spawn_cultist(self, grid_x: int, grid_y: int) -> None:
        if (grid_x, grid_y) == tuple(self.board.player_position):
            return
        if not self.can_spawn_enemy(Cultist):
            return

        self.enemies.append(Cultist(self, (grid_x, grid_y)))

    def add_curse(self, card_type: str, to_echo: bool = False) -> None:
        card = create_card(card_type)
        targets = card.get("curse_targets", ["action"])

        if to_echo:
            if "echo" not in targets:
                raise ValueError(f"{card_type} cannot be placed in the echo queue")
            self.echo_queue.push_card(card)
        else:
            if "action" not in targets:
                raise ValueError(f"{card_type} cannot be placed in the action queue")
            self.action_queue.push_card(card)

    def place_trap(self, grid_pos: tuple[int, int]) -> None:
        self.board.place_trap(grid_pos)

        for enemy in list(self.enemies):
            if enemy.grid_pos == grid_pos:
                if self.board.trigger_trap(grid_pos):
                    enemy.take_damage(TRAP_ENEMY_DAMAGE)
                break

    def trigger_energy_spike(self) -> None:
        player_x, player_y = self.board.player_position

        for enemy in list(self.enemies):
            distance = math.hypot(
                enemy.grid_pos[0] - player_x,
                enemy.grid_pos[1] - player_y,
            )
            if distance <= ENERGY_SPIKE_RADIUS_TILES:
                enemy.take_damage(ENERGY_SPIKE_DAMAGE)

        self.effects.append(EnergySpikeEffect(self))
        self.screen_shake_time = ENERGY_SPIKE_SHAKE_DURATION
        self.screen_shake_duration = ENERGY_SPIKE_SHAKE_DURATION
        self.screen_shake_intensity = ENERGY_SPIKE_SHAKE_INTENSITY
        self.screen_flash_time = ENERGY_SPIKE_FLASH_DURATION
        self.screen_flash_duration = ENERGY_SPIKE_FLASH_DURATION

    def get_screen_shake_offset(self) -> tuple[float, float]:
        if self.screen_shake_time <= 0 or self.screen_shake_duration <= 0:
            return 0.0, 0.0

        strength = self.screen_shake_intensity * (
            self.screen_shake_time / self.screen_shake_duration
        ) ** 2
        return (
            self.shake_rng.uniform(-strength, strength),
            self.shake_rng.uniform(-strength, strength),
        )

    def handle_input(self, event: pygame.Event) -> None:
        if self.menu == "main":
            self.main_menu.handle_input(event)
        elif self.menu == "game":
            self.action_queue.handle_input(event)
            self.confirm_button.handle_input(event)
            # self.player.handle_input(event)
        elif self.menu == "dead_screen":
            self.dead_menu.handle_input(event)
    
    def update(self) -> None:
        if self.menu == "main":
            self.main_menu.update()
        elif self.menu == "game":
            self.simulation.update()
            self.player.update(self.dt, self.board)
            for enemy in self.enemies:
                enemy.update(self.dt)
            for effect in list(self.effects):
                if not effect.update(self.dt):
                    self.effects.remove(effect)
            self.screen_shake_time = max(0.0, self.screen_shake_time - self.dt)
            self.screen_flash_time = max(0.0, self.screen_flash_time - self.dt)
            self.hud.update(self.dt)
            if self.renderer is not None:
                self.renderer.update(self.dt)
        elif self.menu == "dead_screen":
            self.dead_menu.update()

    def render(self) -> None:
        self.board.render(self.rendering_surface, self.text_layer)
        self.player.render(self.rendering_surface, self.text_layer)
        for enemy in self.enemies:
            enemy.render(self.rendering_surface, self.text_layer)

        self.player.render_effects(self.rendering_surface)
        for effect in self.effects:
            effect.render(self.rendering_surface)

        self.action_queue.render(self.rendering_surface, self.text_layer)
        self.echo_queue.render(self.rendering_surface, self.text_layer)
        self.confirm_button.render(self.rendering_surface, self.text_layer)

        if self.screen_flash_time > 0 and self.screen_flash_duration > 0:
            alpha = int(
                ENERGY_SPIKE_FLASH_ALPHA
                * self.screen_flash_time
                / self.screen_flash_duration
            )
            self.overlay_surface.fill((*self.screen_flash_color, alpha))

        self.hud.render(self.hud_surface, self.text_layer)

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
            elif self.menu == "dead_screen":
                self.dead_menu.render()
                self.screen.blit(self.dead_menu.surface, (0, 0))
            else:
                self.rendering_surface.fill(CARD_QUEUE_BACKGROUND_COLOR)
                self.hud_surface.fill((0, 0, 0, 0))
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
                    self.hud_surface,
                    self.hud.health_pct,
                    self.hud.display_experience_pct,
                    self.get_screen_shake_offset(),
                )

            self.dt = self.clock.tick(120) / 1000
            pygame.display.flip()



def main() -> None:
    game: Game = Game()
    game.run()


if __name__ == "__main__":
    main()

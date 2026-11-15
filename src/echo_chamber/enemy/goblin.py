import random
from typing import TYPE_CHECKING

from echo_chamber.config import *
from echo_chamber.enemy.enemy import AbstractEnemy
from echo_chamber.layer import TextLayer

if TYPE_CHECKING:
    from echo_chamber.main import Game


class Goblin(AbstractEnemy):
    def __init__(self, game: "Game", grid_pos: tuple[int, int]) -> None:
        super().__init__(game, grid_pos)

        self.textures = {
            "idle": {
                "up": load_image("assets/goblin/idle/back.png"),
                "down": load_image("assets/goblin/idle/front.png"),
                "left": load_image("assets/goblin/idle/left.png"),
                "right": load_image("assets/goblin/idle/right.png"),

            }
        }

        self.direction = random.choice(["up", "down", "left", "right"])
        self.state = "idle"

        self.health = GOBLIN_MAX_HEALTH

        self.origin = (
            PLAYER_SCREEN_POS[0] - PLAYER_WIDTH / 2,
            PLAYER_SCREEN_POS[1] + PLAYER_HEIGHT / 4,
        )

    def take_damage(self, damage: int) -> None:
        self.health -= damage
        if self.health <= 0:
            self.game.enemies.remove(self)
            self.game.player.experience += GOBLIN_KILL_EXPERIENCE_GAIN

    def render(self, surface: pygame.Surface, text_layer: TextLayer) -> None:
        x, y = self.get_render_position()

        x += (TILE_SIZE - GOBLIN_WIDTH) / 2
        y += (TILE_SIZE - GOBLIN_HEIGHT) / 2

        texture = self.textures[self.state][self.direction]
        surface.blit(texture, (x, y))

    def attack(self) -> None:
        player_x, player_y = self.game.board.player_position
        dx = player_x - self.grid_pos[0]
        dy = player_y - self.grid_pos[1]

        self.direction = self.direction_from_delta(dx, dy)
        self.lunge_towards(dx, dy)
        self.game.player.take_damage(GOBLIN_ATTACK_DAMAGE)
        print("Goblin attacks")

    def simulation_step(self) -> None:
        path: list[tuple[int, int]] = self.game.board.find_path_to_player(self.grid_pos)
        if len(path) == 2:
            self.attack()
            return

        if len(path) <= 1:
            return

        if random.randint(0, 2) == 0:
            return

        # print(f"Moving: {len(path)}")
        if self.jump_to(path[1]):
            #print(f"Moved closer: {len(path)}")
            ...

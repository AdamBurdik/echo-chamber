import random
import sys
import pygame

TILE_SIZE = 32

DISPLAY_WIDTH = 1920
DISPLAY_HEIGHT = 1080
SCREEN_WIDTH = 480
SCREEN_HEIGHT = 270

class Board:
    def __init__(self, grid_width: int, grid_height: int) -> None:
        self.grid_width = grid_width
        self.grid_height = grid_height

    def render(self, surface: pygame.Surface) -> None:
        for y in range(self.grid_height):
            for x in range(self.grid_width):
                # Multiply by TILE_SIZE instead of grid dimensions to space tiles correctly
                rect = pygame.Rect(x * TILE_SIZE, y * TILE_SIZE, TILE_SIZE, TILE_SIZE)
                pygame.draw.rect(surface, (random.randint(0, 255), 0, 0), rect)

    def update(self) -> None:
        ...


def main() -> None:
    pygame.init()
    pygame.display.set_caption("Echo Chamber")

    # Removed OPENGL flag so standard pygame.draw functions work normally
    screen = pygame.display.set_mode((1920, 1080), pygame.FULLSCREEN)
    clock = pygame.time.Clock()

    board: Board = Board(5, 7)

    rendering_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()

        # Rendering
        screen.fill((0, 0, 0))

        board.render(rendering_surface)
        
        # Scale and blit rendering surface
        scaled = pygame.transform.scale(rendering_surface, (DISPLAY_WIDTH, DISPLAY_HEIGHT))
        screen.blit(scaled, (0, 0))

        # Idk
        clock.tick(120)
        pygame.display.flip()

if __name__ == "__main__":
    main()
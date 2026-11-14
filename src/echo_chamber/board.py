from echo_chamber.config import *


class Board:
    def __init__(self) -> None:
        self.board_width = TILE_SIZE * BOARD_GRID_WIDTH
        self.board_height = TILE_SIZE * BOARD_GRID_HEIGHT
        self.origin = (
            (SCREEN_WIDTH - self.board_width) / 6,
            (SCREEN_HEIGHT - self.board_height) / 2
        )
        
        self.tile_map = {}
        self.generate_initial_tilemap()
        
    def generate_initial_tilemap(self) -> None:
        for grid_y in range(BOARD_GRID_HEIGHT):
            for grid_x in range(BOARD_GRID_WIDTH):
                if grid_y not in self.tile_map:
                    self.tile_map[grid_y] = {}
                
                self.tile_map[grid_y][grid_x] = "empty"

    def render(self, surface: pygame.Surface) -> None:
        for grid_y in range(BOARD_GRID_HEIGHT):
            for grid_x in range(BOARD_GRID_WIDTH):
                tile_id = self.tile_map[grid_y][grid_x]
                
                tile = TILE_REGISTRY.get(tile_id)
                if tile is None:
                    # Some null handling, cause why not
                    tile = TILE_REGISTRY["empty"]
                    
                image = tile["image"]
                
                x = grid_x * TILE_SIZE + self.origin[0]
                y = grid_y * TILE_SIZE + self.origin[1]
                surface.blit(image, (x, y))

    def update(self) -> None:
        ...
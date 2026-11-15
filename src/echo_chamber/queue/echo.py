from typing import TYPE_CHECKING

from echo_chamber.config import *
from echo_chamber.layer import TextLayer
from echo_chamber.utils import load_image

if TYPE_CHECKING:
    from echo_chamber.main import Game

class EchoQueue:
    def __init__(self, game: "Game") -> None:
        self.game: Game = game

        self.capacity = 5
        self.queue = []
        self.icon_cache = {}

        diff = SCREEN_WIDTH - CARD_QUEUE_WIDTH

        self.origin = (
            diff / 2 + diff / 2.2,
            0
        )

    def push_card(self, card: dict) -> None:
        self.queue.append(card)

    def _get_icon(self, card: dict) -> pygame.Surface | None:
        path = card.get("icon")
        if path is None:
            return None

        rotation = card.get("icon_rotation", 0)
        key = (path, rotation)
        if key not in self.icon_cache:
            icon = load_image(path).copy()
            icon.fill(CARD_ICON_COLOR, special_flags=pygame.BLEND_RGBA_MULT)
            if rotation:
                icon = pygame.transform.rotate(icon, rotation)
            self.icon_cache[key] = icon

        return self.icon_cache[key]

    def _get_card_rects(self) -> list[tuple[dict, pygame.Rect]]:
        cards = []

        offset_y = CARD_QUEUE_HEIGHT - CARD_HEIGHT

        for card in self.queue:
            card_x = self.origin[0] + CARD_QUEUE_PADDING
            rect = pygame.Rect(card_x, offset_y, CARD_WIDTH, CARD_HEIGHT)

            cards.append((
                card,
                rect
            ))

            card["temp"] = {}

            offset_y -= CARD_HEIGHT + CARD_QUEUE_GAP

        return cards

    def render(self, surface: pygame.Surface, text_layer: TextLayer) -> None:
        # Render background
        bg_rect = pygame.Rect(self.origin[0], self.origin[1], CARD_QUEUE_WIDTH, CARD_QUEUE_HEIGHT)
        pygame.draw.rect(surface, CARD_QUEUE_BACKGROUND_COLOR, bg_rect)

        cards = self._get_card_rects()

        # def is_next_selected(i: int) -> bool:
        #     if i >= len(cards):
        #         return False
        #     return cards[i + 1][0]["selected"]

        for i, (card, rect) in enumerate(cards):
            pygame.draw.rect(surface, CARD_BACKGROUND_COLOR, rect)

            line_offset_y = 0
            for line in card["lines"]:
                text_layer.draw_text(line, (rect.x + 3, rect.y + line_offset_y), CARD_TEXT_COLOR, layer="behind")
                line_offset_y += text_layer.text_size(line)[1]

            icon = self._get_icon(card)
            if icon is not None:
                icon_x = rect.right - icon.get_width() - CARD_ICON_PADDING
                icon_y = rect.top + CARD_ICON_PADDING
                surface.blit(icon, (icon_x, icon_y))

        # if self.game.simulation.running:
        #     shadow = pygame.Surface((bg_rect.width, bg_rect.height), pygame.SRCALPHA)   # per-pixel alpha
        #     shadow.fill((0, 0, 0, 128))                         # notice the alpha value in the color
        #     surface.blit(shadow, (bg_rect.x, bg_rect.y))

        # offset_y = SCREEN_HEIGHT - CARD_HEIGHT
        # 
        # for card in self.inventory:
        #     display = CARD_REGISTRY[card["type"]]
        # 
        #     color = display["color"]
        #     card_x = self.origin[0] + CARD_QUEUE_PADDING
        # 
        #     pygame.draw.rect(surface, color, (card_x, offset_y, CARD_WIDTH, CARD_HEIGHT))
        # 
        #     line_offset_y = 0
        #     for line in display["lines"]:
        #         text_layer.draw_text(line, (card_x, offset_y + line_offset_y))
        #         line_offset_y += text_layer.text_size(line)[1]
        # 
        #     offset_y -= CARD_HEIGHT + CARD_QUEUE_GAP

    def update(self) -> None:
        ...

    def handle_input(self, event: pygame.Event) -> None:
        ...
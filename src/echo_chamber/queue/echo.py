import math
from typing import TYPE_CHECKING

from echo_chamber.config import *
from echo_chamber.layer import TextLayer
from echo_chamber.queue.card_render import render_card

if TYPE_CHECKING:
    from echo_chamber.main import Game

class EchoQueue:
    def __init__(self, game: "Game") -> None:
        self.game: Game = game

        self.capacity = ECHO_QUEUE_CAPACITY
        self.queue = []
        self.icon_cache = {}

        diff = SCREEN_WIDTH - CARD_QUEUE_WIDTH

        self.origin = (
            diff / 2 + diff / 2.2,
            0
        )

    def push_card(self, card: dict) -> None:
        if len(self.queue) >= self.capacity:
            self.overflow()

        card["countdown"] = card.get("echo_countdown", ECHO_COUNTDOWN_DEFAULT)
        self.queue.append(card)

    def overflow(self) -> None:
        count = max(1, math.ceil(len(self.queue) / ECHO_OVERFLOW_DIVISOR))
        overflow_cards = self.queue[:count]
        del self.queue[:count]

        for card in overflow_cards:
            self.game.simulation.play_echo_card(card)

        self.game.trigger_energy_spike()

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

        for card, rect in cards:
            render_card(surface, text_layer, card, rect, self.icon_cache)

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
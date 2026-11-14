import pygame

from echo_chamber.config import *
from echo_chamber.layer import TextLayer
from echo_chamber.utils import get_mouse_position

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from echo_chamber.main import Game

class ActionQueue:
    def __init__(self, game: "Game") -> None:
        self.game: Game = game
        
        self.capacity = 5
        self.inventory = []
        self.selected = []

        diff = SCREEN_WIDTH - CARD_QUEUE_WIDTH

        self.origin = (
            diff / 2 + diff / 4,
            0
        )

    def push_card(self, card: dict) -> None:
        self.inventory.append(card)

    def _get_card_rects(self) -> list[tuple[dict, pygame.Rect]]:
        cards = []

        offset_y = CARD_QUEUE_HEIGHT - CARD_HEIGHT

        for card in self.selected:
            card_x = self.origin[0] + CARD_QUEUE_PADDING
            rect = pygame.Rect(card_x, offset_y, CARD_WIDTH, CARD_HEIGHT)

            cards.append((
                card,
                rect
            ))

            card["temp"] = {}

            offset_y -= CARD_HEIGHT + CARD_QUEUE_GAP

        if 0 < len(self.selected):
            offset_y -= CARD_QUEUE_SELECTED_GAP
            cards[-1][0]["temp"]["last_selected"] = True

        for card in self.inventory:
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
        pygame.draw.rect(surface, (59, 64, 94), bg_rect)

        cards = self._get_card_rects()

        # def is_next_selected(i: int) -> bool:
        #     if i >= len(cards):
        #         return False
        #     return cards[i + 1][0]["selected"]

        for i, (card, rect) in enumerate(cards):
            color = card["color"]

            pygame.draw.rect(surface, color, rect)

            line_offset_y = 0
            for line in card["lines"]:
                text_layer.draw_text(line, (rect.x, rect.y + line_offset_y))
                line_offset_y += text_layer.text_size(line)[1]

            if card["temp"].get("last_selected", False):
                text_size = text_layer.text_size(f"Selected cards")
                text_layer.draw_text(f"Selected cards", (rect.x + (CARD_WIDTH - text_size[0]) / 2, rect.y + line_offset_y - CARD_HEIGHT - 3), argb_int_to_rgba(0xcdd4a5))

        if self.game.simulation.running:
            shadow = pygame.Surface((bg_rect.width, bg_rect.height), pygame.SRCALPHA)   # per-pixel alpha
            shadow.fill((0, 0, 0, 128))                         # notice the alpha value in the color
            surface.blit(shadow, (bg_rect.x, bg_rect.y))

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
        if event.type != pygame.MOUSEBUTTONDOWN or self.game.simulation.running:
            return

        mouse_x, mouse_y = get_mouse_position()

        for card, rect in self._get_card_rects():
            if rect.collidepoint(mouse_x, mouse_y):
                is_selected = card["selected"]

                if not is_selected:
                    self.inventory.remove(card)
                    self.selected.append(card)
                    card["selected"] = True
                    print("Selected")
                else:
                    self.selected.remove(card)
                    self.inventory.insert(0, card)
                    card["selected"] = False
                return
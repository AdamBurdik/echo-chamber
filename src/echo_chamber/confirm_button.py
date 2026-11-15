from echo_chamber.config import *
from echo_chamber.layer import TextLayer
from echo_chamber.queue.action import ActionQueue
from echo_chamber.simulation import Simulation
from echo_chamber.utils import get_mouse_position

class ConfirmButton:
    def __init__(self, simulation: Simulation, action_queue: ActionQueue) -> None:
        self.simulation = simulation
        self.action_queue: ActionQueue = action_queue
        
        diff = SCREEN_WIDTH - CARD_QUEUE_WIDTH

        self.origin = (
            diff / 2 + diff / 4.25,
            SCREEN_HEIGHT - CONFIRM_BUTTON_HEIGHT - 10
        )
    
    def render(self, surface: pygame.Surface, text_layer: TextLayer) -> None:
        rect = pygame.Rect(self.origin[0], self.origin[1], CONFIRM_BUTTON_WIDTH, CONFIRM_BUTTON_HEIGHT)
        pygame.draw.rect(surface, argb_int_to_rgba(0x2e2a4f), rect)
        
        text_size = text_layer.text_size("BEGIN TURN", text_scale=2)
        text_layer.draw_text(
            "BEGIN RUN",
            (
                rect.x + (CONFIRM_BUTTON_WIDTH - text_size[0]) / 2,
                rect.y + (CONFIRM_BUTTON_HEIGHT - text_size[1]) / 2
            ),
            argb_int_to_rgba(0xcdd4a5) if not self.simulation.running else argb_int_to_rgba(0x686b54),
            text_scale=2
        )
    
    def handle_input(self, event: pygame.event.Event) -> None:
        if event.type == pygame.MOUSEBUTTONDOWN and not self.simulation.running:
            mouse_x, mouse_y = get_mouse_position()
            
            rect = pygame.Rect(self.origin[0], self.origin[1], CONFIRM_BUTTON_WIDTH, CONFIRM_BUTTON_HEIGHT)
            if rect.collidepoint(mouse_x, mouse_y):
                print("BEGIN RUN")
                self.simulation.begin_simulation(self.action_queue.selected)
                return
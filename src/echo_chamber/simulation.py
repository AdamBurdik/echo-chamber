from echo_chamber.board import Board
from echo_chamber.config import SIMULATION_DELAY


class Simulation:
    def __init__(self, board: Board) -> None:
        self.board = board
        
        self.running: bool = False
        self.selected_cards: list[dict] = None
        
        self.cooldown = 0
        
    def next_step(self) -> None:
        if len(self.selected_cards) == 0:
            self.running = False
            return

        card = self.selected_cards.pop(0)
        
        actions = card["actions"]
        for action in actions:
            print("Action: ", action)
            if "move" in action:
                print("Moving: ", action)
                amount = action["move"]["amount"]
                direction = action["move"]["direction"]
                
                self.board.move_player_relative(direction, amount)
                
        
    def begin_simulation(self, selected: list[dict]) -> None:
        self.running = True
        self.selected_cards = selected
            
    def update(self) -> None:
        if self.running:
            if self.cooldown <= 0:
                self.next_step()
                self.cooldown = SIMULATION_DELAY
            else:
                self.cooldown -= 1
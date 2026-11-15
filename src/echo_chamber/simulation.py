from typing import TYPE_CHECKING

from echo_chamber.board import Board
from echo_chamber.config import SIMULATION_DELAY

if TYPE_CHECKING:
    from echo_chamber.main import Game

class Simulation:
    def __init__(self, game: "Game") -> None:
        self.game: Game = game
        self.board: Board = game.board
        
        self.running: bool = False
        self.selected_cards: list[dict] = None
        
        self.cooldown = 0
        
    def next_step(self) -> None:
        if len(self.selected_cards) == 0:
            self.running = False
            return

        # Execute card actions
        card = self.selected_cards.pop(0)
        
        if card.get("echo", False):
            self.game.echo_queue.push_card(card)
        
        actions = card["actions"]
        for action in actions:
            print("Action: ", action)
            if "move" in action:
                print("Moving: ", action)
                amount = action["move"]["amount"]
                direction = action["move"]["direction"]

                self.game.player.jump(self.board, direction, amount)
            if "attack_forward" in action:
                damage = action["attack_forward"]["damage"]
                self.game.player.attack_forward(damage)
            if "spin_attack" in action:
                damage = action["spin_attack"]["damage"]
                self.game.player.spin_attack(damage)
            if "rotate" in action:
                direction = action["rotate"]["direction"]
                self.game.player.rotate(direction)
            if "heal" in action:
                amount = action["heal"]["amount"]
                self.game.player.heal(amount)
            if "regenerate" in action:
                amount = action["regenerate"]["amount"]
                duration = action["regenerate"]["duration"]
                self.game.player.start_regeneration(amount, duration)

        self.game.player.simulation_step()

        # Tick enemies
        for enemy in self.game.enemies:
            enemy.simulation_step()
        
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
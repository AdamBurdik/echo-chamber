import math
import random
from typing import TYPE_CHECKING

from echo_chamber.board import Board
from echo_chamber.config import ECHO_COUNTDOWN_DEFAULT, SIMULATION_DELAY
from echo_chamber.utils import create_card

if TYPE_CHECKING:
    from echo_chamber.main import Game

class Simulation:
    def __init__(self, game: "Game") -> None:
        self.game: Game = game
        self.board: Board = game.board
        
        self.running: bool = False
        self.selected_cards: list[dict] = None
        
        self.cooldown = 0

    def tick_echo_queue(self) -> None:
        queue = self.game.echo_queue.queue
        if not queue:
            return

        card = queue[0]
        if "countdown" not in card:
            card["countdown"] = card.get(
                "echo_countdown", ECHO_COUNTDOWN_DEFAULT
            )
        card["countdown"] -= 1
        if card["countdown"] > 0:
            return

        queue.pop(0)
        self.play_echo_card(card)

    def play_echo_card(self, card: dict) -> None:
        if card.get("curse_effect") == "dead_weight":
            self.explode_dead_weight()
            return

        self.execute_card(card)

    def explode_dead_weight(self) -> None:
        action_queue = self.game.action_queue
        cards = [*action_queue.selected, *action_queue.inventory]
        if not cards:
            return

        destroy_count = max(1, math.ceil(len(cards) / 3))
        for card in random.sample(cards, min(destroy_count, len(cards))):
            self.remove_action_card(card)

    def remove_action_card(self, card: dict) -> None:
        if card in self.selected_cards:
            self.selected_cards.remove(card)
        if card in self.game.action_queue.selected:
            self.game.action_queue.selected.remove(card)
        if card in self.game.action_queue.inventory:
            self.game.action_queue.inventory.remove(card)

    def trigger_parasites(self) -> None:
        action_queue = self.game.action_queue
        parasites = [
            card for card in action_queue.selected + action_queue.inventory
            if card.get("curse_effect") == "parasite"
        ]

        for parasite in parasites:
            cards = action_queue.selected + action_queue.inventory
            index = next(
                (i for i, card in enumerate(cards) if card is parasite),
                None,
            )
            if index is None:
                continue

            neighbor_indices = [
                i for i in (index - 1, index + 1)
                if 0 <= i < len(cards)
            ]
            if not neighbor_indices:
                continue

            target_index = random.choice(neighbor_indices)
            selected_count = len(action_queue.selected)
            dummy = create_card("dummy")
            if target_index < selected_count:
                action_queue.selected[target_index] = dummy
            else:
                action_queue.inventory[target_index - selected_count] = dummy

    def execute_card(self, card: dict) -> None:
        for action in card["actions"]:
            print("Action: ", action)
            if "move_relative" in action:
                amount = action["move_relative"]["amount"]
                direction = action["move_relative"]["direction"]

                self.game.player.jump_relative(self.board, direction, amount)
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
            if "random_step" in action:
                self.game.player.random_step(self.board)
            if "spawn_trap" in action:
                self.game.player.place_trap(self.board)
            if "heal" in action:
                amount = action["heal"]["amount"]
                self.game.player.heal(amount)
            if "regenerate" in action:
                amount = action["regenerate"]["amount"]
                duration = action["regenerate"]["duration"]
                self.game.player.start_regeneration(amount, duration)
            if "block" in action:
                charges = action["block"].get("charges", 0)
                all_surrounding = action["block"].get("all_surrounding", False)
                self.game.player.add_block(charges, all_surrounding)

    def next_step(self) -> None:
        if len(self.selected_cards) == 0:
            self.running = False
            self.game.action_queue.grant_turn_end_cards()

            for enemy in self.game.enemies:
                enemy.simulation_step()

            self.trigger_parasites()
            
            return

        card = self.selected_cards.pop(0)

        if card.get("echo", False):
            self.game.echo_queue.push_card(card)

        self.execute_card(card)
        self.game.player.simulation_step()

        # Tick enemies
        for enemy in self.game.enemies:
            enemy.simulation_step()

        self.trigger_parasites()

    def begin_simulation(self, selected: list[dict]) -> None:
        self.game.player.start_turn()
        self.running = True
        self.selected_cards = selected
        self.tick_echo_queue()
            
    def update(self) -> None:
        if self.running:
            if self.cooldown <= 0:
                self.next_step()
                self.cooldown = SIMULATION_DELAY
            else:
                self.cooldown -= 1
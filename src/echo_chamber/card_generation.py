import random
from typing import TYPE_CHECKING

from echo_chamber.config import *
from echo_chamber.utils import create_card

if TYPE_CHECKING:
    from echo_chamber.main import Game


CARD_CATEGORIES = {
    "movement": (
        "move-forward",
    ),
    "rotation": (
        "rotate-left",
        "rotate-right",
    ),
    "combat": (
        "attack-forward",
        "spin-attack",
        "spawn-trap",
    ),
    "defense": (
        "block-one",
        "block-all",
    ),
    "heal": (
        "instant-heal",
        "regeneration",
    ),
}

CARD_TYPE_TO_CATEGORY = {
    card_type: category
    for category, card_types in CARD_CATEGORIES.items()
    for card_type in card_types
}

ALL_GENERATED_CARD_TYPES = [
    card_type
    for card_types in CARD_CATEGORIES.values()
    for card_type in card_types
]


def nearby_enemy_count(game: "Game") -> int:
    player_x, player_y = game.board.player_position
    return sum(
        max(
            abs(enemy.grid_pos[0] - player_x),
            abs(enemy.grid_pos[1] - player_y),
        ) <= CARD_GEN_THREAT_RADIUS
        for enemy in game.enemies
    )


def category_weights(game: "Game") -> dict[str, float]:
    threat_count = nearby_enemy_count(game)

    if threat_count >= CARD_GEN_THREAT_HIGH_COUNT:
        weights = dict(CARD_GEN_THREAT_WEIGHTS)
    elif threat_count >= CARD_GEN_THREAT_MEDIUM_COUNT:
        weights = dict(CARD_GEN_MEDIUM_WEIGHTS)
    else:
        weights = dict(CARD_GEN_CALM_WEIGHTS)

    if game.player.health <= PLAYER_MAX_HEALTH * CARD_GEN_LOW_HEALTH_RATIO:
        weights["heal"] = CARD_GEN_LOW_HEALTH_HEAL_WEIGHT

    return weights


def inventory_card_counts(game: "Game") -> tuple[dict[str, int], dict[str, int]]:
    cards = [*game.action_queue.inventory, *game.action_queue.selected]

    type_counts: dict[str, int] = {}
    category_counts = {category: 0 for category in CARD_CATEGORIES}

    for card in cards:
        card_type = card.get("type")
        if card_type is None:
            continue

        type_counts[card_type] = type_counts.get(card_type, 0) + 1

        category = CARD_TYPE_TO_CATEGORY.get(card_type)
        if category is not None:
            category_counts[category] += 1

    return type_counts, category_counts


def generate_cards_for_turn(game: "Game", count: int) -> list[dict]:
    cards: list[dict] = []
    type_counts, category_counts = inventory_card_counts(game)
    weights = category_weights(game)
    available_types = list(ALL_GENERATED_CARD_TYPES)
    heals_generated = 0

    for _ in range(count):
        candidate_categories = []
        candidate_category_weights = []

        for category, weight in weights.items():
            if not any(
                card_type in available_types
                for card_type in CARD_CATEGORIES[category]
            ):
                continue

            if category == "heal":
                if heals_generated >= CARD_GEN_MAX_HEAL_PER_BATCH:
                    continue
                if category_counts["heal"] >= CARD_GEN_MAX_HEAL_IN_INVENTORY:
                    continue

            adjusted_weight = weight / (
                1
                + category_counts[category]
                * CARD_GEN_DUPLICATE_CATEGORY_PENALTY
            )
            if adjusted_weight <= 0:
                continue

            candidate_categories.append(category)
            candidate_category_weights.append(adjusted_weight)

        if not candidate_categories:
            break

        category = random.choices(
            candidate_categories,
            weights=candidate_category_weights,
            k=1,
        )[0]

        candidate_types = [
            card_type
            for card_type in CARD_CATEGORIES[category]
            if card_type in available_types
        ]
        candidate_type_weights = [
            1
            / (
                1
                + type_counts.get(card_type, 0)
                * CARD_GEN_DUPLICATE_TYPE_PENALTY
            )
            for card_type in candidate_types
        ]

        card_type = random.choices(
            candidate_types,
            weights=candidate_type_weights,
            k=1,
        )[0]

        cards.append(create_card(card_type))
        type_counts[card_type] = type_counts.get(card_type, 0) + 1
        category_counts[category] += 1

        if category == "heal":
            heals_generated += 1

        available_types.remove(card_type)

    return cards

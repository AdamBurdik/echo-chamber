import pygame

from echo_chamber.config import (
    CARD_BACKGROUND_COLOR,
    CARD_ICON_COLOR,
    CARD_ICON_PADDING,
    CARD_TEXT_COLOR,
    CURSE_CARD_BACKGROUND_COLOR,
    CURSE_CARD_BORDER_DARK_COLOR,
    CURSE_CARD_BORDER_LIGHT_COLOR,
    CURSE_CARD_ICON_COLOR,
    CURSE_CARD_TEXT_COLOR,
    ECHO_CARD_BACKGROUND_COLOR,
    ECHO_CARD_BORDER_DARK_COLOR,
    ECHO_CARD_BORDER_LIGHT_COLOR,
    ECHO_CARD_ICON_COLOR,
)
from echo_chamber.layer import TextLayer
from echo_chamber.utils import load_image


def get_card_icon(card: dict, cache: dict) -> pygame.Surface | None:
    path = card.get("icon")
    if path is None:
        return None

    rotation = card.get("icon_rotation", 0)
    is_echo = bool(card.get("echo", False))
    is_curse = bool(card.get("curse", False))
    key = (path, rotation, is_echo, is_curse)
    if key not in cache:
        icon = load_image(path).copy()
        if is_curse:
            tint = CURSE_CARD_ICON_COLOR
        elif is_echo:
            tint = ECHO_CARD_ICON_COLOR
        else:
            tint = CARD_ICON_COLOR
        icon.fill(tint, special_flags=pygame.BLEND_RGBA_MULT)
        if rotation:
            icon = pygame.transform.rotate(icon, rotation)
        cache[key] = icon

    return cache[key]


def render_card(
    surface: pygame.Surface,
    text_layer: TextLayer,
    card: dict,
    rect: pygame.Rect,
    icon_cache: dict,
) -> int:
    is_echo = bool(card.get("echo", False))
    is_curse = bool(card.get("curse", False))

    if is_curse:
        background = CURSE_CARD_BACKGROUND_COLOR
        border_dark = CURSE_CARD_BORDER_DARK_COLOR
        border_light = CURSE_CARD_BORDER_LIGHT_COLOR
        text_color = CURSE_CARD_TEXT_COLOR
    elif is_echo:
        background = ECHO_CARD_BACKGROUND_COLOR
        border_dark = ECHO_CARD_BORDER_DARK_COLOR
        border_light = ECHO_CARD_BORDER_LIGHT_COLOR
        text_color = CARD_TEXT_COLOR
    else:
        background = CARD_BACKGROUND_COLOR
        border_dark = None
        border_light = None
        text_color = CARD_TEXT_COLOR

    pygame.draw.rect(surface, background, rect)

    if border_dark is not None and border_light is not None:
        right = rect.x + rect.width - 1
        bottom = rect.y + rect.height - 1
        pygame.draw.line(
            surface,
            border_dark,
            (rect.x, rect.y),
            (right, rect.y),
        )
        pygame.draw.line(
            surface,
            border_dark,
            (rect.x, rect.y),
            (rect.x, bottom),
        )
        pygame.draw.line(
            surface,
            border_light,
            (right, rect.y),
            (right, bottom),
        )
        pygame.draw.line(
            surface,
            border_light,
            (rect.x, bottom),
            (right, bottom),
        )

    line_offset_y = 0
    for line in card.get("lines", ()):
        text_layer.draw_text(
            line,
            (rect.x + 3, rect.y + line_offset_y),
            text_color,
            layer="behind",
        )
        line_offset_y += text_layer.text_size(line)[1]

    countdown = card.get("countdown")
    if countdown is not None:
        countdown_text = str(countdown)
        countdown_width, countdown_height = text_layer.text_size(countdown_text)
        text_layer.draw_text(
            countdown_text,
            (
                rect.right - countdown_width - 2,
                rect.bottom - countdown_height - 1,
            ),
            text_color,
            layer="behind",
        )

    icon = get_card_icon(card, icon_cache)
    if icon is not None:
        icon_x = rect.right - icon.get_width() - CARD_ICON_PADDING
        icon_y = rect.top + CARD_ICON_PADDING
        surface.blit(icon, (icon_x, icon_y))

    return line_offset_y

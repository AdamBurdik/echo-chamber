import pygame


class TextLayer:
    def __init__(self, low_width: int, low_height: int, scale: int,
                 font_path: str, base_font_size: int,
                 text_scale: float = 1.0) -> None:
        self.scale = scale
        self.text_scale = text_scale
        self.font_path = font_path
        self.base_font_size = base_font_size
        self.surface = pygame.Surface(
            (low_width * scale, low_height * scale), pygame.SRCALPHA
        )
        self._fonts: dict[float, pygame.font.Font] = {}

    def get_font(self, text_scale: float | None = None) -> pygame.font.Font:
        ts = self.text_scale if text_scale is None else text_scale
        if ts not in self._fonts:
            px = max(1, round(self.base_font_size * self.scale * ts))
            self._fonts[ts] = pygame.font.Font(self.font_path, px)
        return self._fonts[ts]

    def project(self, x: float, y: float) -> tuple[int, int]:
        """Low-res point -> hi-res point."""
        return round(x * self.scale), round(y * self.scale)

    def unproject(self, x: float, y: float) -> tuple[float, float]:
        return x / self.scale, y / self.scale

    def text_size(self, text: str,
                  text_scale: float | None = None) -> tuple[float, float]:
        w, h = self.get_font(text_scale).size(text)
        return w / self.scale, h / self.scale

    def clear(self) -> None:
        self.surface.fill((0, 0, 0, 0))

    def draw_text(self, text: str, pos: tuple[float, float],
                  color: tuple[int, int, int] = (255, 255, 255),
                  text_scale: float | None = None) -> None:
        text_surface = self.get_font(text_scale).render(text, False, color)
        self.surface.blit(text_surface, self.project(*pos))
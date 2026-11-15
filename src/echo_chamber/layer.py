import pygame


class TextLayer:
    def __init__(self, low_width: int, low_height: int, scale: int,
                 font_path: str, base_font_size: int,
                 text_scale: float = 1.0) -> None:
        self.scale = scale
        self.text_scale = text_scale
        self.font_path = font_path
        self.base_font_size = base_font_size
        size = (low_width * scale, low_height * scale)
        self.surface = pygame.Surface(size, pygame.SRCALPHA)
        self.behind_surface = pygame.Surface(size, pygame.SRCALPHA)
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

    def clear(self, layer: str | None = None) -> None:
        if layer is None:
            self.surface.fill((0, 0, 0, 0))
            self.behind_surface.fill((0, 0, 0, 0))
            return

        self.get_surface(layer).fill((0, 0, 0, 0))

    def get_surface(self, layer: str) -> pygame.Surface:
        match layer:
            case "above":
                return self.surface
            case "behind":
                return self.behind_surface
            case _:
                raise ValueError(f"Unknown text layer: {layer!r}")

    def draw_text(self, text: str, pos: tuple[float, float],
                  color: tuple[int, int, int] = (255, 255, 255),
                  text_scale: float | None = None,
                  layer: str = "above",
                  alpha: int = 255) -> None:
        text_surface = self.get_font(text_scale).render(text, False, color)
        text_surface.set_alpha(max(0, min(255, alpha)))
        self.get_surface(layer).blit(text_surface, self.project(*pos))
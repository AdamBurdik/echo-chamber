import struct
from pathlib import Path

import moderngl
import pygame

from echo_chamber.config import (
    BACKDROP_INTENSITY,
    BACKDROP_PATH,
    BACKDROP_SPEED,
    FRAGMENT_SHADER_PATH,
    HUD_EDGE_WIDTH,
    HUD_EXPERIENCE_RECT,
    HUD_HEALTH_RECT,
    HUD_HP_WAVE_AMPLITUDE,
    HUD_HP_WAVE_SPEED,
    HUD_XP_WAVE_AMPLITUDE,
    HUD_XP_WAVE_SPEED,
    VERTEX_SHADER_PATH,
)


class Renderer:
    def __init__(
        self,
        low_res: tuple[int, int],
        text_size: tuple[int, int],
        backdrop_path: str = BACKDROP_PATH,
    ) -> None:
        self.ctx = moderngl.create_context()
        self.ctx.disable(moderngl.BLEND)

        self.low_res = low_res
        self.text_size = text_size
        self.intensity = BACKDROP_INTENSITY
        self.time = 0.0

        backdrop = pygame.image.load(backdrop_path).convert_alpha()
        if backdrop.get_size() != low_res:
            backdrop = pygame.transform.scale(backdrop, low_res)
        self.backdrop_size = backdrop.get_size()

        self.game_texture = self._texture(low_res, moderngl.NEAREST)
        self.overlay_texture = self._texture(low_res, moderngl.NEAREST)
        self.text_above_texture = self._texture(text_size, moderngl.NEAREST)
        self.text_behind_texture = self._texture(text_size, moderngl.NEAREST)

        self.backdrop_texture = self.ctx.texture(
            self.backdrop_size, 4, backdrop.get_buffer().raw
        )
        self.backdrop_texture.filter = (moderngl.NEAREST, moderngl.NEAREST)
        self.backdrop_texture.repeat_x = False
        self.backdrop_texture.repeat_y = False

        vertex_shader = Path(VERTEX_SHADER_PATH).read_text()
        fragment_shader = Path(FRAGMENT_SHADER_PATH).read_text()

        self.program = self.ctx.program(
            vertex_shader=vertex_shader,
            fragment_shader=fragment_shader,
        )
        self.program["u_game"] = 0
        self.program["u_overlay"] = 1
        self.program["u_text_above"] = 2
        self.program["u_backdrop"] = 3
        self.program["u_text_behind"] = 4
        self.program["u_low_res"] = low_res
        self.program["u_time"] = 0.0
        self.program["u_intensity"] = self.intensity
        self.program["u_backdrop_speed"] = BACKDROP_SPEED
        self.program["u_hp_rect"] = HUD_HEALTH_RECT
        self.program["u_xp_rect"] = HUD_EXPERIENCE_RECT
        self.program["u_hp"] = 1.0
        self.program["u_xp"] = 0.0
        self.program["u_hp_wave_speed"] = HUD_HP_WAVE_SPEED
        self.program["u_hp_wave_amplitude"] = HUD_HP_WAVE_AMPLITUDE
        self.program["u_xp_wave_speed"] = HUD_XP_WAVE_SPEED
        self.program["u_xp_wave_amplitude"] = HUD_XP_WAVE_AMPLITUDE
        self.program["u_hud_edge_width"] = HUD_EDGE_WIDTH

        vertices = struct.pack(
            "16f",
            -1.0,  1.0, 0.0, 0.0,
             1.0,  1.0, 1.0, 0.0,
            -1.0, -1.0, 0.0, 1.0,
             1.0, -1.0, 1.0, 1.0,
        )
        self.vbo = self.ctx.buffer(vertices)
        self.vao = self.ctx.vertex_array(
            self.program, [(self.vbo, "2f 2f", "in_position", "in_uv")]
        )

    def _texture(self, size: tuple[int, int], filter_mode: int) -> moderngl.Texture:
        texture = self.ctx.texture(size, 4)
        texture.filter = (filter_mode, filter_mode)
        texture.repeat_x = False
        texture.repeat_y = False
        return texture

    def update(self, dt: float) -> None:
        self.time += dt

    def render(
        self,
        game_surface: pygame.Surface,
        overlay_surface: pygame.Surface,
        text_above_surface: pygame.Surface,
        text_behind_surface: pygame.Surface,
        health: float = 1.0,
        experience: float = 0.0,
    ) -> None:
        self.game_texture.write(game_surface.get_buffer().raw)
        self.overlay_texture.write(overlay_surface.get_buffer().raw)
        self.text_above_texture.write(text_above_surface.get_buffer().raw)
        self.text_behind_texture.write(text_behind_surface.get_buffer().raw)

        self.ctx.screen.use()
        self.ctx.viewport = (0, 0, *self.ctx.screen.size)
        self.ctx.clear(0.0, 0.0, 0.0, 1.0)

        self.program["u_time"] = self.time
        self.program["u_hp"] = max(0.0, min(1.0, health))
        self.program["u_xp"] = max(0.0, min(1.0, experience))

        self.game_texture.use(0)
        self.overlay_texture.use(1)
        self.text_above_texture.use(2)
        self.backdrop_texture.use(3)
        self.text_behind_texture.use(4)

        self.vao.render(moderngl.TRIANGLE_STRIP)

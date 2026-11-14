import struct

import moderngl
import pygame

from echo_chamber.config import BACKDROP_INTENSITY, BACKDROP_PATH

VERTEX_SHADER = """
#version 330

in vec2 in_position;
in vec2 in_uv;
out vec2 uv;

void main() {
    uv = in_uv;
    gl_Position = vec4(in_position, 0.0, 1.0);
}
"""

FRAGMENT_SHADER = """
#version 330

uniform sampler2D u_game;
uniform sampler2D u_overlay;
uniform sampler2D u_text_above;
uniform sampler2D u_text_behind;
uniform sampler2D u_backdrop;

uniform vec2 u_low_res;
uniform float u_time;
uniform float u_intensity;

in vec2 uv;
out vec4 f_color;

float hash(vec2 p) {
    p = fract(p * vec2(123.34, 456.21));
    p += dot(p, p + 45.32);
    return fract(p.x * p.y);
}

float noise(vec2 p) {
    vec2 i = floor(p);
    vec2 f = fract(p);
    f = f * f * (3.0 - 2.0 * f);

    float a = hash(i);
    float b = hash(i + vec2(1.0, 0.0));
    float c = hash(i + vec2(0.0, 1.0));
    float d = hash(i + vec2(1.0, 1.0));

    return mix(mix(a, b, f.x), mix(c, d, f.x), f.y);
}

void main() {
    vec3 color = texture(u_game, uv).bgra.rgb;

    vec4 text_behind = texture(u_text_behind, uv).bgra;
    color = mix(color, text_behind.rgb, text_behind.a);

    vec2 low_px = floor(uv * u_low_res);
    vec2 low_uv = (low_px + 0.5) / u_low_res;

    vec2 texel = 1.0 / u_low_res;
    float a_l = texture(u_backdrop, low_uv - vec2(texel.x, 0.0)).bgra.a;
    float a_r = texture(u_backdrop, low_uv + vec2(texel.x, 0.0)).bgra.a;
    float a_d = texture(u_backdrop, low_uv - vec2(0.0, texel.y)).bgra.a;
    float a_u = texture(u_backdrop, low_uv + vec2(0.0, texel.y)).bgra.a;
    float edge = clamp(abs(a_r - a_l) + abs(a_u - a_d), 0.0, 1.0);

    float t = u_time;
    vec2 drift = vec2(sin(t * 0.35 + low_uv.y * 6.0), cos(t * 0.31 - low_uv.x * 5.0));
    vec2 ripple = vec2(sin(low_uv.y * 26.0 + t * 1.7), cos(low_uv.x * 23.0 - t * 1.4));
    vec2 offset_px = (drift * 0.6 + ripple * 1.2) * (0.15 + edge) * u_intensity;

    vec2 offset = floor(offset_px + 0.5) / u_low_res;
    vec4 backdrop = texture(u_backdrop, clamp(low_uv + offset, 0.0, 1.0)).bgra;

    float n = noise(low_uv * 9.0 + vec2(t * 0.12, -t * 0.09));
    vec3 tinted = backdrop.rgb + vec3(0.02, 0.015, 0.03) * edge * (0.5 + 0.5 * n);
    color = mix(color, tinted, backdrop.a);

    vec4 overlay = texture(u_overlay, uv).bgra;
    color = mix(color, overlay.rgb, overlay.a);

    vec4 text_above = texture(u_text_above, uv).bgra;
    color = mix(color, text_above.rgb, text_above.a);

    f_color = vec4(color, 1.0);
}
"""


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

        self.program = self.ctx.program(
            vertex_shader=VERTEX_SHADER,
            fragment_shader=FRAGMENT_SHADER,
        )
        self.program["u_game"] = 0
        self.program["u_overlay"] = 1
        self.program["u_text_above"] = 2
        self.program["u_backdrop"] = 3
        self.program["u_text_behind"] = 4
        self.program["u_low_res"] = low_res
        self.program["u_time"] = 0.0
        self.program["u_intensity"] = self.intensity

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
    ) -> None:
        self.game_texture.write(game_surface.get_buffer().raw)
        self.overlay_texture.write(overlay_surface.get_buffer().raw)
        self.text_above_texture.write(text_above_surface.get_buffer().raw)
        self.text_behind_texture.write(text_behind_surface.get_buffer().raw)

        self.ctx.screen.use()
        self.ctx.viewport = (0, 0, *self.ctx.screen.size)
        self.ctx.clear(0.0, 0.0, 0.0, 1.0)

        self.program["u_time"] = self.time

        self.game_texture.use(0)
        self.overlay_texture.use(1)
        self.text_above_texture.use(2)
        self.backdrop_texture.use(3)
        self.text_behind_texture.use(4)

        self.vao.render(moderngl.TRIANGLE_STRIP)

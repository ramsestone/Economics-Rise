# ============================================================
#  UI – Componentes reutilizables
# ============================================================
import pygame
from game.constants import *


def get_font(size, bold=False):
    """Fuente pixelada (usa la del sistema si no hay otra)."""
    try:
        font = pygame.font.SysFont("Consolas", size, bold=bold)
    except Exception:
        font = pygame.font.Font(None, size)
    return font


# ── Botón ─────────────────────────────────────────────────────
class Button:
    def __init__(self, x, y, w, h, text, color=CYAN, text_color=BLACK):
        self.rect = pygame.Rect(x, y, w, h)
        self.text = text
        self.color = color
        self.dark = tuple(max(0, c - 60) for c in color)
        self.text_color = text_color
        self.hovered = False
        self.font = get_font(18, bold=True)

    def draw(self, surface):
        col = self.color if self.hovered else self.dark
        border_col = self.color
        # sombra pixel
        shadow = self.rect.move(3, 3)
        pygame.draw.rect(surface, BLACK, shadow, border_radius=4)
        pygame.draw.rect(surface, col, self.rect, border_radius=4)
        pygame.draw.rect(surface, border_col, self.rect, 2, border_radius=4)
        txt = self.font.render(self.text, True, self.text_color)
        tx = self.rect.centerx - txt.get_width() // 2
        ty = self.rect.centery - txt.get_height() // 2
        surface.blit(txt, (tx, ty))

    def update(self, mouse_pos):
        self.hovered = self.rect.collidepoint(mouse_pos)

    def is_clicked(self, event):
        clicked = (event.type == pygame.MOUSEBUTTONDOWN and
                   event.button == 1 and
                   self.rect.collidepoint(event.pos))
        if clicked:
            try:
                from game.audio import audio
                audio.play("click")
            except Exception:
                pass
        return clicked


# ── Slider ────────────────────────────────────────────────────
class Slider:
    def __init__(self, x, y, w, label, min_val=0, max_val=100,
                 value=50, color=CYAN, unit=""):
        self.x, self.y, self.w = x, y, w
        self.label = label
        self.min_val = min_val
        self.max_val = max_val
        self.value = value
        self.color = color
        self.unit = unit
        self.dragging = False
        self.font_lbl = get_font(15, bold=True)
        self.font_val = get_font(15)
        self.track_h = 10
        self.knob_r = 10
        self.track_rect = pygame.Rect(x, y + 22, w, self.track_h)
        self._last_sound_val = value

    @property
    def ratio(self):
        return (self.value - self.min_val) / (self.max_val - self.min_val)

    def _knob_x(self):
        return int(self.x + self.ratio * self.w)

    def draw(self, surface):
        # label
        lbl = self.font_lbl.render(self.label, True, GRAY_LIGHT)
        surface.blit(lbl, (self.x, self.y))
        # valor
        val_str = f"{self.value:.1f}{self.unit}"
        val = self.font_val.render(val_str, True, self.color)
        surface.blit(val, (self.x + self.w - val.get_width(), self.y))
        # track fondo
        pygame.draw.rect(surface, GRAY_DARK, self.track_rect, border_radius=4)
        # track relleno
        fill_w = int(self.ratio * self.w)
        if fill_w > 0:
            fill_rect = pygame.Rect(self.x, self.y + 22, fill_w, self.track_h)
            pygame.draw.rect(surface, self.color, fill_rect, border_radius=4)
        # knob
        kx = self._knob_x()
        ky = self.y + 22 + self.track_h // 2
        pygame.draw.circle(surface, self.color, (kx, ky), self.knob_r)
        pygame.draw.circle(surface, WHITE, (kx, ky), self.knob_r - 3)
        pygame.draw.circle(surface, self.color, (kx, ky), self.knob_r - 6)

    def _trigger_slider_sound(self):
        if abs(self.value - self._last_sound_val) >= (self.max_val - self.min_val) * 0.05:
            self._last_sound_val = self.value
            try:
                from game.audio import audio
                audio.play("slider")
            except Exception:
                pass

    def update(self, mouse_pos=None):
        if mouse_pos is not None and self.dragging:
            if not pygame.mouse.get_pressed()[0]:
                self.dragging = False
            else:
                ratio = (mouse_pos[0] - self.x) / self.w
                ratio = max(0.0, min(1.0, ratio))
                self.value = self.min_val + ratio * (self.max_val - self.min_val)
                self._trigger_slider_sound()

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            kx = self._knob_x()
            ky = self.y + 22 + self.track_h // 2
            hit_knob = ((event.pos[0] - kx) ** 2 + (event.pos[1] - ky) ** 2) <= (self.knob_r + 4) ** 2
            hit_track = self.track_rect.inflate(6, 12).collidepoint(event.pos)
            if hit_knob or hit_track:
                self.dragging = True
                ratio = (event.pos[0] - self.x) / self.w
                ratio = max(0.0, min(1.0, ratio))
                self.value = self.min_val + ratio * (self.max_val - self.min_val)
                self._trigger_slider_sound()
        elif event.type == pygame.MOUSEBUTTONUP:
            self.dragging = False
        elif event.type == pygame.MOUSEMOTION and self.dragging:
            ratio = (event.pos[0] - self.x) / self.w
            ratio = max(0.0, min(1.0, ratio))
            self.value = self.min_val + ratio * (self.max_val - self.min_val)
            self._trigger_slider_sound()



# ── Panel con borde pixel ─────────────────────────────────────
class Panel:
    def __init__(self, x, y, w, h, color=PANEL_BG, border=CYAN):
        self.rect = pygame.Rect(x, y, w, h)
        self.color = color
        self.border = border

    def draw(self, surface):
        # sombra
        shadow = self.rect.move(4, 4)
        s = pygame.Surface((self.rect.w, self.rect.h), pygame.SRCALPHA)
        s.fill((0, 0, 0, 80))
        surface.blit(s, shadow.topleft)
        pygame.draw.rect(surface, self.color, self.rect, border_radius=6)
        pygame.draw.rect(surface, self.border, self.rect, 2, border_radius=6)


# ── Gráfico de líneas ─────────────────────────────────────────
class LineChart:
    def __init__(self, x, y, w, h, label="", color=CYAN, max_points=60):
        self.rect = pygame.Rect(x, y, w, h)
        self.label = label
        self.color = color
        self.data = []
        self.max_points = max_points
        self.font = get_font(13)

    def push(self, value):
        self.data.append(value)
        if len(self.data) > self.max_points:
            self.data.pop(0)

    add_point = push

    def draw(self, surface):
        pygame.draw.rect(surface, PANEL_DARK, self.rect, border_radius=4)
        pygame.draw.rect(surface, GRAY_DARK, self.rect, 1, border_radius=4)
        if self.label:
            lbl = self.font.render(self.label, True, GRAY_LIGHT)
            surface.blit(lbl, (self.rect.x + 4, self.rect.y + 2))
        if len(self.data) < 2:
            return
        mn = min(self.data)
        mx = max(self.data)
        rng = mx - mn if mx != mn else 1
        pad = 20
        points = []
        for i, v in enumerate(self.data):
            px = self.rect.x + pad + (i / (len(self.data) - 1)) * (self.rect.w - 2 * pad)
            py = self.rect.y + self.rect.h - pad - ((v - mn) / rng) * (self.rect.h - 2 * pad)
            points.append((int(px), int(py)))
        if len(points) >= 2:
            pygame.draw.lines(surface, self.color, False, points, 2)
        # último valor
        last = self.font.render(f"{self.data[-1]:.1f}", True, self.color)
        surface.blit(last, (self.rect.right - last.get_width() - 4,
                             self.rect.y + self.rect.h - 18))


# ── Barra de progreso ─────────────────────────────────────────
class ProgressBar:
    def __init__(self, x, y, w, h, label="", color=GREEN, max_val=100):
        self.rect = pygame.Rect(x, y, w, h)
        self.label = label
        self.color = color
        self.value = 0
        self.max_val = max_val
        self.font = get_font(14, bold=True)

    def draw(self, surface, value=None):
        if value is not None:
            self.value = value
        pygame.draw.rect(surface, GRAY_DARK, self.rect, border_radius=4)
        ratio = max(0, min(1, self.value / self.max_val))
        if ratio > 0:
            fill = pygame.Rect(self.rect.x, self.rect.y,
                               int(ratio * self.rect.w), self.rect.h)
            pygame.draw.rect(surface, self.color, fill, border_radius=4)
        pygame.draw.rect(surface, GRAY, self.rect, 1, border_radius=4)
        txt = self.font.render(f"{self.label}: {self.value:.0f}", True, WHITE)
        tx = self.rect.centerx - txt.get_width() // 2
        ty = self.rect.centery - txt.get_height() // 2
        surface.blit(txt, (tx, ty))


# ── Texto parpadeante ─────────────────────────────────────────
class BlinkText:
    def __init__(self, text, x, y, color=YELLOW, size=20, interval=500):
        self.text = text
        self.pos = (x, y)
        self.color = color
        self.font = get_font(size, bold=True)
        self.interval = interval
        self._timer = 0
        self._visible = True

    def update(self, dt):
        self._timer += dt
        if self._timer >= self.interval:
            self._timer = 0
            self._visible = not self._visible

    def draw(self, surface):
        if self._visible:
            txt = self.font.render(self.text, True, self.color)
            surface.blit(txt, self.pos)


def draw_scene_title(surface, title, subtitle="", accent=CYAN):
    # barra superior
    pygame.draw.rect(surface, PANEL_DARK, (0, 0, SCREEN_W, 70))
    pygame.draw.line(surface, accent, (0, 70), (SCREEN_W, 70), 2)

    # Ancho disponible antes de chocar con los botones superiores derechos (que inician en SCREEN_W - 370)
    max_title_w = SCREEN_W - 380

    # Auto-ajuste de tamaño de fuente para el título
    title_size = 32
    font_big = get_font(title_size, bold=True)
    while font_big.size(title)[0] > max_title_w and title_size > 18:
        title_size -= 2
        font_big = get_font(title_size, bold=True)

    txt = font_big.render(title, True, accent)
    surface.blit(txt, (20, 12))

    if subtitle:
        sub_size = 15
        font_sub = get_font(sub_size)
        while font_sub.size(subtitle)[0] > max_title_w and sub_size > 11:
            sub_size -= 1
            font_sub = get_font(sub_size)
        stxt = font_sub.render(subtitle, True, GRAY_LIGHT)
        surface.blit(stxt, (22, 46))


def draw_back_button(surface, mouse_pos):
    """Dibuja botón MENÚ y retorna su rect."""
    font = get_font(15, bold=True)
    rect = pygame.Rect(SCREEN_W - 110, 12, 95, 36)
    hovered = rect.collidepoint(mouse_pos)
    col = GRAY if hovered else GRAY_DARK
    pygame.draw.rect(surface, col, rect, border_radius=4)
    pygame.draw.rect(surface, GRAY_LIGHT, rect, 1, border_radius=4)
    txt = font.render("◄ MENÚ", True, WHITE)
    surface.blit(txt, (rect.centerx - txt.get_width() // 2,
                       rect.centery - txt.get_height() // 2))
    return rect


def text(surface, msg, x, y, color=WHITE, size=16, bold=False):
    f = get_font(size, bold=bold)
    t = f.render(msg, True, color)
    surface.blit(t, (x, y))
    return t.get_width()


# ── Notificación flotante ─────────────────────────────────────
class Notification:
    def __init__(self):
        self.messages = []
        self.font = get_font(15, bold=True)

    def add(self, msg, color=YELLOW, duration=2500):
        self.messages.append({"msg": msg, "color": color,
                               "timer": duration, "alpha": 255})
        try:
            from game.audio import audio
            if color == RED:
                audio.play("warning")
            elif color == GREEN:
                audio.play("success")
        except Exception:
            pass

    def update(self, dt):
        for m in self.messages:
            m["timer"] -= dt
            if m["timer"] < 500:
                m["alpha"] = int(255 * (m["timer"] / 500))
        self.messages = [m for m in self.messages if m["timer"] > 0]

    def draw(self, surface):
        by = SCREEN_H - 100
        for m in reversed(self.messages):
            txt = self.font.render(m["msg"], True, m["color"])
            s = pygame.Surface((txt.get_width() + 12, txt.get_height() + 6),
                                pygame.SRCALPHA)
            s.fill((0, 0, 0, 140))
            s.set_alpha(m["alpha"])
            surface.blit(s, (SCREEN_W // 2 - s.get_width() // 2, by - 2))
            ts = txt.copy()
            ts.set_alpha(m["alpha"])
            surface.blit(ts, (SCREEN_W // 2 - txt.get_width() // 2, by))
            by -= 32

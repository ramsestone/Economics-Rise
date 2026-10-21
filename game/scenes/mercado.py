# ============================================================
#  ESCENA: MERCADO
#  Visualización animada del flujo compradores/vendedores.
#  El jugador controla número de vendedores, compradores, precio.
# ============================================================
import pygame
import math
import random
from game.scenes.base import BaseScene
from game.constants import *
from game.ui import (Slider, Panel, LineChart, Notification,
                     text, get_font)
from game.sprites import sprite_consumidor, sprite_fabricante, sprite_moneda


class _Agente:
    """Partícula animada en el mercado."""
    def __init__(self, kind, x, y, target_x, target_y):
        self.kind = kind           # "buyer" o "seller"
        self.x, self.y = float(x), float(y)
        self.tx, self.ty = float(target_x), float(target_y)
        self.speed = random.uniform(0.5, 1.5)
        self.done  = False
        self.alpha = 255
        self.color = YELLOW if kind == "buyer" else GREEN

    def update(self, dt):
        dx = self.tx - self.x
        dy = self.ty - self.y
        dist = math.hypot(dx, dy)
        if dist < 3:
            self.done = True
        else:
            step = self.speed * dt * 0.06
            self.x += dx / dist * step
            self.y += dy / dist * step

    def draw(self, surface):
        col = self.color
        r   = 6
        pygame.draw.circle(surface, col, (int(self.x), int(self.y)), r)
        pygame.draw.circle(surface, WHITE, (int(self.x), int(self.y)), r - 2)
        pygame.draw.circle(surface, col, (int(self.x), int(self.y)), r - 4)


class MercadoScene(BaseScene):
    KEY      = "mercado"
    TITLE    = "Mercado"
    SUBTITLE = "Observa el flujo de compradores y vendedores en el mercado"

    def build(self):
        accent = self.accent
        self.sliders = [
            Slider(60, 110, 280, "Nº Vendedores",    1, 20, 8,
                   color=GREEN,  unit=""),
            Slider(60, 170, 280, "Nº Compradores",   1, 20, 10,
                   color=YELLOW, unit=""),
            Slider(60, 230, 280, "Precio de Mercado", 1, 200, 60,
                   color=CYAN,   unit="$"),
            Slider(60, 290, 280, "Calidad del Bien",  1, 10,  5,
                   color=PURPLE, unit=""),
        ]
        self.chart_trans = LineChart(700, 90, 290, 130, "Transacciones",
                                     color=CYAN)
        self.notif  = Notification()
        self.sprite_c = sprite_consumidor()
        self.sprite_s = sprite_fabricante()
        self.agentes  = []
        self._spawn_timer = 0
        self._calc_timer  = 0
        self.transacciones = 0
        self.vol_total     = 0.0
        self.satisfaccion  = 0.0
        # Centro del mercado (canvas)
        self.cx = 520
        self.cy = 300

    def handle_event(self, event):
        for s in self.sliders:
            s.handle_event(event)

    def _spawn_agents(self):
        n_buy = int(self.sliders[1].value)
        n_sell= int(self.sliders[0].value)
        # compradores vienen de la izquierda
        for _ in range(min(n_buy, 3)):
            y0 = random.randint(120, 500)
            a = _Agente("buyer", 400, y0,
                        self.cx + random.randint(-60, 60),
                        self.cy + random.randint(-60, 60))
            self.agentes.append(a)
        # vendedores vienen de la derecha
        for _ in range(min(n_sell, 3)):
            y0 = random.randint(120, 500)
            a = _Agente("seller", 680, y0,
                        self.cx + random.randint(-60, 60),
                        self.cy + random.randint(-60, 60))
            self.agentes.append(a)
        if len(self.agentes) > 60:
            self.agentes = self.agentes[-60:]

    def update(self, dt):
        super().update(dt)
        mouse = pygame.mouse.get_pos()
        for s in self.sliders:
            s.update(mouse)
        # Spawn
        self._spawn_timer += dt
        if self._spawn_timer >= 1200:
            self._spawn_timer = 0
            self._spawn_agents()
        # Mover agentes
        for a in self.agentes:
            a.update(dt)
        self.agentes = [a for a in self.agentes if not a.done]
        # Cálculo
        self._calc_timer += dt
        if self._calc_timer >= 900:
            self._calc_timer = 0
            precio = self.sliders[2].value
            calidad= self.sliders[3].value
            n_buy  = self.sliders[1].value
            n_sell = self.sliders[0].value
            # transacciones = mínimo de oferta/demanda ponderado
            q_dem = n_buy * (100 / max(1, precio)) * calidad * 0.5
            q_ofe = n_sell * (precio / 20) * 1.5
            self.transacciones = round(min(q_dem, q_ofe), 1)
            self.vol_total     = round(self.transacciones * precio, 1)
            self.satisfaccion  = round(calidad / 10 * 100, 1)
            self.chart_trans.push(self.transacciones)
        self.notif.update(dt)

    def draw_content(self, surface):
        accent = self.accent

        # Panel de controles
        p = Panel(40, 85, 330, 270, border=accent)
        p.draw(surface)
        text(surface, "Variables del Mercado", 55, 95, color=accent,
             size=14, bold=True)
        for s in self.sliders:
            s.draw(surface)

        # Canvas central del mercado
        market_rect = pygame.Rect(400, 85, 280, 300)
        pygame.draw.rect(surface, PANEL_DARK, market_rect, border_radius=8)
        pygame.draw.rect(surface, accent, market_rect, 2, border_radius=8)
        text(surface, "PLAZA DEL MERCADO", 475, 92, color=GRAY_LIGHT, size=12)

        # Zona de compradores / vendedores
        pygame.draw.line(surface, GRAY_DARK, (400, 85), (400, 385), 1)
        surface.blit(self.sprite_c, (415, 90))
        surface.blit(self.sprite_s, (645, 90))

        # Agentes animados
        for a in self.agentes:
            a.draw(surface)

        # Símbolo "mercado"
        pygame.draw.circle(surface, accent, (self.cx, self.cy), 30, 3)
        text(surface, "$", self.cx - 8, self.cy - 12, color=accent,
             size=22, bold=True)

        # KPIs
        font_kpi = get_font(20, bold=True)
        font_lab = get_font(12)
        kpis = [
            ("TRANSACCIONES", f"{self.transacciones:.1f}", CYAN),
            ("VOLUMEN",       f"${self.vol_total:.0f}",    YELLOW),
            ("SATISFACCIÓN",  f"{self.satisfaccion:.0f}%", GREEN),
        ]
        kx, ky = 60, 380
        for lab, val, col in kpis:
            p2 = Panel(kx, ky, 130, 60, border=col)
            p2.draw(surface)
            surface.blit(font_lab.render(lab, True, GRAY_LIGHT), (kx+6, ky+6))
            surface.blit(font_kpi.render(val, True, col),        (kx+6, ky+28))
            kx += 140

        # Gráfica transacciones
        self.chart_trans.draw(surface)

        # Info
        infos = [
            "► El mercado coordina a compradores y vendedores.",
            "► Las transacciones = mín(Oferta, Demanda).",
            "► Mayor calidad → mayor satisfacción del consumidor.",
        ]
        iy = 240
        for info in infos:
            text(surface, info, 700, iy, color=GRAY_LIGHT, size=12)
            iy += 18
        self.notif.draw(surface)

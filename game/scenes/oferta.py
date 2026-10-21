# ============================================================
#  ESCENA: OFERTA
#  Curva de oferta interactiva. El jugador mueve factores
#  que desplazan la curva (costos, tecnología, insumos).
# ============================================================
import pygame
import math
from game.scenes.base import BaseScene
from game.constants import *
from game.ui import (Slider, Panel, LineChart, Notification,
                     text, get_font)
from game.sprites import sprite_flecha_arriba, sprite_fabrica


class OfertaScene(BaseScene):
    KEY      = "oferta"
    TITLE    = "Oferta"
    SUBTITLE = "Desplaza la curva de oferta modificando sus determinantes"

    def build(self):
        accent = self.accent
        self.sliders = [
            Slider(60, 110, 280, "Costo de Insumos",   0, 100, 40,
                   color=RED,    unit=""),
            Slider(60, 170, 280, "Tecnología",         0, 100, 50,
                   color=CYAN,   unit="%"),
            Slider(60, 230, 280, "Nº Productores",     1,  20,  8,
                   color=GREEN,  unit=""),
            Slider(60, 290, 280, "Expectativas Prec.", 0, 100, 50,
                   color=PURPLE, unit=""),
        ]
        self.chart = LineChart(700, 90, 290, 150, "Oferta Total",
                               color=GREEN)
        self.notif  = Notification()
        self.sprite_arr = sprite_flecha_arriba(color=GREEN)
        self.sprite_fac = sprite_fabrica()
        self._timer = 0
        self.oferta_total = 0
        self.precio_equilibrio = 50

    # Convierte cantidad→px en el gráfico de curva
    def _curve_point(self, precio, desplazamiento, rect):
        """Retorna (x,y) en el canvas del gráfico para (precio, cantidad ofrecida)."""
        q = (precio / 10) * (1 + desplazamiento / 50)
        x = rect.x + 40 + q * 3
        y = rect.y + rect.h - 40 - (precio / 200) * (rect.h - 60)
        return int(x), int(y)

    def handle_event(self, event):
        for s in self.sliders:
            s.handle_event(event)

    def update(self, dt):
        super().update(dt)
        mouse = pygame.mouse.get_pos()
        for s in self.sliders:
            s.update(mouse)
        self._timer += dt
        if self._timer >= 800:
            self._timer = 0
            costo = self.sliders[0].value
            tech  = self.sliders[1].value
            prod  = self.sliders[2].value
            exp   = self.sliders[3].value
            # Oferta sube con tech y productores, baja con costos y con expectativas de precios futuros más altos (retención de inventario hoy)
            self.oferta_total = round(
                max(0, (tech * 0.5 + prod * 5 - costo * 0.4 - exp * 0.25) * 0.8), 1)
            self.chart.push(self.oferta_total)
            if self.oferta_total < 5:
                self.notif.add("⬇ Oferta muy baja: mercado desabastecido", RED)
            elif self.oferta_total > 80:
                self.notif.add("⬆ Alta oferta: posible excedente", GREEN)
        self.notif.update(dt)

    def _draw_curve(self, surface, rect, desp):
        pygame.draw.rect(surface, PANEL_DARK, rect, border_radius=6)
        pygame.draw.rect(surface, GRAY_DARK, rect, 1, border_radius=6)
        # Ejes
        ax = rect.x + 35; ay = rect.y + rect.h - 35
        pygame.draw.line(surface, GRAY, (ax, rect.y+10), (ax, ay), 2)
        pygame.draw.line(surface, GRAY, (ax, ay), (rect.right-10, ay), 2)
        text(surface, "Q", rect.right - 22, ay - 8, GRAY, 12)
        text(surface, "P", ax - 16, rect.y + 6, GRAY, 12)
        text(surface, "Curva de Oferta", rect.x + 40, rect.y + 4, GREEN, 12)

        # Curva base (referencia)
        pts_base = []
        for p in range(10, 200, 8):
            x, y = self._curve_point(p, 50, rect)
            if rect.x < x < rect.right and rect.y < y < rect.bottom:
                pts_base.append((x, y))
        if len(pts_base) >= 2:
            pygame.draw.lines(surface, GRAY_DARK, False, pts_base, 1)

        # Curva actual
        pts = []
        for p in range(10, 200, 8):
            x, y = self._curve_point(p, desp, rect)
            if rect.x < x < rect.right and rect.y < y < rect.bottom:
                pts.append((x, y))
        if len(pts) >= 2:
            pygame.draw.lines(surface, GREEN, False, pts, 3)

        # Etiqueta S
        if pts:
            lx, ly = pts[-1]
            text(surface, "S", lx + 2, ly - 10, GREEN, 14, bold=True)

        # Flecha de desplazamiento
        if desp > 50:
            text(surface, "→", rect.x + 60, rect.centery, GREEN, 18)
        elif desp < 50:
            text(surface, "←", rect.x + 60, rect.centery, RED, 18)

    def draw_content(self, surface):
        accent = self.accent
        p = Panel(40, 85, 330, 275, border=accent)
        p.draw(surface)
        text(surface, "Determinantes de la Oferta", 55, 95,
             color=accent, size=14, bold=True)
        for s in self.sliders:
            s.draw(surface)

        # Curva interactiva
        costo = self.sliders[0].value
        tech  = self.sliders[1].value
        prod  = self.sliders[2].value
        exp   = self.sliders[3].value
        desp  = tech - costo * 0.5 + prod * 2 - exp * 0.3
        curve_rect = pygame.Rect(400, 85, 280, 260)
        self._draw_curve(surface, curve_rect, desp)

        # KPIs
        font_kpi = get_font(22, bold=True)
        font_lab = get_font(13)
        p2 = Panel(60, 400, 160, 65, border=GREEN)
        p2.draw(surface)
        surface.blit(font_lab.render("OFERTA TOTAL", True, GRAY_LIGHT), (68, 408))
        surface.blit(font_kpi.render(f"{max(0,self.oferta_total):.1f} u",
                                     True, GREEN), (68, 430))

        # Sprites integrados en encabezado de panel
        surface.blit(self.sprite_fac, (310, 90))
        surface.blit(self.sprite_arr, (340, 90))

        # Gráfica tendencia
        self.chart.draw(surface)

        # Factores desplazadores
        text(surface, "Factores que aumentan la Oferta:", 400, 260,
             color=GRAY_LIGHT, size=14, bold=True)
        factores = [
            ("✔ Menor costo de insumos", GREEN),
            ("✔ Mayor tecnología",       GREEN),
            ("✔ Más productores",        GREEN),
            ("✗ Expectativa precio alto (retiene inventario)", RED),
        ]
        fy = 282
        for f, col in factores:
            text(surface, f, 408, fy, col, 13)
            fy += 18

        # Info general
        infos = [
            "► La curva S sube cuando los costos bajan o la tech mejora.",
            "► Más productores desplazan la curva a la derecha (↑Q).",
            "► Expectativas de precios futuros afectan oferta actual.",
        ]
        iy = 400
        for info in infos:
            text(surface, info, 400, iy, color=GRAY_LIGHT, size=12)
            iy += 18
        self.notif.draw(surface)

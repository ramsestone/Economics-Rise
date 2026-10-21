# ============================================================
#  ESCENA: EQUILIBRIO
#  Punto de equilibrio oferta-demanda en tiempo real.
#  El jugador mueve ambas curvas y ve cómo el precio/cantidad
#  de equilibrio cambia.
# ============================================================
import pygame
import math
from game.scenes.base import BaseScene
from game.constants import *
from game.ui import (Slider, Panel, LineChart, Notification,
                     text, get_font)
from game.sprites import sprite_balanza


class EquilibrioScene(BaseScene):
    KEY      = "equilibrio"
    TITLE    = "Equilibrio"
    SUBTITLE = "Encuentra el punto donde Oferta = Demanda"

    def build(self):
        accent = self.accent
        self.sliders = [
            Slider(60, 110, 280, "Desplaz. Oferta",   -50, 50, 0,
                   color=GREEN,  unit=""),
            Slider(60, 170, 280, "Desplaz. Demanda",  -50, 50, 0,
                   color=RED,    unit=""),
            Slider(60, 230, 280, "Elasticidad Ofe.",    1, 10, 5,
                   color=CYAN,   unit=""),
            Slider(60, 290, 280, "Elasticidad Dem.",    1, 10, 5,
                   color=PURPLE, unit=""),
        ]
        self.chart_p = LineChart(700, 90,  290, 130, "Precio Eq.",
                                 color=YELLOW)
        self.chart_q = LineChart(700, 240, 290, 130, "Cantidad Eq.",
                                 color=CYAN)
        self.notif  = Notification()
        self.sprite_b = sprite_balanza()
        self._timer = 0
        self.p_eq   = 0.0
        self.q_eq   = 0.0

    def handle_event(self, event):
        for s in self.sliders:
            s.handle_event(event)

    def _supply_q(self, p, desp_s, elast_s):
        """Cantidad ofrecida dado precio p."""
        return max(0, (p / 10) * elast_s + desp_s * 0.5)

    def _demand_q(self, p, desp_d, elast_d):
        """Cantidad demandada dado precio p."""
        return max(0, (20 - p / 8) * elast_d + desp_d * 0.5)

    def _find_equilibrium(self, desp_s, desp_d, elast_s, elast_d):
        """Bisección para encontrar precio de equilibrio."""
        lo, hi = 0.1, 200.0
        for _ in range(40):
            mid = (lo + hi) / 2
            if self._supply_q(mid, desp_s, elast_s) < self._demand_q(mid, desp_d, elast_d):
                lo = mid
            else:
                hi = mid
        p = (lo + hi) / 2
        q = (self._supply_q(p, desp_s, elast_s) +
             self._demand_q(p, desp_d, elast_d)) / 2
        return round(p, 1), round(q, 1)

    def update(self, dt):
        super().update(dt)
        mouse = pygame.mouse.get_pos()
        for s in self.sliders:
            s.update(mouse)
        self._timer += dt
        if self._timer >= 600:
            self._timer = 0
            ds = self.sliders[0].value
            dd = self.sliders[1].value
            es = self.sliders[2].value
            ed = self.sliders[3].value
            self.p_eq, self.q_eq = self._find_equilibrium(ds, dd, es, ed)
            self.chart_p.push(self.p_eq)
            self.chart_q.push(self.q_eq)
            if self.p_eq > 120:
                self.notif.add("💲 Precio de equilibrio muy alto", RED)
            elif self.p_eq < 20:
                self.notif.add("💲 Precio de equilibrio muy bajo", CYAN)
        self.notif.update(dt)

    def _draw_both_curves(self, surface, rect, ds, dd, es, ed):
        """Dibuja oferta y demanda con punto de equilibrio."""
        pygame.draw.rect(surface, PANEL_DARK, rect, border_radius=6)
        pygame.draw.rect(surface, GRAY_DARK, rect, 1, border_radius=6)
        # Ejes
        ax = rect.x + 40; ay = rect.y + rect.h - 35
        pygame.draw.line(surface, GRAY, (ax, rect.y+10), (ax, ay), 2)
        pygame.draw.line(surface, GRAY, (ax, ay), (rect.right - 10, ay), 2)
        text(surface, "Q", rect.right - 22, ay - 8, GRAY, 11)
        text(surface, "P", ax - 14, rect.y + 4, GRAY, 11)

        w = rect.w - 60; h = rect.h - 50
        p_max = 160.0

        def to_px(p, q):
            x = ax + q * 2.5
            y = ay - (p / p_max) * h
            return int(x), int(y)

        # Oferta (pendiente positiva)
        pts_s = []
        for p in range(5, int(p_max), 5):
            q = self._supply_q(p, ds, es)
            x, y = to_px(p, q)
            if rect.x + 40 < x < rect.right - 5 and rect.y < y < ay:
                pts_s.append((x, y))
        if len(pts_s) >= 2:
            pygame.draw.lines(surface, GREEN, False, pts_s, 3)
        if pts_s:
            text(surface, "S", pts_s[-1][0]+2, pts_s[-1][1]-10, GREEN, 12, True)

        # Demanda (pendiente negativa)
        pts_d = []
        for p in range(5, int(p_max), 5):
            q = self._demand_q(p, dd, ed)
            x, y = to_px(p, q)
            if rect.x + 40 < x < rect.right - 5 and rect.y < y < ay:
                pts_d.append((x, y))
        if len(pts_d) >= 2:
            pygame.draw.lines(surface, RED, False, pts_d, 3)
        if pts_d:
            lx, ly = pts_d[-1]
            text(surface, "D", lx+2, ly+2, RED, 12, True)

        # Punto de equilibrio
        eq_x, eq_y = to_px(self.p_eq, self.q_eq)
        if rect.x + 40 < eq_x < rect.right and rect.y < eq_y < ay:
            # Líneas punteadas
            for dash in range(ax, eq_x, 8):
                pygame.draw.line(surface, YELLOW, (dash, eq_y), (min(dash+4, eq_x), eq_y), 1)
            for dash in range(eq_y, ay, 8):
                pygame.draw.line(surface, YELLOW, (eq_x, dash), (eq_x, min(dash+4, ay)), 1)
            pygame.draw.circle(surface, YELLOW, (eq_x, eq_y), 8)
            pygame.draw.circle(surface, WHITE,  (eq_x, eq_y), 4)
        text(surface, "Equilibrio O=D", rect.x + 4, rect.y + 2,
             YELLOW, 10, bold=True)

    def draw_content(self, surface):
        accent = self.accent
        p = Panel(40, 85, 330, 275, border=accent)
        p.draw(surface)
        text(surface, "Ajuste al Equilibrio", 55, 95, color=accent,
             size=14, bold=True)
        for s in self.sliders:
            s.draw(surface)

        ds = self.sliders[0].value
        dd = self.sliders[1].value
        es = self.sliders[2].value
        ed = self.sliders[3].value
        curve_rect = pygame.Rect(400, 85, 280, 270)
        self._draw_both_curves(surface, curve_rect, ds, dd, es, ed)

        # KPIs equilibrio
        font_kpi = get_font(24, bold=True)
        font_lab = get_font(13)
        for i, (lab, val, col) in enumerate([
            ("PRECIO EQ.",   f"${self.p_eq:.1f}", YELLOW),
            ("CANTIDAD EQ.", f"{self.q_eq:.1f} u", CYAN),
        ]):
            kx = 60 + i * 165
            p2 = Panel(kx, 390, 155, 70, border=col)
            p2.draw(surface)
            surface.blit(font_lab.render(lab, True, GRAY_LIGHT), (kx+8, 398))
            surface.blit(font_kpi.render(val, True, col),        (kx+8, 422))

        # Balanza sprite con efecto "equilibrio" integrada en panel izquierdo
        offset = int(math.sin(self.tick / 400) * 3)
        surface.blit(self.sprite_b, (330, 90 + offset))

        self.chart_p.draw(surface)
        self.chart_q.draw(surface)

        infos = [
            "► Equilibrio ocurre donde Oferta = Demanda.",
            "► Shocks desplazan el precio y cantidad (P*, Q*).",
            "► Elasticidad define la sensibilidad al precio.",
        ]
        iy = 365
        for info in infos:
            text(surface, info, 400, iy, color=GRAY_LIGHT, size=11)
            iy += 16
        self.notif.draw(surface)

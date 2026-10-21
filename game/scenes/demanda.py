# ============================================================
#  ESCENA: DEMANDA
#  Curva de demanda interactiva. El jugador controla factores
#  que la desplazan: ingresos, preferencias, bienes sustitutos.
# ============================================================
import pygame
from game.scenes.base import BaseScene
from game.constants import *
from game.ui import (Slider, Panel, LineChart, Notification,
                     text, get_font)
from game.sprites import sprite_flecha_abajo, sprite_consumidor


class DemandaScene(BaseScene):
    KEY      = "demanda"
    TITLE    = "Demanda"
    SUBTITLE = "Desplaza la curva de demanda modificando sus determinantes"

    def build(self):
        accent = self.accent
        self.sliders = [
            Slider(60, 110, 280, "Ingreso del Consumidor", 0, 100, 60,
                   color=YELLOW, unit=""),
            Slider(60, 170, 280, "Preferencias (0-10)",    0,  10,  5,
                   color=PURPLE, unit=""),
            Slider(60, 230, 280, "Precio de Sustitutos",   0, 100, 40,
                   color=CYAN,   unit="$"),
            Slider(60, 290, 280, "Nº Compradores",         1,  50, 20,
                   color=RED,    unit=""),
        ]
        self.chart = LineChart(700, 90, 290, 150, "Demanda Total",
                               color=RED)
        self.notif  = Notification()
        self.sprite_arr = sprite_flecha_abajo(color=RED)
        self.sprite_con = sprite_consumidor()
        self._timer = 0
        self.demanda_total = 0

    def handle_event(self, event):
        for s in self.sliders:
            s.handle_event(event)

    def _curve_point(self, precio, desp, rect):
        """Curva de demanda: pendiente negativa."""
        q = (1 - precio / 200) * (1 + desp / 100)
        q = max(0, q)
        x = rect.x + 40 + q * (rect.w - 60)
        y = rect.y + rect.h - 40 - (precio / 200) * (rect.h - 60)
        return int(x), int(y)

    def update(self, dt):
        super().update(dt)
        mouse = pygame.mouse.get_pos()
        for s in self.sliders:
            s.update(mouse)
        self._timer += dt
        if self._timer >= 800:
            self._timer = 0
            ing   = self.sliders[0].value
            pref  = self.sliders[1].value
            sust  = self.sliders[2].value
            comp  = self.sliders[3].value
            # Demanda sube con ingreso, preferencias, sustitutos caros, más compradores
            self.demanda_total = round(
                ing * 0.4 + pref * 5 + sust * 0.3 + comp * 1.2, 1)
            self.chart.push(self.demanda_total)
            if self.demanda_total < 15:
                self.notif.add("⬇ Demanda muy baja", RED)
            elif self.demanda_total > 120:
                self.notif.add("⬆ Alta demanda: posible escasez", YELLOW)
        self.notif.update(dt)

    def _draw_curve(self, surface, rect, desp):
        pygame.draw.rect(surface, PANEL_DARK, rect, border_radius=6)
        pygame.draw.rect(surface, GRAY_DARK, rect, 1, border_radius=6)
        ax = rect.x + 35; ay = rect.y + rect.h - 35
        pygame.draw.line(surface, GRAY, (ax, rect.y+10), (ax, ay), 2)
        pygame.draw.line(surface, GRAY, (ax, ay), (rect.right-10, ay), 2)
        text(surface, "Q", rect.right - 22, ay - 8, GRAY, 12)
        text(surface, "P", ax - 16, rect.y + 6, GRAY, 12)
        text(surface, "Curva de Demanda", rect.x + 40, rect.y + 4, RED, 12)

        # Curva base
        pts_base = []
        for p in range(10, 190, 8):
            x, y = self._curve_point(p, 50, rect)
            if rect.x < x < rect.right and rect.y < y < rect.bottom:
                pts_base.append((x, y))
        if len(pts_base) >= 2:
            pygame.draw.lines(surface, GRAY_DARK, False, pts_base, 1)

        # Curva actual
        pts = []
        for p in range(10, 190, 8):
            x, y = self._curve_point(p, desp, rect)
            if rect.x < x < rect.right and rect.y < y < rect.bottom:
                pts.append((x, y))
        if len(pts) >= 2:
            pygame.draw.lines(surface, RED, False, pts, 3)

        if pts:
            lx, ly = pts[-1]
            text(surface, "D", lx - 16, ly + 2, RED, 14, bold=True)

        if desp > 50:
            text(surface, "→", rect.x + 80, rect.centery, RED, 18)
        elif desp < 50:
            text(surface, "←", rect.x + 80, rect.centery, GRAY, 18)

    def draw_content(self, surface):
        accent = self.accent
        p = Panel(40, 85, 330, 275, border=accent)
        p.draw(surface)
        text(surface, "Determinantes de la Demanda", 55, 95,
             color=accent, size=14, bold=True)
        for s in self.sliders:
            s.draw(surface)

        # Desplazamiento de la curva
        ing  = self.sliders[0].value
        pref = self.sliders[1].value
        sust = self.sliders[2].value
        comp = self.sliders[3].value
        desp = ing * 0.5 + pref * 5 + sust * 0.2 + comp * 0.8

        curve_rect = pygame.Rect(400, 85, 280, 260)
        self._draw_curve(surface, curve_rect, desp)

        # KPI
        font_kpi = get_font(22, bold=True)
        font_lab = get_font(13)
        p2 = Panel(60, 400, 160, 65, border=RED)
        p2.draw(surface)
        surface.blit(font_lab.render("DEMANDA TOTAL", True, GRAY_LIGHT), (68, 408))
        surface.blit(font_kpi.render(f"{self.demanda_total:.1f} u",
                                     True, RED), (68, 430))

        # Sprites integrados en encabezado de panel
        surface.blit(self.sprite_con, (310, 90))
        surface.blit(self.sprite_arr, (340, 90))

        self.chart.draw(surface)

        text(surface, "Factores que aumentan la Demanda:", 400, 260,
             color=GRAY_LIGHT, size=14, bold=True)
        factores = [
            ("✔ Mayor ingreso del consumidor", YELLOW),
            ("✔ Mayor preferencia por el bien",  PURPLE),
            ("✔ Precio alto de sustitutos",      CYAN),
            ("✔ Mayor número de compradores",    RED),
        ]
        fy = 282
        for f, col in factores:
            text(surface, f, 408, fy, col, 13)
            fy += 18

        infos = [
            "► Ley de demanda: precio ↑ → cantidad demandada ↓.",
            "► Desplazamiento D ≠ movimiento sobre la curva.",
            "► Bienes inferiores: demanda cae cuando el ingreso sube.",
        ]
        iy = 400
        for info in infos:
            text(surface, info, 400, iy, color=GRAY_LIGHT, size=12)
            iy += 18
        self.notif.draw(surface)

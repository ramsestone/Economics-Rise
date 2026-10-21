# ============================================================
#  ESCENA: ESCASEZ
#  El jugador gestiona recursos limitados: asignarlos entre
#  necesidades que compiten. Muestra costo de oportunidad.
# ============================================================
import pygame
import math
import random
from game.scenes.base import BaseScene
from game.constants import *
from game.ui import (Slider, Panel, LineChart, Notification,
                     Button, ProgressBar, text, get_font)
from game.sprites import sprite_caja_vacia


class EscasezScene(BaseScene):
    KEY      = "escasez"
    TITLE    = "Escasez"
    SUBTITLE = "Administra recursos limitados: toda elección implica un costo de oportunidad"

    def build(self):
        accent = self.accent
        self.RECURSOS_MAX = 100
        self.sliders = [
            Slider(60, 110, 280, "Recursos → Alimentos", 0, 100, 30,
                   color=(80, 200, 80),   unit="%"),
            Slider(60, 170, 280, "Recursos → Salud",     0, 100, 25,
                   color=(80, 160, 255),  unit="%"),
            Slider(60, 230, 280, "Recursos → Educación", 0, 100, 25,
                   color=(220, 180, 60),  unit="%"),
            Slider(60, 290, 280, "Recursos → Vivienda",  0, 100, 20,
                   color=(200, 100, 80),  unit="%"),
        ]
        self.btn_reset = Button(60, 380, 120, 34, "Resetear", GRAY)
        self.btn_crisis= Button(195, 380, 140, 34, "¡Crisis!", RED)
        self.notif   = Notification()
        self.sprite_c = sprite_caja_vacia()
        self._timer   = 0
        self.bienestar    = 50.0
        self.total_usado  = 0
        self.costo_op     = 0.0
        self.crisis_mode  = False
        self.crisis_timer = 0

        self.bars = [
            ProgressBar(400, 100 + i*55, 260, 26,
                        lab, col, max_val=100)
            for i, (lab, col) in enumerate([
                ("Alimentos", (80, 200, 80)),
                ("Salud",     (80, 160, 255)),
                ("Educación", (220, 180, 60)),
                ("Vivienda",  (200, 100, 80)),
            ])
        ]
        self.chart_bien = LineChart(700, 90, 290, 150, "Bienestar Social",
                                    color=CYAN)

    def handle_event(self, event):
        for s in self.sliders:
            s.handle_event(event)
        if self.btn_reset.is_clicked(event):
            vals = [25, 25, 25, 25]
            for s, v in zip(self.sliders, vals):
                s.value = v
            self.notif.add("🔄 Recursos redistribuidos equitativamente", GRAY_LIGHT)
        if self.btn_crisis.is_clicked(event):
            self.crisis_mode  = True
            self.crisis_timer = 8000
            self.RECURSOS_MAX = 50
            self.notif.add("🌪 ¡Crisis! Recursos reducidos a la mitad", RED)

    def update(self, dt):
        super().update(dt)
        mouse = pygame.mouse.get_pos()
        for s in self.sliders:
            s.update(mouse)
        self.btn_reset.update(mouse)
        self.btn_crisis.update(mouse)
        if self.crisis_timer > 0:
            self.crisis_timer -= dt
            if self.crisis_timer <= 0:
                self.crisis_mode  = False
                self.RECURSOS_MAX = 100
                self.notif.add("✔ Crisis superada. Recursos normales.", GREEN)
        self._timer += dt
        if self._timer >= 700:
            self._timer = 0
            vals = [s.value for s in self.sliders]
            self.total_usado = sum(vals)
            # Si supera máximo, hay sobreasignación imposible
            extra = max(0, self.total_usado - self.RECURSOS_MAX)
            # Bienestar: función de qué tan cubierta queda cada necesidad
            sat = [min(v, self.RECURSOS_MAX * 0.35) / (self.RECURSOS_MAX * 0.35)
                   for v in vals]
            self.bienestar = round(sum(sat) / 4 * 100 * (1 - extra / 200), 1)
            self.bienestar = max(0, min(100, self.bienestar))
            # Costo de oportunidad: recursos y bienestar sacrificados en las alternativas desatendidas
            # al desviar presupuesto hacia el sector más favorecido
            base_equilibrada = self.RECURSOS_MAX / 4.0
            sorted_vals = sorted(vals, reverse=True)
            # Mide la suma de lo que los demás sectores pierden por debajo del nivel óptimo equilibrado
            sacrificio_alternativas = sum(max(0.0, base_equilibrada - v) for v in sorted_vals[1:])
            self.costo_op = round(sacrificio_alternativas, 1)
            for bar, val in zip(self.bars, vals):
                bar.value = min(val, self.RECURSOS_MAX)
            self.chart_bien.push(self.bienestar)
            if self.total_usado > self.RECURSOS_MAX + 5:
                self.notif.add(f"⚠ Sobreasignación: {self.total_usado:.0f}% > {self.RECURSOS_MAX}%!", RED)
            if self.bienestar < 30:
                self.notif.add("😟 Bienestar social crítico", RED)
        self.notif.update(dt)

    def _draw_ppf(self, surface, rect):
        """Frontera de Posibilidades de Producción simplificada."""
        pygame.draw.rect(surface, PANEL_DARK, rect, border_radius=6)
        pygame.draw.rect(surface, GRAY_DARK, rect, 1, border_radius=6)
        text(surface, "FPP (2 sectores)", rect.x + 4, rect.y + 2, ORANGE, 10)
        ax = rect.x + 30; ay = rect.y + rect.h - 25
        pygame.draw.line(surface, GRAY, (ax, rect.y+10), (ax, ay), 2)
        pygame.draw.line(surface, GRAY, (ax, ay), (rect.right - 10, ay), 2)
        text(surface, "X", rect.right-18, ay-8, GRAY, 10)
        text(surface, "Y", ax-14, rect.y+4, GRAY, 10)
        # PPF curva (forma de cuarto de elipse)
        pts = []
        w = rect.right - 10 - ax; h = ay - (rect.y + 10)
        for i in range(50):
            t = i / 49 * math.pi / 2
            x = ax + w * math.sin(t)
            y = ay - h * math.cos(t)
            pts.append((int(x), int(y)))
        if len(pts) >= 2:
            pygame.draw.lines(surface, ORANGE, False, pts, 2)
        # Punto actual
        v0 = min(1.0, self.sliders[0].value / 100)
        v1 = min(1.0, self.sliders[1].value / 100)
        total = v0 + v1
        if total > 0:
            ratio = v0 / total
            px = ax + w * ratio
            py = ay - h * (1 - ratio)
            inside = v0 + v1 <= 1.0
            col = GREEN if inside else RED
            pygame.draw.circle(surface, col, (int(px), int(py)), 6)

    def draw_content(self, surface):
        accent = self.accent
        p = Panel(40, 85, 330, 295, border=accent)
        p.draw(surface)
        text(surface, "Asignación de Recursos Escasos", 55, 95,
             color=accent, size=13, bold=True)
        for s in self.sliders:
            s.draw(surface)
        self.btn_reset.draw(surface)
        self.btn_crisis.draw(surface)

        # Indicador de recursos usados
        usado_col = RED if self.total_usado > self.RECURSOS_MAX else GREEN
        text(surface, f"Recursos usados: {self.total_usado:.0f}% / {self.RECURSOS_MAX}%",
             60, 425, color=usado_col, size=14, bold=True)

        # Crisis overlay
        if self.crisis_mode:
            font_c = get_font(18, bold=True)
            t = font_c.render("⚡ MODO CRISIS ACTIVO", True, RED)
            surface.blit(t, (60, 450))

        # Barras de sectores
        for bar in self.bars:
            bar.draw(surface)

        # FPP
        ppf_rect = pygame.Rect(400, 240, 180, 150)
        self._draw_ppf(surface, ppf_rect)

        # KPIs
        font_kpi = get_font(20, bold=True)
        font_lab = get_font(12)
        kpis = [
            ("BIENESTAR",   f"{self.bienestar:.0f}%",
             GREEN if self.bienestar > 60 else (YELLOW if self.bienestar > 30 else RED)),
            ("COSTO OPT.", f"{self.costo_op:.0f}%", ORANGE),
        ]
        kx = 400
        for lab, val, col in kpis:
            p2 = Panel(kx, 405, 140, 60, border=col)
            p2.draw(surface)
            surface.blit(font_lab.render(lab, True, GRAY_LIGHT), (kx+6, 413))
            surface.blit(font_kpi.render(val, True, col),        (kx+6, 435))
            kx += 155

        surface.blit(self.sprite_c, (330, 90))
        self.chart_bien.draw(surface)

        infos = [
            "► Escasez: los recursos son limitados, las necesidades infinitas.",
            "► Costo de oportunidad: lo que se sacrifica al elegir algo.",
            "► FPP: frontera de posibilidades de producción.",
            "► Sobreasignar = imposible (fuera de la FPP).",
        ]
        iy = 480
        for info in infos:
            text(surface, info, 400, iy, color=GRAY_LIGHT, size=11)
            iy += 16
        self.notif.draw(surface)

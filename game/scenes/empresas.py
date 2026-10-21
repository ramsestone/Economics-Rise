# ============================================================
#  ESCENA: EMPRESAS
#  Gestiona ingresos, costos fijos, costos variables, utilidad
# ============================================================
import pygame
import math
from game.scenes.base import BaseScene
from game.constants import *
from game.ui import (Slider, Panel, LineChart, ProgressBar,
                     Notification, Button, text, get_font)
from game.sprites import sprite_empresa


class EmpresasScene(BaseScene):
    KEY      = "empresas"
    TITLE    = "Empresas"
    SUBTITLE = "Administra los recursos y maximiza la utilidad empresarial"

    def build(self):
        accent = self.accent
        self.sliders = [
            Slider(60, 110, 280, "Precio de Venta ($)",  5, 200, 80,
                   color=GREEN,  unit=""),
            Slider(60, 170, 280, "Unidades Vendidas",    0, 500, 150,
                   color=CYAN,   unit=" u"),
            Slider(60, 230, 280, "Costos Fijos ($)",    10, 5000, 2000,
                   color=RED,    unit=""),
            Slider(60, 290, 280, "Costo Variable/u ($)", 1, 100,  30,
                   color=ORANGE, unit=""),
        ]
        self.btn_invest = Button(60, 380, 130, 36, "Invertir +$500",
                                 color=PURPLE)
        self.btn_cut    = Button(210, 380, 130, 36, "Recortar costos",
                                 color=RED)
        self.chart_ut = LineChart(400, 90, 380, 150, "Utilidad Neta ($)",
                                  color=GREEN)
        self.chart_mg = LineChart(400, 260, 380, 130, "Margen (%)",
                                  color=CYAN)
        self.notif   = Notification()
        self.sprite  = sprite_empresa()
        self._timer  = 0
        self.ingresos = 0
        self.costos   = 0
        self.utilidad = 0
        self.margen   = 0
        self.inversion_bonus = 0

    def handle_event(self, event):
        for s in self.sliders:
            s.handle_event(event)
        if self.btn_invest.is_clicked(event):
            self.sliders[3].value = max(1, self.sliders[3].value - 6)
            self.notif.add("📈 Inversión en eficiencia: costo variable unitario -$6", PURPLE)
        if self.btn_cut.is_clicked(event):
            self.sliders[2].value = max(10, self.sliders[2].value * 0.85)
            self.notif.add("✂ Costos fijos reducidos 15%", ORANGE)

    def update(self, dt):
        super().update(dt)
        mouse = pygame.mouse.get_pos()
        for s in self.sliders:
            s.update(mouse)
        self.btn_invest.update(mouse)
        self.btn_cut.update(mouse)
        self._timer += dt
        if self._timer >= 800:
            self._timer = 0
            precio = self.sliders[0].value
            unid   = self.sliders[1].value
            cf     = self.sliders[2].value
            cv     = self.sliders[3].value
            # Principio contable: Ingresos = Precio * Unidades
            self.ingresos = round(precio * unid, 1)
            # Costo Total = Costos Fijos + (Costo Variable Unitario * Unidades)
            self.costos   = round(cf + cv * unid, 1)
            self.utilidad = round(self.ingresos - self.costos, 1)
            self.margen   = round((self.utilidad / max(1.0, self.ingresos)) * 100, 1)
            self.chart_ut.push(self.utilidad)
            self.chart_mg.push(self.margen)
            if self.utilidad < 0:
                self.notif.add("⚠ ¡Empresa en pérdida!", RED)
            elif self.margen > 30:
                self.notif.add("🏆 Excelente margen empresarial!", GREEN)
        self.notif.update(dt)

    def draw_content(self, surface):
        accent = self.accent
        p = Panel(40, 85, 330, 280, border=accent)
        p.draw(surface)
        text(surface, "Parámetros Financieros", 55, 95,
             color=accent, size=14, bold=True)
        for s in self.sliders:
            s.draw(surface)
        self.btn_invest.draw(surface)
        self.btn_cut.draw(surface)

        font_kpi = get_font(20, bold=True)
        font_lab = get_font(12)
        kpis = [
            ("INGRESOS",  f"${self.ingresos:.0f}",  GREEN),
            ("COSTOS",    f"${self.costos:.0f}",    RED),
            ("UTILIDAD",  f"${self.utilidad:.0f}",  YELLOW if self.utilidad>=0 else RED),
            ("MARGEN",    f"{self.margen:.1f}%",    CYAN),
        ]
        kx, ky = 60, 440
        for lab, val, col in kpis:
            p2 = Panel(kx, ky, 120, 60, border=col)
            p2.draw(surface)
            surface.blit(font_lab.render(lab, True, GRAY_LIGHT), (kx+6, ky+6))
            surface.blit(font_kpi.render(val, True, col),        (kx+6, ky+28))
            kx += 130
            if kx > 400:
                kx, ky = 60, ky + 68

        # Sprite empresa integrado en panel izquierdo
        surface.blit(self.sprite, (330, 90))

        # Gráficas
        self.chart_ut.draw(surface)
        self.chart_mg.draw(surface)

        # Semáforo de salud
        salud_y = 410
        text(surface, "Salud financiera:", 400, salud_y, color=GRAY_LIGHT, size=14)
        if self.utilidad > 500:
            col_sem = GREEN;  label_sem = "EXCELENTE"
        elif self.utilidad > 0:
            col_sem = YELLOW; label_sem = "POSITIVA"
        else:
            col_sem = RED;    label_sem = "CRÍTICA"
        pygame.draw.circle(surface, col_sem, (590, salud_y + 8), 10)
        text(surface, label_sem, 608, salud_y, color=col_sem, size=14, bold=True)

        infos = [
            "► Ingresos = Precio × Unidades vendidas",
            "► Utilidad = Ingresos − (Costos fijos + Costos variables × u)",
            "► Margen = Utilidad / Ingresos × 100%",
        ]
        iy = 440
        for info in infos:
            text(surface, info, 400, iy, color=GRAY_LIGHT, size=12)
            iy += 18

        self.notif.draw(surface)

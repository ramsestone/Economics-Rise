# ============================================================
#  ESCENA: GOBIERNO
#  El jugador establece políticas: gasto público, impuestos,
#  subsidios. Resultado: PIB, desempleo, déficit.
# ============================================================
import pygame
import math
from game.scenes.base import BaseScene
from game.constants import *
from game.ui import (Slider, Panel, LineChart, ProgressBar,
                     Notification, Button, text, get_font)
from game.sprites import sprite_gobierno


class GobiernoScene(BaseScene):
    KEY      = "gobierno"
    TITLE    = "Gobierno"
    SUBTITLE = "Define políticas públicas: gasto, impuestos y subsidios"

    def build(self):
        accent = self.accent
        self.sliders = [
            Slider(60, 110, 280, "Gasto Público (%PIB)", 5, 60, 25,
                   color=PURPLE, unit="%"),
            Slider(60, 170, 280, "Tasa de Impuesto",    10, 70, 30,
                   color=RED,    unit="%"),
            Slider(60, 230, 280, "Subsidios",            0, 50, 10,
                   color=GREEN,  unit="%"),
            Slider(60, 290, 280, "Inversión en Edu.",    0, 40, 15,
                   color=CYAN,   unit="%"),
        ]
        self.btn_estimulo = Button(60, 380, 150, 36, "Estímulo Fiscal",
                                   color=GREEN)
        self.btn_austeridad = Button(225, 380, 150, 36, "Austeridad",
                                     color=RED)
        self.chart_pib  = LineChart(400, 90,  380, 130, "PIB (índice)",
                                    color=PURPLE)
        self.chart_desemp = LineChart(400, 240, 380, 130, "Desempleo (%)",
                                      color=RED)
        self.notif  = Notification()
        self.sprite = sprite_gobierno()
        self._timer = 0
        self.pib        = 100.0
        self.desempleo  = 5.0
        self.deficit    = 0.0
        self.aprobacion = 50.0

    def handle_event(self, event):
        for s in self.sliders:
            s.handle_event(event)
        if self.btn_estimulo.is_clicked(event):
            self.sliders[0].value = min(60, self.sliders[0].value + 10)
            self.notif.add("💰 Estímulo fiscal activado (+gasto)", GREEN)
        if self.btn_austeridad.is_clicked(event):
            self.sliders[0].value = max(5, self.sliders[0].value - 10)
            self.sliders[1].value = min(70, self.sliders[1].value + 5)
            self.notif.add("✂ Austeridad aplicada (-gasto, +impuesto)", RED)

    def update(self, dt):
        super().update(dt)
        mouse = pygame.mouse.get_pos()
        for s in self.sliders:
            s.update(mouse)
        self.btn_estimulo.update(mouse)
        self.btn_austeridad.update(mouse)
        self._timer += dt
        if self._timer >= 900:
            self._timer = 0
            gp   = self.sliders[0].value
            imp  = self.sliders[1].value
            sub  = self.sliders[2].value
            edu  = self.sliders[3].value
            # PIB sube con gasto/subsidios/edu, baja con impuestos altos
            delta_pib = (gp * 0.4 + sub * 0.3 + edu * 0.5 - imp * 0.6) * 0.1
            self.pib = max(50, min(200, self.pib + delta_pib))
            # Desempleo baja con gasto público
            self.desempleo = max(1, min(30, 25 - gp * 0.4 + imp * 0.15 - sub * 0.1))
            # Déficit = (gasto público + subsidios + inversión educación) - ingresos por impuesto
            ingresos_imp = imp * 2.0
            self.deficit = round(gp + sub + edu - ingresos_imp, 1)
            # Aprobación ciudadana: premia bienestar y educación, penaliza impuestos y déficit descontrolado
            castigo_deficit = max(0.0, self.deficit - 5.0) * 0.85
            self.aprobacion = max(0, min(100, 50 + sub * 0.8 - imp * 0.45 + edu * 0.65 - castigo_deficit))
            self.chart_pib.push(self.pib)
            self.chart_desemp.push(self.desempleo)
            if self.deficit > 20:
                self.notif.add("⚠ ¡Déficit fiscal elevado!", RED)
            if self.desempleo < 3:
                self.notif.add("✔ ¡Pleno empleo alcanzado!", GREEN)
        self.notif.update(dt)

    def draw_content(self, surface):
        accent = self.accent
        p = Panel(40, 85, 330, 290, border=accent)
        p.draw(surface)
        text(surface, "Política Económica", 55, 95, color=accent, size=14, bold=True)
        for s in self.sliders:
            s.draw(surface)
        self.btn_estimulo.draw(surface)
        self.btn_austeridad.draw(surface)

        # KPIs
        font_kpi = get_font(20, bold=True)
        font_lab = get_font(12)
        kpis = [
            ("PIB",        f"{self.pib:.1f}",      PURPLE),
            ("DESEMPLEO",  f"{self.desempleo:.1f}%", RED),
            ("DÉFICIT",    f"{self.deficit:.1f}%",
             RED if self.deficit > 5 else GREEN),
            ("APROBACIÓN", f"{self.aprobacion:.0f}%", YELLOW),
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

        # Sprite gobierno integrado en panel izquierdo
        surface.blit(self.sprite, (330, 90))

        self.chart_pib.draw(surface)
        self.chart_desemp.draw(surface)

        infos = [
            "► Gasto Público impulsa el PIB (multiplicador fiscal).",
            "► Impuestos altos reducen consumo e inversión.",
            "► Subsidios sostienen empleo y producción.",
            "► Educación mejora productividad a largo plazo.",
        ]
        iy = 390
        for info in infos:
            text(surface, info, 400, iy, color=GRAY_LIGHT, size=13)
            iy += 20
        self.notif.draw(surface)

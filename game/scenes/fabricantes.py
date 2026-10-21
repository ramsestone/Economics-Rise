# ============================================================
#  ESCENA: FABRICANTES
#  El jugador controla: materias primas, trabajadores, tecnología
#  Resultado: producción y ganancia.
# ============================================================
import pygame
import math
from game.scenes.base import BaseScene
from game.constants import *
from game.ui import (Slider, Panel, LineChart, ProgressBar,
                     Notification, text, get_font)
from game.sprites import sprite_fabricante, sprite_fabrica


class FabricantesScene(BaseScene):
    KEY      = "fabricantes"
    TITLE    = "Fabricantes"
    SUBTITLE = "Controla la producción: materias primas, mano de obra y tecnología"

    def build(self):
        accent = self.accent
        self.sliders = [
            Slider(60, 110, 280, "Materias Primas", 0, 100, 50,
                   color=GREEN, unit=" ton"),
            Slider(60, 170, 280, "Trabajadores",    0, 100, 40,
                   color=CYAN,  unit=" ops"),
            Slider(60, 230, 280, "Tecnología",      0, 100, 30,
                   color=PURPLE, unit="%"),
        ]
        self.chart_prod  = LineChart(400, 90, 380, 130, "Producción",
                                     color=GREEN)
        self.chart_ganan = LineChart(400, 240, 380, 130, "Ganancia ($)",
                                     color=YELLOW)
        self.notif = Notification()
        self.sprite_fab = sprite_fabricante()
        self.sprite_fac = sprite_fabrica()
        self._timer = 0
        self.produccion = 0
        self.ganancia   = 0

    def handle_event(self, event):
        for s in self.sliders:
            s.handle_event(event)

    def update(self, dt):
        super().update(dt)
        for s in self.sliders:
            s.update(pygame.mouse.get_pos())
        self._timer += dt
        if self._timer >= 800:
            self._timer = 0
            mp  = self.sliders[0].value
            trab = self.sliders[1].value
            tech = self.sliders[2].value
            # Función de producción Cobb-Douglas: Y = A(Tech) * MP^α * L^β (α+β = 0.9, rendimientos decrecientes a escala)
            a_tech = 1.0 + (tech / 35.0)
            self.produccion = round((mp ** 0.45) * (trab ** 0.45) * a_tech * 1.6, 1) if (mp > 0 and trab > 0) else 0.0
            costo = mp * 1.2 + trab * 0.8
            self.ganancia = round(self.produccion * 3.5 - costo, 1)
            self.chart_prod.push(self.produccion)
            self.chart_ganan.push(self.ganancia)
            if self.ganancia < 0:
                self.notif.add("⚠ ¡Producción con pérdidas!", RED)
            elif self.ganancia > 200:
                self.notif.add("✔ Producción muy rentable!", GREEN)
        self.notif.update(dt)

    def draw_content(self, surface):
        accent = self.accent
        # Panel izquierdo
        p = Panel(40, 85, 330, 265, border=accent)
        p.draw(surface)
        text(surface, "Variables de Producción", 55, 95,
             color=accent, size=14, bold=True)
        for s in self.sliders:
            s.draw(surface)

        # KPIs
        font_kpi = get_font(22, bold=True)
        font_lab = get_font(13)

        kpi_x = 60
        kpi_y = 310

        labels = [
            ("PRODUCCIÓN", f"{self.produccion:.1f} u", GREEN),
            ("GANANCIA",   f"${self.ganancia:.1f}", YELLOW if self.ganancia >= 0 else RED),
        ]
        for lab, val, col in labels:
            p2 = Panel(kpi_x, kpi_y, 145, 65, border=col)
            p2.draw(surface)
            lbl = font_lab.render(lab, True, GRAY_LIGHT)
            v   = font_kpi.render(val, True, col)
            surface.blit(lbl, (kpi_x + 8, kpi_y + 6))
            surface.blit(v,   (kpi_x + 8, kpi_y + 28))
            kpi_x += 165

        # Sprites integrados en el encabezado del panel izquierdo
        surface.blit(self.sprite_fab, (305, 90))
        surface.blit(self.sprite_fac, (335, 90))

        # Gráficas
        self.chart_prod.draw(surface)
        self.chart_ganan.draw(surface)

        # Explicación
        infos = [
            "► Materias Primas: insumo principal de manufactura.",
            "► Trabajadores: mano de obra que transforma los insumos.",
            "► Tecnología: multiplica la eficiencia del proceso.",
            "► Producción = f(MP, Trab, Tech)  [Cobb-Douglas]",
        ]
        iy = 400
        for info in infos:
            text(surface, info, 400, iy, color=GRAY_LIGHT, size=13)
            iy += 20

        self.notif.draw(surface)

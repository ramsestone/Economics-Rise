# ============================================================
#  ESCENA: CONSUMIDORES
#  El jugador controla: presupuesto, precio del bien y preferencias
#  Resultado: cantidad demandada y utilidad.
# ============================================================
import pygame
import math
from game.scenes.base import BaseScene
from game.constants import *
from game.ui import (Slider, Panel, LineChart, ProgressBar,
                     Notification, text, get_font)
from game.sprites import sprite_consumidor, sprite_moneda


class ConsumidoresScene(BaseScene):
    KEY      = "consumidores"
    TITLE    = "Consumidores"
    SUBTITLE = "Gestiona el presupuesto y analiza el comportamiento de compra"

    def build(self):
        accent = self.accent
        self.sliders = [
            Slider(60, 110, 280, "Presupuesto ($)",  10, 500, 200,
                   color=YELLOW, unit=""),
            Slider(60, 170, 280, "Precio del Bien",   1, 100,  30,
                   color=RED,    unit="$"),
            Slider(60, 230, 280, "Preferencia (0-10)", 0, 10, 5,
                   color=PURPLE, unit=""),
            Slider(60, 290, 280, "Bienes Sustitutos",  0, 10, 3,
                   color=CYAN,   unit=""),
        ]
        self.chart = LineChart(400, 90, 380, 150, "Cantidad Demandada",
                               color=YELLOW)
        self.chart_ut = LineChart(400, 260, 380, 130, "Utilidad Total",
                                  color=PURPLE)
        self.notif = Notification()
        self.sprite_c = sprite_consumidor()
        self.sprite_m = sprite_moneda()
        self._timer = 0
        self.cantidad  = 0
        self.utilidad  = 0
        self.bienes_com = []   # lista de artículos "comprados"

    def handle_event(self, event):
        for s in self.sliders:
            s.handle_event(event)

    def update(self, dt):
        super().update(dt)
        for s in self.sliders:
            s.update(pygame.mouse.get_pos())
        self._timer += dt
        if self._timer >= 700:
            self._timer = 0
            pres  = self.sliders[0].value
            precio = max(1, self.sliders[1].value)
            pref  = self.sliders[2].value
            sust  = self.sliders[3].value
            # Cantidad adquirida según restricción presupuestaria, preferencia y sustitutos
            q_max = pres / precio
            self.cantidad = round(max(0.0, q_max * (pref / 10.0) * (1.0 - sust * 0.05)), 1)
            # Función de Utilidad con rendimientos marginales decrecientes (U' > 0, U'' < 0)
            # Cada unidad extra aporta menos satisfacción que la anterior
            self.utilidad = round(24.0 * (pref + 1.5) * math.sqrt(self.cantidad), 1)
            self.chart.push(self.cantidad)
            self.chart_ut.push(self.utilidad)
            if self.cantidad < 1:
                self.notif.add("❌ ¡Presupuesto insuficiente para comprar!", RED)
            elif self.cantidad > 15:
                self.notif.add("🛒 ¡Consumo elevado!", YELLOW)
        self.notif.update(dt)

    def draw_content(self, surface):
        accent = self.accent
        p = Panel(40, 85, 330, 310, border=accent)
        p.draw(surface)
        text(surface, "Variables del Consumidor", 55, 95,
             color=accent, size=14, bold=True)
        for s in self.sliders:
            s.draw(surface)

        # KPIs
        font_kpi = get_font(22, bold=True)
        font_lab = get_font(13)
        kpi_data = [
            ("CANTIDAD", f"{self.cantidad:.1f} u", YELLOW),
            ("UTILIDAD", f"{self.utilidad:.1f}",   PURPLE),
        ]
        kx = 60
        for lab, val, col in kpi_data:
            p2 = Panel(kx, 420, 145, 65, border=col)
            p2.draw(surface)
            surface.blit(font_lab.render(lab, True, GRAY_LIGHT), (kx+8, 428))
            surface.blit(font_kpi.render(val, True, col),        (kx+8, 450))
            kx += 165

        # Sprite integrado en el panel izquierdo
        surface.blit(self.sprite_c, (330, 90))

        # Carrito visual de compra
        cant_vis = min(int(self.cantidad), 12)
        for i in range(cant_vis):
            cx = 415 + (i % 6) * 24
            cy = 420 + (i // 6) * 24
            pygame.draw.rect(surface, YELLOW, (cx, cy, 16, 16), border_radius=3)
            pygame.draw.rect(surface, YELLOW_DARK, (cx, cy, 16, 16), 1, border_radius=3)

        # Gráficas
        self.chart.draw(surface)
        self.chart_ut.draw(surface)

        # Ley de demanda info
        infos = [
            "► Ley de Demanda: a mayor precio → menor cantidad demandada.",
            "► Bienes sustitutos reducen el consumo del bien original.",
            "► Preferencia alta aumenta la disposición a pagar.",
            "► Utilidad marginal: cada unidad extra da menos satisfacción.",
        ]
        iy = 405
        for info in infos:
            text(surface, info, 400, iy, color=GRAY_LIGHT, size=13)
            iy += 20

        self.notif.draw(surface)

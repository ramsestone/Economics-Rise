# ============================================================
#  ESCENA: IMPUESTOS
#  El jugador fija tasas de impuesto y observa la carga fiscal,
#  recaudación y efecto sobre el bienestar (peso muerto).
# ============================================================
import pygame
import math
from game.scenes.base import BaseScene
from game.constants import *
from game.ui import (Slider, Panel, LineChart, Notification,
                     Button, text, get_font, ProgressBar)
from game.sprites import sprite_recibo, sprite_gobierno


class ImpuestosScene(BaseScene):
    KEY      = "impuestos"
    TITLE    = "Impuestos"
    SUBTITLE = "Fija tasas impositivas y observa su efecto en la economía"

    def build(self):
        accent = self.accent
        self.sliders = [
            Slider(60, 110, 280, "ISR – Ingreso (%)",      0, 60, 25,
                   color=RED,    unit="%"),
            Slider(60, 170, 280, "IVA – Consumo (%)",      0, 30, 16,
                   color=ORANGE, unit="%"),
            Slider(60, 230, 280, "Imp. Empresarial (%)",   0, 50, 20,
                   color=PURPLE, unit="%"),
            Slider(60, 290, 280, "Actividad Económica",    0, 100, 70,
                   color=GREEN,  unit=""),
        ]
        self.btn_reform   = Button(60, 370, 140, 34, "Reforma fiscal", PURPLE)
        self.btn_exento   = Button(215, 370, 140, 34, "Exención PyME",  GREEN)
        self.bar_recaud   = ProgressBar(400, 88, 260, 28, "Recaudación",
                                        color=ORANGE, max_val=5000)
        self.bar_bienestar= ProgressBar(400, 128, 260, 28, "Bienestar",
                                         color=GREEN, max_val=100)
        self.chart = LineChart(700, 90, 290, 150, "Recaudación ($)",
                               color=ORANGE)
        self.notif  = Notification()
        self.sprite_rec = sprite_recibo()
        self.sprite_gov = sprite_gobierno()
        self._timer = 0
        self.recaudacion = 0
        self.bienestar   = 0
        self.peso_muerto = 0
        self.exento_bonus = 0

    def handle_event(self, event):
        for s in self.sliders:
            s.handle_event(event)
        if self.btn_reform.is_clicked(event):
            for s in self.sliders[:3]:
                s.value = max(0, s.value - 5)
            self.notif.add("📜 Reforma fiscal: tasas reducidas -5%", PURPLE)
        if self.btn_exento.is_clicked(event):
            self.exento_bonus = 20
            self.notif.add("🏭 Exención PyME activada (+actividad)", GREEN)

    def update(self, dt):
        super().update(dt)
        mouse = pygame.mouse.get_pos()
        for s in self.sliders:
            s.update(mouse)
        self.btn_reform.update(mouse)
        self.btn_exento.update(mouse)
        self._timer += dt
        if self._timer >= 800:
            self._timer = 0
            isr  = self.sliders[0].value
            iva  = self.sliders[1].value
            iemp = self.sliders[2].value
            act_base = self.sliders[3].value + self.exento_bonus

            # Carga impositiva total
            total_imp = isr + iva + iemp

            # Curva de Laffer: la actividad económica real (base imponible) se contrae
            # exponencialmente cuando los impuestos son confiscatorios (desincentivo al trabajo e inversión)
            factor_actividad = max(0.12, 1.0 - ((total_imp / 115.0) ** 2.2))
            act_efectiva = act_base * factor_actividad

            # Tasa impositiva ponderada
            tasa_ponderada = (isr * 0.4 + iva * 0.3 + iemp * 0.3)
            # Recaudación = Tasa * Base Imponible Efectiva
            self.recaudacion = round(tasa_ponderada * act_efectiva * 1.5, 1)

            # Bienestar del consumidor/ciudadano cae conforme sube la presión fiscal
            self.bienestar = round(max(0.0, 100.0 - total_imp * 0.75), 1)

            # Pérdida de peso muerto (pérdida irrecuperable de eficiencia crece cuadráticamente con el impuesto)
            self.peso_muerto = round((total_imp ** 2) * 0.012, 1)

            self.chart.push(self.recaudacion)
            if total_imp > 75:
                self.notif.add("⚠ Zona decreciente de Laffer: impuestos altos destruyen recaudación", RED)
            elif self.recaudacion > 2600 and self.bienestar > 50:
                self.notif.add("✔ Zona óptima de Laffer: alta recaudación con bienestar preservado", GREEN)
        self.notif.update(dt)

    def _draw_laffer(self, surface, rect):
        """Curva de Laffer simplificada."""
        pygame.draw.rect(surface, PANEL_DARK, rect, border_radius=6)
        pygame.draw.rect(surface, GRAY_DARK, rect, 1, border_radius=6)
        text(surface, "Curva de Laffer", rect.x + 4, rect.y + 2, ORANGE, 11)
        # Dibujar curva
        pts = []
        for i in range(rect.w - 20):
            t_pct = i / (rect.w - 20)
            rev = t_pct * (1 - t_pct) * 4  # curva parabólica
            x = rect.x + 10 + i
            y = rect.y + rect.h - 10 - int(rev * (rect.h - 20))
            pts.append((x, y))
        if len(pts) >= 2:
            pygame.draw.lines(surface, ORANGE, False, pts, 2)
        # Marcar tasa actual
        total_imp = sum(s.value for s in self.sliders[:3])
        t_pos = min(1.0, total_imp / 180)
        ix = rect.x + 10 + int(t_pos * (rect.w - 20))
        rev = t_pos * (1 - t_pos) * 4
        iy = rect.y + rect.h - 10 - int(rev * (rect.h - 20))
        pygame.draw.circle(surface, RED, (ix, iy), 6)
        text(surface, "▲ Tasa actual", ix - 30, iy + 8, RED, 10)

    def draw_content(self, surface):
        accent = self.accent
        p = Panel(40, 85, 330, 285, border=accent)
        p.draw(surface)
        text(surface, "Política Tributaria", 55, 95, color=accent,
             size=14, bold=True)
        for s in self.sliders:
            s.draw(surface)
        self.btn_reform.draw(surface)
        self.btn_exento.draw(surface)

        # Barras de progreso
        self.bar_recaud.draw(surface, self.recaudacion)
        self.bar_bienestar.draw(surface, self.bienestar)

        # KPIs
        font_kpi = get_font(20, bold=True)
        font_lab = get_font(12)
        kpis = [
            ("RECAUDACIÓN",  f"${self.recaudacion:.0f}", ORANGE),
            ("BIENESTAR",    f"{self.bienestar:.0f}%",   GREEN if self.bienestar>60 else RED),
            ("PESO MUERTO",  f"{self.peso_muerto:.1f}",  RED),
        ]
        kx = 400
        for lab, val, col in kpis:
            p2 = Panel(kx, 170, 100, 60, border=col)
            p2.draw(surface)
            surface.blit(font_lab.render(lab, True, GRAY_LIGHT), (kx+5, 178))
            surface.blit(font_kpi.render(val, True, col),        (kx+5, 198))
            kx += 110

        # Curva de Laffer
        laffer_rect = pygame.Rect(400, 245, 280, 120)
        self._draw_laffer(surface, laffer_rect)

        # Sprite integrado en panel izquierdo
        surface.blit(self.sprite_rec, (330, 90))

        # Gráfica
        self.chart.draw(surface)

        infos = [
            "► ISR: grava el ingreso de personas y empresas.",
            "► IVA: impuesto al consumo, lo paga el consumidor final.",
            "► Curva de Laffer: tasas muy altas reducen la recaudación.",
            "► Peso muerto: ineficiencia generada por el impuesto.",
        ]
        iy = 378
        for info in infos:
            text(surface, info, 400, iy, color=GRAY_LIGHT, size=12)
            iy += 18
        self.notif.draw(surface)

# ============================================================
#  ESCENA: INFLACIÓN
#  El jugador maneja la masa monetaria, tasa de interés y
#  expectativas. Resultado: tasa de inflación y poder adquisitivo.
# ============================================================
import pygame
import math
from game.scenes.base import BaseScene
from game.constants import *
from game.ui import (Slider, Panel, LineChart, Notification,
                     Button, ProgressBar, text, get_font)
from game.sprites import sprite_llama


class InflacionScene(BaseScene):
    KEY      = "inflacion"
    TITLE    = "Inflación"
    SUBTITLE = "Controla la masa monetaria y las tasas para combatir la inflación"

    def build(self):
        accent = self.accent
        self.sliders = [
            Slider(60, 110, 280, "Masa Monetaria (M2)", 0, 100, 40,
                   color=RED,    unit="%"),
            Slider(60, 170, 280, "Tasa de Interés",     0,  30, 5,
                   color=CYAN,   unit="%"),
            Slider(60, 230, 280, "Gasto Público",       0, 100, 30,
                   color=ORANGE, unit="%"),
            Slider(60, 290, 280, "Expectativas Inflac.", 0, 100, 20,
                   color=YELLOW, unit=""),
        ]
        self.btn_suba = Button(60, 380, 135, 34, "Subir tasa +2%",  CYAN)
        self.btn_inyec= Button(210, 380, 135, 34, "Inyectar dinero", RED)
        self.bar_poder= ProgressBar(400, 88, 260, 26, "Poder Adquisitivo",
                                    color=GREEN, max_val=100)
        self.chart_inf = LineChart(700, 90,  290, 140, "Inflación (%)",
                                   color=RED)
        self.chart_poder= LineChart(700, 250, 290, 130, "Poder Adq.",
                                    color=GREEN)
        self.notif  = Notification()
        self.sprite_l = sprite_llama()
        self._timer   = 0
        self.inflacion     = 3.0
        self.poder_adq     = 100.0
        self.inflacion_hist = []

    def handle_event(self, event):
        for s in self.sliders:
            s.handle_event(event)
        if self.btn_suba.is_clicked(event):
            self.sliders[1].value = min(30, self.sliders[1].value + 2)
            self.notif.add("🏦 Tasa de interés subida +2%", CYAN)
        if self.btn_inyec.is_clicked(event):
            self.sliders[0].value = min(100, self.sliders[0].value + 10)
            self.notif.add("💸 Masa monetaria inyectada +10%", RED)

    def update(self, dt):
        super().update(dt)
        mouse = pygame.mouse.get_pos()
        for s in self.sliders:
            s.update(mouse)
        self.btn_suba.update(mouse)
        self.btn_inyec.update(mouse)
        self._timer += dt
        if self._timer >= 800:
            self._timer = 0
            mm    = self.sliders[0].value
            tasa  = self.sliders[1].value
            gp    = self.sliders[2].value
            exp   = self.sliders[3].value
            # Presiones de demanda (masa monetaria, gasto, expectativas) vs freno monetario (tasas de interés)
            inflacion_calc = (mm * 0.22 + gp * 0.12 + exp * 0.10) - (tasa * 0.65) - 2.0
            self.inflacion = round(max(-5.0, min(60.0, inflacion_calc)), 1)

            # Dinámica del poder adquisitivo:
            # - En deflación (< 0%): los precios caen y el poder adquisitivo sube.
            # - En inflación controlada (0% - 3.5%): salarios se indexan/ajustan, el poder adquisitivo se RECUPERA.
            # - En inflación alta (> 3.5%): el poder adquisitivo se erosiona.
            if self.inflacion < 0.0:
                self.poder_adq = min(120.0, round(self.poder_adq + abs(self.inflacion) * 0.6, 1))
            elif self.inflacion <= 3.5:
                self.poder_adq = min(100.0, round(self.poder_adq + 1.2, 1))
            else:
                self.poder_adq = max(10.0, round(self.poder_adq - (self.inflacion - 3.0) * 0.35, 1))

            self.chart_inf.push(self.inflacion)
            self.chart_poder.push(self.poder_adq)

            if self.inflacion > 25:
                self.notif.add("🔥 ¡HIPERINFLACIÓN! Destrucción del poder adquisitivo", RED)
            elif self.inflacion > 5:
                self.notif.add("📈 Inflación elevada: erosiona los salarios reales", ORANGE)
            elif self.inflacion < 0:
                self.notif.add("❄ ¡DEFLACIÓN! Caída generalizada de precios (<0%)", CYAN)
            elif 0 <= self.inflacion < 2:
                self.notif.add("📉 Inflación baja (desaceleración económica)", YELLOW)
            else:
                self.notif.add("✔ Inflación en rango meta (estabilidad de precios)", GREEN)
        self.notif.update(dt)

    def _draw_thermometer(self, surface, x, y, value, max_val=50):
        """Termómetro de inflación."""
        h = 200; w = 20
        pygame.draw.rect(surface, GRAY_DARK, (x - w//2, y, w, h), border_radius=10)
        ratio = max(0.0, min(1.0, value / max_val))
        fill_h = int(ratio * h)
        col = CYAN if value < 0 else (GREEN if ratio < 0.1 else (YELLOW if ratio < 0.3 else RED))
        if fill_h > 0:
            pygame.draw.rect(surface, col, (x - w//2, y + h - fill_h, w, fill_h),
                             border_radius=10)
        pygame.draw.rect(surface, GRAY, (x - w//2, y, w, h), 2, border_radius=10)
        pygame.draw.circle(surface, RED, (x, y + h + 16), 18)
        pygame.draw.circle(surface, WHITE, (x, y + h + 16), 10)
        pygame.draw.circle(surface, RED, (x, y + h + 16), 7)
        font = get_font(12, bold=True)
        lbl = font.render(f"{value:.1f}%", True, WHITE)
        surface.blit(lbl, (x - lbl.get_width()//2, y - 18))
        lab = font.render("INFLACIÓN", True, GRAY_LIGHT)
        surface.blit(lab, (x - lab.get_width()//2, y + h + 36))
        # marcas
        for mark in [0, 10, 20, 30, 40, 50]:
            my = y + h - int((mark / max_val) * h)
            pygame.draw.line(surface, GRAY, (x + w//2, my), (x + w//2 + 8, my), 1)
            mk = get_font(9).render(str(mark), True, GRAY)
            surface.blit(mk, (x + w//2 + 10, my - 5))

    def draw_content(self, surface):
        accent = self.accent
        p = Panel(40, 85, 330, 285, border=accent)
        p.draw(surface)
        text(surface, "Variables Monetarias", 55, 95, color=accent,
             size=14, bold=True)
        for s in self.sliders:
            s.draw(surface)
        self.btn_suba.draw(surface)
        self.btn_inyec.draw(surface)

        # Barra poder adquisitivo
        self.bar_poder.rect.x = 380
        self.bar_poder.rect.y = 85
        self.bar_poder.rect.w = 200
        self.bar_poder.draw(surface, min(100, self.poder_adq))

        # Llama animada
        flame_x = 595 + int(math.sin(self.tick / 200) * 4)
        flame_y = 82 + int(math.cos(self.tick / 300) * 3)
        surface.blit(self.sprite_l, (flame_x, flame_y))

        # Termómetro
        self._draw_thermometer(surface, 610, 145, self.inflacion)

        # KPIs
        font_kpi = get_font(22, bold=True)
        font_lab = get_font(12)
        inf_col = CYAN if self.inflacion < 0 else (RED if self.inflacion > 5 else GREEN)
        kpis = [
            ("INFLACIÓN", f"{self.inflacion:.1f}%", inf_col),
            ("PODER ADQ.", f"{self.poder_adq:.0f}",
             GREEN if self.poder_adq > 80 else RED),
        ]
        kx = 60
        for lab, val, col in kpis:
            p2 = Panel(kx, 435, 145, 65, border=col)
            p2.draw(surface)
            surface.blit(font_lab.render(lab, True, GRAY_LIGHT), (kx+8, 443))
            surface.blit(font_kpi.render(val, True, col),        (kx+8, 465))
            kx += 160

        self.chart_inf.draw(surface)
        self.chart_poder.draw(surface)

        infos = [
            "► Teoria cuantitativa: MV = PQ.",
            "► Sube tasa para frenar inflacion.",
            "► Expectativas son autorrealizables.",
            "► Hiperinflacion: alza continua >50%.",
        ]
        iy = 130
        for info in infos:
            text(surface, info, 380, iy, color=GRAY_LIGHT, size=11)
            iy += 18
        self.notif.draw(surface)

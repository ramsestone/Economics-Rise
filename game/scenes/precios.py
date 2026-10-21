# ============================================================
#  ESCENA: PRECIOS
#  El jugador observa cómo el precio señaliza oferta y demanda.
#  Sliders: precio base, subsidio de precio, control de precios.
# ============================================================
import pygame
import math
from game.scenes.base import BaseScene
from game.constants import *
from game.ui import (Slider, Panel, LineChart, Notification,
                     Button, text, get_font)
from game.sprites import sprite_moneda


class PreciosScene(BaseScene):
    KEY      = "precios"
    TITLE    = "Precios"
    SUBTITLE = "Analiza el papel del precio como señal en la economía"

    def build(self):
        accent = self.accent
        self.sliders = [
            Slider(60, 110, 280, "Precio ($)",          1, 200, 60,
                   color=YELLOW, unit=""),
            Slider(60, 170, 280, "Oferta disponible",   0, 200, 80,
                   color=GREEN,  unit=" u"),
            Slider(60, 230, 280, "Demanda existente",   0, 200, 90,
                   color=RED,    unit=" u"),
            Slider(60, 290, 280, "Control de precios",  0, 100,  0,
                   color=PURPLE, unit="%"),
        ]
        self.btn_techo   = Button(60, 380, 130, 34, "Precio máximo",  RED)
        self.btn_piso    = Button(205, 380, 130, 34, "Precio mínimo", GREEN)
        self.btn_libre   = Button(350, 380, 130, 34, "Libre mercado", CYAN)

        self.chart = LineChart(700, 90, 290, 150, "Precio de Mercado",
                               color=YELLOW)
        self.notif  = Notification()
        self.sprite_m = sprite_moneda()
        self._timer   = 0
        self.excedente = 0
        self.escasez_val = 0
        self.precio_eq = 60
        self.modo = "libre"

    def handle_event(self, event):
        for s in self.sliders:
            s.handle_event(event)
        if self.btn_techo.is_clicked(event):
            self.sliders[3].value = 60
            self.modo = "techo"
            # Precio máximo vinculante fijado un 35% por debajo del equilibrio
            self.sliders[0].value = max(10, round(self.precio_eq * 0.65, 1))
            self.notif.add("🔴 Precio máximo (techo) fijado bajo el equilibrio -> Escasez", RED)
        if self.btn_piso.is_clicked(event):
            self.sliders[3].value = 60
            self.modo = "piso"
            # Precio mínimo vinculante fijado un 40% por encima del equilibrio
            self.sliders[0].value = min(200, round(self.precio_eq * 1.4, 1))
            self.notif.add("🟢 Precio mínimo (piso) fijado sobre el equilibrio -> Excedente", GREEN)
        if self.btn_libre.is_clicked(event):
            self.sliders[3].value = 0
            self.modo = "libre"
            self.sliders[0].value = round(self.precio_eq, 1)
            self.notif.add("🔵 Mercado libre: el precio se autorregula al equilibrio", CYAN)

    def update(self, dt):
        super().update(dt)
        mouse = pygame.mouse.get_pos()
        for s in self.sliders:
            s.update(mouse)
        self.btn_techo.update(mouse)
        self.btn_piso.update(mouse)
        self.btn_libre.update(mouse)
        self._timer += dt
        if self._timer >= 800:
            self._timer = 0
            precio_slider = self.sliders[0].value
            oferta_base   = self.sliders[1].value
            demanda_base  = self.sliders[2].value
            ctrl          = self.sliders[3].value

            # Precio de equilibrio determinado por la escasez relativa de oferta frente a demanda
            # Si hay más demanda que oferta, el equilibrio natural es más caro.
            ratio_mercado = (demanda_base + 30) / max(10, oferta_base + 30)
            self.precio_eq = round(max(15.0, min(180.0, 75.0 * ratio_mercado)), 1)

            # En modo libre mercado sin control, el precio converge al equilibrio
            if self.modo == "libre" and ctrl == 0:
                diff = self.precio_eq - precio_slider
                if abs(diff) > 1.0:
                    precio_slider = round(precio_slider + diff * 0.35, 1)
                    self.sliders[0].value = precio_slider

            # Precio efectivo considerando controles oficiales
            precio_real = precio_slider
            if self.modo == "techo" and ctrl > 0:
                # Techo limita precio hacia abajo
                precio_real = min(precio_slider, self.precio_eq * (1 - ctrl / 200))
            elif self.modo == "piso" and ctrl > 0:
                # Piso fuerza precio hacia arriba
                precio_real = max(precio_slider, self.precio_eq * (1 + ctrl / 200))

            # Cantidades ofrecidas y demandadas efectivas en función del precio real
            # Ley de oferta: mayor precio -> más oferta ofrecida
            # Ley de demanda: mayor precio -> menor demanda requerida
            rel_p = precio_real / max(1.0, self.precio_eq)
            q_ofrecida = oferta_base * (rel_p ** 0.65)
            q_demandada = demanda_base * ((1.0 / max(0.1, rel_p)) ** 0.65)

            if precio_real > self.precio_eq + 1.5:
                self.excedente = round(max(0.0, q_ofrecida - q_demandada), 1)
                self.escasez_val = 0.0
            elif precio_real < self.precio_eq - 1.5:
                self.escasez_val = round(max(0.0, q_demandada - q_ofrecida), 1)
                self.excedente = 0.0
            else:
                self.excedente = 0.0
                self.escasez_val = 0.0

            self.chart.push(round(precio_real, 1))
            if self.escasez_val > 25:
                self.notif.add("⚠ ¡Escasez y desabasto en el mercado!", RED)
            elif self.excedente > 25:
                self.notif.add("📦 Excedente: inventario sin vender acumulado", YELLOW)
            elif self.excedente == 0 and self.escasez_val == 0:
                self.notif.add("✔ Mercado despejado en equilibrio", GREEN)
        self.notif.update(dt)

    def _draw_gauge(self, surface, x, y, label, value, max_v, color):
        """Indicador circular tipo velocímetro."""
        r = 45
        pygame.draw.circle(surface, PANEL_DARK, (x, y), r)
        pygame.draw.circle(surface, color, (x, y), r, 2)
        ratio = min(1, value / max(1, max_v))
        angle = -math.pi * 0.8 + ratio * math.pi * 1.6
        ex = x + int(math.cos(angle) * (r - 8))
        ey = y + int(math.sin(angle) * (r - 8))
        pygame.draw.line(surface, color, (x, y), (ex, ey), 3)
        font = get_font(11, bold=True)
        lbl = font.render(label, True, GRAY_LIGHT)
        surface.blit(lbl, (x - lbl.get_width()//2, y + r + 2))
        val = font.render(f"{value:.0f}", True, color)
        surface.blit(val, (x - val.get_width()//2, y - 8))

    def draw_content(self, surface):
        accent = self.accent
        p = Panel(40, 85, 330, 290, border=accent)
        p.draw(surface)
        text(surface, "Señales de Precio", 55, 95, color=accent,
             size=14, bold=True)
        for s in self.sliders:
            s.draw(surface)
        self.btn_techo.draw(surface)
        self.btn_piso.draw(surface)
        self.btn_libre.draw(surface)

        # Indicadores de velocímetro
        gauge_y = 460
        self._draw_gauge(surface, 150, gauge_y, "EXCEDENTE",
                         self.excedente, 100, YELLOW)
        self._draw_gauge(surface, 280, gauge_y, "ESCASEZ",
                         self.escasez_val, 100, RED)

        # KPI precio equilibrio
        font_kpi = get_font(20, bold=True)
        font_lab = get_font(12)
        p2 = Panel(390, 88, 290, 70, border=YELLOW)
        p2.draw(surface)
        surface.blit(font_lab.render("PRECIO DE EQUILIBRIO ESTIMADO", True, GRAY_LIGHT),
                     (398, 96))
        surface.blit(font_kpi.render(f"${self.precio_eq:.1f}", True, YELLOW),
                     (398, 118))

        # Modo actual
        modo_col = {"libre": CYAN, "techo": RED, "piso": GREEN}.get(self.modo, CYAN)
        p3 = Panel(390, 170, 290, 50, border=modo_col)
        p3.draw(surface)
        surface.blit(font_lab.render("MODO:", True, GRAY_LIGHT), (398, 178))
        surface.blit(font_kpi.render(self.modo.upper(), True, modo_col), (450, 178))

        # Sprite moneda animada integrado en el panel izquierdo
        offset = int(math.sin(self.tick / 300) * 4)
        surface.blit(self.sprite_m, (330, 90 + offset))

        self.chart.draw(surface)

        infos = [
            "► Precio de equilibrio: Oferta = Demanda.",
            "► Precio máximo (techo): genera escasez.",
            "► Precio mínimo (piso): genera excedente.",
            "► Mercado libre ajusta precio naturalmente.",
        ]
        iy = 250
        for info in infos:
            text(surface, info, 700, iy, color=GRAY_LIGHT, size=12)
            iy += 18
        self.notif.draw(surface)

# ============================================================
#  ESCENA: COMPETENCIA
#  Simulación de mercado con múltiples empresas compitiendo.
#  El jugador maneja su empresa: precio, calidad, publicidad.
# ============================================================
import pygame
import math
import random
from game.scenes.base import BaseScene
from game.constants import *
from game.ui import (Slider, Panel, LineChart, Notification,
                     Button, ProgressBar, text, get_font)
from game.sprites import sprite_trofeo, sprite_empresa


class _Rival:
    def __init__(self, name, precio, calidad, pub, innov=20):
        self.name    = name
        self.precio  = precio
        self.calidad = calidad
        self.pub     = pub
        self.innov   = innov
        self.cuota   = 0.0
        self.color   = (random.randint(80, 220),
                        random.randint(80, 220),
                        random.randint(80, 220))

    @property
    def score(self):
        return max(1.0, (self.calidad * 3.0 + self.pub * 0.5 + self.innov * 0.4 - self.precio * 0.35))


class CompetenciaScene(BaseScene):
    KEY      = "competencia"
    TITLE    = "Competencia"
    SUBTITLE = "Compite contra empresas rivales por la cuota de mercado"

    def build(self):
        accent = self.accent
        self.sliders = [
            Slider(60, 110, 280, "Tu Precio ($)",        1, 200, 80,
                   color=YELLOW, unit=""),
            Slider(60, 170, 280, "Tu Calidad (1-10)",    1,  10,  6,
                   color=GREEN,  unit=""),
            Slider(60, 230, 280, "Publicidad ($k)",      0, 100, 30,
                   color=PURPLE, unit=""),
            Slider(60, 290, 280, "Innovación",           0, 100, 20,
                   color=CYAN,   unit="%"),
        ]
        self.btn_dumping = Button(60, 380, 130, 34, "Price Dumping", RED)
        self.btn_innov   = Button(205, 380, 130, 34, "Innovar ×2",   CYAN)
        self.rivals = [
            _Rival("Alfa S.A.",     70,  7, 40, innov=25),
            _Rival("Beta Corp.",   100,  9, 60, innov=35),
            _Rival("Gamma Inc.",    50,  5, 20, innov=15),
            _Rival("Delta Ltd.",   120, 10, 80, innov=45),
        ]
        self.chart_cuota = LineChart(700, 90, 290, 150, "Tu Cuota (%)",
                                     color=YELLOW)
        self.notif   = Notification()
        self.sprite_t = sprite_trofeo()
        self.sprite_e = sprite_empresa()
        self._timer   = 0
        self.mi_cuota      = 20.0
        self.inov_bonus    = 0
        self.dumping_timer = 0

    def handle_event(self, event):
        for s in self.sliders:
            s.handle_event(event)
        if self.btn_dumping.is_clicked(event):
            self.sliders[0].value = max(1, self.sliders[0].value * 0.6)
            self.dumping_timer = 5000
            self.notif.add("⚔ Price Dumping: precio -40%!", RED)
        if self.btn_innov.is_clicked(event):
            self.inov_bonus = 30
            self.sliders[1].value = min(10, self.sliders[1].value + 1)
            self.notif.add("🚀 Innovación aplicada: calidad +1", CYAN)

    def update(self, dt):
        super().update(dt)
        mouse = pygame.mouse.get_pos()
        for s in self.sliders:
            s.update(mouse)
        self.btn_dumping.update(mouse)
        self.btn_innov.update(mouse)
        if self.dumping_timer > 0:
            self.dumping_timer -= dt
        self._timer += dt
        if self._timer >= 900:
            self._timer = 0
            mi_precio  = self.sliders[0].value
            mi_calidad = self.sliders[1].value
            mi_pub     = self.sliders[2].value
            mi_innov   = self.sliders[3].value + self.inov_bonus
            mi_score   = max(1.0, mi_calidad * 3.0 + mi_pub * 0.5 + mi_innov * 0.4 - mi_precio * 0.35)
            # Actualizar rivales ligeramente
            for r in self.rivals:
                r.precio  = max(10, r.precio + random.randint(-5, 5))
                r.calidad = max(1, min(10, r.calidad + random.uniform(-0.3, 0.3)))
                r.pub     = max(0, r.pub + random.randint(-5, 5))
            total = mi_score + sum(r.score for r in self.rivals)
            self.mi_cuota = round(max(0, (mi_score / max(1, total)) * 100), 1)
            self.chart_cuota.push(self.mi_cuota)
            if self.mi_cuota > 50:
                self.notif.add("🏆 ¡Monopolio de mercado!", YELLOW)
            elif self.mi_cuota < 5:
                self.notif.add("📉 ¡Tu empresa pierde cuota!", RED)
        self.notif.update(dt)

    def _draw_pie_chart(self, surface, cx, cy, r, shares, labels, colors):
        """Gráfico de pastel de cuotas."""
        total = sum(shares)
        if total <= 0:
            return
        angle = -math.pi / 2
        for share, label, col in zip(shares, labels, colors):
            sweep = (share / total) * 2 * math.pi
            # Dibujar sector (aproximación con polígono)
            pts = [(cx, cy)]
            steps = max(4, int(sweep / 0.1))
            for i in range(steps + 1):
                a = angle + i * sweep / steps
                pts.append((cx + r * math.cos(a), cy + r * math.sin(a)))
            if len(pts) >= 3:
                pygame.draw.polygon(surface, col, pts)
            # Borde
            pygame.draw.polygon(surface, DARK_BG, pts, 2)
            # Etiqueta
            mid_a = angle + sweep / 2
            lx = cx + (r + 20) * math.cos(mid_a)
            ly = cy + (r + 20) * math.sin(mid_a)
            font = get_font(10)
            pct = font.render(f"{share:.0f}%", True, WHITE)
            surface.blit(pct, (lx - pct.get_width()//2, ly - 5))
            angle += sweep

    def draw_content(self, surface):
        accent = self.accent
        p = Panel(40, 85, 330, 285, border=accent)
        p.draw(surface)
        text(surface, "Tu Empresa vs. Rivales", 55, 95,
             color=accent, size=14, bold=True)
        for s in self.sliders:
            s.draw(surface)
        self.btn_dumping.draw(surface)
        self.btn_innov.draw(surface)

        # Tabla de rivales
        ty = 430
        text(surface, "EMPRESA", 60, ty, GRAY_LIGHT, 12, bold=True)
        text(surface, "PRC", 200, ty, GRAY_LIGHT, 12, bold=True)
        text(surface, "CAL", 250, ty, GRAY_LIGHT, 12, bold=True)
        text(surface, "PUB", 295, ty, GRAY_LIGHT, 12, bold=True)
        ty += 16
        for r in self.rivals:
            text(surface, r.name[:12], 60, ty, r.color, 11)
            text(surface, f"{r.precio:.0f}", 200, ty, GRAY_LIGHT, 11)
            text(surface, f"{r.calidad:.1f}", 250, ty, GRAY_LIGHT, 11)
            text(surface, f"{r.pub:.0f}", 295, ty, GRAY_LIGHT, 11)
            ty += 15

        # Gráfico de torta
        total = sum(r.score for r in self.rivals)
        shares = [self.mi_cuota] + [(r.score / max(1, total + (self.mi_cuota / max(1, 100 - self.mi_cuota) * total))) * (100 - self.mi_cuota)
                                     for r in self.rivals]
        shares_norm = [self.mi_cuota] + [(r.score / max(1, sum(r2.score for r2 in self.rivals))) * (100 - self.mi_cuota) for r in self.rivals]
        labels  = ["Tú"] + [r.name for r in self.rivals]
        colors  = [YELLOW] + [r.color for r in self.rivals]
        self._draw_pie_chart(surface, 540, 280, 120, shares_norm, labels, colors)

        # Leyenda torta
        lx = 460; ly = 415
        for lab, col in zip(labels, colors):
            pygame.draw.rect(surface, col, (lx, ly, 12, 12))
            text(surface, lab[:10], lx + 16, ly, col, 11)
            lx += 130
            if lx > 700:
                lx = 460; ly += 16

        # Sprite trofeo integrado en panel izquierdo
        surface.blit(self.sprite_t, (330, 90))

        # KPI cuota
        font_kpi = get_font(26, bold=True)
        p2 = Panel(700, 250, 180, 70, border=YELLOW)
        p2.draw(surface)
        text(surface, "TU CUOTA", 710, 258, GRAY_LIGHT, 12)
        col = GREEN if self.mi_cuota > 25 else (YELLOW if self.mi_cuota > 10 else RED)
        vt = font_kpi.render(f"{self.mi_cuota:.1f}%", True, col)
        surface.blit(vt, (710, 276))

        self.chart_cuota.draw(surface)

        # Información didáctica en columna central inferior (evita solaparse con health_widget a la derecha)
        infos = [
            "► Competencia perfecta: muchos compradores y vendedores.",
            "► Dumping: rebaja de precio para desplazar competidores.",
            "► Innovación crea ventaja competitiva sostenible.",
        ]
        iy = 450
        for info in infos:
            text(surface, info, 400, iy, color=GRAY_LIGHT, size=11)
            iy += 17
        self.notif.draw(surface)

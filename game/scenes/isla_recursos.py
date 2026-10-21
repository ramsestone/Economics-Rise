# ============================================================
#  LA FRONTERA DE RECURSOS – Fusión de Fundamentos y Consumo
#  Integra: Escasez, Consumidores y Utilidad
# ============================================================
import math
import random
import pygame

from game.constants import *
from game.ui import Panel, Slider, Button, LineChart, Notification, text, get_font
from game.sprites import sprite_caja_vacia, sprite_consumidor, sprite_moneda
from game.scenes.base import BaseScene
from game.feedback import update_scene_health


class IslaRecursosScene(BaseScene):
    KEY = "isla_recursos"
    TITLE = "La Frontera de Recursos: FPP y Bienestar"
    SUBTITLE = "Asigna recursos escasos y maximiza la utilidad social de la población"

    def build(self):
        accent = self.accent
        self.notif = Notification()

        # Sprites
        self.sprite_caja = sprite_caja_vacia()
        self.sprite_con = sprite_consumidor()
        self.sprite_m = sprite_moneda()

        # Sliders panel izquierdo
        self.s_alimentos = Slider(60, 115, 280, "Recursos a Alimentos (Consumo)", 0, 100, 50, color=ORANGE, unit="%")
        self.s_tecnol = Slider(60, 175, 280, "Recursos a Tecnología (Capital)", 0, 100, 50, color=CYAN, unit="%")
        self.s_innova = Slider(60, 235, 280, "Inversión en Productividad", 0, 100, 20, color=GREEN, unit="pts")
        self.s_pref = Slider(60, 295, 280, "Preferencia Social por Alimentos", 1, 9, 5, color=YELLOW, unit="/10")

        # Botones de presets de asignación
        self.btn_eq = Button(60, 365, 88, 28, "50 / 50", GREEN)
        self.btn_agro = Button(156, 365, 88, 28, "Agro 75%", ORANGE)
        self.btn_tech = Button(252, 365, 88, 28, "Tech 75%", CYAN)

        # Gráfico histórico de utilidad
        self.chart_ut = LineChart(710, 85, 280, 125, "Utilidad Social (%)", color=ORANGE)

        # Variables calculadas
        self.prod_alimentos = 0.0
        self.prod_tecnol = 0.0
        self.uso_recursos = 100.0
        self.costo_oportunidad = 1.0
        self.utilidad_total = 80.0
        self.estado_fpp = "EFICIENTE"

        self._tick_timer = 0
        self.calcular_frontera()

    def handle_event(self, event):
        self.s_alimentos.handle_event(event)
        self.s_tecnol.handle_event(event)
        self.s_innova.handle_event(event)
        self.s_pref.handle_event(event)

        if self.btn_eq.is_clicked(event):
            self.s_alimentos.value = 50
            self.s_tecnol.value = 50
            self.notif.add("Asignación balanceada: 50% alimentos y 50% tecnología.", GREEN)
        elif self.btn_agro.is_clicked(event):
            self.s_alimentos.value = 75
            self.s_tecnol.value = 25
            self.notif.add("Enfoque prioritario en consumo alimentario inmediato.", ORANGE)
        elif self.btn_tech.is_clicked(event):
            self.s_alimentos.value = 25
            self.s_tecnol.value = 75
            self.notif.add("Enfoque intensivo en bienes de capital y tecnología futura.", CYAN)

    def calcular_frontera(self):
        ra = self.s_alimentos.value
        rt = self.s_tecnol.value
        inv = self.s_innova.value
        alpha = self.s_pref.value / 10.0  # ponderador de preferencia entre 0.1 y 0.9

        self.uso_recursos = ra + rt

        # Expansión de la FPP con la inversión tecnológica
        escala_fpp = 10.0 * (1.0 + inv * 0.008)

        # Producción con rendimientos marginales decrecientes (ra^0.5, rt^0.5)
        self.prod_alimentos = escala_fpp * math.sqrt(max(0.0, ra))
        self.prod_tecnol = escala_fpp * math.sqrt(max(0.0, rt))

        # Estado FPP
        if self.uso_recursos > 100.0:
            self.estado_fpp = "INALCANZABLE (SOBREASIGNADO)"
            penalizacion = (self.uso_recursos - 100.0) * 1.5
        elif self.uso_recursos < 90.0:
            self.estado_fpp = "INEFICIENTE (RECURSOS OCIOSOS)"
            penalizacion = (100.0 - self.uso_recursos) * 0.7
        else:
            self.estado_fpp = "EFICIENTE (EN LA FPP)"
            penalizacion = 0.0

        # Costo de oportunidad: Tasa Marginal de Transformación = dY / dX
        # A mayor asignación a alimentos, mayor es el sacrificio de tecnología por unidad adicional
        if ra > 1 and rt > 1:
            self.costo_oportunidad = math.sqrt(rt / ra)
        else:
            self.costo_oportunidad = 1.0

        # Utilidad Social: función Cobb-Douglas U = X^alpha * Y^(1-alpha)
        # Normalizada sobre el máximo potencial
        max_ut = escala_fpp * (math.sqrt(50) ** alpha) * (math.sqrt(50) ** (1.0 - alpha))
        if max_ut > 0:
            raw_ut = (self.prod_alimentos ** alpha) * (self.prod_tecnol ** (1.0 - alpha))
            ut_calc = (raw_ut / max_ut) * 100.0 - penalizacion
            self.utilidad_total = max(5.0, min(100.0, ut_calc))
        else:
            self.utilidad_total = 50.0

    def update(self, dt):
        super().update(dt)
        mouse = pygame.mouse.get_pos()
        self.s_alimentos.update(mouse)
        self.s_tecnol.update(mouse)
        self.s_innova.update(mouse)
        self.s_pref.update(mouse)
        self.btn_eq.update(mouse)
        self.btn_agro.update(mouse)
        self.btn_tech.update(mouse)

        self.calcular_frontera()

        self._tick_timer += dt
        if self._tick_timer >= 650:
            self._tick_timer = 0
            self.chart_ut.push(self.utilidad_total)

        update_scene_health(self.KEY, self, self.health_widget)

    def draw_fpp_chart(self, surface, rect):
        """Dibuja la Frontera de Posibilidades de Producción cóncava."""
        pygame.draw.rect(surface, PANEL_DARK, rect, border_radius=8)
        pygame.draw.rect(surface, GRAY_DARK, rect, 1, border_radius=8)

        text(surface, "FRONTERA DE POSIBILIDADES (FPP)", rect.x + 12, rect.y + 8, ORANGE, 12, bold=True)

        ox, oy = rect.x + 40, rect.bottom - 28
        ax_w, ax_h = rect.w - 55, rect.h - 55

        pygame.draw.line(surface, GRAY, (ox, oy), (ox + ax_w, oy), 2)
        pygame.draw.line(surface, GRAY, (ox, oy), (ox, oy - ax_h), 2)

        text(surface, "Alimentos (X)", ox + ax_w - 75, oy + 4, ORANGE, 10, bold=True)
        text(surface, "Tecnol. (Y)", ox - 30, oy - ax_h - 4, CYAN, 10, bold=True)

        # Máximos de escala
        escala_max = 10.0 * (1.0 + self.s_innova.value * 0.008) * 10.0 * 1.3

        def to_s(x_val, y_val):
            sx = ox + (min(escala_max, max(0.0, x_val)) / escala_max) * ax_w
            sy = oy - (min(escala_max, max(0.0, y_val)) / escala_max) * ax_h
            return int(sx), int(sy)

        # 1. Curva FPP cóncava (100% de recursos)
        escala_fpp = 10.0 * (1.0 + self.s_innova.value * 0.008)
        pts_fpp = []
        for i in range(51):
            theta = (i / 50.0) * (math.pi / 2.0)
            # Ra = 100 * cos^2, Rt = 100 * sin^2
            x_fpp = escala_fpp * 10.0 * math.cos(theta)
            y_fpp = escala_fpp * 10.0 * math.sin(theta)
            pts_fpp.append(to_s(x_fpp, y_fpp))

        if len(pts_fpp) >= 2:
            # Sombreado de área alcanzable
            poly_pts = [(ox, oy)] + pts_fpp + [(ox, oy)]
            poly_surf = pygame.Surface((rect.w, rect.h), pygame.SRCALPHA)
            # Offset a coordenadas relativas de poly_surf
            rel_poly = [(px - rect.x, py - rect.y) for px, py in poly_pts]
            pygame.draw.polygon(poly_surf, (0, 200, 100, 25), rel_poly)
            surface.blit(poly_surf, rect.topleft)

            pygame.draw.lines(surface, (255, 180, 50), False, pts_fpp, 2)

        # 2. Punto operativo actual
        cur_x, cur_y = to_s(self.prod_alimentos, self.prod_tecnol)
        col_pt = GREEN if self.estado_fpp.startswith("EFICIENTE") else (RED if self.estado_fpp.startswith("INALCANZABLE") else YELLOW)
        pygame.draw.circle(surface, col_pt, (cur_x, cur_y), 7)
        pygame.draw.circle(surface, WHITE, (cur_x, cur_y), 7, 1)

        # Líneas al origen
        pygame.draw.line(surface, GRAY_DARK, (ox, cur_y), (cur_x, cur_y), 1)
        pygame.draw.line(surface, GRAY_DARK, (cur_x, oy), (cur_x, cur_y), 1)

        # Insignia de estado FPP
        badge_rect = pygame.Rect(ox + 8, oy - ax_h + 4, 185, 16)
        pygame.draw.rect(surface, col_pt, badge_rect, border_radius=3)
        text(surface, self.estado_fpp[:22], badge_rect.x + 4, badge_rect.y + 2, BLACK, 9, bold=True)

    def draw_island_canvas(self, surface, rect):
        """Dibuja la civilización / isla interactiva y su bienestar social."""
        pygame.draw.rect(surface, PANEL_DARK, rect, border_radius=8)
        border_col = GREEN if self.utilidad_total >= 75 else (YELLOW if self.utilidad_total >= 50 else RED)
        pygame.draw.rect(surface, border_col, rect, 2, border_radius=8)

        text(surface, "ECOSISTEMA DE LA COMUNIDAD", rect.x + 12, rect.y + 8, GRAY_LIGHT, 12, bold=True)

        # Suelo de la isla
        isla_rect = pygame.Rect(rect.x + 20, rect.y + 35, rect.w - 40, rect.h - 50)
        pygame.draw.rect(surface, (30, 42, 58), isla_rect, border_radius=8)
        pygame.draw.rect(surface, GRAY_DARK, isla_rect, 1, border_radius=8)

        # Sector Agrícola (Izquierda)
        pygame.draw.rect(surface, (50, 45, 25), (isla_rect.x + 10, isla_rect.y + 10, 115, isla_rect.h - 20), border_radius=6)
        text(surface, "SECTOR ALIMENTOS", isla_rect.x + 16, isla_rect.y + 14, ORANGE, 10, bold=True)
        surface.blit(self.sprite_caja, (isla_rect.x + 16, isla_rect.y + 35))
        text(surface, f"Q={self.prod_alimentos:.0f} u", isla_rect.x + 50, isla_rect.y + 38, ORANGE, 12, bold=True)
        # Cultivos pixel art
        num_trigo = min(8, int(self.prod_alimentos // 12))
        for i in range(num_trigo):
            tx = isla_rect.x + 18 + (i % 4) * 22
            ty = isla_rect.y + 70 + (i // 4) * 20
            pygame.draw.rect(surface, YELLOW, (tx, ty, 4, 12))
            pygame.draw.circle(surface, (255, 200, 50), (tx + 2, ty), 3)

        # Sector Tecnológico (Derecha)
        pygame.draw.rect(surface, (25, 40, 55), (isla_rect.right - 125, isla_rect.y + 10, 115, isla_rect.h - 20), border_radius=6)
        text(surface, "SECTOR CAPITAL", isla_rect.right - 120, isla_rect.y + 14, CYAN, 10, bold=True)
        surface.blit(self.sprite_con, (isla_rect.right - 120, isla_rect.y + 35))
        text(surface, f"Q={self.prod_tecnol:.0f} u", isla_rect.right - 85, isla_rect.y + 38, CYAN, 12, bold=True)
        # Engranajes pixel art
        num_tech = min(8, int(self.prod_tecnol // 12))
        for i in range(num_tech):
            tx = isla_rect.right - 118 + (i % 4) * 24
            ty = isla_rect.y + 70 + (i // 4) * 20
            pygame.draw.rect(surface, CYAN, (tx, ty, 8, 8), border_radius=2)
            pygame.draw.rect(surface, WHITE, (tx + 2, ty + 2, 4, 4))

        # Felicidad en el centro
        cx = isla_rect.centerx
        surface.blit(self.sprite_m, (cx - 10, isla_rect.y + 20))
        text(surface, f"Utilidad: {self.utilidad_total:.0f}%", cx - 35, isla_rect.bottom - 22,
             GREEN if self.utilidad_total >= 75 else RED, 11, bold=True)

    def draw_content(self, surface):
        # 1. Panel Izquierdo: Controles
        p_left = Panel(40, 85, 330, 520, border=self.accent)
        p_left.draw(surface)

        text(surface, "Asignación de Recursos Escasos", 55, 95, self.accent, 12, bold=True)
        self.s_alimentos.draw(surface)
        self.s_tecnol.draw(surface)

        text(surface, "Innovación y Preferencias", 55, 215, GREEN, 12, bold=True)
        self.s_innova.draw(surface)
        self.s_pref.draw(surface)

        text(surface, "Presets de Reparto", 55, 345, YELLOW, 12, bold=True)
        self.btn_eq.draw(surface)
        self.btn_agro.draw(surface)
        self.btn_tech.draw(surface)

        text(surface, "• Costo de Oportunidad: Sacrificio de Y para ganar 1 unidad de X.", 55, 420, GRAY_LIGHT, 10)
        text(surface, "• Ley de Rendimientos Decrecientes: Cada % extra rinde menos.", 55, 440, GRAY_LIGHT, 10)
        text(surface, "• Más del 100% total es inviable e inalcanzable (Sobreasignación).", 55, 460, GRAY_LIGHT, 10)

        # Sprite cabecera izquierda
        surface.blit(self.sprite_caja, (330, 92))

        # 2. Columna Central: Gráfico FPP + Ecosistema de la Comunidad
        fpp_rect = pygame.Rect(390, 85, 305, 290)
        self.draw_fpp_chart(surface, fpp_rect)

        island_rect = pygame.Rect(390, 390, 305, 215)
        self.draw_island_canvas(surface, island_rect)

        # 3. Columna Derecha: Gráfico de Utilidad + Health Widget + KPIs
        self.chart_ut.draw(surface)
        self.health_widget.draw(surface)

        # Panel de Métricas / KPIs
        p_kpi = Panel(710, 405, 280, 200, border=self.accent)
        p_kpi.draw(surface)
        text(surface, "Indicadores de Bienestar", 725, 415, self.accent, 12, bold=True)

        font_kpi = get_font(18, bold=True)
        font_lab = get_font(11)

        col_uso = GREEN if 95 <= self.uso_recursos <= 100 else (YELLOW if self.uso_recursos < 95 else RED)
        col_ut = GREEN if self.utilidad_total >= 75 else (YELLOW if self.utilidad_total >= 50 else RED)

        kpis = [
            ("UTILIDAD SOCIAL TOTAL", f"{self.utilidad_total:.0f} pts", col_ut),
            ("RECURSOS UTILIZADOS", f"{self.uso_recursos:.0f}% / 100%", col_uso),
            ("COSTO DE OPORTUNIDAD", f"1 Alim = {self.costo_oportunidad:.2f} Tech", CYAN),
            ("EFICIENCIA DE PARETO", "ÓPTIMO" if self.estado_fpp.startswith("EFICIENTE") else "SUBÓPTIMO", col_ut),
        ]

        ky = 438
        for lab, val, col in kpis:
            surface.blit(font_lab.render(lab, True, GRAY_LIGHT), (725, ky))
            surface.blit(font_kpi.render(val, True, col), (725, ky + 13))
            ky += 38

        self.notif.draw(surface)

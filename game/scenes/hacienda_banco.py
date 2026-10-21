# ============================================================
#  HACIENDA & BANCO CENTRAL – Fusión Macroeconómica Institucional
#  Integra: Gobierno, Impuestos e Inflación
# ============================================================
import math
import random
import pygame

from game.constants import *
from game.ui import Panel, Slider, Button, LineChart, ProgressBar, Notification, text, get_font
from game.sprites import sprite_gobierno, sprite_recibo, sprite_llama, sprite_moneda
from game.scenes.base import BaseScene
from game.feedback import update_scene_health


class HaciendaBancoScene(BaseScene):
    KEY = "hacienda_banco"
    TITLE = "Gabinete Económico: Hacienda y Banco Central"
    SUBTITLE = "Coordina impuestos, Curva de Laffer, presupuesto e inflación"

    def build(self):
        accent = self.accent
        self.notif = Notification()

        # Sprites
        self.sprite_gov = sprite_gobierno()
        self.sprite_rec = sprite_recibo()
        self.sprite_l = sprite_llama()
        self.sprite_m = sprite_moneda()

        # Sliders panel izquierdo
        # 1. Política Fiscal
        self.s_tasa_imp = Slider(60, 115, 280, "Tasa Impositiva", 5, 85, 28, color=RED, unit="%")
        self.s_gasto_pub = Slider(60, 175, 280, "Gasto Público", 40, 250, 110, color=PURPLE, unit="$M")

        # 2. Política Monetaria
        self.s_masa_m2 = Slider(60, 270, 280, "Inyección Monetaria (M2)", 0, 100, 35, color=ORANGE, unit="%")
        self.s_tasa_int = Slider(60, 330, 280, "Tasa de Interés de Referencia", 1, 25, 6, color=CYAN, unit="%")

        # Botones de medidas rápidas
        self.btn_freno = Button(60, 410, 135, 30, "Subir Tasa +2%", CYAN)
        self.btn_estimulo = Button(205, 410, 135, 30, "Inyectar Gasto +20", PURPLE)

        # Gráfico histórico de inflación
        self.chart_inf = LineChart(710, 85, 280, 125, "Inflación Anual (%)", color=RED)

        # Variables calculadas
        self.recaudacion = 0.0
        self.base_imponible = 0.0
        self.gasto = 0.0
        self.deficit = 0.0
        self.inflacion = 3.0
        self.poder_adq = 100.0
        self.aprobacion = 65.0
        self.tasa_optima_laffer = 42.0

        self._tick_timer = 0
        self.calcular_gabinete()

    def handle_event(self, event):
        self.s_tasa_imp.handle_event(event)
        self.s_gasto_pub.handle_event(event)
        self.s_masa_m2.handle_event(event)
        self.s_tasa_int.handle_event(event)

        if self.btn_freno.is_clicked(event):
            self.s_tasa_int.value = min(25, self.s_tasa_int.value + 2)
            self.notif.add("Banco Central: Tasa de interés subida +2% para enfriar precios.", CYAN)
        elif self.btn_estimulo.is_clicked(event):
            self.s_gasto_pub.value = min(250, self.s_gasto_pub.value + 20)
            self.notif.add("Ministerio de Hacienda: Gasto público expandido +$20M en obras.", PURPLE)

    def calcular_gabinete(self):
        t = self.s_tasa_imp.value
        g = self.s_gasto_pub.value
        m2 = self.s_masa_m2.value
        ti = self.s_tasa_int.value

        # Curva de Laffer:
        # La base imponible cae conforme la tasa impositiva sube por desincentivo y evasión
        # Base(t) = 450 * (1 - (t/100)^1.8)
        self.base_imponible = max(40.0, 450.0 * (1.0 - (t / 100.0) ** 1.8))
        self.recaudacion = (t / 100.0) * self.base_imponible
        self.gasto = float(g)

        # Balance Fiscal: Superávit si rec > gasto, Déficit si gasto > rec
        balance = self.recaudacion - self.gasto
        self.deficit = -balance  # Déficit positivo si falta dinero

        # Ecuación cuantitativa e inflación (MV = PY)
        # Presiones de demanda: M2 + déficit fiscal monetizado vs ancla de tasas de interés
        deficit_presion = max(0.0, self.deficit * 0.08)
        inflacion_calc = (m2 * 0.22 + deficit_presion) - (ti * 0.70) + 1.0
        self.inflacion = round(max(-2.0, min(50.0, inflacion_calc)), 1)

        # Poder adquisitivo real
        if self.inflacion > 0:
            self.poder_adq = max(20.0, min(100.0, 100.0 / (1.0 + self.inflacion * 0.05)))
        else:
            self.poder_adq = 100.0

        # Aprobación ciudadana:
        # Le gusta el gasto público y los bajos impuestos, pero detesta la inflación y el déficit excesivo
        aprob = 50.0 + (g * 0.12) - (t * 0.35) - (max(0.0, self.inflacion - 3.0) * 2.2) - (max(0.0, self.deficit) * 0.15)
        self.aprobacion = max(10.0, min(95.0, aprob))

    def update(self, dt):
        super().update(dt)
        mouse = pygame.mouse.get_pos()
        self.s_tasa_imp.update(mouse)
        self.s_gasto_pub.update(mouse)
        self.s_masa_m2.update(mouse)
        self.s_tasa_int.update(mouse)
        self.btn_freno.update(mouse)
        self.btn_estimulo.update(mouse)

        self.calcular_gabinete()

        self._tick_timer += dt
        if self._tick_timer >= 650:
            self._tick_timer = 0
            self.chart_inf.push(self.inflacion)

        update_scene_health(self.KEY, self, self.health_widget)

    def draw_laffer_curve(self, surface, rect):
        """Dibuja la Curva de Laffer en vivo mostrando el óptimo recaudatorio."""
        pygame.draw.rect(surface, PANEL_DARK, rect, border_radius=8)
        pygame.draw.rect(surface, GRAY_DARK, rect, 1, border_radius=8)

        text(surface, "CURVA DE LAFFER (Recaudación vs Impuesto)", rect.x + 12, rect.y + 8, PURPLE, 12, bold=True)

        ox, oy = rect.x + 40, rect.bottom - 28
        ax_w, ax_h = rect.w - 55, rect.h - 55

        pygame.draw.line(surface, GRAY, (ox, oy), (ox + ax_w, oy), 2)
        pygame.draw.line(surface, GRAY, (ox, oy), (ox, oy - ax_h), 2)

        text(surface, "t(%)", ox + ax_w - 14, oy + 4, GRAY_LIGHT, 10, bold=True)
        text(surface, "T($)", ox - 20, oy - ax_h - 4, GRAY_LIGHT, 10, bold=True)

        max_t = 100.0
        max_rec = 160.0

        def to_s(t_val, r_val):
            sx = ox + (t_val / max_t) * ax_w
            sy = oy - (min(max_rec, max(0.0, r_val)) / max_rec) * ax_h
            return int(sx), int(sy)

        # Dibujar curva de Laffer
        pts = []
        for step_t in range(0, 101, 2):
            base_t = 450.0 * (1.0 - (step_t / 100.0) ** 1.8)
            r_step = (step_t / 100.0) * max(0.0, base_t)
            pts.append(to_s(step_t, r_step))

        if len(pts) >= 2:
            pygame.draw.lines(surface, (220, 100, 220), False, pts, 2)

        # Zona Prohibida de Laffer (derecha del óptimo)
        opt_x = to_s(self.tasa_optima_laffer, 0)[0]
        zona_w = (ox + ax_w) - opt_x
        if zona_w > 0:
            z_surf = pygame.Surface((zona_w, ax_h), pygame.SRCALPHA)
            z_surf.fill((255, 40, 40, 25))
            surface.blit(z_surf, (opt_x, oy - ax_h))
            text(surface, "Zona Ineficiente", opt_x + 6, oy - ax_h + 8, (255, 120, 120), 10)

        # Punto actual
        cur_x, cur_y = to_s(self.s_tasa_imp.value, self.recaudacion)
        col_pt = GREEN if self.s_tasa_imp.value <= self.tasa_optima_laffer else RED
        pygame.draw.circle(surface, col_pt, (cur_x, cur_y), 6)
        text(surface, f"t={self.s_tasa_imp.value}%", cur_x - 14, cur_y - 14, col_pt, 10, bold=True)

    def draw_macro_canvas(self, surface, rect):
        """Dibuja el termómetro de inflación y el palacio institucional."""
        pygame.draw.rect(surface, PANEL_DARK, rect, border_radius=8)
        border_col = RED if self.inflacion > 10.0 else (GREEN if self.deficit <= 0 else CYAN)
        pygame.draw.rect(surface, border_col, rect, 2, border_radius=8)

        text(surface, "BANCO CENTRAL & TEMPERATURA DE PRECIOS", rect.x + 12, rect.y + 8, GRAY_LIGHT, 12, bold=True)

        # Termómetro de Inflación
        tx, ty = rect.x + 35, rect.y + 40
        th_w, th_h = 16, 120
        pygame.draw.rect(surface, GRAY_DARK, (tx, ty, th_w, th_h), border_radius=8)
        pygame.draw.rect(surface, GRAY, (tx, ty, th_w, th_h), 1, border_radius=8)

        inf_ratio = max(0.0, min(1.0, (self.inflacion + 2.0) / 25.0))
        fill_h = int(th_h * inf_ratio)
        col_inf = CYAN if self.inflacion < 0 else (GREEN if self.inflacion <= 4.0 else (YELLOW if self.inflacion <= 9.0 else RED))
        pygame.draw.rect(surface, col_inf, (tx, ty + th_h - fill_h, th_w, fill_h), border_radius=8)

        # Bulbo del termómetro
        pygame.draw.circle(surface, col_inf, (tx + th_w // 2, ty + th_h + 8), 12)
        pygame.draw.circle(surface, GRAY, (tx + th_w // 2, ty + th_h + 8), 12, 1)

        # Llama animada si la inflación es alta
        if self.inflacion >= 5.0:
            flame_y = ty + th_h - fill_h - 18 + int(math.sin(self.tick / 150) * 3)
            surface.blit(self.sprite_l, (tx - 8, flame_y))

        # Indicadores en el termómetro
        text(surface, f"{self.inflacion:.1f}%", tx + 24, ty + th_h - fill_h - 6, col_inf, 12, bold=True)
        text(surface, "Meta 3%", tx + 24, ty + th_h - int(th_h * 0.25) - 6, GREEN, 9)

        # Barra de Poder Adquisitivo
        bx, by = rect.x + 105, rect.y + 50
        text(surface, "Poder Adquisitivo Popular:", bx, by, GRAY_LIGHT, 11)
        pygame.draw.rect(surface, GRAY_DARK, (bx, by + 16, 180, 16), border_radius=4)
        pw = int(180 * (self.poder_adq / 100.0))
        col_pw = GREEN if self.poder_adq >= 80 else (YELLOW if self.poder_adq >= 50 else RED)
        if pw > 0:
            pygame.draw.rect(surface, col_pw, (bx, by + 16, pw, 16), border_radius=4)
        text(surface, f"{self.poder_adq:.0f}%", bx + 185, by + 17, col_pw, 11, bold=True)

        # Palacio / Arcas del Estado
        px, py = rect.x + 105, rect.y + 98
        pygame.draw.rect(surface, (35, 45, 65), (px, py, 180, 85), border_radius=6)
        pygame.draw.rect(surface, PURPLE, (px, py, 180, 85), 1, border_radius=6)

        surface.blit(self.sprite_gov, (px + 12, py + 12))
        surface.blit(self.sprite_m, (px + 140, py + 12))

        text(surface, "Arcas del Tesoro", px + 45, py + 14, PURPLE, 11, bold=True)
        bal_txt = f"Superávit: +${abs(self.deficit):.1f}M" if self.deficit <= 0 else f"Déficit: -${self.deficit:.1f}M"
        col_bal = GREEN if self.deficit <= 0 else RED
        text(surface, bal_txt, px + 45, py + 34, col_bal, 11, bold=True)
        text(surface, f"Base Gravable: ${self.base_imponible:.0f}M", px + 45, py + 54, GRAY_LIGHT, 10)

    def draw_content(self, surface):
        # 1. Panel Izquierdo: Controles
        p_left = Panel(40, 85, 330, 520, border=self.accent)
        p_left.draw(surface)

        text(surface, "Política Fiscal (Hacienda)", 55, 95, RED, 12, bold=True)
        self.s_tasa_imp.draw(surface)
        self.s_gasto_pub.draw(surface)

        text(surface, "Política Monetaria (Banco Central)", 55, 245, CYAN, 12, bold=True)
        self.s_masa_m2.draw(surface)
        self.s_tasa_int.draw(surface)

        text(surface, "Medidas Rápidas del Gabinete", 55, 385, YELLOW, 12, bold=True)
        self.btn_freno.draw(surface)
        self.btn_estimulo.draw(surface)

        text(surface, "• Curva de Laffer: Cobrar >42% desestimula la economía y recauda menos.", 55, 455, GRAY_LIGHT, 10)
        text(surface, "• Ecuación Cuantitativa: Más dinero circulando sin respaldo genera inflación.", 55, 475, GRAY_LIGHT, 10)

        # Sprite en cabecera izquierda
        surface.blit(self.sprite_rec, (330, 92))

        # 2. Columna Central: Curva de Laffer + Temperatura Macroeconómica
        laf_rect = pygame.Rect(390, 85, 305, 290)
        self.draw_laffer_curve(surface, laf_rect)

        macro_rect = pygame.Rect(390, 390, 305, 215)
        self.draw_macro_canvas(surface, macro_rect)

        # 3. Columna Derecha: Gráfico de Inflación + Health Widget + KPIs
        self.chart_inf.draw(surface)
        self.health_widget.draw(surface)

        # Panel de Métricas / KPIs
        p_kpi = Panel(710, 405, 280, 200, border=self.accent)
        p_kpi.draw(surface)
        text(surface, "Equilibrio Macroeconómico", 725, 415, self.accent, 12, bold=True)

        font_kpi = get_font(18, bold=True)
        font_lab = get_font(11)

        col_def = GREEN if self.deficit <= 0 else (YELLOW if self.deficit <= 15 else RED)
        col_inf = GREEN if self.inflacion <= 4.0 else (YELLOW if self.inflacion <= 8.0 else RED)

        kpis = [
            ("RECAUDACIÓN TRIBUTARIA", f"${self.recaudacion:.1f} M", CYAN),
            ("BALANCE FISCAL", f"{'-$' if self.deficit > 0 else '+$'}{abs(self.deficit):.1f} M", col_def),
            ("INFLACIÓN ANUAL", f"{self.inflacion:.1f}%", col_inf),
            ("APROBACIÓN CIUDADANA", f"{self.aprobacion:.0f}%",
             GREEN if self.aprobacion >= 60 else RED),
        ]

        ky = 438
        for lab, val, col in kpis:
            surface.blit(font_lab.render(lab, True, GRAY_LIGHT), (725, ky))
            surface.blit(font_kpi.render(val, True, col), (725, ky + 13))
            ky += 38

        self.notif.draw(surface)

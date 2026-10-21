# ============================================================
#  EMPRESA TYCOON – Fusión de Teoría de la Firma y Competencia
#  Integra: Fabricantes, Empresas y Competencia
# ============================================================
import math
import random
import pygame

from game.constants import *
from game.ui import Panel, Slider, Button, LineChart, Notification, text, get_font
from game.sprites import (sprite_empresa, sprite_fabrica, sprite_fabricante,
                          sprite_trofeo, sprite_moneda)
from game.scenes.base import BaseScene
from game.feedback import update_scene_health


class EmpresaTycoonScene(BaseScene):
    KEY = "empresa_tycoon"
    TITLE = "Tycoon Empresarial: Costos y Competencia"
    SUBTITLE = "Optimiza costos, escala productiva y márgenes según la estructura de mercado"

    def build(self):
        accent = self.accent
        self.notif = Notification()

        # Sprites
        self.sprite_emp = sprite_empresa()
        self.sprite_fac = sprite_fabrica()
        self.sprite_op = sprite_fabricante()
        self.sprite_m = sprite_moneda()

        # Estructura de mercado
        self.estructura = "COMPETENCIA"  # "COMPETENCIA", "OLIGOPOLIO", "MONOPOLIO"
        self.btn_comp = Button(60, 115, 90, 28, "C. Perfecta", GREEN)
        self.btn_oligo = Button(155, 115, 90, 28, "Oligopolio", BLUE)
        self.btn_mono = Button(250, 115, 90, 28, "Monopolio", PURPLE)

        # Sliders panel izquierdo
        self.s_capital = Slider(60, 180, 280, "Inversión en Maquinaria (CF)", 60, 300, 120, color=BLUE, unit="$")
        self.s_obreros = Slider(60, 235, 280, "Trabajadores Contratados", 4, 40, 12, color=BLUE, unit="pers")
        self.s_insumos = Slider(60, 290, 280, "Costo de Materia Prima", 5, 30, 12, color=ORANGE, unit="$/u")
        self.s_id = Slider(60, 345, 280, "I+D / Eficiencia Tecnológica", 0, 100, 25, color=CYAN, unit="pts")
        self.s_precio = Slider(60, 400, 280, "Precio de Venta Unitario", 10, 50, 25, color=YELLOW, unit="$")

        # Gráfico histórico de beneficios
        self.chart_ben = LineChart(710, 85, 280, 125, "Beneficio Neto ($)", color=GREEN)

        # Partículas de humo de la fábrica
        self.humo_particulas = []
        self._smoke_timer = 0
        self._chart_timer = 0

        # Variables calculadas
        self.q_prod = 0.0
        self.q_vend = 0.0
        self.costo_fijo = 0.0
        self.costo_var = 0.0
        self.costo_total = 0.0
        self.costo_medio = 0.0
        self.ingreso_total = 0.0
        self.beneficio = 0.0
        self.margen_pct = 0.0
        self.cuota_mercado = 0.0
        self.punto_equilibrio_q = 0.0

        self.simular_empresa()

    def handle_event(self, event):
        self.s_capital.handle_event(event)
        self.s_obreros.handle_event(event)
        self.s_insumos.handle_event(event)
        self.s_id.handle_event(event)
        if self.estructura != "COMPETENCIA":
            self.s_precio.handle_event(event)

        if self.btn_comp.is_clicked(event):
            self.estructura = "COMPETENCIA"
            self.notif.add("Mercado competitivo: eres precio-aceptante (P=$20).", GREEN)
        elif self.btn_oligo.is_clicked(event):
            self.estructura = "OLIGOPOLIO"
            self.notif.add("Oligopolio: compites contra 3 rivales agresivos.", BLUE)
        elif self.btn_mono.is_clicked(event):
            self.estructura = "MONOPOLIO"
            self.notif.add("Monopolio: poder exclusivo de fijación de precios.", PURPLE)

    def simular_empresa(self):
        k = self.s_capital.value
        l = self.s_obreros.value
        mp = self.s_insumos.value
        id_tec = self.s_id.value

        # Función de producción Cobb-Douglas: Q = A * (K^0.4) * (L^0.6)
        factor_a = 2.2 * (1.0 + id_tec * 0.01)
        self.q_prod = factor_a * (k ** 0.40) * (l ** 0.60)

        # Costos
        # CF: depreciación de maquinaria + estructura
        self.costo_fijo = k * 0.85
        # Salario por obrero $15, más costo variable de materias primas por unidad
        costo_var_unit = max(4.0, mp * (1.0 - id_tec * 0.003))
        self.costo_var = (l * 15.0) + (self.q_prod * costo_var_unit)
        self.costo_total = self.costo_fijo + self.costo_var
        self.costo_medio = self.costo_total / max(1.0, self.q_prod)

        # Determinación de Precio y Demanda según Estructura
        if self.estructura == "COMPETENCIA":
            # Precio fijado por el mercado
            precio_mercado = 22.0
            self.precio_efectivo = precio_mercado
            # Puedes vender todo lo producido a precio de mercado si eres competitivo
            self.q_vend = self.q_prod
            self.cuota_mercado = min(100.0, (self.q_prod / 600.0) * 100.0)
        elif self.estructura == "OLIGOPOLIO":
            self.precio_efectivo = self.s_precio.value
            # Si cobras más de $24 los rivales te quitan clientes
            demanda_potencial = max(0.0, 180.0 - 4.5 * self.precio_efectivo)
            self.q_vend = min(self.q_prod, demanda_potencial)
            self.cuota_mercado = max(5.0, min(80.0, 45.0 - (self.precio_efectivo - 22.0) * 3.0))
        else:  # MONOPOLIO
            self.precio_efectivo = self.s_precio.value
            demanda_mercado = max(0.0, 240.0 - 5.0 * self.precio_efectivo)
            self.q_vend = min(self.q_prod, demanda_mercado)
            self.cuota_mercado = 100.0

        # Ingresos y Beneficio
        self.ingreso_total = self.precio_efectivo * self.q_vend
        self.beneficio = self.ingreso_total - self.costo_total
        self.margen_pct = (self.beneficio / max(1.0, self.ingreso_total)) * 100.0

        # Punto de equilibrio Q_pe = CF / (P - CV_unit)
        margen_unit = max(0.5, self.precio_efectivo - costo_var_unit)
        self.punto_equilibrio_q = self.costo_fijo / margen_unit

    def update(self, dt):
        super().update(dt)
        mouse = pygame.mouse.get_pos()
        self.s_capital.update(mouse)
        self.s_obreros.update(mouse)
        self.s_insumos.update(mouse)
        self.s_id.update(mouse)
        if self.estructura != "COMPETENCIA":
            self.s_precio.update(mouse)

        self.btn_comp.update(mouse)
        self.btn_oligo.update(mouse)
        self.btn_mono.update(mouse)

        self.simular_empresa()

        # Partículas de humo
        self._smoke_timer += dt
        if self._smoke_timer >= 120 and self.q_prod > 10:
            self._smoke_timer = 0
            self.humo_particulas.append([432, 420, random.uniform(-0.4, 0.4), random.uniform(-1.0, -1.8), 1.0])

        for p in self.humo_particulas:
            p[0] += p[2] * dt * 0.05
            p[1] += p[3] * dt * 0.05
            p[4] -= dt * 0.0012
        self.humo_particulas = [p for p in self.humo_particulas if p[4] > 0]

        self._chart_timer += dt
        if self._chart_timer >= 650:
            self._chart_timer = 0
            self.chart_ben.push(self.beneficio)

        update_scene_health(self.KEY, self, self.health_widget)

    def draw_breakeven_chart(self, surface, rect):
        """Dibuja el gráfico de ingresos vs costos y Punto de Equilibrio (Break-Even)."""
        pygame.draw.rect(surface, PANEL_DARK, rect, border_radius=8)
        pygame.draw.rect(surface, GRAY_DARK, rect, 1, border_radius=8)

        text(surface, "PUNTO DE EQUILIBRIO (Break-Even)", rect.x + 12, rect.y + 8, BLUE, 12, bold=True)

        ox, oy = rect.x + 40, rect.bottom - 28
        ax_w, ax_h = rect.w - 55, rect.h - 55

        pygame.draw.line(surface, GRAY, (ox, oy), (ox + ax_w, oy), 2)
        pygame.draw.line(surface, GRAY, (ox, oy), (ox, oy - ax_h), 2)

        text(surface, "Q", ox + ax_w - 6, oy + 4, GRAY_LIGHT, 10, bold=True)
        text(surface, "$", ox - 20, oy - ax_h - 4, GRAY_LIGHT, 10, bold=True)

        max_q = 200.0
        max_val = 3000.0

        def to_s(q, val):
            sx = ox + (min(max_q, max(0.0, q)) / max_q) * ax_w
            sy = oy - (min(max_val, max(0.0, val)) / max_val) * ax_h
            return int(sx), int(sy)

        # 1. Línea Costo Fijo (horizontal punteada)
        cf_y = to_s(0, self.costo_fijo)[1]
        pygame.draw.line(surface, (150, 100, 100), (ox, cf_y), (ox + ax_w, cf_y), 1)
        text(surface, f"CF=${self.costo_fijo:.0f}", ox + ax_w - 60, cf_y - 12, (180, 120, 120), 10)

        # 2. Curva Costo Total (rojo)
        cv_u = (self.costo_var / max(1.0, self.q_prod))
        pts_ct = [to_s(0, self.costo_fijo), to_s(max_q, self.costo_fijo + cv_u * max_q)]
        pygame.draw.line(surface, RED, pts_ct[0], pts_ct[1], 2)
        text(surface, "CT", pts_ct[1][0] - 20, pts_ct[1][1] - 12, RED, 10, bold=True)

        # 3. Curva Ingreso Total (verde)
        pts_it = [to_s(0, 0), to_s(max_q, self.precio_efectivo * max_q)]
        pygame.draw.line(surface, GREEN, pts_it[0], pts_it[1], 2)
        text(surface, "IT", pts_it[1][0] - 20, pts_it[1][1] - 12, GREEN, 10, bold=True)

        # Punto de equilibrio
        if 0 < self.punto_equilibrio_q <= max_q:
            pe_x, pe_y = to_s(self.punto_equilibrio_q, self.precio_efectivo * self.punto_equilibrio_q)
            pygame.draw.circle(surface, YELLOW, (pe_x, pe_y), 5)
            pygame.draw.line(surface, GRAY_DARK, (pe_x, oy), (pe_x, pe_y), 1)
            text(surface, f"Q*={self.punto_equilibrio_q:.0f}", pe_x - 14, oy + 4, YELLOW, 9)

        # Operación actual
        cur_x, cur_y = to_s(self.q_prod, self.ingreso_total)
        col_op = GREEN if self.beneficio >= 0 else RED
        pygame.draw.circle(surface, col_op, (cur_x, cur_y), 6)
        text(surface, f"Q={self.q_prod:.0f}", cur_x - 10, cur_y - 14, col_op, 10, bold=True)

    def draw_factory(self, surface, rect):
        """Dibuja una fábrica industrial pixel-art interactiva."""
        pygame.draw.rect(surface, PANEL_DARK, rect, border_radius=8)
        pygame.draw.rect(surface, BLUE, rect, 2, border_radius=8)
        text(surface, "PLANTA INDUSTRIAL Y LOGÍSTICA", rect.x + 12, rect.y + 8, GRAY_LIGHT, 12, bold=True)

        # Suelo
        pygame.draw.line(surface, GRAY_DARK, (rect.x + 10, rect.bottom - 20), (rect.right - 10, rect.bottom - 20), 2)

        # Edificio de la fábrica
        bx, by = rect.x + 30, rect.bottom - 95
        pygame.draw.rect(surface, (45, 55, 75), (bx, by, 90, 75), border_radius=3)
        pygame.draw.rect(surface, (30, 40, 55), (bx, by, 90, 75), 2, border_radius=3)

        # Chimenea
        pygame.draw.rect(surface, (60, 70, 90), (bx + 12, by - 25, 18, 25))
        # Humo
        for p in self.humo_particulas:
            alpha = int(p[4] * 200)
            hs = pygame.Surface((8, 8), pygame.SRCALPHA)
            hs.fill((160, 160, 180, alpha))
            surface.blit(hs, (int(p[0]), int(p[1])))

        # Ventanas iluminadas
        for wx in range(3):
            for wy in range(2):
                col_win = YELLOW if self.q_prod > 20 else GRAY_DARK
                pygame.draw.rect(surface, col_win, (bx + 14 + wx * 24, by + 18 + wy * 24, 14, 12))

        # Sprites operarios y máquinas
        surface.blit(self.sprite_fac, (rect.x + 140, rect.bottom - 80))
        surface.blit(self.sprite_op, (rect.x + 215, rect.bottom - 55))

        # Cajas producidas
        num_cajas = min(8, int(self.q_prod // 15))
        cx = rect.right - 45
        for i in range(num_cajas):
            cy = rect.bottom - 28 - (i % 4) * 12
            col_box = (190, 140, 80)
            pygame.draw.rect(surface, col_box, (cx - (i // 4) * 14, cy, 11, 10))
            pygame.draw.rect(surface, (130, 90, 40), (cx - (i // 4) * 14, cy, 11, 10), 1)

    def draw_content(self, surface):
        # 1. Panel Izquierdo: Controles
        p_left = Panel(40, 85, 330, 520, border=self.accent)
        p_left.draw(surface)

        text(surface, "Estructura de Mercado", 55, 95, self.accent, 12, bold=True)
        self.btn_comp.draw(surface)
        self.btn_oligo.draw(surface)
        self.btn_mono.draw(surface)

        text(surface, "Factores de Producción", 55, 160, BLUE, 12, bold=True)
        self.s_capital.draw(surface)
        self.s_obreros.draw(surface)
        self.s_insumos.draw(surface)
        self.s_id.draw(surface)

        text(surface, "Comercialización", 55, 380, YELLOW, 12, bold=True)
        if self.estructura != "COMPETENCIA":
            self.s_precio.draw(surface)
        else:
            text(surface, "✔ C. Perfecta: Precio impuesto por el mercado ($22.0).", 55, 420, GRAY_LIGHT, 11)

        # Sprites en el encabezado izquierdo
        surface.blit(self.sprite_emp, (330, 92))

        # 2. Columna Central: Break-Even + Fábrica interactiva
        be_rect = pygame.Rect(390, 85, 305, 290)
        self.draw_breakeven_chart(surface, be_rect)

        fac_rect = pygame.Rect(390, 390, 305, 215)
        self.draw_factory(surface, fac_rect)

        # 3. Columna Derecha: Gráfico de Beneficio + Health Widget + KPIs
        self.chart_ben.draw(surface)
        self.health_widget.draw(surface)

        # Panel de Métricas / KPIs
        p_kpi = Panel(710, 405, 280, 200, border=self.accent)
        p_kpi.draw(surface)
        text(surface, "Rendimiento Financiero", 725, 415, self.accent, 12, bold=True)

        font_kpi = get_font(18, bold=True)
        font_lab = get_font(11)

        col_ben = GREEN if self.beneficio >= 0 else RED
        kpis = [
            ("BENEFICIO NETO", f"${self.beneficio:.1f}", col_ben),
            ("MARGEN OPERATIVO", f"{self.margen_pct:.1f}%", col_ben),
            ("PRODUCCIÓN vs VENTAS", f"{self.q_prod:.0f} / {self.q_vend:.0f} u", CYAN),
            ("COSTO MEDIO UNITARIO", f"${self.costo_medio:.1f}", ORANGE),
        ]

        ky = 438
        for lab, val, col in kpis:
            surface.blit(font_lab.render(lab, True, GRAY_LIGHT), (725, ky))
            surface.blit(font_kpi.render(val, True, col), (725, ky + 13))
            ky += 38

        self.notif.draw(surface)

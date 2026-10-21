# ============================================================
#  GRAN MERCADO – Fusión Microeconómica Total
#  Integra: Oferta, Demanda, Precios, Equilibrio y Mercado
# ============================================================
import math
import random
import pygame

from game.constants import *
from game.ui import Panel, Slider, Button, LineChart, Notification, text, get_font
from game.sprites import (sprite_balanza, sprite_consumidor,
                          sprite_fabricante, sprite_moneda, sprite_flecha_arriba)
from game.scenes.base import BaseScene
from game.feedback import update_scene_health


class MercadoAgente:
    def __init__(self, tipo, bounds):
        self.tipo = tipo  # "comprador" o "vendedor"
        self.bounds = bounds
        self.x = random.uniform(bounds.x + 20, bounds.right - 20)
        self.y = random.uniform(bounds.y + 40, bounds.bottom - 20)
        self.vx = random.uniform(-0.8, 0.8)
        self.vy = random.uniform(-0.6, 0.6)
        self.state = "normal"  # "feliz", "enfadado", "esperando"

    def update(self, dt, estado_mercado):
        self.x += self.vx * (dt * 0.05)
        self.y += self.vy * (dt * 0.05)

        if self.x < self.bounds.x + 10 or self.x > self.bounds.right - 10:
            self.vx *= -1
            self.x = max(self.bounds.x + 10, min(self.bounds.right - 10, self.x))
        if self.y < self.bounds.y + 35 or self.y > self.bounds.bottom - 10:
            self.vy *= -1
            self.y = max(self.bounds.y + 35, min(self.bounds.bottom - 10, self.y))

        if estado_mercado == "EQUILIBRIO":
            self.state = "feliz"
        elif estado_mercado == "ESCASEZ":
            self.state = "enfadado" if self.tipo == "comprador" else "normal"
        else:
            self.state = "enfadado" if self.tipo == "vendedor" else "normal"

    def draw(self, surface, sprite_c, sprite_v):
        spr = sprite_c if self.tipo == "comprador" else sprite_v
        surface.blit(spr, (int(self.x) - 10, int(self.y) - 14))

        if self.state == "feliz":
            text(surface, "★", int(self.x) + 4, int(self.y) - 20, YELLOW, 10, bold=True)
        elif self.state == "enfadado":
            text(surface, "!", int(self.x) + 4, int(self.y) - 20, RED, 12, bold=True)


class GranMercadoScene(BaseScene):
    KEY = "gran_mercado"
    TITLE = "El Gran Mercado: Microeconomía Total"
    SUBTITLE = "Coordina Oferta, Demanda, Precios y Equilibrio Marshalliano"

    def build(self):
        accent = self.accent
        self.notif = Notification()

        # Sprites
        self.sprite_b = sprite_balanza()
        self.sprite_c = sprite_consumidor()
        self.sprite_v = sprite_fabricante()
        self.sprite_m = sprite_moneda()

        # Sliders panel izquierdo
        # 1. Demanda
        self.s_ingreso = Slider(60, 115, 290, "Ingreso Consumidores", 40, 200, 100, color=CYAN, unit="$")
        self.s_gustos = Slider(60, 170, 290, "Preferencia / Tendencia", 1, 10, 5, color=CYAN, unit="pts")

        # 2. Oferta
        self.s_insumos = Slider(60, 240, 290, "Costo de Materias Primas", 10, 80, 35, color=GREEN, unit="$")
        self.s_tecnol = Slider(60, 295, 290, "Tecnología de Producción", 1, 10, 5, color=GREEN, unit="pts")

        # 3. Regulación de Precios
        self.modo_precio = "LIBRE"  # "LIBRE", "CONTROL_MAX", "CONTROL_MIN", "FIJO"
        self.s_precio_fijo = Slider(60, 420, 290, "Precio Regulado Manual", 5, 50, 20, color=YELLOW, unit="$")

        self.btn_modo_libre = Button(60, 360, 140, 28, "Libre Mercado", GREEN)
        self.btn_modo_max = Button(210, 360, 140, 28, "Precio Máximo", RED)
        self.btn_modo_min = Button(60, 392, 140, 28, "Precio Mínimo", BLUE)
        self.btn_modo_fijo = Button(210, 392, 140, 28, "Fijar Manual", ORANGE)

        # Historial de precios y transacciones
        self.chart_hist = LineChart(710, 85, 280, 125, "Historial Precio ($)", color=YELLOW)

        # Canvas plaza de agentes
        self.plaza_rect = pygame.Rect(390, 390, 305, 215)
        self.agentes = []
        for _ in range(7):
            self.agentes.append(MercadoAgente("comprador", self.plaza_rect))
        for _ in range(6):
            self.agentes.append(MercadoAgente("vendedor", self.plaza_rect))

        # Variables calculadas
        self.p_eq = 20.0
        self.q_eq = 50.0
        self.p_actual = 20.0
        self.q_demanda = 50.0
        self.q_oferta = 50.0
        self.q_trans = 50.0
        self.gap_precio = 0.0
        self.exceso_tipo = "EQUILIBRIO"
        self.exceso_val = 0.0
        self.excedente_total = 1000.0
        self.satisfaccion = 90.0

        self._tick_timer = 0
        self.calcular_mercado()

    def handle_event(self, event):
        self.s_ingreso.handle_event(event)
        self.s_gustos.handle_event(event)
        self.s_insumos.handle_event(event)
        self.s_tecnol.handle_event(event)
        if self.modo_precio != "LIBRE":
            self.s_precio_fijo.handle_event(event)

        if self.btn_modo_libre.is_clicked(event):
            self.modo_precio = "LIBRE"
            self.notif.add("Mecanismo de precios libre: ajuste automático a P*", GREEN)
        elif self.btn_modo_max.is_clicked(event):
            self.modo_precio = "CONTROL_MAX"
            self.s_precio_fijo.value = max(5, int(self.p_eq - 7))
            self.notif.add(f"Precio Máximo decretado en ${self.s_precio_fijo.value:.1f}", RED)
        elif self.btn_modo_min.is_clicked(event):
            self.modo_precio = "CONTROL_MIN"
            self.s_precio_fijo.value = min(50, int(self.p_eq + 7))
            self.notif.add(f"Precio Mínimo de sustentación en ${self.s_precio_fijo.value:.1f}", BLUE)
        elif self.btn_modo_fijo.is_clicked(event):
            self.modo_precio = "FIJO"
            self.notif.add("Fijación de precio manual activa.", ORANGE)

    def calcular_mercado(self):
        ing = self.s_ingreso.value
        gus = self.s_gustos.value
        ins = self.s_insumos.value
        tec = self.s_tecnol.value

        # Parámetros Marshallianos
        # Qd(P) = intercepto_d - pendiente_d * P
        intercepto_d = 20.0 + (ing * 0.45) + (gus * 6.0)
        pendiente_d = 2.4

        # Qs(P) = intercepto_s + pendiente_s * P
        intercepto_s = -10.0 - (ins * 0.40) + (tec * 6.5)
        pendiente_s = 2.6

        # Equilibrio P* = (int_d - int_s) / (pend_d + pend_s)
        divisor = pendiente_d + pendiente_s
        self.p_eq = max(3.0, (intercepto_d - intercepto_s) / divisor)
        self.q_eq = max(5.0, intercepto_d - pendiente_d * self.p_eq)

        # Precio Efectivo según modo
        if self.modo_precio == "LIBRE":
            self.p_actual = self.p_eq
        elif self.modo_precio == "CONTROL_MAX":
            self.p_actual = min(self.s_precio_fijo.value, self.p_eq)
        elif self.modo_precio == "CONTROL_MIN":
            self.p_actual = max(self.s_precio_fijo.value, self.p_eq)
        else:  # FIJO
            self.p_actual = self.s_precio_fijo.value

        # Cantidades
        self.q_demanda = max(0.0, intercepto_d - pendiente_d * self.p_actual)
        self.q_oferta = max(0.0, intercepto_s + pendiente_s * self.p_actual)
        self.q_trans = min(self.q_demanda, self.q_oferta)

        # Excesos
        diff = self.q_demanda - self.q_oferta
        self.gap_precio = abs(self.p_actual - self.p_eq)

        if abs(diff) < 2.0:
            self.exceso_tipo = "EQUILIBRIO"
            self.exceso_val = 0.0
            self.satisfaccion = 95.0
        elif diff > 0:
            self.exceso_tipo = "ESCASEZ"
            self.exceso_val = diff
            self.satisfaccion = max(20.0, 90.0 - diff * 1.5)
        else:
            self.exceso_tipo = "SOBREOFERTA"
            self.exceso_val = -diff
            self.satisfaccion = max(25.0, 90.0 - abs(diff) * 1.2)

        # Excedentes aproximados
        p_max_res = intercepto_d / pendiente_d
        excedente_cons = 0.5 * max(0.0, p_max_res - self.p_actual) * self.q_trans
        excedente_prod = 0.5 * max(0.0, self.p_actual - max(0, -intercepto_s / pendiente_s)) * self.q_trans
        self.excedente_total = excedente_cons + excedente_prod

    def update(self, dt):
        super().update(dt)
        mouse = pygame.mouse.get_pos()
        self.s_ingreso.update(mouse)
        self.s_gustos.update(mouse)
        self.s_insumos.update(mouse)
        self.s_tecnol.update(mouse)
        if self.modo_precio != "LIBRE":
            self.s_precio_fijo.update(mouse)

        self.btn_modo_libre.update(mouse)
        self.btn_modo_max.update(mouse)
        self.btn_modo_min.update(mouse)
        self.btn_modo_fijo.update(mouse)

        self.calcular_mercado()

        for a in self.agentes:
            a.update(dt, self.exceso_tipo)

        self._tick_timer += dt
        if self._tick_timer >= 600:
            self._tick_timer = 0
            self.chart_hist.push(self.p_actual)

        update_scene_health(self.KEY, self, self.health_widget)

    def draw_marshall_chart(self, surface, rect):
        """Dibuja el gráfico canónico de tijeras Marshallianas P vs Q."""
        pygame.draw.rect(surface, PANEL_DARK, rect, border_radius=8)
        pygame.draw.rect(surface, GRAY_DARK, rect, 1, border_radius=8)

        text(surface, "TIJERAS MARSHALLIANAS (P vs Q)", rect.x + 12, rect.y + 8, CYAN, 12, bold=True)

        # Ejes
        ox, oy = rect.x + 35, rect.bottom - 28
        ax_w, ax_h = rect.w - 50, rect.h - 55

        pygame.draw.line(surface, GRAY, (ox, oy), (ox + ax_w, oy), 2)
        pygame.draw.line(surface, GRAY, (ox, oy), (ox, oy - ax_h), 2)

        text(surface, "Q", ox + ax_w - 8, oy + 4, GRAY_LIGHT, 10, bold=True)
        text(surface, "P($)", ox - 26, oy - ax_h - 4, GRAY_LIGHT, 10, bold=True)

        max_p = 50.0
        max_q = 120.0

        def to_screen(q, p):
            sx = ox + (min(max_q, max(0.0, q)) / max_q) * ax_w
            sy = oy - (min(max_p, max(0.0, p)) / max_p) * ax_h
            return int(sx), int(sy)

        # Curva de Demanda D (azul/roja)
        pts_d = []
        for i in range(11):
            p_step = i * (max_p / 10.0)
            q_step = max(0.0, (20.0 + self.s_ingreso.value * 0.45 + self.s_gustos.value * 6.0) - 2.4 * p_step)
            pts_d.append(to_screen(q_step, p_step))
        if len(pts_d) >= 2:
            pygame.draw.lines(surface, (230, 80, 80), False, pts_d, 2)
            text(surface, "D", pts_d[-1][0] + 4, pts_d[-1][1] - 4, (230, 80, 80), 11, bold=True)

        # Curva de Oferta S (verde)
        pts_s = []
        for i in range(11):
            p_step = i * (max_p / 10.0)
            q_step = max(0.0, (-10.0 - self.s_insumos.value * 0.40 + self.s_tecnol.value * 6.5) + 2.6 * p_step)
            pts_s.append(to_screen(q_step, p_step))
        if len(pts_s) >= 2:
            pygame.draw.lines(surface, (80, 220, 80), False, pts_s, 2)
            text(surface, "S", pts_s[-1][0] + 4, pts_s[-1][1] - 4, (80, 220, 80), 11, bold=True)

        # Punto de equilibrio natural (P*, Q*)
        eq_x, eq_y = to_screen(self.q_eq, self.p_eq)
        pygame.draw.circle(surface, YELLOW, (eq_x, eq_y), 5)
        # Líneas punteadas al equilibrio
        pygame.draw.line(surface, GRAY_DARK, (ox, eq_y), (eq_x, eq_y), 1)
        pygame.draw.line(surface, GRAY_DARK, (eq_x, oy), (eq_x, eq_y), 1)
        text(surface, f"P*=${self.p_eq:.1f}", ox + 4, eq_y - 12, YELLOW, 10)

        # Línea de Precio Actual
        act_y = to_screen(0, self.p_actual)[1]
        col_act = GREEN if self.exceso_tipo == "EQUILIBRIO" else (RED if self.exceso_tipo == "ESCASEZ" else BLUE)
        pygame.draw.line(surface, col_act, (ox, act_y), (ox + ax_w, act_y), 2)
        text(surface, f"P Vigente: ${self.p_actual:.1f}", ox + ax_w - 90, act_y - 12, col_act, 10, bold=True)

        # Sombreado de Exceso / Escasez
        if self.exceso_tipo != "EQUILIBRIO":
            x_qd = to_screen(self.q_demanda, self.p_actual)[0]
            x_qs = to_screen(self.q_oferta, self.p_actual)[0]
            left_x, right_x = min(x_qd, x_qs), max(x_qd, x_qs)
            gap_w = right_x - left_x
            if gap_w > 2:
                gap_surf = pygame.Surface((gap_w, 14), pygame.SRCALPHA)
                gap_col = (255, 60, 60, 90) if self.exceso_tipo == "ESCASEZ" else (80, 140, 255, 90)
                gap_surf.fill(gap_col)
                surface.blit(gap_surf, (left_x, act_y - 7))
                msg = f"Escasez (-{self.exceso_val:.0f}u)" if self.exceso_tipo == "ESCASEZ" else f"Exceso (+{self.exceso_val:.0f}u)"
                text(surface, msg, left_x + 4, act_y + 4, RED if self.exceso_tipo == "ESCASEZ" else CYAN, 10, bold=True)

    def draw_content(self, surface):
        # 1. Panel Izquierdo: Controles
        p_left = Panel(40, 85, 330, 520, border=self.accent)
        p_left.draw(surface)

        text(surface, "Demanda (Familias)", 55, 95, CYAN, 12, bold=True)
        self.s_ingreso.draw(surface)
        self.s_gustos.draw(surface)

        text(surface, "Oferta (Empresas)", 55, 220, GREEN, 12, bold=True)
        self.s_insumos.draw(surface)
        self.s_tecnol.draw(surface)

        text(surface, "Regulación de Precios", 55, 340, YELLOW, 12, bold=True)
        self.btn_modo_libre.draw(surface)
        self.btn_modo_max.draw(surface)
        self.btn_modo_min.draw(surface)
        self.btn_modo_fijo.draw(surface)

        if self.modo_precio != "LIBRE":
            self.s_precio_fijo.draw(surface)
        else:
            text(surface, "✔ Modo Libre Mercado: El precio se vacía en P* automáticamente.",
                 55, 435, GRAY_LIGHT, 11)

        # Sprites en el encabezado izquierdo
        surface.blit(self.sprite_b, (325, 92))

        # 2. Columna Central: Gráfico Marshalliano + Plaza de Agentes
        marshall_rect = pygame.Rect(390, 85, 305, 290)
        self.draw_marshall_chart(surface, marshall_rect)

        # Plaza de Mercado animada
        pygame.draw.rect(surface, PANEL_DARK, self.plaza_rect, border_radius=8)
        border_col = GREEN if self.exceso_tipo == "EQUILIBRIO" else (RED if self.exceso_tipo == "ESCASEZ" else BLUE)
        pygame.draw.rect(surface, border_col, self.plaza_rect, 2, border_radius=8)
        text(surface, "PLAZA DE COMERCIO VIVO", self.plaza_rect.x + 12, self.plaza_rect.y + 8, GRAY_LIGHT, 12, bold=True)

        for a in self.agentes:
            a.draw(surface, self.sprite_c, self.sprite_v)

        # Insignia de estado de la plaza
        status_txt = f"ESTADO: {self.exceso_tipo}"
        status_bg = GREEN if self.exceso_tipo == "EQUILIBRIO" else (RED if self.exceso_tipo == "ESCASEZ" else ORANGE)
        s_rect = pygame.Rect(self.plaza_rect.x + 12, self.plaza_rect.bottom - 26, 170, 18)
        pygame.draw.rect(surface, status_bg, s_rect, border_radius=4)
        text(surface, status_txt, s_rect.x + 6, s_rect.y + 3, BLACK, 10, bold=True)

        # 3. Columna Derecha: Gráfico de Línea + Feedback Widget + KPIs
        self.chart_hist.draw(surface)
        self.health_widget.draw(surface)

        # Panel de Métricas / KPIs
        p_kpi = Panel(710, 405, 280, 200, border=self.accent)
        p_kpi.draw(surface)
        text(surface, "Métricas del Mercado", 725, 415, self.accent, 12, bold=True)

        font_kpi = get_font(18, bold=True)
        font_lab = get_font(11)

        kpis = [
            ("PRECIO DE EQUILIBRIO", f"${self.p_eq:.1f}", YELLOW),
            ("CANTIDAD TRANSADA", f"{self.q_trans:.0f} u", GREEN),
            ("EXCEDENTE SOCIAL", f"${self.excedente_total:.0f}", CYAN),
            ("SATISFACCIÓN CONSUMIDOR", f"{self.satisfaccion:.0f}%",
             GREEN if self.satisfaccion >= 75 else RED),
        ]

        ky = 438
        for lab, val, col in kpis:
            surface.blit(font_lab.render(lab, True, GRAY_LIGHT), (725, ky))
            surface.blit(font_kpi.render(val, True, col), (725, ky + 13))
            ky += 38

        self.notif.draw(surface)

# ============================================================
#  ESCENA: ECOTYCOON – Minijuego de Gestión Económica Total
#  El jugador gobierna la economía durante 8 trimestres (2 años).
#  Integra todos los modelos: política fiscal, monetaria,
#  mercado, producción, inflación, Laffer y bienestar social.
# ============================================================
import pygame
import math
import random
from game.scenes.base import BaseScene
from game.constants import *
from game.ui import (Slider, Panel, LineChart, Notification,
                     Button, ProgressBar, text, get_font)
from game.sprites import sprite_trofeo, sprite_gobierno, sprite_moneda, sprite_fabrica
from game.audio import audio


class EcoTycoonScene(BaseScene):
    KEY      = "ecotycoon"
    TITLE    = "EcoTycoon: Desafío de Gestión Total"
    SUBTITLE = "Gobierna la nación durante 8 trimestres: equilibra crecimiento, inflación y bienestar"

    EVENTOS_TRIMESTRALES = {
        2: {
            "titulo": "⚡ SHOCK PETROLERO MUNDIAL",
            "desc": "El precio internacional del crudo se dispara un 40%. Aumentan los costos de insumos para las fábricas y hay presión inflacionaria externa.",
            "impacto": "Inflación +2.5%, Costos de producción +15%",
            "efecto_pi": 2.5,
            "efecto_pib": -3.0
        },
        3: {
            "titulo": "🚀 REVOLUCIÓN TECNOLÓGICA",
            "desc": "Las empresas nacionales adoptan automatización e inteligencia artificial. La productividad de los fabricantes se dispara.",
            "impacto": "PIB +4.5%, Oferta disponible +20%",
            "efecto_pi": -1.0,
            "efecto_pib": 4.5
        },
        4: {
            "titulo": "🛍 BOOM DE CONSUMO INTERNO",
            "desc": "Confianza del consumidor al alza. Las familias gastan sus ahorros elevando la demanda agregada y el volumen de mercado.",
            "impacto": "Demanda +25%, Recaudación fiscal +10%",
            "efecto_pi": 1.8,
            "efecto_pib": 3.5
        },
        5: {
            "titulo": "🌐 FUGA DE CAPITALES GLOBAL",
            "desc": "Incertidumbre en los mercados internacionales. Los inversores extranjeros retiran fondos buscando refugios seguros.",
            "impacto": "Reservas -$150M, Desempleo +1.5%",
            "efecto_pi": 1.2,
            "efecto_pib": -2.5
        },
        6: {
            "titulo": "🌾 SEQUÍA Y ESCASEZ DE ALIMENTOS",
            "desc": "Malas cosechas provocan escasez en el sector primario. Sube la canasta básica y se requiere apoyo social focalizado.",
            "impacto": "Costo de vida sube, Aprobación -8%",
            "efecto_pi": 2.0,
            "efecto_pib": -2.0
        },
        7: {
            "titulo": "🤝 TRATADO DE LIBRE COMERCIO",
            "desc": "Firma de un acuerdo arancelario con potencias extranjeras. Nuevas oportunidades para empresas competitivas.",
            "impacto": "Mercado expandido +20%, PIB +4.0%",
            "efecto_pi": -0.8,
            "efecto_pib": 4.0
        },
    }

    def build(self):
        accent = self.accent
        self.MAX_QUARTERS = 8
        self.quarter = 1

        # ── Sliders de Políticas Económicas (Las 4 palancas del gobierno) ──
        self.sliders = [
            Slider(60, 160, 280, "Tasa de Interés (%)",    0,  25,  6,
                   color=CYAN,   unit="%"),
            Slider(60, 215, 280, "Gasto Público (%PIB)",  10,  50, 24,
                   color=PURPLE, unit="%"),
            Slider(60, 270, 280, "Tasa Impositiva (%)",   10,  60, 28,
                   color=RED,    unit="%"),
            Slider(60, 325, 280, "Incentivo a Producción", 0,  40, 15,
                   color=GREEN,  unit="%"),
        ]

        # Botón para ejecutar el trimestre
        self.btn_next_q = Button(40, 400, 330, 42, "Avanzar Trimestre ▶",
                                 color=YELLOW)

        # Gráficas históricas
        self.chart_pib = LineChart(400, 85, 280, 120, "PIB (Crecimiento)",
                                   color=PURPLE)
        self.chart_inf = LineChart(710, 85, 280, 120, "Inflación (%)",
                                   color=RED)

        self.notif   = Notification()
        self.sprite_g = sprite_gobierno()
        self.sprite_t = sprite_trofeo()

        # Variables macroeconómicas
        self.pib         = 100.0
        self.inflacion   = 3.2
        self.desempleo   = 5.5
        self.poder_adq   = 100.0
        self.deficit     = 2.0
        self.aprobacion  = 65.0
        self.reservas    = 1000.0  # Millones de $

        self.chart_pib.push(self.pib)
        self.chart_inf.push(self.inflacion)

        # Estados de juego: "PLAYING", "GAMEOVER", "VICTORY"
        self.game_state   = "PLAYING"
        self.game_over_reason = ""
        self.game_over_title  = ""
        self.game_over_lesson = ""

        # Modal de evento trimestral
        self.active_event = None

        # Botones de fin de juego
        self.btn_retry = Button(SCREEN_W // 2 - 170, 480, 160, 42, "Reintentar ↻", CYAN)
        self.btn_exit  = Button(SCREEN_W // 2 + 10,  480, 160, 42, "Menú Principal", GRAY)

    def _trigger_next_quarter(self):
        if self.game_state != "PLAYING":
            return

        tasa  = self.sliders[0].value
        gasto = self.sliders[1].value
        imp   = self.sliders[2].value
        inc   = self.sliders[3].value

        # ── 1. CÁLCULO DE LA INFLACIÓN ──
        # Masa monetaria y presiones de gasto vs freno de tasas
        shock_pi = self.active_event.get("efecto_pi", 0.0) if self.active_event else 0.0
        pi_calc = (gasto * 0.18 + inc * 0.08) - (tasa * 0.70) - 1.2 + shock_pi
        self.inflacion = round(max(-3.0, min(50.0, pi_calc)), 1)

        # ── 2. PODER ADQUISITIVO ──
        if self.inflacion < 0.0:
            self.poder_adq = min(120.0, round(self.poder_adq + abs(self.inflacion) * 0.8, 1))
        elif self.inflacion <= 4.0:
            self.poder_adq = min(100.0, round(self.poder_adq + 1.5, 1))
        else:
            self.poder_adq = max(5.0, round(self.poder_adq - (self.inflacion - 3.5) * 0.7, 1))

        # ── 3. PIB Y PRODUCCIÓN (Cobb-Douglas & Keynes) ──
        shock_pib = self.active_event.get("efecto_pib", 0.0) if self.active_event else 0.0
        # Curva de Laffer en la actividad privada
        factor_laffer = max(0.15, 1.0 - ((imp / 65.0) ** 2.2))
        crec_pib = (gasto * 0.25 + inc * 0.35 + factor_laffer * 15.0 - tasa * 0.35 - imp * 0.20) * 0.15 + shock_pib
        self.pib = round(max(50.0, min(200.0, self.pib + crec_pib)), 1)

        # ── 4. DESEMPLEO ──
        desemp_target = max(2.5, min(30.0, 18.0 - (self.pib - 100.0) * 0.22 - gasto * 0.25 + imp * 0.15))
        self.desempleo = round(self.desempleo + (desemp_target - self.desempleo) * 0.6, 1)

        # ── 5. FISCAL: DÉFICIT Y RESERVAS (Laffer aplicado a recaudación) ──
        recaudacion = imp * 1.8 * factor_laffer
        gasto_total = gasto + inc * 0.6
        self.deficit = round(gasto_total - recaudacion, 1)
        # Si hay déficit, se gasta reservas; si hay superávit, se acumula
        self.reservas = round(self.reservas - self.deficit * 18.0, 1)

        # ── 6. APROBACIÓN CIUDADANA ──
        castigo_deficit = max(0.0, self.deficit - 5.0) * 1.2
        castigo_inflac  = max(0.0, self.inflacion - 4.5) * 1.4
        castigo_desemp  = max(0.0, self.desempleo - 6.0) * 1.5
        premio_bienestar= (self.poder_adq - 80.0) * 0.4 + (self.pib - 100.0) * 0.3
        self.aprobacion = round(max(0.0, min(100.0, 60.0 + premio_bienestar - castigo_deficit - castigo_inflac - castigo_desemp)), 1)

        # Históricos
        self.chart_pib.push(self.pib)
        self.chart_inf.push(self.inflacion)

        # ── VERIFICACIÓN DE CONDICIONES DE GAME OVER ──
        if self.inflacion >= 22.0 or self.poder_adq <= 25.0:
            self._set_game_over(
                "HIPERINFLACIÓN DESCONTROLADA",
                f"La inflación alcanzó el {self.inflacion:.1f}% y el poder adquisitivo se desplomó al {self.poder_adq:.0f}%. "
                "Los precios se volvieron inaccesibles y el dinero perdió su valor de cambio.",
                "Lección económica: Emitir dinero o mantener tasas de interés ultra bajas frente a un gasto desmedido "
                "crea espirales hiperinflacionarias destructivas."
            )
            return

        if self.desempleo >= 18.0 or self.aprobacion <= 18.0:
            self._set_game_over(
                "COLAPSO SOCIAL Y DESEMPLEO MASIVO",
                f"El desempleo trepó al {self.desempleo:.1f}% y la aprobación ciudadana se hundió al {self.aprobacion:.0f}%. "
                "Huelgas masivas y protestas populares obligaron a tu gabinete a renunciar.",
                "Lección económica: Una austeridad extrema o impuestos asfixiantes destruyen el empleo formal "
                "y paralizan el bienestar ciudadano."
            )
            return

        if self.reservas <= 0 and self.deficit >= 16.0:
            self._set_game_over(
                "QUIEBRA FISCAL Y DEFAULT SOBERANO",
                f"Las reservas del Tesoro se agotaron ($0M) con un déficit desbocado del {self.deficit:.1f}%. "
                "El Estado no puede pagar deudas ni salarios públicos; el país entró en default.",
                "Lección económica: El gasto público debe tener sustento en ingresos tributarios reales. "
                "Financiar déficit permanente agota las reservas de la nación."
            )
            return

        if self.pib <= 72.0:
            self._set_game_over(
                "GRAN DEPRESIÓN ECONÓMICA",
                f"El PIB nacional colapsó a {self.pib:.1f} puntos. Quiebras empresariales masivas desmantelaron "
                "el aparato productivo nacional.",
                "Lección económica: La producción requiere incentivos a la tecnología, insumos y tasas fiscales justas "
                "para mantenerse en crecimiento."
            )
            return

        # ── VERIFICACIÓN DE VICTORIA ──
        if self.quarter >= self.MAX_QUARTERS:
            if self.pib >= 105.0 and self.aprobacion >= 45.0 and self.reservas > 0:
                self.game_state = "VICTORY"
                audio.play("success")
            else:
                self._set_game_over(
                    "MANDATO FALLIDO (METAS NO ALCANZADAS)",
                    f"Concluiste los 8 trimestres pero el país terminó estancado: PIB en {self.pib:.1f}, "
                    f"Aprobación en {self.aprobacion:.0f}% y Reservas en ${self.reservas:.0f}M.",
                    "Lección económica: La estabilidad a largo plazo exige coordinar crecimiento, empleo y cuentas públicas ordenadas."
                )
            return

        # Avanzar al siguiente trimestre
        self.quarter += 1
        audio.play("click")
        self.notif.add(f"📅 Iniciando Trimestre {self.quarter} de {self.MAX_QUARTERS}", CYAN)

        # Cargar evento del nuevo trimestre
        self.active_event = self.EVENTOS_TRIMESTRALES.get(self.quarter, None)
        if self.active_event:
            audio.play("warning")

    def _set_game_over(self, title, reason, lesson):
        self.game_state = "GAMEOVER"
        self.game_over_title = title
        self.game_over_reason = reason
        self.game_over_lesson = lesson
        audio.play("warning")

    def _restart_game(self):
        self.quarter = 1
        self.pib         = 100.0
        self.inflacion   = 3.2
        self.desempleo   = 5.5
        self.poder_adq   = 100.0
        self.deficit     = 2.0
        self.aprobacion  = 65.0
        self.reservas    = 1000.0
        self.game_state  = "PLAYING"
        self.active_event = None
        self.chart_pib.data.clear()
        self.chart_inf.data.clear()
        self.chart_pib.push(self.pib)
        self.chart_inf.push(self.inflacion)
        self.sliders[0].value = 6
        self.sliders[1].value = 24
        self.sliders[2].value = 28
        self.sliders[3].value = 15
        audio.play("click")

    def handle_event(self, event):
        if self.game_state == "PLAYING":
            for s in self.sliders:
                s.handle_event(event)
            if self.btn_next_q.is_clicked(event):
                self._trigger_next_quarter()
        else:
            if self.btn_retry.is_clicked(event):
                self._restart_game()
            if self.btn_exit.is_clicked(event):
                self.next_scene = "menu"
                audio.play("click")

    def update(self, dt):
        super().update(dt)
        mouse = pygame.mouse.get_pos()
        if self.game_state == "PLAYING":
            for s in self.sliders:
                s.update(mouse)
            self.btn_next_q.update(mouse)
        else:
            self.btn_retry.update(mouse)
            self.btn_exit.update(mouse)
        self.notif.update(dt)

    def _draw_game_over(self, surface):
        # Overlay oscuro transparente
        overlay = pygame.Surface((SCREEN_W, SCREEN_H), pygame.SRCALPHA)
        overlay.fill((14, 4, 8, 240))
        surface.blit(overlay, (0, 0))

        # Panel de derrota
        pw, ph = 680, 430
        px, py = SCREEN_W // 2 - pw // 2, SCREEN_H // 2 - ph // 2 - 10
        pygame.draw.rect(surface, (28, 12, 16), (px, py, pw, ph), border_radius=10)
        pygame.draw.rect(surface, RED, (px, py, pw, ph), 3, border_radius=10)

        # Título
        font_t = get_font(26, bold=True)
        t_surf = font_t.render("☠  GAME OVER: COLAPSO ECONÓMICO  ☠", True, RED)
        surface.blit(t_surf, (SCREEN_W // 2 - t_surf.get_width() // 2, py + 22))

        # Causa
        font_sub = get_font(18, bold=True)
        sub_surf = font_sub.render(self.game_over_title, True, YELLOW)
        surface.blit(sub_surf, (SCREEN_W // 2 - sub_surf.get_width() // 2, py + 65))

        # Cuadro de descripción
        font_desc = get_font(13)
        desc_box = pygame.Rect(px + 30, py + 105, pw - 60, 140)
        pygame.draw.rect(surface, (18, 18, 26), desc_box, border_radius=6)
        pygame.draw.rect(surface, GRAY_DARK, desc_box, 1, border_radius=6)

        # Wrap text descripción
        words = self.game_over_reason.split(" ")
        lines, cur = [], []
        for w in words:
            if font_desc.size(" ".join(cur + [w]))[0] <= desc_box.w - 20:
                cur.append(w)
            else:
                lines.append(" ".join(cur))
                cur = [w]
        if cur: lines.append(" ".join(cur))

        ty = desc_box.y + 16
        for line in lines:
            rendered = font_desc.render(line, True, WHITE)
            surface.blit(rendered, (desc_box.x + 12, ty))
            ty += 22

        # Cuadro pedagógico
        pedag_box = pygame.Rect(px + 30, py + 260, pw - 60, 95)
        pygame.draw.rect(surface, (22, 28, 42), pedag_box, border_radius=6)
        pygame.draw.rect(surface, CYAN_DARK, pedag_box, 1, border_radius=6)
        text(surface, "💡 LECCIÓN DE APRENDIZAJE:", pedag_box.x + 12, pedag_box.y + 10, CYAN, 12, bold=True)

        w_words = self.game_over_lesson.split(" ")
        w_lines, w_cur = [], []
        for w in w_words:
            if font_desc.size(" ".join(w_cur + [w]))[0] <= pedag_box.w - 20:
                w_cur.append(w)
            else:
                w_lines.append(" ".join(w_cur))
                w_cur = [w]
        if w_cur: w_lines.append(" ".join(w_cur))

        ly = pedag_box.y + 32
        for line in w_lines:
            rend = font_desc.render(line, True, GRAY_LIGHT)
            surface.blit(rend, (pedag_box.x + 12, ly))
            ly += 20

        # Botones
        self.btn_retry.draw(surface)
        self.btn_exit.draw(surface)

    def _draw_victory(self, surface):
        # Overlay oscuro celebratorio
        overlay = pygame.Surface((SCREEN_W, SCREEN_H), pygame.SRCALPHA)
        overlay.fill((8, 18, 14, 240))
        surface.blit(overlay, (0, 0))

        pw, ph = 700, 460
        px, py = SCREEN_W // 2 - pw // 2, SCREEN_H // 2 - ph // 2 - 10
        pygame.draw.rect(surface, (14, 30, 22), (px, py, pw, ph), border_radius=10)
        pygame.draw.rect(surface, YELLOW, (px, py, pw, ph), 3, border_radius=10)

        # Trofeo
        surface.blit(self.sprite_t, (px + 30, py + 20))
        surface.blit(self.sprite_t, (px + pw - 70, py + 20))

        font_t = get_font(26, bold=True)
        t_surf = font_t.render("🏆  ¡MISIÓN CUMPLIDA: MANDATO EXITOSO!  🏆", True, YELLOW)
        surface.blit(t_surf, (SCREEN_W // 2 - t_surf.get_width() // 2, py + 25))

        # Calcular Score y Rango
        score = int(self.pib * 0.4 + self.aprobacion * 0.3 + (self.poder_adq * 0.2) - (self.desempleo * 2.0) - abs(self.inflacion - 3.0) * 3.0)
        if score >= 85:
            rank = "S"; rank_title = "ESTADISTA LEGENDARIO"; rank_col = YELLOW
        elif score >= 70:
            rank = "A"; rank_title = "MINISTRO EJEMPLAR"; rank_col = GREEN
        elif score >= 55:
            rank = "B"; rank_title = "GESTOR COMPETENTE"; rank_col = CYAN
        else:
            rank = "C"; rank_title = "SUPERVIVIENTE ECONÓMICO"; rank_col = WHITE

        font_r = get_font(42, bold=True)
        rs = font_r.render(f"RANGO {rank}", True, rank_col)
        surface.blit(rs, (SCREEN_W // 2 - rs.get_width() // 2, py + 68))
        text(surface, rank_title, SCREEN_W // 2, py + 120, rank_col, 14, bold=True, center=True)

        # Tablero de resultados finales
        results_panel = pygame.Rect(px + 40, py + 145, pw - 80, 180)
        pygame.draw.rect(surface, (18, 22, 34), results_panel, border_radius=6)
        pygame.draw.rect(surface, GRAY_DARK, results_panel, 1, border_radius=6)

        kpis_final = [
            ("PIB FINAL",          f"{self.pib:.1f} pts",  PURPLE),
            ("INFLACIÓN FINAL",    f"{self.inflacion:.1f}%", GREEN if 1.5 <= self.inflacion <= 4.5 else YELLOW),
            ("DESEMPLEO FINAL",    f"{self.desempleo:.1f}%", GREEN if self.desempleo < 6 else RED),
            ("PODER ADQUISITIVO",  f"{self.poder_adq:.0f}%", GREEN),
            ("APROBACIÓN FINAL",   f"{self.aprobacion:.0f}%", YELLOW),
            ("RESERVAS FISCALES",  f"${self.reservas:.0f}M", CYAN),
        ]
        font_k = get_font(16, bold=True)
        font_l = get_font(11)
        rx, ry = results_panel.x + 20, results_panel.y + 18
        for i, (lab, val, col) in enumerate(kpis_final):
            p = Panel(rx, ry, 185, 65, border=col)
            p.draw(surface)
            surface.blit(font_l.render(lab, True, GRAY_LIGHT), (rx + 8, ry + 8))
            surface.blit(font_k.render(val, True, col),        (rx + 8, ry + 32))
            rx += 205
            if (i + 1) % 3 == 0:
                rx = results_panel.x + 20
                ry += 80

        text(surface, "¡Demostraste que la economía coordinada genera prosperidad y estabilidad social!",
             SCREEN_W // 2, py + 345, GREEN, 13, bold=True, center=True)

        self.btn_retry.draw(surface)
        self.btn_exit.draw(surface)

    def draw_content(self, surface):
        accent = self.accent

        # ── Banner Superior del Mandato ──
        banner_rect = pygame.Rect(40, 75, 330, 48)
        pygame.draw.rect(surface, PANEL_BG, banner_rect, border_radius=6)
        pygame.draw.rect(surface, YELLOW, banner_rect, 2, border_radius=6)
        text(surface, f"TRIMESTRE {self.quarter} DE {self.MAX_QUARTERS}",
             55, 82, YELLOW, 15, bold=True)
        # Barra de progreso de trimestres
        progress_w = int((self.quarter / self.MAX_QUARTERS) * 290)
        pygame.draw.rect(surface, GRAY_DARK, (55, 105, 290, 8), border_radius=4)
        pygame.draw.rect(surface, YELLOW, (55, 105, progress_w, 8), border_radius=4)

        # ── Panel de Palancas de Política Económica ──
        p_ctrl = Panel(40, 132, 330, 255, border=accent)
        p_ctrl.draw(surface)
        text(surface, "Palancas de Política Macroeconómica", 55, 140,
             color=accent, size=13, bold=True)
        for s in self.sliders:
            s.draw(surface)

        self.btn_next_q.draw(surface)

        # ── Sprite del asesor dentro del banner del trimestre ──
        surface.blit(self.sprite_g, (335, 82))

        # ── Panel Central: Evento Activo / Shocks ──
        ev_rect = pygame.Rect(400, 220, 280, 145)
        pygame.draw.rect(surface, PANEL_BG, ev_rect, border_radius=6)
        pygame.draw.rect(surface, ORANGE if self.active_event else CYAN_DARK, ev_rect, 1, border_radius=6)
        if self.active_event:
            text(surface, self.active_event["titulo"], ev_rect.x + 10, ev_rect.y + 10, ORANGE, 12, bold=True)
            # Renderizado de texto con salto
            words = self.active_event["desc"].split(" ")
            lines, cur = [], []
            font_ev = get_font(11)
            for w in words:
                if font_ev.size(" ".join(cur + [w]))[0] <= ev_rect.w - 20:
                    cur.append(w)
                else:
                    lines.append(" ".join(cur))
                    cur = [w]
            if cur: lines.append(" ".join(cur))
            ey = ev_rect.y + 32
            for l in lines:
                surface.blit(font_ev.render(l, True, WHITE), (ev_rect.x + 10, ey))
                ey += 16
            text(surface, f"Impacto: {self.active_event['impacto']}", ev_rect.x + 10, ev_rect.bottom - 22, YELLOW, 11, bold=True)
        else:
            text(surface, "SITUACIÓN MACROECONÓMICA ESTABLE", ev_rect.x + 10, ev_rect.y + 12, CYAN, 12, bold=True)
            text(surface, "Ajusta tus políticas fiscales y monetarias", ev_rect.x + 10, ev_rect.y + 40, GRAY_LIGHT, 11)
            text(surface, "para sostener el crecimiento y la meta de inflación.", ev_rect.x + 10, ev_rect.y + 60, GRAY_LIGHT, 11)
            text(surface, "Pulsa 'Avanzar Trimestre' para simular los efectos.", ev_rect.x + 10, ev_rect.y + 85, YELLOW, 11)

        # ── KPIs del Dashboard Macroeconómico ──
        kpis = [
            ("DESEMPLEO",  f"{self.desempleo:.1f}%", RED if self.desempleo > 8 else GREEN),
            ("PODER ADQ.", f"{self.poder_adq:.0f}%", GREEN if self.poder_adq > 75 else RED),
            ("DÉFICIT",    f"{self.deficit:.1f}%",   RED if self.deficit > 10 else GREEN),
            ("APROBACIÓN", f"{self.aprobacion:.0f}%", YELLOW if self.aprobacion > 50 else RED),
            ("RESERVAS",   f"${self.reservas:.0f}M", CYAN if self.reservas > 300 else RED),
        ]
        font_k = get_font(18, bold=True)
        font_l = get_font(11)
        kx = 400
        for lab, val, col in kpis[:3]:
            p = Panel(kx, 380, 88, 62, border=col)
            p.draw(surface)
            surface.blit(font_l.render(lab, True, GRAY_LIGHT), (kx + 6, 386))
            surface.blit(font_k.render(val, True, col),        (kx + 6, 410))
            kx += 96

        kx = 400
        for lab, val, col in kpis[3:]:
            p = Panel(kx, 452, 137, 62, border=col)
            p.draw(surface)
            surface.blit(font_l.render(lab, True, GRAY_LIGHT), (kx + 8, 458))
            surface.blit(font_k.render(val, True, col),        (kx + 8, 482))
            kx += 145

        # ── Gráficas ──
        self.chart_pib.draw(surface)
        self.chart_inf.draw(surface)

        # Panel de reglas del juego (posicionado debajo del monitor de salud a y=410)
        rules_rect = pygame.Rect(710, 410, 280, 195)
        pygame.draw.rect(surface, PANEL_BG, rules_rect, border_radius=6)
        pygame.draw.rect(surface, GRAY_DARK, rules_rect, 1, border_radius=6)
        text(surface, "OBJETIVOS DE GESTIÓN:", rules_rect.x + 8, rules_rect.y + 8, YELLOW, 12, bold=True)
        rules = [
            "✔ Sobrevivir 8 trimestres con PIB >= 105.",
            "✔ Mantener Inflación en 2-4%.",
            "✔ Desempleo menor a 8%.",
            "✔ Preservar Reservas > $0M.",
            "",
            "⚠ CONDICIONES DE GAME OVER:",
            "• Hiperinflación (>22%) / Poder Adq (<25%).",
            "• Desempleo masivo (>18%) / Protestas.",
            "• Quiebra fiscal (Déficit>16% y Reservas $0).",
            "• Gran Depresión Económica (PIB < 72 pts).",
        ]
        ry = rules_rect.y + 26
        for r in rules:
            col = RED if "•" in r else (YELLOW if "CONDICIONES" in r else GRAY_LIGHT)
            text(surface, r, rules_rect.x + 8, ry, col, 10, bold=("CONDICIONES" in r))
            ry += 16

        self.notif.draw(surface)

        # Overlays de fin de juego si aplica
        if self.game_state == "GAMEOVER":
            self._draw_game_over(surface)
        elif self.game_state == "VICTORY":
            self._draw_victory(surface)

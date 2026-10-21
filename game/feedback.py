# ============================================================
#  FEEDBACK & ANIMATIONS – Monitor de Estado y Mascota 8-bit
# ============================================================
import math
import random
import pygame
from game.constants import *
from game.ui import get_font


def wrap_text_lines(text_str, font, max_w):
    """Divide texto en líneas que no excedan max_w."""
    lines = []
    for paragraph in text_str.split("\n"):
        words = paragraph.split(" ")
        cur = []
        for w in words:
            test = " ".join(cur + [w])
            if font.size(test)[0] <= max_w:
                cur.append(w)
            else:
                if cur:
                    lines.append(" ".join(cur))
                cur = [w]
        if cur:
            lines.append(" ".join(cur))
    return lines


class PixelParticle:
    def __init__(self, x, y, kind="star"):
        self.x = float(x)
        self.y = float(y)
        self.kind = kind
        self.max_life = random.uniform(800, 1400)
        self.age = 0
        self.life = 1.0
        if kind == "star":
            self.vx = random.uniform(-0.4, 0.4)
            self.vy = random.uniform(-0.8, -1.5)
            self.color = random.choice([(255, 215, 0), YELLOW, (120, 255, 180), WHITE])
            self.size = random.choice([2, 3, 4])
        elif kind == "sweat":
            self.vx = random.uniform(0.2, 0.7)
            self.vy = random.uniform(0.8, 1.6)
            self.color = (80, 180, 255)
            self.size = random.choice([3, 4])
        elif kind == "smoke":
            self.vx = random.uniform(-0.5, 0.5)
            self.vy = random.uniform(-0.6, -1.2)
            self.color = random.choice([(140, 60, 60), (180, 80, 80), (100, 100, 120)])
            self.size = random.choice([4, 6])
        else:
            self.vx = random.uniform(-0.3, 0.3)
            self.vy = random.uniform(-0.5, -1.0)
            self.color = CYAN
            self.size = 2

    def update(self, dt):
        self.age += dt
        self.life = max(0.0, 1.0 - (self.age / self.max_life))
        self.x += self.vx * dt * 0.06
        self.y += self.vy * dt * 0.06

    def draw(self, surface):
        if self.life <= 0:
            return
        alpha = int(self.life * 255)
        s = pygame.Surface((self.size * 2, self.size * 2), pygame.SRCALPHA)
        col = (self.color[0], self.color[1], self.color[2], alpha)
        if self.kind == "star":
            # Forma de cruz brillante 8-bit
            s.fill(col, (self.size // 2, 0, self.size, self.size * 2))
            s.fill(col, (0, self.size // 2, self.size * 2, self.size))
        elif self.kind == "sweat":
            pygame.draw.circle(s, col, (self.size, self.size), self.size)
        else:
            s.fill(col)
        surface.blit(s, (int(self.x), int(self.y)))


class ModelHealthWidget:
    """
    Widget visual animado que evalúa en tiempo real si el jugador
    lo está haciendo BIEN, REGULAR o MAL en el modelo económico.
    """
    def __init__(self, x, y, w=285, h=180):
        self.rect = pygame.Rect(x, y, w, h)
        self.state = "NEUTRAL"   # "GOOD", "NEUTRAL", "BAD"
        self.score = 50.0        # 0 a 100
        self.title_msg = "ESTABLE"
        self.desc_msg = "El modelo opera en equilibrio regular."
        self.tip_msg = "Ajusta las variables para maximizar resultados."
        self.particles = []
        self._particle_timer = 0
        self.tick = 0

        # Fuentes
        self.font_header = get_font(13, bold=True)
        self.font_badge = get_font(12, bold=True)
        self.font_body = get_font(11)
        self.font_bold = get_font(11, bold=True)

    def set_status(self, state, score, title_msg, desc_msg, tip_msg=""):
        self.state = state
        self.score = max(0.0, min(100.0, float(score)))
        self.title_msg = title_msg
        self.desc_msg = desc_msg
        self.tip_msg = tip_msg

    def update(self, dt):
        self.tick += dt
        self._particle_timer += dt

        # Spawn de partículas según el estado
        rate = 110 if self.state != "NEUTRAL" else 300
        if self._particle_timer >= rate:
            self._particle_timer = 0
            if self.state == "GOOD":
                px = self.rect.x + 36 + random.randint(-16, 16)
                py = self.rect.y + 70 + random.randint(-8, 8)
                self.particles.append(PixelParticle(px, py, kind="star"))
            elif self.state == "BAD":
                px = self.rect.x + 46 + random.randint(0, 10)
                py = self.rect.y + 55 + random.randint(-4, 4)
                self.particles.append(PixelParticle(px, py, kind="sweat"))
                if random.random() < 0.4:
                    self.particles.append(PixelParticle(self.rect.x + 32, self.rect.y + 40, kind="smoke"))
            elif self.state == "NEUTRAL":
                if random.random() < 0.3:
                    px = self.rect.x + 36 + random.randint(-12, 12)
                    py = self.rect.y + 60 + random.randint(-6, 6)
                    self.particles.append(PixelParticle(px, py, kind="neutral"))

        # Actualizar partículas vivas
        for p in self.particles:
            p.update(dt)
        self.particles = [p for p in self.particles if p.life > 0]

    def _draw_mascot(self, surface, cx, cy):
        """Dibuja la mascota pixelada animada de 32x32 según el estado."""
        if self.state == "GOOD":
            bounce_y = int(math.sin(self.tick * 0.008) * 4)
            shake_x = 0
        elif self.state == "BAD":
            bounce_y = 0
            shake_x = int(math.sin(self.tick * 0.04) * 2)
        else:
            bounce_y = int(math.sin(self.tick * 0.003) * 1.5)
            shake_x = 0

        mx = cx + shake_x
        my = cy + bounce_y

        # Sombra del personaje en el suelo
        shadow_rect = pygame.Rect(cx - 16, cy + 22, 32, 6)
        s_shadow = pygame.Surface((32, 6), pygame.SRCALPHA)
        s_shadow.fill((0, 0, 0, 90))
        surface.blit(s_shadow, shadow_rect.topleft)

        head_w, head_h = 32, 28
        hx, hy = mx - 16, my - 14

        if self.state == "GOOD":
            skin_col = (255, 215, 60)       # Dorado radiante
            border_col = (180, 140, 20)
        elif self.state == "BAD":
            is_flash = (self.tick // 250) % 2 == 0
            skin_col = (255, 120, 110) if is_flash else (230, 160, 160)
            border_col = RED
        else:
            skin_col = (130, 215, 250)      # Cyan tecnológico
            border_col = (40, 120, 180)

        # Cara
        pygame.draw.rect(surface, skin_col, (hx, hy, head_w, head_h), border_radius=6)
        pygame.draw.rect(surface, border_col, (hx, hy, head_w, head_h), 2, border_radius=6)

        # Ojos y expresión
        if self.state == "GOOD":
            # Gafas de sol retro con brillo
            pygame.draw.rect(surface, (20, 20, 40), (hx + 4, hy + 7, 10, 8), border_radius=2)
            pygame.draw.rect(surface, WHITE, (hx + 5, hy + 8, 3, 3))
            pygame.draw.rect(surface, (20, 20, 40), (hx + 18, hy + 7, 10, 8), border_radius=2)
            pygame.draw.rect(surface, WHITE, (hx + 19, hy + 8, 3, 3))
            pygame.draw.rect(surface, (20, 20, 40), (hx + 14, hy + 9, 4, 3))
            # Sonrisa amplia
            pygame.draw.arc(surface, (140, 40, 20), (hx + 9, hy + 13, 14, 10), 3.14, 6.28, 2)
            # Rubor
            pygame.draw.rect(surface, (255, 140, 100), (hx + 3, hy + 17, 4, 3))
            pygame.draw.rect(surface, (255, 140, 100), (hx + 25, hy + 17, 4, 3))

        elif self.state == "BAD":
            # Ojos en X
            pygame.draw.line(surface, (30, 10, 10), (hx + 5, hy + 6), (hx + 11, hy + 12), 2)
            pygame.draw.line(surface, (30, 10, 10), (hx + 5, hy + 12), (hx + 11, hy + 6), 2)
            pygame.draw.line(surface, (30, 10, 10), (hx + 21, hy + 6), (hx + 27, hy + 12), 2)
            pygame.draw.line(surface, (30, 10, 10), (hx + 21, hy + 12), (hx + 27, hy + 6), 2)
            # Boca temblorosa en O
            pygame.draw.circle(surface, (80, 20, 20), (hx + 16, hy + 20), 4)
            # Gota de sudor animada
            drop_offset = (self.tick // 80) % 12
            pygame.draw.rect(surface, (60, 160, 255), (hx + 28, hy + 2 + drop_offset, 3, 5), border_radius=1)

        else:
            # Ojos neutrales parpadeantes
            blink = (self.tick % 3000) < 180
            if blink:
                pygame.draw.line(surface, (20, 30, 50), (hx + 6, hy + 10), (hx + 12, hy + 10), 2)
                pygame.draw.line(surface, (20, 30, 50), (hx + 20, hy + 10), (hx + 26, hy + 10), 2)
            else:
                pygame.draw.rect(surface, (20, 30, 50), (hx + 6, hy + 7, 6, 7), border_radius=2)
                pygame.draw.rect(surface, WHITE, (hx + 7, hy + 8, 2, 2))
                pygame.draw.rect(surface, (20, 30, 50), (hx + 20, hy + 7, 6, 7), border_radius=2)
                pygame.draw.rect(surface, WHITE, (hx + 21, hy + 8, 2, 2))
            # Boca neutra
            pygame.draw.line(surface, (20, 30, 50), (hx + 11, hy + 19), (hx + 21, hy + 19), 2)

    def draw(self, surface):
        if self.state == "GOOD":
            accent_col = GREEN
            bg_col = (16, 32, 24)
            badge_text = "EXCELENTE"
            badge_col = GREEN
            badge_text_col = BLACK
        elif self.state == "BAD":
            accent_col = RED
            pulse = 0.5 + 0.5 * math.sin(self.tick * 0.006)
            bg_r = int(36 + 25 * pulse)
            bg_col = (bg_r, 16, 18)
            badge_text = "ALERTA CRISIS"
            badge_col = RED
            badge_text_col = WHITE
        else:
            accent_col = YELLOW
            bg_col = (22, 26, 40)
            badge_text = "EQUILIBRADO"
            badge_col = YELLOW
            badge_text_col = BLACK

        # Panel principal con sombra pixel
        shadow_rect = self.rect.move(4, 4)
        pygame.draw.rect(surface, BLACK, shadow_rect, border_radius=6)
        pygame.draw.rect(surface, bg_col, self.rect, border_radius=6)
        pygame.draw.rect(surface, accent_col, self.rect, 2, border_radius=6)

        # Cabecera
        hdr_rect = pygame.Rect(self.rect.x, self.rect.y, self.rect.w, 28)
        pygame.draw.rect(surface, (12, 16, 28), hdr_rect,
                         border_top_left_radius=6, border_top_right_radius=6)
        pygame.draw.line(surface, accent_col,
                         (self.rect.x, self.rect.y + 28),
                         (self.rect.right, self.rect.y + 28), 1)

        hdr_str = "ESTADO" if self.rect.w < 250 else "SALUD DEL MODELO"
        t_hdr = self.font_header.render(hdr_str, True, accent_col)
        surface.blit(t_hdr, (self.rect.x + 8, self.rect.y + 6))

        # Badge de estado
        badge_w = 90 if self.rect.w < 250 else 104
        badge_h = 20
        badge_rect = pygame.Rect(self.rect.right - badge_w - 6, self.rect.y + 4, badge_w, badge_h)
        pygame.draw.rect(surface, badge_col, badge_rect, border_radius=4)
        t_b = self.font_badge.render(badge_text, True, badge_text_col)
        surface.blit(t_b, (badge_rect.centerx - t_b.get_width() // 2,
                           badge_rect.centery - t_b.get_height() // 2))

        # Mascota animada
        mascot_cx = self.rect.x + 28
        mascot_cy = self.rect.y + 66
        self._draw_mascot(surface, mascot_cx, mascot_cy)

        # Partículas
        for p in self.particles:
            p.draw(surface)

        # Barra de Desempeño
        bar_x = self.rect.x + 56
        bar_y = self.rect.y + 36
        bar_w = self.rect.w - 64
        bar_h = 14

        pygame.draw.rect(surface, GRAY_DARK, (bar_x, bar_y, bar_w, bar_h), border_radius=3)
        fill_w = int(bar_w * (self.score / 100.0))
        if fill_w > 0:
            fill_col = GREEN if self.score >= 70 else (YELLOW if self.score >= 40 else RED)
            pygame.draw.rect(surface, fill_col, (bar_x, bar_y, fill_w, bar_h), border_radius=3)
        pygame.draw.rect(surface, GRAY, (bar_x, bar_y, bar_w, bar_h), 1, border_radius=3)

        score_lbl = f"SALUD: {self.score:.0f}%" if self.rect.w < 250 else f"PUNTAJE: {self.score:.0f}/100"
        score_text = self.font_badge.render(score_lbl, True, WHITE)
        surface.blit(score_text, (bar_x + 4, bar_y - 1))

        # Diagnóstico en tiempo real
        diag_x = self.rect.x + 56
        diag_y = self.rect.y + 54
        max_diag_w = self.rect.w - 64

        t_title = self.font_bold.render(f"> {self.title_msg}", True, accent_col)
        surface.blit(t_title, (diag_x, diag_y))

        desc_lines = wrap_text_lines(self.desc_msg, self.font_body, max_diag_w)
        line_y = diag_y + 15
        for line in desc_lines[:2]:
            t_line = self.font_body.render(line, True, WHITE)
            surface.blit(t_line, (diag_x, line_y))
            line_y += 13

        # Consejo inferior
        if self.tip_msg:
            bot_y = self.rect.bottom - 36
            tip_rect = pygame.Rect(self.rect.x + 8, bot_y, self.rect.w - 16, 28)
            pygame.draw.rect(surface, (14, 18, 30), tip_rect, border_radius=4)
            pygame.draw.rect(surface, GRAY_DARK, tip_rect, 1, border_radius=4)

            tip_lines = wrap_text_lines(f"* {self.tip_msg}", self.font_body, tip_rect.w - 12)
            ty = tip_rect.y + 4
            for tl in tip_lines[:2]:
                stl = self.font_body.render(tl, True, GRAY_LIGHT)
                surface.blit(stl, (tip_rect.x + 6, ty))
                ty += 12


def update_scene_health(key, scene, widget):
    """Evalúa la lógica de cada uno de los 13 modelos y actualiza el widget."""
    try:
        if key == "fabricantes":
            gan = getattr(scene, "ganancia", 0.0)
            if gan >= 150:
                widget.set_status("GOOD", min(100, 70 + gan * 0.1),
                                  "Fabrica Muy Rentable",
                                  "La tecnologia y mano de obra generan altos ingresos netos.",
                                  "Manten la tecnologia alta para amortizar el costo de insumos.")
            elif gan >= 0:
                widget.set_status("NEUTRAL", 40 + (gan / 150) * 30,
                                  "Operacion Estable",
                                  "Cubres insumos y salarios pero con poco margen de utilidad.",
                                  "Sube la tecnologia para elevar produccion sin pagar mas materias.")
            else:
                widget.set_status("BAD", max(5, 35 + gan * 0.2),
                                  "Perdidas Operativas",
                                  "Pagas mas en insumos y obreros de lo que vendes ($3.5/u).",
                                  "Reduce compras de insumos o mano de obra excedente de inmediato.")

        elif key == "consumidores":
            q = getattr(scene, "cantidad", 0.0)
            ut = getattr(scene, "utilidad", 0.0)
            if q >= 4 and ut >= 180:
                widget.set_status("GOOD", 88,
                                  "Consumo Satisfactorio",
                                  "El consumidor adquiere canastas amplias maximizando bienestar.",
                                  "Excelente equilibrio entre precio accesible y preferencia.")
            elif q >= 1:
                widget.set_status("NEUTRAL", 55,
                                  "Consumo Limitado",
                                  "Se realizan compras pero el presupuesto o sustitutos restringen.",
                                  "Un precio mas bajo o mayor preferencia elevaria la utilidad.")
            else:
                widget.set_status("BAD", 15,
                                  "Poder de Compra Nulo",
                                  "Precio prohibitivo o sustitutos atractivos destruyen la demanda.",
                                  "Baja el precio del bien o incrementa el presupuesto disponible.")

        elif key == "empresas":
            ut = getattr(scene, "utilidad", 0.0)
            mg = getattr(scene, "margen", 0.0)
            if ut > 800 and mg >= 20:
                widget.set_status("GOOD", min(100, 65 + mg * 0.7),
                                  "Empresa Prospera",
                                  "Generas un margen operativo saludable sobre el punto de equilibrio.",
                                  "Usa 'Invertir' para abaratar costos variables unitarios.")
            elif ut >= 0:
                widget.set_status("NEUTRAL", 45 + mg,
                                  "Margen Ajustado",
                                  "La empresa sobrevive pero con margen vulnerable ante imprevistos.",
                                  "Aplica 'Recortar costos' para ganar margen de seguridad.")
            else:
                widget.set_status("BAD", max(10, 40 + ut * 0.01),
                                  "Quiebra Financiera",
                                  "Los ingresos totales no cubren los costos fijos y variables.",
                                  "Aumenta el precio de venta o recorta costos fijos urgentemente.")

        elif key == "gobierno":
            desemp = getattr(scene, "desempleo", 5.0)
            defic = getattr(scene, "deficit", 0.0)
            aprob = getattr(scene, "aprobacion", 50.0)
            pib = getattr(scene, "pib", 100.0)
            if desemp <= 5.5 and defic <= 10.0 and pib >= 105 and aprob >= 50:
                widget.set_status("GOOD", 90,
                                  "Auge y Bienestar",
                                  "Economia en expansion, bajo desempleo y deficit bajo control.",
                                  "Prioriza gasto en educacion para sostener el crecimiento.")
            elif desemp > 9.0 or defic > 20.0 or aprob < 35:
                widget.set_status("BAD", 20,
                                  "Crisis Macroeconomica",
                                  "Desempleo disparado o deficit asfixiante hunden la aprobacion.",
                                  "Aplica 'Estimulo' si hay desempleo, o 'Austeridad' ante deficit.")
            else:
                widget.set_status("NEUTRAL", 55,
                                  "Politica en Equilibrio",
                                  "Variables estables pero con tension entre gasto social e impuestos.",
                                  "Equilibra la tasa impositiva con la recaudacion necesaria.")

        elif key == "mercado":
            trans = getattr(scene, "transacciones", 0)
            vol = getattr(scene, "volumen", 0.0)
            if trans >= 7 and vol >= 500:
                widget.set_status("GOOD", 88,
                                  "Mercado Muy Activo",
                                  "Compradores y vendedores cierran tratos continuamente.",
                                  "La calidad del bien sostiene un alto volumen de transacciones.")
            elif vol < 150 or trans <= 2:
                widget.set_status("BAD", 20,
                                  "Mercado Paralizado",
                                  "Precios desalineados o desproporcion severa entre agentes.",
                                  "Ajusta el precio hacia el centro o equipara oferentes y clientes.")
            else:
                widget.set_status("NEUTRAL", 55,
                                  "Actividad Moderada",
                                  "Se concretan ventas pero queda capacidad ociosa en puestos.",
                                  "Eleva la calidad para cerrar intercambios mas rapidamente.")

        elif key == "oferta":
            q = getattr(scene, "oferta_total", 0.0)
            if q >= 50:
                widget.set_status("GOOD", 86,
                                  "Oferta Abundante",
                                  "Innovacion y costos accesibles estimulan el abastecimiento.",
                                  "La curva se expande hacia la derecha favoreciendo el mercado.")
            elif q >= 20:
                widget.set_status("NEUTRAL", 55,
                                  "Oferta Regular",
                                  "Abastecimiento normal con capacidad de expansion.",
                                  "Incorpora mas tecnologia o incentiva la entrada de productores.")
            else:
                widget.set_status("BAD", 20,
                                  "Desabasto Critico",
                                  "Insumos excesivamente caros asfixian la disposicion a producir.",
                                  "Reduce costos de insumos o impulsa tecnologia productiva.")

        elif key == "demanda":
            q = getattr(scene, "demanda_total", 0.0)
            if q >= 70:
                widget.set_status("GOOD", 86,
                                  "Demanda Vibrante",
                                  "Clientes con buen poder de compra y alta preferencia por el bien.",
                                  "Excelente posicionamiento de marca frente a los sustitutos.")
            elif q >= 30:
                widget.set_status("NEUTRAL", 55,
                                  "Demanda Estable",
                                  "Consumo sostenido; el mercado absorbe la oferta normal.",
                                  "Estimula preferencias para desplazar la curva a la derecha.")
            else:
                widget.set_status("BAD", 20,
                                  "Demanda Deprimida",
                                  "Ingreso insuficiente o sustitutos baratos alejan compradores.",
                                  "Aumenta la preferencia o busca segmentos de mayor ingreso.")

        elif key == "precios":
            exc = getattr(scene, "excedente", 0.0)
            esc = getattr(scene, "escasez_val", 0.0)
            if exc < 15 and esc < 15:
                widget.set_status("GOOD", 92,
                                  "Precio de Equilibrio",
                                  "El precio actua como senal perfecta: Oferta iguala Demanda.",
                                  "No hay colas de espera ni mercancia estancada en anaqueles.")
            elif esc >= 25:
                widget.set_status("BAD", 25,
                                  "Escasez y Filas",
                                  "Precio artificialmente bajo genera sobredemanda y desabasto.",
                                  "Permite que el precio suba hacia el equilibrio de mercado.")
            elif exc >= 25:
                widget.set_status("BAD", 25,
                                  "Excedente Masivo",
                                  "Precio demasiado alto: mercancia acumulada sin vender.",
                                  "Baja el precio para liquidar inventarios no vendidos.")
            else:
                widget.set_status("NEUTRAL", 58,
                                  "Ajuste en Curso",
                                  "Leve desfase entre oferta y demanda buscando estabilidad.",
                                  "Usa el modo 'Libre mercado' para converger al equilibrio.")

        elif key == "impuestos":
            rec = getattr(scene, "recaudacion", 0.0)
            bien = getattr(scene, "bienestar", 50.0)
            if bien >= 58 and rec >= 1600:
                widget.set_status("GOOD", 88,
                                  "Equilibrio Fiscal",
                                  "Recaudacion solida del Estado preservando el bienestar social.",
                                  "Zona optima de la Curva de Laffer alcanzada exitosamente.")
            elif bien < 38:
                widget.set_status("BAD", 20,
                                  "Asfixia Tributaria",
                                  "Impuestos confiscatorios destruyen la actividad economica.",
                                  "Aplica 'Reforma fiscal' para reactivar incentivos al trabajo.")
            else:
                widget.set_status("NEUTRAL", 55,
                                  "Presion Moderada",
                                  "Tributacion estandar con perdida de peso muerto contenida.",
                                  "Usa 'Exencion PyME' para dinamizar la base productiva.")

        elif key == "equilibrio":
            p = getattr(scene, "p_eq", 50.0)
            q = getattr(scene, "q_eq", 20.0)
            if 30 <= p <= 110 and q >= 25:
                widget.set_status("GOOD", 90,
                                  "Balanza Perfecta",
                                  "Mercado despejado en equilibrio estable con buen volumen.",
                                  "Los shocks externos mueven simultaneamente P* y Q*.")
            elif q < 12:
                widget.set_status("BAD", 25,
                                  "Mercado Colapsado",
                                  "Cantidad transaccionada en niveles criticos.",
                                  "Desplaza las curvas hacia terreno positivo para reactivar.")
            else:
                widget.set_status("NEUTRAL", 60,
                                  "Equilibrio Estable",
                                  "El punto existe pero con precios sensibles a las pendientes.",
                                  "Prueba alterar elasticidades para ver la respuesta.")

        elif key == "inflacion":
            inf = getattr(scene, "inflacion", 3.0)
            pod = getattr(scene, "poder_adq", 100.0)
            if 1.5 <= inf <= 4.5 and pod >= 75:
                widget.set_status("GOOD", 92,
                                  "Estabilidad de Precios",
                                  "Inflacion controlada en rango meta: poder adquisitivo en recuperacion.",
                                  "Buena coordinacion entre tasa de interes y masa monetaria.")
            elif inf < 0.0:
                widget.set_status("BAD", 28,
                                  "Espiral Deflacionaria",
                                  "Precios cayendo (<0%): riesgo de contraccion de demanda y recesion.",
                                  "Baja la tasa de interes o reactiva el credito productivo.")
            elif inf > 8.0 or pod < 50:
                widget.set_status("BAD", 18,
                                  "Espiral Inflacionaria",
                                  "El alza continua de precios destruye el salario real.",
                                  "Sube la tasa de interes y frena la emision de dinero M2.")
            else:
                widget.set_status("NEUTRAL", 55,
                                  "Presion Moderada",
                                  "Inflacion detectable pero contenida por la politica del banco.",
                                  "Vigila que las expectativas no aceleren los aumentos.")

        elif key == "competencia":
            cuota = getattr(scene, "mi_cuota", 20.0)
            if cuota >= 30.0:
                widget.set_status("GOOD", min(100, 60 + cuota),
                                  "Lider del Mercado",
                                  "Dominas las ventas del sector superando a las 4 empresas rivales.",
                                  "Excelente relacion entre calidad, publicidad e innovacion.")
            elif cuota >= 18.0:
                widget.set_status("NEUTRAL", 55,
                                  "Competidor Activo",
                                  "Mantienes una cuota respetable pero los rivales te presionan.",
                                  "Usa 'Innovar x2' para diferenciar tu producto frente a rivales.")
            else:
                widget.set_status("BAD", 20,
                                  "Perdida de Mercado",
                                  "Tus rivales captan a tus clientes con mejor precio o calidad.",
                                  "Ajusta tu precio o invierte mas en publicidad e innovacion.")

        elif key == "escasez":
            usado = getattr(scene, "total_usado", 100)
            bien = getattr(scene, "bienestar", 50.0)
            if 90 <= usado <= 100 and bien >= 60:
                widget.set_status("GOOD", min(100, bien + 15),
                                  "Gestion Ejemplar",
                                  "Aprovechas al 100% los recursos escasos sin sobregirar.",
                                  "Armonia entre alimentos, salud, educacion y vivienda.")
            elif usado > 100:
                widget.set_status("BAD", 15,
                                  "Sobregiro de Recursos",
                                  "Gastas mas del 100% disponible: la crisis desploma el bienestar.",
                                  "Baja los sliders de inmediato hasta sumar 100% o menos.")
            else:
                widget.set_status("NEUTRAL", 50,
                                  "Recursos Ociosos",
                                  "No hay sobregiro pero quedan necesidades basicas desatendidas.",
                                  "Asigna el porcentaje restante para elevar el bienestar social.")

        elif key == "ecotycoon":
            pib = getattr(scene, "pib", 100.0)
            inf = getattr(scene, "inflacion", 3.0)
            aprob = getattr(scene, "aprobacion", 65.0)
            desemp = getattr(scene, "desempleo", 5.5)
            if pib >= 110.0 and 1.5 <= inf <= 4.5 and aprob >= 60.0 and desemp <= 6.0:
                widget.set_status("GOOD", 95,
                                  "Mandato Sobresaliente",
                                  "Crecimiento solido con inflacion en meta y aprobacion ciudadana récord.",
                                  "¡Continua asi hasta completar los 8 trimestres!")
            elif inf > 15.0 or aprob < 30.0 or desemp > 12.0:
                widget.set_status("BAD", 20,
                                  "Riesgo de Game Over",
                                  "Variables en terreno critico: la economia se acerca al colapso.",
                                  "Reajusta tasas de interes y gasto publico de inmediato.")
            else:
                widget.set_status("NEUTRAL", 60,
                                  "Mandato en Curso",
                                  "Variables macroeconomicas bajo control moderado.",
                                  "Vigila los shocks mundiales y el déficit fiscal.")
        elif key == "gran_mercado":
            gap = getattr(scene, "gap_precio", 0.0)
            exceso = getattr(scene, "exceso_tipo", "EQUILIBRIO")
            satis = getattr(scene, "satisfaccion", 80.0)
            if exceso == "EQUILIBRIO" and satis >= 80:
                widget.set_status("GOOD", 96,
                                  "Equilibrio de Mercado",
                                  "Precio y cantidad vacian el mercado. No hay escasez ni sobrantes.",
                                  "Prueba alterar preferencias de consumidores o costos de insumos.")
            elif exceso == "ESCASEZ":
                widget.set_status("BAD", 30,
                                  "Escasez y Filas",
                                  "El precio esta por debajo del equilibrio: la demanda supera la oferta.",
                                  "Permite que el precio suba o estimula la tecnologia de produccion.")
            else: # SOBREOFERTA
                widget.set_status("BAD", 35,
                                  "Exceso de Produccion",
                                  "El precio es muy alto: se acumula stock invendido y merman ventas.",
                                  "Baja el precio de venta o incentiva el ingreso de los hogares.")

        elif key == "empresa_tycoon":
            ben = getattr(scene, "beneficio", 0.0)
            margen = getattr(scene, "margen_pct", 0.0)
            if ben >= 250 and margen >= 25:
                widget.set_status("GOOD", 95,
                                  "Empresa Lider y Rentable",
                                  "Tu estructura de costos e ingresos genera fuerte beneficio neto.",
                                  "Invierte en I+D para blindar tu ventaja competitiva.")
            elif ben >= 0:
                widget.set_status("NEUTRAL", 55,
                                  "Operando en Punto Muerto",
                                  "Cubres costos fijos y variables pero tu beneficio es limitado.",
                                  "Ajusta el precio o reduce costos variables contratando con cuidado.")
            else:
                widget.set_status("BAD", 20,
                                  "Perdidas y Riesgo Quiebra",
                                  "Los costos superan los ingresos totales: flujo de caja negativo.",
                                  "Aumenta la eficiencia o cierra lineas de costo fijo excesivas.")

        elif key == "hacienda_banco":
            defic = getattr(scene, "deficit", 0.0)
            inf = getattr(scene, "inflacion", 3.0)
            aprob = getattr(scene, "aprobacion", 65.0)
            if abs(defic) <= 2.5 and 1.5 <= inf <= 4.5 and aprob >= 65:
                widget.set_status("GOOD", 94,
                                  "Gestion Publica Ejemplar",
                                  "Presupuesto balanceado, inflacion a raya y alta aprobacion social.",
                                  "Mantente en la cuspide de la Curva de Laffer.")
            elif inf > 10.0 or defic > 6.0:
                widget.set_status("BAD", 25,
                                  "Desajuste Macroeconómico",
                                  "La emision monetaria o el déficit descontrolan los precios.",
                                  "Sube la tasa de interes y racionaliza el gasto publico.")
            else:
                widget.set_status("NEUTRAL", 60,
                                  "Equilibrio Fiscal Tenso",
                                  "Las cuentas cierran pero con presiones en precios o aprobacion.",
                                  "Calibra la tasa impositiva para no ahogar la recaudacion.")

        elif key == "isla_recursos":
            ut = getattr(scene, "utilidad_total", 50.0)
            uso = getattr(scene, "uso_recursos", 100.0)
            if ut >= 80 and 95 <= uso <= 100:
                widget.set_status("GOOD", 96,
                                  "Optimo de Pareto",
                                  "Maxima utilidad social sin exceder la FPP ni dejar ociosidad.",
                                  "Has encontrado la canasta de maximo bienestar ciudadano.")
            elif uso > 100:
                widget.set_status("BAD", 15,
                                  "Asignacion Imposible",
                                  "La economia opera fuera de la FPP: sobreexplotacion inviable.",
                                  "Reduce los recursos asignados hasta llegar al 100%.")
            else:
                widget.set_status("NEUTRAL", 50,
                                  "Capacidad Subutilizada",
                                  "Quedan recursos ociosos sin transformar en bienestar comun.",
                                  "Asigna el 100% disponible entre alimentos y tecnologia.")
    except Exception as e:
        print(f"[Feedback] Error evaluando estado de {key}: {e}")

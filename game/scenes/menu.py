# ============================================================
#  MENÚ PRINCIPAL – Experiencias Fusionadas y Modo EcoTycoon
# ============================================================
import pygame
import math
from game.constants import *
from game.ui import get_font, text, Panel
from game.sprites import draw_pixel_stars, draw_pixel_grid
from game.audio import audio


class MenuScene:
    def __init__(self):
        self.next_scene = None
        self.toggle_fullscreen_requested = False
        self.view_mode = "fusionados"  # "fusionados" o "individuales"
        self.active_category = "todos"
        self._bg = None
        self._tick = 0
        self._build()

    def _build(self):
        self.font_title = get_font(40, bold=True)
        self.font_sub   = get_font(15)
        self.font_tab   = get_font(12, bold=True)
        self.font_card  = get_font(15, bold=True)
        self.font_badge = get_font(10, bold=True)
        self.font_desc  = get_font(11)
        self.font_btn   = get_font(12, bold=True)

        # ── Banner del Minijuego Campaña EcoTycoon ──
        self.banner_rect = pygame.Rect(60, 108, SCREEN_W - 120, 84)
        self.btn_play_tycoon = pygame.Rect(self.banner_rect.right - 180, self.banner_rect.y + 22, 160, 40)

        # ── Botones de Modo (Fusionados vs Individuales) ──
        self.btn_mode_fusion = pygame.Rect(60, 206, 260, 32)
        self.btn_mode_indiv  = pygame.Rect(330, 206, 260, 32)

        # ── Pestañas de Ejes Temáticos (para modo individuales) ──
        self.tabs = []
        tab_w = 172
        tab_h = 30
        tab_gap = 10
        tab_start_x = 60
        tab_y = 246

        for cat in CATEGORIAS:
            r = pygame.Rect(tab_start_x, tab_y, tab_w, tab_h)
            self.tabs.append({
                "id": cat["id"],
                "nombre": cat["nombre"],
                "icono": cat["icono"],
                "rect": r,
                "color": cat.get("color", CYAN)
            })
            tab_start_x += tab_w + tab_gap

        # Botones de utilidad superior
        self.btn_fs = pygame.Rect(SCREEN_W - 130, 16, 110, 32)
        self.btn_snd = pygame.Rect(SCREEN_W - 245, 16, 105, 32)

        self._build_fused_cards()
        self._rebuild_cards()

    def _build_fused_cards(self):
        """Genera las 4 tarjetas grandes para las experiencias fusionadas."""
        self.fused_cards = [
            {
                "key": "gran_mercado",
                "nombre": "El Gran Mercado",
                "sub": "Microeconomía Total",
                "cat": "OFERTA + DEMANDA + PRECIOS + EQUILIBRIO",
                "desc": "Controla las dos fuerzas del mercado, ajusta precios máximos/mínimos y analiza las tijeras Marshallianas.",
                "accent": (0, 220, 220),
                "icon": "⚖",
                "rect": pygame.Rect(60, 252, 440, 165),
                "hovered": False,
            },
            {
                "key": "empresa_tycoon",
                "nombre": "Tycoon Empresarial",
                "sub": "Teoría de la Firma & Mercados",
                "cat": "FABRICANTES + EMPRESAS + COMPETENCIA",
                "desc": "Gestiona maquinaria, personal e I+D. Optimiza tu punto de equilibrio frente a monopolios y rivales.",
                "accent": (60, 140, 255),
                "icon": "🏭",
                "rect": pygame.Rect(524, 252, 440, 165),
                "hovered": False,
            },
            {
                "key": "hacienda_banco",
                "nombre": "Gabinete Económico",
                "sub": "Hacienda & Banco Central",
                "cat": "GOBIERNO + IMPUESTOS (LAFFER) + INFLACIÓN",
                "desc": "Calibra la tasa impositiva óptima, financia el gasto social y maneja la masa monetaria para frenar la inflación.",
                "accent": (210, 80, 220),
                "icon": "🏛",
                "rect": pygame.Rect(60, 432, 440, 165),
                "hovered": False,
            },
            {
                "key": "isla_recursos",
                "nombre": "La Frontera de Recursos",
                "sub": "FPP & Utilidad Social",
                "cat": "ESCASEZ + CONSUMIDORES + BIENESTAR",
                "desc": "Encuentra el óptimo de Pareto asignando recursos escasos entre alimentos y tecnología sin caer en el sobregiro.",
                "accent": (255, 160, 40),
                "icon": "🏝",
                "rect": pygame.Rect(524, 432, 440, 165),
                "hovered": False,
            },
        ]

    def _rebuild_cards(self):
        """Genera las tarjetas de los modelos individuales según la categoría seleccionada."""
        self.cards = []
        allowed_keys = None
        for cat in CATEGORIAS:
            if cat["id"] == self.active_category:
                allowed_keys = cat["modelos"]
                break
        if allowed_keys is None:
            allowed_keys = [k for n, k in MODELOS if k != "ecotycoon"]

        filtered = [(n, k) for n, k in MODELOS if k in allowed_keys and k != "ecotycoon"]

        cols = 5
        pad_x, pad_y = 60, 288
        cw, ch = 166, 74
        gap_x, gap_y = 18, 14

        for i, (nombre, key) in enumerate(filtered):
            col = i % cols
            row = i // cols
            x = pad_x + col * (cw + gap_x)
            y = pad_y + row * (ch + gap_y)
            accent = MODELO_COLORES.get(key, CYAN)

            cat_label = "ECONOMÍA"
            for cat in CATEGORIAS:
                if cat["id"] != "todos" and key in cat["modelos"]:
                    cat_label = cat["id"].upper()
                    break

            self.cards.append({
                "rect":   pygame.Rect(x, y, cw, ch),
                "nombre": nombre,
                "key":    key,
                "accent": accent,
                "cat":    cat_label,
                "hovered": False,
            })

    def _make_bg(self, surface):
        bg = pygame.Surface(surface.get_size())
        bg.fill(DARK_BG)
        draw_pixel_grid(bg, cell=40, color=(16, 16, 38))
        draw_pixel_stars(bg, seed=42)
        self._bg = bg

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_m:
                audio.toggle_mute()
                return

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.btn_fs.collidepoint(event.pos):
                audio.play("toggle")
                self.toggle_fullscreen_requested = True
                return
            if self.btn_snd.collidepoint(event.pos):
                audio.toggle_mute()
                return

            # Clic en el banner de EcoTycoon
            if self.banner_rect.collidepoint(event.pos):
                audio.play("click")
                self.next_scene = "ecotycoon"
                return

            # Clic en pestañas de vista (Fusionados vs Individuales)
            if self.btn_mode_fusion.collidepoint(event.pos):
                if self.view_mode != "fusionados":
                    self.view_mode = "fusionados"
                    audio.play("click")
                return
            if self.btn_mode_indiv.collidepoint(event.pos):
                if self.view_mode != "individuales":
                    self.view_mode = "individuales"
                    audio.play("click")
                return

            # Clic en tarjetas fusionadas
            if self.view_mode == "fusionados":
                for fc in self.fused_cards:
                    if fc["rect"].collidepoint(event.pos):
                        audio.play("click")
                        self.next_scene = fc["key"]
                        return

            # Modo individuales
            if self.view_mode == "individuales":
                for t in self.tabs:
                    if t["rect"].collidepoint(event.pos):
                        if self.active_category != t["id"]:
                            self.active_category = t["id"]
                            audio.play("click")
                            self._rebuild_cards()
                        return

                for c in self.cards:
                    if c["rect"].collidepoint(event.pos):
                        audio.play("click")
                        self.next_scene = c["key"]
                        return

    def update(self, dt):
        self._tick += dt
        mx, my = pygame.mouse.get_pos()
        if self.view_mode == "fusionados":
            for fc in self.fused_cards:
                fc["hovered"] = fc["rect"].collidepoint(mx, my)
        else:
            for c in self.cards:
                c["hovered"] = c["rect"].collidepoint(mx, my)

    def draw(self, surface):
        if self._bg is None:
            self._make_bg(surface)
        surface.blit(self._bg, (0, 0))

        mouse = pygame.mouse.get_pos()

        # ── Botones de utilidades superiores ──
        hov_fs = self.btn_fs.collidepoint(mouse)
        pygame.draw.rect(surface, CYAN if hov_fs else (24, 34, 50), self.btn_fs, border_radius=4)
        pygame.draw.rect(surface, CYAN, self.btn_fs, 1, border_radius=4)
        t_fs = self.font_btn.render("⛶ PANTALLA", True, BLACK if hov_fs else CYAN)
        surface.blit(t_fs, (self.btn_fs.centerx - t_fs.get_width() // 2,
                            self.btn_fs.centery - t_fs.get_height() // 2))

        hov_snd = self.btn_snd.collidepoint(mouse)
        snd_col = RED if audio.muted else GREEN
        pygame.draw.rect(surface, snd_col if hov_snd else (24, 34, 50), self.btn_snd, border_radius=4)
        pygame.draw.rect(surface, snd_col, self.btn_snd, 1, border_radius=4)
        snd_label = "MUTE: ON" if audio.muted else "SND: ACTIVO"
        t_snd = self.font_btn.render(snd_label, True, BLACK if hov_snd else snd_col)
        surface.blit(t_snd, (self.btn_snd.centerx - t_snd.get_width() // 2,
                             self.btn_snd.centery - t_snd.get_height() // 2))

        # ── Cabecera Principal ──
        t_title = self.font_title.render("EcoSim: Simulador Económico", True, YELLOW)
        surface.blit(t_title, (60, 24))

        t_sub = self.font_sub.render(
            "Emprendimiento 2  •  Modelos Interactivos de Microeconomía y Macroeconomía",
            True, GRAY_LIGHT)
        surface.blit(t_sub, (60, 72))

        # ── Banner del Minijuego Campaña EcoTycoon ──
        b_hov = self.banner_rect.collidepoint(mouse)
        pygame.draw.rect(surface, (18, 24, 40), self.banner_rect, border_radius=8)
        pygame.draw.rect(surface, YELLOW if b_hov else (180, 140, 20), self.banner_rect, 2 if b_hov else 1, border_radius=8)

        # Insignia "MODO INTEGRADO"
        badge_rect = pygame.Rect(self.banner_rect.x + 14, self.banner_rect.y + 12, 140, 20)
        pygame.draw.rect(surface, YELLOW, badge_rect, border_radius=3)
        t_bg = self.font_badge.render("★ CAMPAÑA MACRO", True, BLACK)
        surface.blit(t_bg, (badge_rect.x + 6, badge_rect.y + 4))

        # Título del banner
        font_bt = get_font(17, bold=True)
        t_bn = font_bt.render("EcoTycoon: Desafío de Gestión Macroeconómica Total", True, WHITE if b_hov else YELLOW)
        surface.blit(t_bn, (self.banner_rect.x + 165, self.banner_rect.y + 12))

        # Descripción del banner
        t_bd = self.font_desc.render(
            "Gobierna la nación durante 8 trimestres: coordina tasas, impuestos y gasto público. ¡Evita el Game Over y gana!",
            True, GRAY_LIGHT)
        surface.blit(t_bd, (self.banner_rect.x + 16, self.banner_rect.y + 45))

        # Botón "JUGAR RETO ▶"
        btn_hov = self.btn_play_tycoon.collidepoint(mouse)
        pygame.draw.rect(surface, YELLOW if btn_hov else YELLOW_DARK, self.btn_play_tycoon, border_radius=5)
        t_play = self.font_btn.render("JUGAR CAMPAÑA ▶", True, BLACK)
        surface.blit(t_play, (self.btn_play_tycoon.centerx - t_play.get_width() // 2,
                              self.btn_play_tycoon.centery - t_play.get_height() // 2))

        # ── Pestañas de Selección de Modo ──
        # 1. Modo Fusionados
        is_fus = (self.view_mode == "fusionados")
        fus_hov = self.btn_mode_fusion.collidepoint(mouse)
        fus_bg = CYAN if is_fus else ((28, 38, 56) if fus_hov else PANEL_BG)
        pygame.draw.rect(surface, fus_bg, self.btn_mode_fusion, border_top_left_radius=6, border_top_right_radius=6)
        pygame.draw.rect(surface, CYAN, self.btn_mode_fusion, 2 if is_fus else 1, border_top_left_radius=6, border_top_right_radius=6)
        txt_fus = self.font_tab.render("★ 4 MINIJUEGOS FUSIONADOS (DIRECTO)", True, BLACK if is_fus else CYAN)
        surface.blit(txt_fus, (self.btn_mode_fusion.centerx - txt_fus.get_width() // 2,
                               self.btn_mode_fusion.centery - txt_fus.get_height() // 2))

        # 2. Modo Clásico Individual
        is_ind = (self.view_mode == "individuales")
        ind_hov = self.btn_mode_indir = self.btn_mode_indiv.collidepoint(mouse)
        ind_bg = GRAY_LIGHT if is_ind else ((28, 38, 56) if ind_hov else PANEL_BG)
        pygame.draw.rect(surface, ind_bg, self.btn_mode_indiv, border_top_left_radius=6, border_top_right_radius=6)
        pygame.draw.rect(surface, GRAY_LIGHT if is_ind else GRAY_DARK, self.btn_mode_indiv, 2 if is_ind else 1, border_top_left_radius=6, border_top_right_radius=6)
        txt_ind = self.font_tab.render("LABORATORIOS CLÁSICOS (13 MÓDULOS)", True, BLACK if is_ind else GRAY_LIGHT)
        surface.blit(txt_ind, (self.btn_mode_indiv.centerx - txt_ind.get_width() // 2,
                               self.btn_mode_indiv.centery - txt_ind.get_height() // 2))

        # Línea divisoria
        pygame.draw.line(surface, GRAY_DARK, (60, 238), (SCREEN_W - 60, 238), 2)

        # ── VISTA 1: MINIJUEGOS FUSIONADOS ──
        if self.view_mode == "fusionados":
            for fc in self.fused_cards:
                accent = fc["accent"]
                rect = fc["rect"]
                hov = fc["hovered"]

                # Sombra
                s_surf = pygame.Surface((rect.w + 4, rect.h + 4), pygame.SRCALPHA)
                s_surf.fill((0, 0, 0, 90))
                surface.blit(s_surf, (rect.x + 2, rect.y + 2))

                # Fondo
                bg_col = tuple(min(255, c_ + 24) for c_ in PANEL_BG) if hov else PANEL_BG
                pygame.draw.rect(surface, bg_col, rect, border_radius=8)
                border_w = 3 if hov else 1
                pygame.draw.rect(surface, accent if hov else GRAY_DARK, rect, border_w, border_radius=8)

                # Barra indicadora lateral
                ind = pygame.Rect(rect.x, rect.y + 8, 6, rect.h - 16)
                pygame.draw.rect(surface, accent, ind, border_radius=3)

                # Insignia de módulos absorbidos
                badge_w = 340
                b_r = pygame.Rect(rect.x + 18, rect.y + 12, badge_w, 18)
                pygame.draw.rect(surface, (20, 30, 48), b_r, border_radius=3)
                pygame.draw.rect(surface, accent, b_r, 1, border_radius=3)
                t_cat = self.font_badge.render(f"FUSIÓN: {fc['cat']}", True, accent)
                surface.blit(t_cat, (b_r.x + 6, b_r.y + 3))

                # Título e ícono
                t_nom = self.font_card.render(f"{fc['icon']} {fc['nombre']}", True, WHITE if hov else accent)
                surface.blit(t_nom, (rect.x + 18, rect.y + 38))

                # Subtítulo temático
                t_sub = self.font_desc.render(f"— {fc['sub']}", True, GRAY_LIGHT)
                surface.blit(t_sub, (rect.x + 22 + t_nom.get_width(), rect.y + 40))

                # Descripción pedagógica
                render_lines = [fc['desc']]
                # Dividir en dos líneas si es largo
                words = fc['desc'].split(" ")
                mid = len(words) // 2
                l1 = " ".join(words[:mid])
                l2 = " ".join(words[mid:])

                surface.blit(self.font_desc.render(l1, True, GRAY_LIGHT), (rect.x + 18, rect.y + 66))
                surface.blit(self.font_desc.render(l2, True, GRAY_LIGHT), (rect.x + 18, rect.y + 84))

                # Botón de entrada en la tarjeta
                btn_card_rect = pygame.Rect(rect.right - 145, rect.bottom - 42, 130, 30)
                pygame.draw.rect(surface, accent if hov else (28, 38, 56), btn_card_rect, border_radius=4)
                pygame.draw.rect(surface, accent, btn_card_rect, 1, border_radius=4)
                t_entrar = self.font_btn.render("JUGAR RETO ▶", True, BLACK if hov else accent)
                surface.blit(t_entrar, (btn_card_rect.centerx - t_entrar.get_width() // 2,
                                        btn_card_rect.centery - t_entrar.get_height() // 2))

        # ── VISTA 2: LABORATORIOS CLÁSICOS ──
        else:
            # Pestañas de categoría
            for t in self.tabs:
                is_active = (self.active_category == t["id"])
                t_rect = t["rect"]
                thov = t_rect.collidepoint(mouse)

                if is_active:
                    tab_col = t["color"]
                    txt_col = BLACK
                    bg_c = t["color"]
                elif thov:
                    tab_col = t["color"]
                    txt_col = WHITE
                    bg_c = (28, 32, 48)
                else:
                    tab_col = GRAY_DARK
                    txt_col = GRAY_LIGHT
                    bg_c = PANEL_BG

                pygame.draw.rect(surface, bg_c, t_rect, border_top_left_radius=6, border_top_right_radius=6)
                pygame.draw.rect(surface, tab_col, t_rect, 1 if not is_active else 2, border_top_left_radius=6, border_top_right_radius=6)

                txt = self.font_tab.render(f"{t['icono']} {t['nombre']}", True, txt_col)
                surface.blit(txt, (t_rect.centerx - txt.get_width() // 2,
                                   t_rect.centery - txt.get_height() // 2))

            pygame.draw.line(surface, GRAY_DARK, (60, 276), (SCREEN_W - 60, 276), 2)

            for c in self.cards:
                accent = c["accent"]
                rect   = c["rect"]
                hov    = c["hovered"]

                s_surf = pygame.Surface((rect.w + 4, rect.h + 4), pygame.SRCALPHA)
                s_surf.fill((0, 0, 0, 90))
                surface.blit(s_surf, (rect.x + 2, rect.y + 2))

                bg_col = tuple(min(255, c_ + 22) for c_ in PANEL_BG) if hov else PANEL_BG
                pygame.draw.rect(surface, bg_col, rect, border_radius=6)
                border_w = 2 if not hov else 3
                pygame.draw.rect(surface, accent if hov else GRAY_DARK, rect, border_w, border_radius=6)

                ind = pygame.Rect(rect.x, rect.y + 6, 4, rect.h - 12)
                pygame.draw.rect(surface, accent, ind, border_radius=2)

                t_cat = self.font_badge.render(c["cat"], True, accent)
                surface.blit(t_cat, (rect.x + 12, rect.y + 10))

                color = WHITE if hov else GRAY_LIGHT
                nom = self.font_card.render(c["nombre"], True, color)
                surface.blit(nom, (rect.x + 12, rect.y + 26))

                if hov:
                    arr = self.font_card.render("▶ entrar", True, accent)
                    surface.blit(arr, (rect.x + 12, rect.y + 48))

        # Pie de página
        foot = self.font_desc.render(
            "F11: Pantalla Completa  •  M: Mutear/Desmutear  •  4 Minijuegos Fisionados + Campaña EcoTycoon", True, GRAY_LIGHT)
        surface.blit(foot, (SCREEN_W // 2 - foot.get_width() // 2, SCREEN_H - 18))

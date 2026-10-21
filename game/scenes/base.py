# ============================================================
#  BASE SCENE – clase base para todas las escenas
# ============================================================
import pygame
from game.constants import *
from game.ui import draw_scene_title, draw_back_button, get_font
from game.sprites import draw_pixel_grid, draw_pixel_stars
from game.tutorials import TutorialModal
from game.audio import audio
from game.feedback import ModelHealthWidget, update_scene_health


class BaseScene:
    """
    Clase base. Las subclases implementan:
      - build()        → crear sliders, gráficas, botones extras
      - update(dt)     → lógica de simulación
      - draw_content() → dibujar contenido específico
    """
    KEY = ""
    TITLE = ""
    SUBTITLE = ""

    _seen_tutorials = set()

    def __init__(self):
        self.next_scene = None
        self.accent = MODELO_COLORES.get(self.KEY, CYAN)
        self._bg = None
        self.tick = 0
        self.tutorial_modal = TutorialModal()
        self.toggle_fullscreen_requested = False

        # Configurar posición del monitor de salud según el modelo
        if self.KEY in ("fabricantes", "consumidores", "empresas", "gobierno"):
            wx, wy, ww, wh = 785, 92, 225, 185
        elif self.KEY == "mercado":
            wx, wy, ww, wh = 720, 415, 285, 180
        elif self.KEY in ("equilibrio", "inflacion"):
            wx, wy, ww, wh = 705, 395, 295, 185
        elif self.KEY == "competencia":
            wx, wy, ww, wh = 705, 330, 295, 180
        elif self.KEY == "precios":
            wx, wy, ww, wh = 705, 345, 295, 180
        elif self.KEY in ("ecotycoon", "gran_mercado", "empresa_tycoon", "hacienda_banco", "isla_recursos"):
            wx, wy, ww, wh = 710, 220, 280, 175
        else: # oferta, demanda, impuestos, escasez
            wx, wy, ww, wh = 705, 250, 295, 180

        self.health_widget = ModelHealthWidget(wx, wy, ww, wh)

        # Mostrar el tutorial automáticamente la primera vez que se visita este módulo
        self.show_tutorial = False
        if self.KEY and self.KEY not in BaseScene._seen_tutorials:
            self.show_tutorial = True
            BaseScene._seen_tutorials.add(self.KEY)
            audio.play("guide")
        self.build()

    def _make_bg(self, surface):
        bg = pygame.Surface(surface.get_size())
        bg.fill(DARK_BG)
        draw_pixel_grid(bg, cell=40, color=(16, 16, 40))
        draw_pixel_stars(bg, seed=hash(self.KEY) & 0xFFFF)
        self._bg = bg

    # ── Override en subclases ──────────────────────────────────
    def build(self):
        pass

    def handle_event(self, event):
        pass

    def update(self, dt):
        self.tick += dt

    def draw_content(self, surface):
        pass

    def _draw_top_buttons(self, surface, mouse_pos):
        """Dibuja los botones de la barra superior: Menú, Guía, Fullscreen y Audio."""
        font = get_font(13, bold=True)

        # 1. Botón ◄ MENÚ
        back_rect = pygame.Rect(SCREEN_W - 95, 14, 85, 34)
        hov_back = back_rect.collidepoint(mouse_pos)
        pygame.draw.rect(surface, GRAY if hov_back else GRAY_DARK, back_rect, border_radius=4)
        pygame.draw.rect(surface, GRAY_LIGHT, back_rect, 1, border_radius=4)
        t_back = font.render("◄ MENU", True, WHITE)
        surface.blit(t_back, (back_rect.centerx - t_back.get_width() // 2,
                              back_rect.centery - t_back.get_height() // 2))

        # 2. Botón ? GUÍA
        guide_rect = pygame.Rect(SCREEN_W - 190, 14, 85, 34)
        hov_guide = guide_rect.collidepoint(mouse_pos)
        col_g = self.accent if hov_guide else (28, 38, 56)
        pygame.draw.rect(surface, col_g, guide_rect, border_radius=4)
        pygame.draw.rect(surface, self.accent, guide_rect, 1, border_radius=4)
        t_guide = font.render("? GUIA", True, BLACK if hov_guide else self.accent)
        surface.blit(t_guide, (guide_rect.centerx - t_guide.get_width() // 2,
                               guide_rect.centery - t_guide.get_height() // 2))

        # 3. Botón ⛶ FULLSCREEN
        fs_rect = pygame.Rect(SCREEN_W - 275, 14, 75, 34)
        hov_fs = fs_rect.collidepoint(mouse_pos)
        col_fs = CYAN if hov_fs else (24, 34, 48)
        pygame.draw.rect(surface, col_fs, fs_rect, border_radius=4)
        pygame.draw.rect(surface, CYAN, fs_rect, 1, border_radius=4)
        t_fs = font.render("[FS]", True, BLACK if hov_fs else CYAN)
        surface.blit(t_fs, (fs_rect.centerx - t_fs.get_width() // 2,
                            fs_rect.centery - t_fs.get_height() // 2))

        # 4. Botón MUTE / AUDIO
        snd_rect = pygame.Rect(SCREEN_W - 365, 14, 80, 34)
        hov_snd = snd_rect.collidepoint(mouse_pos)
        snd_text = "SND: OFF" if audio.muted else "SND: ON"
        snd_col = RED if audio.muted else GREEN
        col_snd = snd_col if hov_snd else (24, 34, 48)
        pygame.draw.rect(surface, col_snd, snd_rect, border_radius=4)
        pygame.draw.rect(surface, snd_col, snd_rect, 1, border_radius=4)
        t_snd = font.render(snd_text, True, BLACK if hov_snd else snd_col)
        surface.blit(t_snd, (snd_rect.centerx - t_snd.get_width() // 2,
                             snd_rect.centery - t_snd.get_height() // 2))

        return back_rect, guide_rect, fs_rect, snd_rect

    # ── Llamado por el motor principal ─────────────────────────
    def _handle_event(self, event):
        mouse = pygame.mouse.get_pos()
        back_rect = pygame.Rect(SCREEN_W - 95, 14, 85, 34)
        guide_rect = pygame.Rect(SCREEN_W - 190, 14, 85, 34)
        fs_rect = pygame.Rect(SCREEN_W - 275, 14, 75, 34)
        snd_rect = pygame.Rect(SCREEN_W - 365, 14, 80, 34)

        # Si el tutorial modal está abierto
        if self.show_tutorial:
            if event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_SPACE, pygame.K_RETURN, pygame.K_ESCAPE, pygame.K_h, pygame.K_F1):
                    self.show_tutorial = False
                    audio.play("click")
                    return
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if self.tutorial_modal.is_close_clicked(event.pos) or not self.tutorial_modal.rect.collidepoint(event.pos):
                    self.show_tutorial = False
                    audio.play("click")
                    return
            return  # Consumir eventos del mouse para no mover sliders de fondo

        # Atajos de teclado universales dentro de la escena
        if event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_h, pygame.K_F1):
                self.show_tutorial = True
                audio.play("guide")
                return
            if event.key == pygame.K_m:
                audio.toggle_mute()
                return

        # Clics normales cuando el tutorial está cerrado
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if back_rect.collidepoint(event.pos):
                audio.play("click")
                self.next_scene = "menu"
                return
            if guide_rect.collidepoint(event.pos):
                self.show_tutorial = True
                audio.play("guide")
                return
            if fs_rect.collidepoint(event.pos):
                audio.play("toggle")
                self.toggle_fullscreen_requested = True
                return
            if snd_rect.collidepoint(event.pos):
                audio.toggle_mute()
                return

        self.handle_event(event)

    def _update(self, dt):
        if self.show_tutorial:
            # Pausar la simulación mientras el usuario lee el tutorial
            return
        self.update(dt)
        if self.KEY and hasattr(self, "health_widget"):
            update_scene_health(self.KEY, self, self.health_widget)
            self.health_widget.update(dt)

    def _draw(self, surface):
        if self._bg is None:
            self._make_bg(surface)
        surface.blit(self._bg, (0, 0))
        draw_scene_title(surface, self.TITLE, self.SUBTITLE, self.accent)
        mouse = pygame.mouse.get_pos()
        self._draw_top_buttons(surface, mouse)
        self.draw_content(surface)
        if self.KEY and hasattr(self, "health_widget"):
            self.health_widget.draw(surface)
        if self.show_tutorial:
            self.tutorial_modal.draw(surface, self.KEY, self.accent)

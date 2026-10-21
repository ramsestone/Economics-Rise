"""
╔══════════════════════════════════════════════════════════╗
║   EcoSim – Simulador Económico  │  Emprendimiento 2      ║
║   Pygame  8-bit  •  13 módulos económicos interactivos   ║
╚══════════════════════════════════════════════════════════╝
Controles:
  Mouse    – interactuar con sliders, botones y menú
  ESC      – salir al menú  /  salir del juego
"""

import sys
import pygame

from game.constants import SCREEN_W, SCREEN_H, FPS, TITLE, DARK_BG
from game.scenes.menu import MenuScene

# ── Importar todas las escenas ────────────────────────────────
from game.scenes.fabricantes  import FabricantesScene
from game.scenes.consumidores import ConsumidoresScene
from game.scenes.empresas     import EmpresasScene
from game.scenes.gobierno     import GobiernoScene
from game.scenes.mercado      import MercadoScene
from game.scenes.oferta       import OfertaScene
from game.scenes.demanda      import DemandaScene
from game.scenes.precios      import PreciosScene
from game.scenes.impuestos    import ImpuestosScene
from game.scenes.equilibrio   import EquilibrioScene
from game.scenes.inflacion    import InflacionScene
from game.scenes.competencia  import CompetenciaScene
from game.scenes.escasez      import EscasezScene
from game.scenes.ecotycoon    import EcoTycoonScene

# ── Minijuegos Fusionados ────────────────────────────────────
from game.scenes.gran_mercado   import GranMercadoScene
from game.scenes.empresa_tycoon import EmpresaTycoonScene
from game.scenes.hacienda_banco import HaciendaBancoScene
from game.scenes.isla_recursos  import IslaRecursosScene


SCENE_MAP = {
    "menu":           MenuScene,
    "ecotycoon":      EcoTycoonScene,
    "gran_mercado":   GranMercadoScene,
    "empresa_tycoon": EmpresaTycoonScene,
    "hacienda_banco": HaciendaBancoScene,
    "isla_recursos":  IslaRecursosScene,
    # Módulos académicos individuales (compatibilidad)
    "fabricantes":    FabricantesScene,
    "consumidores":   ConsumidoresScene,
    "empresas":       EmpresasScene,
    "gobierno":       GobiernoScene,
    "mercado":        MercadoScene,
    "oferta":         OfertaScene,
    "demanda":        DemandaScene,
    "precios":        PreciosScene,
    "impuestos":      ImpuestosScene,
    "equilibrio":     EquilibrioScene,
    "inflacion":      InflacionScene,
    "competencia":    CompetenciaScene,
    "escasez":        EscasezScene,
}


from game.audio import audio


def main():
    pygame.init()
    pygame.display.set_caption(TITLE)

    is_fullscreen = False
    try:
        screen = pygame.display.set_mode((SCREEN_W, SCREEN_H), pygame.SCALED)
    except Exception:
        screen = pygame.display.set_mode((SCREEN_W, SCREEN_H))
    clock  = pygame.time.Clock()

    def do_toggle_fullscreen():
        nonlocal is_fullscreen, screen
        is_fullscreen = not is_fullscreen
        audio.play("toggle")
        if is_fullscreen:
            try:
                screen = pygame.display.set_mode((SCREEN_W, SCREEN_H), pygame.FULLSCREEN | pygame.SCALED)
            except Exception:
                screen = pygame.display.set_mode((SCREEN_W, SCREEN_H), pygame.FULLSCREEN)
        else:
            try:
                screen = pygame.display.set_mode((SCREEN_W, SCREEN_H), pygame.SCALED)
            except Exception:
                screen = pygame.display.set_mode((SCREEN_W, SCREEN_H))

    # Iniciar música de fondo
    audio.start_music()

    # Cargar ícono de la ventana (mascota pixel con gafas de sol)
    try:
        import os
        base_path = getattr(sys, "_MEIPASS", os.getcwd())
        icon_path = os.path.join(base_path, "assets", "icon.png")
        if os.path.exists(icon_path):
            icon_surf = pygame.image.load(icon_path)
            pygame.display.set_icon(icon_surf)
        else:
            icon = pygame.Surface((32, 32), pygame.SRCALPHA)
            pygame.draw.circle(icon, (255, 215, 60), (16, 16), 14)
            pygame.display.set_icon(icon)
    except Exception:
        pass

    current_key = "menu"
    scene = MenuScene()

    running = True
    while running:
        dt = clock.tick(FPS)          # milisegundos

        # ── Eventos ────────────────────────────────────────────
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_F11 or (event.key == pygame.K_RETURN and (event.mod & pygame.KMOD_ALT)):
                    do_toggle_fullscreen()
                    continue
                if event.key == pygame.K_ESCAPE:
                    if current_key == "menu":
                        running = False
                    elif getattr(scene, "show_tutorial", False):
                        scene.show_tutorial = False
                        audio.play("click")
                        continue
                    else:
                        current_key = "menu"
                        scene = MenuScene()
                        audio.play("click")
                        continue

            # Delegar evento a la escena
            if current_key == "menu":
                scene.handle_event(event)
            else:
                scene._handle_event(event)

        # Checar petición de pantalla completa desde la UI
        if getattr(scene, "toggle_fullscreen_requested", False):
            scene.toggle_fullscreen_requested = False
            do_toggle_fullscreen()

        # ── Actualizar ─────────────────────────────────────────
        if current_key == "menu":
            scene.update(dt)
        else:
            scene._update(dt)

        # ── Transición de escena ───────────────────────────────
        if scene.next_scene is not None:
            next_key = scene.next_scene
            scene.next_scene = None
            if next_key in SCENE_MAP:
                current_key = next_key
                scene = SCENE_MAP[next_key]()

        # ── Dibujar ────────────────────────────────────────────
        screen.fill(DARK_BG)
        if current_key == "menu":
            scene.draw(screen)
        else:
            scene._draw(screen)

        pygame.display.flip()

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()

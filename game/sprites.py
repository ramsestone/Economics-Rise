# ============================================================
#  SPRITES 8-BIT DIBUJADOS CON PIXELS
# ============================================================
import pygame
from game.constants import *


def _scale(surf, factor=3):
    w, h = surf.get_size()
    return pygame.transform.scale(surf, (w * factor, h * factor))


def make_surface(pixels, palette, scale=3, colorkey=(255, 0, 255)):
    """
    pixels: lista de strings, cada caracter = índice en palette.
    palette: dict char -> color tuple.  '.' = transparente.
    """
    h = len(pixels)
    w = max(len(r) for r in pixels)
    surf = pygame.Surface((w, h))
    surf.fill(colorkey)
    surf.set_colorkey(colorkey)
    for y, row in enumerate(pixels):
        for x, ch in enumerate(row):
            if ch == '.':
                continue
            surf.set_at((x, y), palette.get(ch, colorkey))
    return _scale(surf, scale)


# ── Paleta compartida ────────────────────────────────────────
_T = (255, 0, 255)   # transparente


# ── Fabricante (hombre con casco) ────────────────────────────
def sprite_fabricante():
    pal = {
        'H': (255, 210,  80),   # casco
        'h': (200, 160,  40),
        'S': (220, 180, 130),   # piel
        's': (180, 140,  90),
        'B': ( 80, 120, 200),   # body
        'b': ( 50,  80, 160),
        'P': (100, 100, 120),   # pantalón
        'p': ( 70,  70,  90),
    }
    pixels = [
        "..HHH..",
        ".HHHHH.",
        ".SSSSS.",
        "..SSS..",
        ".BBBBB.",
        "BBBBBBB",
        ".BBBBB.",
        ".PP.PP.",
        ".pp.pp.",
    ]
    return make_surface(pixels, pal, scale=3)


# ── Consumidor (persona con bolsa) ───────────────────────────
def sprite_consumidor():
    pal = {
        'F': (230, 170, 110),   # piel
        'f': (190, 130,  70),
        'R': (220,  60,  60),   # ropa
        'r': (160,  40,  40),
        'G': (255, 210,   0),   # bolsa
        'g': (200, 160,   0),
        'P': ( 80,  60,  80),   # pantalón
    }
    pixels = [
        "..FFF..",
        ".FFFFF.",
        "..FFF..",
        ".RRRRR.",
        "RRRRRGG",
        ".RRRGG.",
        ".PP.PP.",
        ".PP.PP.",
    ]
    return make_surface(pixels, pal, scale=3)


# ── Empresa (edificio pequeño) ────────────────────────────────
def sprite_empresa():
    pal = {
        'W': (160, 180, 210),   # pared
        'w': (120, 140, 170),
        'D': ( 80,  60,  40),   # puerta
        'G': (100, 200, 220),   # ventana
        'R': (200,  60,  60),   # techo
    }
    pixels = [
        "RRRRRRRRR",
        "RWWWWWWWR",
        "WGWWWGWWW",
        "WGWWWGWWW",
        "WWWWWWWWW",
        "WWDDDWWWW",
        "WWDDDWWWW",
        "WWDDDWWWW",
    ]
    return make_surface(pixels, pal, scale=3)


# ── Gobierno (capitolio estilizado) ───────────────────────────
def sprite_gobierno():
    pal = {
        'C': (210, 180, 130),   # columna/cúpula
        'c': (170, 140,  90),
        'B': (230, 200, 150),   # base
        'b': (180, 150, 100),
        'D': ( 80, 110, 200),   # puerta azul
        'F': (255, 210,   0),   # cúpula dorada
    }
    pixels = [
        "....FFF....",
        "...FFFFF...",
        "...CCCCC...",
        ".CCCCCCCCC.",
        "BBBBBBBBBBB",
        "BBcBBBBBcBB",
        "BBcBBDBBcBB",
        "BBcBBDBBcBB",
        "BBBBBBBBBBB",
    ]
    return make_surface(pixels, pal, scale=3)


# ── Mercado (tienda con toldo) ────────────────────────────────
def sprite_mercado():
    pal = {
        'T': (220,  80,  80),   # toldo
        't': (160,  40,  40),
        'W': (200, 200, 180),   # pared
        'G': (100, 210, 230),   # vitrina
        'P': (100, 180, 100),   # productos
        'D': ( 80,  60,  40),   # marco
    }
    pixels = [
        "TTTTTTTTTT",
        "tTtTtTtTtT",
        "DDDDDDDDDD",
        "WGGGPPPGGW",
        "WGGGPPPGGW",
        "WDDDDDDDDW",
        "WWWWWWWWWW",
    ]
    return make_surface(pixels, pal, scale=3)


# ── Moneda / Precio ───────────────────────────────────────────
def sprite_moneda():
    pal = {
        'Y': (255, 210,   0),
        'y': (200, 160,   0),
        'W': (255, 240, 120),
        'S': (240, 200,  50),
    }
    pixels = [
        ".YYYYY.",
        "YYYYYYY",
        "YWWWWWY",
        "YWySyWY",
        "YWSSSWY",
        "YYYYYYY",
        ".YYYYY.",
    ]
    return make_surface(pixels, pal, scale=3)


# ── Flecha arriba (oferta/demanda) ────────────────────────────
def sprite_flecha_arriba(color=(80, 220, 80)):
    pal = {
        'A': color,
        'a': tuple(max(0, c - 60) for c in color),
    }
    pixels = [
        "...A...",
        "..AAA..",
        ".AAAAA.",
        "AAAAAAA",
        "...A...",
        "...A...",
        "...A...",
    ]
    return make_surface(pixels, pal, scale=3)


def sprite_flecha_abajo(color=(220, 80, 80)):
    pal = {
        'A': color,
        'a': tuple(max(0, c - 60) for c in color),
    }
    pixels = [
        "...A...",
        "...A...",
        "...A...",
        "AAAAAAA",
        ".AAAAA.",
        "..AAA..",
        "...A...",
    ]
    return make_surface(pixels, pal, scale=3)


# ── Llama de inflación ────────────────────────────────────────
def sprite_llama():
    pal = {
        'R': (220,  60,  30),
        'O': (255, 140,   0),
        'Y': (255, 210,   0),
    }
    pixels = [
        "..R.R..",
        ".RRR.R.",
        "RRRRRRR",
        "ROOORRR",
        "ROYYORR",
        "OOYYYYO",
        ".OYYYO.",
        "..OOO..",
    ]
    return make_surface(pixels, pal, scale=3)


# ── Fábrica (chimenea) ────────────────────────────────────────
def sprite_fabrica():
    pal = {
        'B': (100, 120, 160),
        'b': ( 70,  90, 130),
        'C': ( 80,  80,  80),
        'c': ( 60,  60,  60),
        'S': (200, 200, 200),   # humo
        'W': (160, 160, 180),
        'R': (220,  80,  80),
    }
    pixels = [
        ".S.S.S.",
        "S.S.S.S",
        ".C.C...",
        ".C.C...",
        "BBBBBBB",
        "BWWWWWB",
        "BWWWWWB",
        "BBBRBBB",
        "BBBBBBB",
    ]
    return make_surface(pixels, pal, scale=3)


# ── Trofeo (competencia) ─────────────────────────────────────
def sprite_trofeo():
    pal = {
        'Y': (255, 210,   0),
        'y': (200, 160,   0),
        'S': (230, 190,  60),
        'W': (255, 240, 150),
        'B': (180, 140,  60),
    }
    pixels = [
        ".YYYYY.",
        "YYYYYYY",
        "YWWWWWY",
        ".YYYYYYY",
        "..YYYY..",
        "...yy...",
        "..BBBB..",
        ".BBBBBB.",
    ]
    return make_surface(pixels, pal, scale=3)


# ── Caja vacía (escasez) ──────────────────────────────────────
def sprite_caja_vacia():
    pal = {
        'B': (180, 140,  80),
        'b': (140, 100,  50),
        'L': (220, 180, 110),
        '.': _T,
    }
    pixels = [
        "BBBBBBB",
        "BLLLLLB",
        "BL...LB",
        "BL...LB",
        "BL...LB",
        "BBBBBBB",
    ]
    return make_surface(pixels, pal, scale=3)


# ── Balanza (equilibrio) ──────────────────────────────────────
def sprite_balanza():
    pal = {
        'G': (180, 180, 190),
        'g': (140, 140, 150),
        'Y': (255, 210,   0),
        'B': (100, 140, 200),
    }
    pixels = [
        "...G...",
        "GGGGGGG",
        "G..G..G",
        "B..G..B",
        "BB.G.BB",
        "...G...",
        "..GGG..",
        "...G...",
        ".GGGGG.",
    ]
    return make_surface(pixels, pal, scale=3)


# ── Impuesto (recibo) ─────────────────────────────────────────
def sprite_recibo():
    pal = {
        'W': (230, 230, 240),
        'w': (180, 180, 200),
        'G': ( 50, 180,  80),
        'R': (200,  50,  50),
        'L': (100, 100, 120),
    }
    pixels = [
        "WWWWWWW",
        "WLLLLLW",
        "WLLLLLW",
        "WGGGLLW",
        "WLLLLLW",
        "WRRRLLW",
        "WLLLLLW",
        "WWWWWWW",
    ]
    return make_surface(pixels, pal, scale=3)


# ── Fondo de estrellas (decorativo) ──────────────────────────
def draw_pixel_stars(surface, seed=42):
    import random
    rng = random.Random(seed)
    w, h = surface.get_size()
    for _ in range(80):
        x = rng.randint(0, w - 1)
        y = rng.randint(0, h - 1)
        brightness = rng.randint(80, 200)
        r = (brightness, brightness, min(255, brightness + 40))
        surface.set_at((x, y), r)


# ── Grid de píxeles (fondo) ────────────────────────────────────
def draw_pixel_grid(surface, cell=32, color=(20, 20, 45)):
    w, h = surface.get_size()
    for x in range(0, w, cell):
        pygame.draw.line(surface, color, (x, 0), (x, h))
    for y in range(0, h, cell):
        pygame.draw.line(surface, color, (0, y), (w, y))

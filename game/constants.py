# ============================================================
#  CONSTANTES GLOBALES DEL JUEGO
# ============================================================

# Pantalla
SCREEN_W = 1024
SCREEN_H = 640
FPS = 60
TITLE = "EcoSim – Simulador Económico"

# ── Paleta "8-bit oscuro" ────────────────────────────────────
BLACK       = (  0,   0,   0)
WHITE       = (255, 255, 255)
DARK_BG     = ( 10,  10,  25)
PANEL_BG    = ( 18,  18,  45)
PANEL_DARK  = ( 12,  12,  35)

# Colores de acento
CYAN        = (  0, 230, 255)
CYAN_DARK   = (  0, 160, 200)
GREEN       = ( 50, 220,  80)
GREEN_DARK  = ( 30, 140,  50)
RED         = (220,  50,  50)
RED_DARK    = (160,  30,  30)
YELLOW      = (255, 210,   0)
YELLOW_DARK = (180, 140,   0)
ORANGE      = (255, 140,   0)
ORANGE_DARK = (180,  90,   0)
PURPLE      = (160,  80, 220)
PURPLE_DARK = (100,  40, 160)
BLUE        = ( 60, 100, 230)
BLUE_DARK   = ( 40,  60, 160)
PINK        = (230,  80, 160)

# Grises
GRAY        = (120, 120, 140)
GRAY_DARK   = ( 60,  60,  80)
GRAY_LIGHT  = (180, 180, 200)

# ── Nombres de modelos ───────────────────────────────────────
MODELOS = [
    ("Fabricantes",    "fabricantes"),
    ("Consumidores",   "consumidores"),
    ("Empresas",       "empresas"),
    ("Gobierno",       "gobierno"),
    ("Mercado",        "mercado"),
    ("Oferta",         "oferta"),
    ("Demanda",        "demanda"),
    ("Precios",        "precios"),
    ("Impuestos",      "impuestos"),
    ("Equilibrio",     "equilibrio"),
    ("Inflación",      "inflacion"),
    ("Competencia",    "competencia"),
    ("Escasez",        "escasez"),
    ("EcoTycoon",      "ecotycoon"),
]

# ── Ejes temáticos pedagógicos ───────────────────────────────
CATEGORIAS = [
    {
        "id": "todos",
        "nombre": "TODOS (13)",
        "icono": "✦",
        "modelos": ["demanda", "oferta", "equilibrio", "precios", "mercado",
                    "fabricantes", "empresas", "competencia",
                    "consumidores", "escasez",
                    "gobierno", "impuestos", "inflacion"],
    },
    {
        "id": "mercado",
        "nombre": "MERCADO (5)",
        "icono": "⚖",
        "desc": "Microeconomía: oferta, demanda, precios y equilibrio",
        "color": (0, 220, 200),
        "modelos": ["demanda", "oferta", "equilibrio", "precios", "mercado"],
    },
    {
        "id": "empresas",
        "nombre": "EMPRESAS (3)",
        "icono": "🏭",
        "desc": "Teoría de la firma: insumos, costos y competencia",
        "color": (60, 140, 255),
        "modelos": ["fabricantes", "empresas", "competencia"],
    },
    {
        "id": "consumo",
        "nombre": "CONSUMIDOR (2)",
        "icono": "🛒",
        "desc": "Fundamentos: utilidad, presupuesto y escasez",
        "color": (255, 180, 40),
        "modelos": ["consumidores", "escasez"],
    },
    {
        "id": "macro",
        "nombre": "ESTADO (3)",
        "icono": "🏛",
        "desc": "Macroeconomía: política fiscal, Laffer e inflación",
        "color": (210, 80, 220),
        "modelos": ["gobierno", "impuestos", "inflacion"],
    },
]

# Colores por modelo (acento)
MODELO_COLORES = {
    "fabricantes":  (  0, 200, 140),
    "consumidores": (255, 180,  40),
    "empresas":     ( 60, 140, 255),
    "gobierno":     (200,  60, 200),
    "mercado":      (  0, 220, 220),
    "oferta":       ( 80, 220,  80),
    "demanda":      (220,  80,  80),
    "precios":      (255, 210,   0),
    "impuestos":    (200, 100,  50),
    "equilibrio":   (130, 200, 255),
    "inflacion":    (255, 100,  80),
    "competencia":  (180,  80, 255),
    "escasez":      (255, 160,   0),
    "ecotycoon":    (255, 215,   0),
    # ── Minijuegos Fusionados ──
    "gran_mercado":   (  0, 220, 220),
    "empresa_tycoon": ( 60, 140, 255),
    "hacienda_banco": (210,  80, 220),
    "isla_recursos":  (255, 160,  40),
}

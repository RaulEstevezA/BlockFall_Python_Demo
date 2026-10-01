# settings.py

import sys
from functools import lru_cache

import pygame

# True cuando el juego se ejecuta en el navegador (pygbag / WebAssembly)
IS_WEB = sys.platform == "emscripten"

# tamanio de la ventana: formato vertical de movil (9:16)
WINDOW_WIDTH = 540
WINDOW_HEIGHT = 960

# tamanio de cada celda en la cuadricula
GRID_SIZE = 30

# columnas del tablero
COLUMNS = 10

# numero de filas en el tablero
ROWS = 20

# tamanio del tablero
WIDTH = COLUMNS * GRID_SIZE
HEIGHT = ROWS * GRID_SIZE

# posicion del tablero (deja hueco para la pared izquierda)
MARGIN_LEFT = 50
MARGIN_TOP = 80

# panel lateral (siguiente pieza, nivel y puntuacion)
PANEL_X = MARGIN_LEFT + WIDTH + GRID_SIZE + 15
PANEL_WIDTH = WINDOW_WIDTH - PANEL_X - 15

# zona de los botones tactiles, debajo del tablero
CONTROLS_TOP = MARGIN_TOP + HEIGHT + GRID_SIZE + 20

# colores
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GRAY = (50, 50, 50)
LIGHT_GRAY = (180, 180, 180)
YELLOW = (255, 255, 0)
RED = (255, 0, 0)

# lista de colores para las piezas
COLORS = [
    (255, 0, 0),   # rojo
    (0, 255, 0),   # verde
    (0, 0, 255),   # azul
    (255, 255, 0), # amarillo
    (255, 165, 0), # naranja
    (128, 0, 128)  # purpura
]

# controles por defecto
DEFAULT_CONTROLS = {
    "left": pygame.K_LEFT,
    "right": pygame.K_RIGHT,
    "down": pygame.K_DOWN,
    "drop": pygame.K_SPACE,
    "rotate": pygame.K_UP
}

# acciones que se repiten al mantener pulsada la tecla o el boton
REPEATABLE_ACTIONS = ("left", "right", "down")

# milisegundos antes de repetir
KEY_REPEAT_DELAY = 300

# intervalo de repeticion
KEY_REPEAT_RATE = 20

# controles personalizables
CONTROLS = DEFAULT_CONTROLS.copy()

# velocidad de caida de las piezas
DROP_TIME = 1000

# puntuacion necesaria para subir de nivel
LEVEL_UP_SCORE = 300

# coeficientes de puntuacion por lineas
LINE_CLEAR_COEFFICIENTS = {
    1: 1,
    2: 1.2,
    3: 1.6,
    4: 2
}

# coeficientes por nivel
LEVEL_COEFFICIENTS = {
    1: 1,
    2: 1.1,
    3: 1.2,
    4: 1.3,
    5: 1.4,
    6: 1.5,
    7: 1.6,
    8: 1.7,
    9: 1.8,
    10: 2
}

# funcion para calcular la velocidad de caida segun el nivel
def calculate_drop_speed(level):
    return max(100, DROP_TIME - ((level - 1) * 0.1 * DROP_TIME))

# funcion para calcular la puntuacion
def calculate_score(lines_cleared, level):
    line_coefficient = LINE_CLEAR_COEFFICIENTS.get(lines_cleared, 1)
    level_coefficient = LEVEL_COEFFICIENTS.get(level, 1)
    base_score = 10 * lines_cleared
    return int(base_score * line_coefficient * level_coefficient)

# fuentes cacheadas: crear una fuente en cada fotograma es lento en el navegador
@lru_cache(maxsize=None)
def get_font(size):
    return pygame.font.Font(None, size)

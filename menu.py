import pygame
from settings import (
    WINDOW_WIDTH, WINDOW_HEIGHT, WHITE, LIGHT_GRAY, YELLOW, RED, COLORS, IS_WEB, get_font
)

# acciones configurables y su descripcion en pantalla
CONFIGURABLE_ACTIONS = ["left", "right", "down", "drop", "rotate"]
ACTION_DESCRIPTIONS = ["mover izquierda", "mover derecha", "bajar", "caida rapida", "rotar"]


def _blit_centered(screen, text, size, color, y):
    """dibuja un texto centrado horizontalmente"""
    surface = get_font(size).render(text, True, color)
    screen.blit(surface, ((WINDOW_WIDTH - surface.get_width()) // 2, y))


def draw_top_bar(screen):
    """dibuja el titulo del juego en la barra superior"""
    title = get_font(48).render("BLOCKFALL", True, WHITE)
    screen.blit(title, (20, 24))


def show_menu(screen):
    """muestra el menu principal centrado en la pantalla"""
    # fila de bloques de colores como decoracion del titulo
    block = 30
    start_x = (WINDOW_WIDTH - len(COLORS) * block) // 2
    for i, color in enumerate(COLORS):
        pygame.draw.rect(screen, color, (start_x + i * block, 170, block - 2, block - 2))

    _blit_centered(screen, "BLOCKFALL", 96, WHITE, 230)

    _blit_centered(screen, "presiona ENTER o toca", 36, WHITE, 400)
    _blit_centered(screen, "la pantalla para jugar", 36, WHITE, 436)

    _blit_centered(screen, "teclado: flechas para mover y rotar", 28, LIGHT_GRAY, 560)
    _blit_centered(screen, "ESPACIO caida rapida, ESC pausa", 28, LIGHT_GRAY, 592)
    _blit_centered(screen, "movil: botones bajo el tablero", 28, LIGHT_GRAY, 624)

    _blit_centered(screen, "presiona C para configurar controles", 28, LIGHT_GRAY, 720)
    if not IS_WEB:
        _blit_centered(screen, "presiona ESC para salir", 28, LIGHT_GRAY, 752)


def show_pause_menu(screen):
    """muestra el menu de pausa"""
    _blit_centered(screen, "PAUSA", 72, YELLOW, WINDOW_HEIGHT // 3)
    _blit_centered(screen, "presiona ESC o toca", 36, WHITE, WINDOW_HEIGHT // 3 + 100)
    _blit_centered(screen, "la pantalla para continuar", 36, WHITE, WINDOW_HEIGHT // 3 + 136)


def show_game_over(screen, score):
    """muestra la pantalla de game over con la puntuacion final"""
    _blit_centered(screen, "GAME OVER", 80, RED, WINDOW_HEIGHT // 3)
    _blit_centered(screen, f"Final Score: {score:08d}", 44, WHITE, WINDOW_HEIGHT // 3 + 90)
    _blit_centered(screen, "presiona ENTER o toca", 32, LIGHT_GRAY, WINDOW_HEIGHT // 3 + 190)
    _blit_centered(screen, "la pantalla para volver al menu", 32, LIGHT_GRAY, WINDOW_HEIGHT // 3 + 222)


def show_configure_controls(screen, new_controls):
    """muestra las teclas ya elegidas y la accion que espera una tecla nueva"""
    _blit_centered(screen, "presiona la nueva tecla", 40, WHITE, 120)
    _blit_centered(screen, "para cada accion", 40, WHITE, 160)

    for i, action in enumerate(CONFIGURABLE_ACTIONS):
        if action in new_controls:
            text = f"{ACTION_DESCRIPTIONS[i]}: {pygame.key.name(new_controls[action])}"
            color = LIGHT_GRAY
        elif i == len(new_controls):
            text = f"{ACTION_DESCRIPTIONS[i]}: presiona una tecla"
            color = YELLOW
        else:
            text = ACTION_DESCRIPTIONS[i]
            color = LIGHT_GRAY
        screen.blit(get_font(34).render(text, True, color), (50, 260 + i * 50))

    _blit_centered(screen, "ESC para cancelar", 28, LIGHT_GRAY, 560)

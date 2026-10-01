# controls.py

import math
import pygame
from settings import LIGHT_GRAY, WHITE, get_font

# colores de los botones tactiles
BUTTON_BG = (30, 32, 40)
BUTTON_PRESSED = (85, 90, 110)
BUTTON_BORDER = (100, 100, 115)

# margen extra alrededor de cada boton para que sea facil acertar con el dedo
TOUCH_MARGIN = 8


class TouchButton:
    def __init__(self, action, rect, round_shape=False, label=None):
        """boton en pantalla asociado a una accion del juego"""
        self.action = action
        self.rect = pygame.Rect(rect)
        self.round_shape = round_shape
        self.label = label

    def contains(self, pos):
        """indica si una pulsacion en pos cae sobre el boton"""
        if self.round_shape:
            distance = math.hypot(pos[0] - self.rect.centerx, pos[1] - self.rect.centery)
            return distance <= self.rect.width / 2 + TOUCH_MARGIN
        return self.rect.inflate(TOUCH_MARGIN * 2, TOUCH_MARGIN * 2).collidepoint(pos)

    def draw(self, screen, pressed):
        """dibuja el boton y su icono, resaltado si esta pulsado"""
        background = BUTTON_PRESSED if pressed else BUTTON_BG
        if self.round_shape:
            radius = self.rect.width // 2
            pygame.draw.circle(screen, background, self.rect.center, radius)
            pygame.draw.circle(screen, BUTTON_BORDER, self.rect.center, radius, 2)
        else:
            pygame.draw.rect(screen, background, self.rect, border_radius=12)
            pygame.draw.rect(screen, BUTTON_BORDER, self.rect, 2, border_radius=12)

        color = WHITE if pressed else LIGHT_GRAY
        cx, cy = self.rect.center
        if self.label:
            # en los botones con texto, el icono sube un poco para dejarle sitio
            cy -= 8
            text = get_font(20).render(self.label, True, color)
            screen.blit(text, (self.rect.centerx - text.get_width() // 2, cy + 24))
        _draw_icon(screen, self.action, color, cx, cy)


def _draw_icon(screen, action, color, cx, cy):
    """dibuja el icono de cada accion con formas simples (sin depender de fuentes)"""
    if action == "left":
        pygame.draw.polygon(screen, color, [(cx - 14, cy), (cx + 10, cy - 16), (cx + 10, cy + 16)])
    elif action == "right":
        pygame.draw.polygon(screen, color, [(cx + 14, cy), (cx - 10, cy - 16), (cx - 10, cy + 16)])
    elif action == "down":
        pygame.draw.polygon(screen, color, [(cx, cy + 14), (cx - 16, cy - 10), (cx + 16, cy - 10)])
    elif action == "drop":
        pygame.draw.polygon(screen, color, [(cx, cy + 8), (cx - 16, cy - 14), (cx + 16, cy - 14)])
        pygame.draw.rect(screen, color, (cx - 16, cy + 12, 32, 5))
    elif action == "pause":
        pygame.draw.rect(screen, color, (cx - 9, cy - 11, 6, 22))
        pygame.draw.rect(screen, color, (cx + 3, cy - 11, 6, 22))
    elif action == "rotate":
        # flecha circular en sentido horario, como gira la pieza
        radius = 15
        pygame.draw.arc(screen, color, (cx - radius, cy - radius, radius * 2, radius * 2),
                        -4.6, 0.5, 4)
        # la punta va en el extremo superior del arco, apuntando a la derecha
        angle = -4.6
        tip_x = cx + radius * math.cos(angle)
        tip_y = cy - radius * math.sin(angle)
        dx, dy = math.sin(angle), math.cos(angle)
        pygame.draw.polygon(screen, color, [
            (tip_x + dx * 9, tip_y + dy * 9),
            (tip_x - dy * 8, tip_y + dx * 8),
            (tip_x + dy * 8, tip_y - dx * 8),
        ])


class TouchControls:
    def __init__(self):
        """crea la cruceta, los botones de rotar y soltar y el boton de pausa"""
        self.buttons = [
            # cruceta: arriba tambien rota, como la flecha arriba del teclado
            TouchButton("rotate", (118, 735, 84, 66)),
            TouchButton("left", (22, 809, 90, 66)),
            TouchButton("right", (208, 809, 90, 66)),
            TouchButton("down", (118, 883, 84, 66)),
            # botones redondos a la derecha
            TouchButton("rotate", (465 - 52, 790 - 52, 104, 104), True, "ROTAR"),
            TouchButton("drop", (370 - 50, 882 - 50, 100, 100), True, "SOLTAR"),
        ]
        self.pause_button = TouchButton("pause", (468, 18, 52, 44))

    def button_at(self, pos):
        """devuelve el boton que hay en pos, o None"""
        for button in self.buttons + [self.pause_button]:
            if button.contains(pos):
                return button
        return None

    def draw(self, screen, pressed_actions):
        """dibuja todos los botones; pressed_actions son las acciones activas"""
        for button in self.buttons + [self.pause_button]:
            button.draw(screen, button.action in pressed_actions)

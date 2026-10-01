import asyncio
import sys

import pygame

from settings import (
    WINDOW_WIDTH, WINDOW_HEIGHT, BLACK, CONTROLS, LEVEL_UP_SCORE, IS_WEB,
    REPEATABLE_ACTIONS, KEY_REPEAT_DELAY, KEY_REPEAT_RATE,
    calculate_drop_speed, calculate_score
)
from board import Board
from pieces import Piece
from controls import TouchControls
from menu import (
    CONFIGURABLE_ACTIONS, draw_top_bar, show_menu, show_game_over,
    show_pause_menu, show_configure_controls
)

# tiempo tras el game over en el que se ignoran los toques, para no saltarse
# la pantalla sin querer con un toque que iba dirigido al juego
GAME_OVER_TOUCH_DELAY = 800

# tiempo que se ve resaltado un boton de pulsacion unica (rotar, soltar)
BUTTON_FLASH_TIME = 120


class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption("BlockFall")
        self.clock = pygame.time.Clock()
        self.touch_controls = TouchControls()
        self.controls = CONTROLS.copy()

        # estado del juego: menu, playing, paused, game_over o configure
        self.state = "menu"

        # acciones mantenidas: origen (tecla, dedo o raton) -> [accion, instante]
        self.held = {}

        # botones de pulsacion unica resaltados: accion -> instante final
        self.flash = {}

        # en cuanto llega un evento de dedo se ignoran los clics simulados del tactil
        self.finger_seen = False

        self.new_controls = {}
        self.game_over_time = 0
        self.reset()

    def reset(self):
        """inicializa el tablero, las piezas, la puntuacion y el nivel"""
        self.board = Board()
        self.piece = Piece()
        self.next_piece = Piece()
        self.score = 0
        self.level = 1
        self.last_drop_time = pygame.time.get_ticks()
        self.held.clear()

    # ---------- logica ----------

    def update(self):
        """caida automatica y repeticion de las acciones mantenidas"""
        if self.state != "playing":
            return

        current_time = pygame.time.get_ticks()
        if current_time - self.last_drop_time > calculate_drop_speed(self.level):
            if not self.piece.move(0, 1, self.board):
                self.lock_piece()
            self.last_drop_time = current_time

        # teclas y botones mantenidos con control de retardo y repeticion
        for source, (action, pressed_time) in list(self.held.items()):
            if self.state != "playing":
                break
            if current_time - pressed_time >= KEY_REPEAT_DELAY:
                self.perform(action)
                self.held[source] = [action, current_time - (KEY_REPEAT_DELAY - KEY_REPEAT_RATE)]

    def perform(self, action):
        """aplica una accion del jugador a la pieza actual"""
        if action == "left":
            self.piece.move(-1, 0, self.board)
        elif action == "right":
            self.piece.move(1, 0, self.board)
        elif action == "down":
            self.piece.move(0, 1, self.board)
        elif action == "rotate":
            self.piece.rotate(self.board)
        elif action == "drop":
            # hacer que la pieza caiga hasta el fondo y se fije al instante
            while self.piece.move(0, 1, self.board):
                pass
            self.lock_piece()
            self.last_drop_time = pygame.time.get_ticks()

    def lock_piece(self):
        """fija la pieza, puntua las lineas completas y saca la siguiente pieza"""
        if self.board.add_piece_to_board(self.piece, self.level):
            self.end_game()
            return

        lines_cleared, _ = self.board.clear_full_rows(self.level)
        if lines_cleared > 0:
            self.score += calculate_score(lines_cleared, self.level)

        # subir de nivel
        if self.score >= self.level * LEVEL_UP_SCORE:
            self.level += 1

        # nueva pieza
        self.piece = self.next_piece
        self.next_piece = Piece()

        # verificar espacio
        if not self.piece._is_valid_position(self.piece.x, self.piece.y, self.piece.shape, self.board):
            self.end_game()

    def end_game(self):
        self.state = "game_over"
        self.game_over_time = pygame.time.get_ticks()
        self.held.clear()
        stop_music()

    def back_to_menu(self):
        play_music()
        self.reset()
        self.state = "menu"

    def pause(self):
        self.state = "paused"
        self.held.clear()

    def resume(self):
        self.state = "playing"
        self.last_drop_time = pygame.time.get_ticks()

    # ---------- eventos ----------

    def handle_event(self, event):
        if event.type == pygame.QUIT:
            quit_game()

        elif event.type == pygame.KEYDOWN:
            self.on_key_down(event.key)
        elif event.type == pygame.KEYUP:
            self.held.pop(("key", event.key), None)

        elif event.type == pygame.FINGERDOWN:
            self.finger_seen = True
            self.on_pointer_down(("finger", event.finger_id), finger_pos(event))
        elif event.type == pygame.FINGERMOTION:
            self.on_pointer_move(("finger", event.finger_id), finger_pos(event))
        elif event.type == pygame.FINGERUP:
            self.held.pop(("finger", event.finger_id), None)

        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and not self.from_touch(event):
            self.on_pointer_down(("mouse",), event.pos)
        elif event.type == pygame.MOUSEMOTION and event.buttons[0] and not self.from_touch(event):
            self.on_pointer_move(("mouse",), event.pos)
        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1 and not self.from_touch(event):
            self.held.pop(("mouse",), None)

        elif event.type == pygame.WINDOWFOCUSLOST and self.state == "playing":
            # pausar si el jugador cambia de pestania o de ventana
            self.pause()

    def from_touch(self, event):
        """los toques generan tambien clics de raton: se descartan si ya hay eventos de dedo"""
        return self.finger_seen and getattr(event, "touch", False)

    def on_key_down(self, key):
        if self.state == "menu":
            if key == pygame.K_RETURN:
                self.state = "playing"
                self.last_drop_time = pygame.time.get_ticks()
            elif key == pygame.K_c:
                self.new_controls = {}
                self.state = "configure"
            elif key == pygame.K_ESCAPE and not IS_WEB:
                quit_game()

        elif self.state == "playing":
            if key == pygame.K_ESCAPE:
                self.pause()
                return
            action = self.action_for_key(key)
            if action:
                self.perform(action)
                if action in REPEATABLE_ACTIONS:
                    self.held[("key", key)] = [action, pygame.time.get_ticks()]

        elif self.state == "paused":
            if key in (pygame.K_ESCAPE, pygame.K_RETURN):
                self.resume()

        elif self.state == "game_over":
            if key == pygame.K_RETURN:
                self.back_to_menu()

        elif self.state == "configure":
            if key == pygame.K_ESCAPE:
                # cancelar sin cambiar los controles
                self.state = "menu"
                return
            self.new_controls[CONFIGURABLE_ACTIONS[len(self.new_controls)]] = key
            if len(self.new_controls) == len(CONFIGURABLE_ACTIONS):
                self.controls = self.new_controls
                self.state = "menu"

    def action_for_key(self, key):
        for action, bound_key in self.controls.items():
            if key == bound_key:
                return action
        return None

    def on_pointer_down(self, source, pos):
        if self.state == "menu":
            self.state = "playing"
            self.last_drop_time = pygame.time.get_ticks()

        elif self.state == "playing":
            button = self.touch_controls.button_at(pos)
            if button is None:
                return
            if button.action == "pause":
                self.pause()
                return
            self.perform(button.action)
            self.flash[button.action] = pygame.time.get_ticks() + BUTTON_FLASH_TIME
            if button.action in REPEATABLE_ACTIONS:
                self.held[source] = [button.action, pygame.time.get_ticks()]

        elif self.state == "paused":
            self.resume()

        elif self.state == "game_over":
            if pygame.time.get_ticks() - self.game_over_time > GAME_OVER_TOUCH_DELAY:
                self.back_to_menu()

    def on_pointer_move(self, source, pos):
        """permite deslizar el dedo de un boton de la cruceta a otro sin levantarlo"""
        if self.state != "playing" or source not in self.held:
            return
        button = self.touch_controls.button_at(pos)
        action = button.action if button else None
        if action == self.held[source][0]:
            return
        if action in REPEATABLE_ACTIONS:
            self.perform(action)
            self.held[source] = [action, pygame.time.get_ticks()]
        else:
            del self.held[source]

    # ---------- dibujo ----------

    def draw(self):
        self.screen.fill(BLACK)

        if self.state == "menu":
            show_menu(self.screen)
        elif self.state == "playing":
            draw_top_bar(self.screen)
            self.board.draw(self.screen, self.score, self.level, self.next_piece)
            self.piece.draw(self.screen)
            self.touch_controls.draw(self.screen, self.pressed_actions())
        elif self.state == "paused":
            show_pause_menu(self.screen)
        elif self.state == "game_over":
            show_game_over(self.screen, self.score)
        elif self.state == "configure":
            show_configure_controls(self.screen, self.new_controls)

        pygame.display.flip()

    def pressed_actions(self):
        current_time = pygame.time.get_ticks()
        pressed = {action for action, _ in self.held.values()}
        pressed.update(action for action, until in self.flash.items() if until > current_time)
        return pressed


def finger_pos(event):
    """los eventos de dedo traen coordenadas normalizadas entre 0 y 1"""
    return event.x * WINDOW_WIDTH, event.y * WINDOW_HEIGHT


def play_music():
    # el audio puede no estar disponible (sin dispositivo o bloqueado por el navegador)
    try:
        pygame.mixer.music.play(-1)
    except pygame.error:
        pass


def stop_music():
    try:
        pygame.mixer.music.stop()
    except pygame.error:
        pass


def quit_game():
    pygame.quit()
    sys.exit()


async def main():
    # inicializar pygame
    pygame.init()

    # cargar y reproducir musica de fondo
    try:
        pygame.mixer.init()
        pygame.mixer.music.load("music/theme.ogg")
        pygame.mixer.music.set_volume(0.6)
    except pygame.error:
        pass
    play_music()

    game = Game()

    while True:
        for event in pygame.event.get():
            game.handle_event(event)
        game.update()
        game.draw()
        game.clock.tick(60)

        # en el navegador el bucle debe ceder el control en cada fotograma
        await asyncio.sleep(0)


asyncio.run(main())

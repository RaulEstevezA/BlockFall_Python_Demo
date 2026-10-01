"""Pruebas del juego sin ventana (SDL en modo dummy).

Ejecutar desde la raíz del repositorio:  python -m unittest discover tests
"""

import asyncio
import os
import sys
import unittest

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pygame

# main.py arranca el bucle al importarse: se importa sin ejecutarlo
_run = asyncio.run
asyncio.run = lambda coro: coro.close()
try:
    import main
finally:
    asyncio.run = _run

from pieces import Piece
from settings import WINDOW_WIDTH, WINDOW_HEIGHT

# centro de cada boton tactil en coordenadas de la ventana
LEFT_BUTTON = (65, 842)
RIGHT_BUTTON = (253, 842)
DROP_BUTTON = (370, 882)
ROTATE_BUTTON = (465, 790)
PAUSE_BUTTON = (494, 40)


class GameTest(unittest.TestCase):
    def setUp(self):
        pygame.init()
        self.game = main.Game()

    def tearDown(self):
        pygame.quit()

    def finger(self, event_type, finger_id, pos):
        self.game.handle_event(pygame.event.Event(
            event_type, finger_id=finger_id, touch_id=1, dx=0, dy=0,
            x=pos[0] / WINDOW_WIDTH, y=pos[1] / WINDOW_HEIGHT))

    def tap(self, pos, finger_id=1):
        self.finger(pygame.FINGERDOWN, finger_id, pos)
        self.finger(pygame.FINGERUP, finger_id, pos)

    def key(self, key):
        self.game.handle_event(pygame.event.Event(pygame.KEYDOWN, key=key, mod=0, unicode="", scancode=0))

    def filled_cells(self):
        return sum(1 for row in self.game.board.grid for cell in row if cell)

    def test_tap_starts_game(self):
        self.tap((270, 480))
        self.assertEqual(self.game.state, "playing")

    def test_buttons_move_piece(self):
        self.tap((270, 480))
        x = self.game.piece.x
        self.tap(LEFT_BUTTON)
        self.assertEqual(self.game.piece.x, x - 1)
        self.tap(RIGHT_BUTTON)
        self.assertEqual(self.game.piece.x, x)

    def test_slide_between_buttons(self):
        self.tap((270, 480))
        self.finger(pygame.FINGERDOWN, 2, LEFT_BUTTON)
        self.finger(pygame.FINGERMOTION, 2, RIGHT_BUTTON)
        self.assertEqual(self.game.held[("finger", 2)][0], "right")
        self.finger(pygame.FINGERUP, 2, RIGHT_BUTTON)
        self.assertEqual(self.game.held, {})

    def test_touch_mouse_events_ignored_after_finger(self):
        self.tap((270, 480))
        x = self.game.piece.x
        self.game.handle_event(pygame.event.Event(pygame.MOUSEBUTTONDOWN, button=1, pos=LEFT_BUTTON, touch=True))
        self.assertEqual(self.game.piece.x, x)

    def test_mouse_clicks_buttons(self):
        self.key(pygame.K_RETURN)
        x = self.game.piece.x
        self.game.handle_event(pygame.event.Event(pygame.MOUSEBUTTONDOWN, button=1, pos=LEFT_BUTTON, touch=False))
        self.assertEqual(self.game.piece.x, x - 1)

    def test_hard_drop_locks_piece(self):
        self.tap((270, 480))
        self.tap(DROP_BUTTON)
        self.assertEqual(self.filled_cells(), 4)
        self.assertLess(self.game.piece.y, 0)
        self.key(pygame.K_SPACE)
        self.assertEqual(self.filled_cells(), 8)

    def test_line_clear_scores(self):
        self.key(pygame.K_RETURN)
        self.game.board.grid[-1] = [(1, 1, 1)] * 6 + [0] * 4
        piece = Piece()
        piece.shape, piece.x, piece.y = [[1, 1, 1, 1]], 6, 0
        self.game.piece = piece
        self.key(pygame.K_SPACE)
        self.assertEqual(self.game.score, 10)
        self.assertTrue(all(cell == 0 for cell in self.game.board.grid[-1]))

    def test_rotate_button(self):
        self.tap((270, 480))
        piece = Piece()
        piece.shape, piece.x, piece.y = [[1, 1, 1, 1]], 3, 5
        self.game.piece = piece
        self.tap(ROTATE_BUTTON)
        self.assertEqual(len(self.game.piece.shape), 4)

    def test_pause_and_resume(self):
        self.tap((270, 480))
        self.tap(PAUSE_BUTTON)
        self.assertEqual(self.game.state, "paused")
        self.tap((270, 480))
        self.assertEqual(self.game.state, "playing")

    def test_game_over_and_back_to_menu(self):
        self.key(pygame.K_RETURN)
        for row in range(20):
            self.game.board.grid[row] = [(9, 9, 9)] * 9 + [0]
        self.game.lock_piece()
        self.assertEqual(self.game.state, "game_over")
        # un toque inmediato no se salta la pantalla de game over
        self.tap((270, 480))
        self.assertEqual(self.game.state, "game_over")
        self.key(pygame.K_RETURN)
        self.assertEqual(self.game.state, "menu")
        self.assertEqual(self.game.score, 0)

    def test_configure_controls(self):
        self.key(pygame.K_c)
        for key in (pygame.K_a, pygame.K_d, pygame.K_s, pygame.K_w, pygame.K_q):
            self.key(key)
        self.assertEqual(self.game.state, "menu")
        self.assertEqual(self.game.controls["left"], pygame.K_a)
        self.assertEqual(self.game.controls["rotate"], pygame.K_q)

    def test_every_screen_draws(self):
        for state in ("menu", "playing", "paused", "game_over", "configure"):
            self.game.state = state
            self.game.draw()


if __name__ == "__main__":
    unittest.main()

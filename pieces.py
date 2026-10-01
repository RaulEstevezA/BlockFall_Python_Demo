# pieces.py

import pygame
import random
from settings import GRID_SIZE, COLUMNS, ROWS, COLORS, MARGIN_LEFT, MARGIN_TOP

# Definición de las formas del Tetris
SHAPES = [
    [[1, 1, 1, 1]],  # I
    [[1, 1], [1, 1]],  # O
    [[0, 1, 0], [1, 1, 1]],  # T
    [[1, 1, 0], [0, 1, 1]],  # S
    [[0, 1, 1], [1, 1, 0]],  # Z
    [[1, 1, 1], [1, 0, 0]],  # L
    [[1, 1, 1], [0, 0, 1]]   # J
]

class Piece:
    def __init__(self):
        """Inicializa una nueva pieza de Tetris en el centro del tablero"""
        self.shape = random.choice(SHAPES)
        self.color = random.choice(COLORS)
        self.x = COLUMNS // 2 - len(self.shape[0]) // 2  # Centrar en columnas
        self.y = -2  # Empieza un poco más arriba del tablero

    def draw(self, screen):
        """Dibuja la pieza en la pantalla con los márgenes aplicados"""
        for i, row in enumerate(self.shape):
            for j, cell in enumerate(row):
                # las filas por encima del tablero no se dibujan
                if cell and self.y + i >= 0:
                    pygame.draw.rect(screen, self.color,
                                     (MARGIN_LEFT + (self.x + j) * GRID_SIZE, 
                                      MARGIN_TOP + (self.y + i) * GRID_SIZE, 
                                      GRID_SIZE, GRID_SIZE))
    
    def rotate(self, board):
        """Rota la pieza si la rotación es válida y solo la ajusta si se sale del tablero"""
        rotated_shape = list(zip(*self.shape[::-1]))  # Rotación en sentido horario
        rotated_shape = [list(row) for row in rotated_shape]  # Convertir a lista de listas

        # Si la rotación ya es válida sin ajustes, la aplicamos directamente
        if self._is_valid_position(self.x, self.y, rotated_shape, board):
            self.shape = rotated_shape
            return

        # Intentar mover la pieza solo si es necesario para que encaje
        for offset in [-1, 1, -2, 2, -3, 3]:  # Prueba mover ligeramente izquierda o derecha
            if self._is_valid_position(self.x + offset, self.y, rotated_shape, board):
                self.x += offset
                self.shape = rotated_shape
                return  # Se ajustó correctamente, terminamos

    def move(self, dx, dy, board):
        """Mueve la pieza si la nueva posición es válida"""
        new_x = self.x + dx
        new_y = self.y + dy

        if self._is_valid_position(new_x, new_y, self.shape, board):
            self.x = new_x
            self.y = new_y
            return True  # ⬅️ Si el movimiento es válido, devolver True
        return False  # ⬅️ Si no es válido, devolver False

    def _is_valid_position(self, new_x, new_y, shape, board):
        """Verifica si la nueva posición está dentro del tablero y no choca con otras piezas"""
        for i, row in enumerate(shape):
            for j, cell in enumerate(row):
                if cell:
                    test_x = new_x + j
                    test_y = new_y + i

                    if test_x < 0 or test_x >= COLUMNS or test_y >= ROWS:
                        return False  # Se sale del tablero

                    if test_y >= 0 and board.grid[test_y][test_x] != 0:
                        return False  # Hay una colisión con una pieza fija
        return True

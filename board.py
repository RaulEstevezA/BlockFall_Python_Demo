import pygame
from settings import (
    WIDTH, HEIGHT, GRID_SIZE, GRAY, LIGHT_GRAY, WHITE, MARGIN_LEFT, MARGIN_TOP,
    ROWS, COLUMNS, PANEL_X, PANEL_WIDTH, get_font
)

class Board:
    def __init__(self):
        self.columns = WIDTH // GRID_SIZE
        self.rows = HEIGHT // GRID_SIZE
        self.grid = [[0] * self.columns for _ in range(self.rows)]

    def draw(self, screen, score, level, next_piece):
        """dibuja las piezas fijas, la cuadrícula y el panel lateral"""
        for y in range(ROWS):
            for x in range(COLUMNS):
                if self.grid[y][x] != 0:
                    pygame.draw.rect(screen, self.grid[y][x],
                                    (MARGIN_LEFT + x * GRID_SIZE,
                                    MARGIN_TOP + y * GRID_SIZE,
                                    GRID_SIZE, GRID_SIZE))

        for x in range(0, WIDTH, GRID_SIZE):
            pygame.draw.line(screen, GRAY,
                            (MARGIN_LEFT + x, MARGIN_TOP),
                            (MARGIN_LEFT + x, MARGIN_TOP + HEIGHT))
        for y in range(0, HEIGHT, GRID_SIZE):
            pygame.draw.line(screen, GRAY,
                            (MARGIN_LEFT, MARGIN_TOP + y),
                            (MARGIN_LEFT + WIDTH, MARGIN_TOP + y))

        pygame.draw.rect(screen, LIGHT_GRAY, (MARGIN_LEFT - GRID_SIZE,
                                              MARGIN_TOP, GRID_SIZE, HEIGHT))
        pygame.draw.rect(screen, LIGHT_GRAY, (MARGIN_LEFT + WIDTH,
                                              MARGIN_TOP, GRID_SIZE, HEIGHT))
        pygame.draw.rect(screen, LIGHT_GRAY, (MARGIN_LEFT - GRID_SIZE,
                                              MARGIN_TOP + HEIGHT, WIDTH +
                                              GRID_SIZE * 2, GRID_SIZE))

        self.draw_next_piece(screen, next_piece)
        self.draw_level(screen, level)
        self.draw_score(screen, score)

    def draw_next_piece(self, screen, next_piece):
        """dibuja la siguiente pieza centrada en su recuadro del panel"""
        self._draw_label(screen, "NEXT", MARGIN_TOP)
        box = pygame.Rect(PANEL_X, MARGIN_TOP + 28, PANEL_WIDTH, 100)
        pygame.draw.rect(screen, GRAY, box, 2, border_radius=6)

        cell = 24
        shape = next_piece.shape
        start_x = box.centerx - len(shape[0]) * cell // 2
        start_y = box.centery - len(shape) * cell // 2
        for i, row in enumerate(shape):
            for j, value in enumerate(row):
                if value:
                    pygame.draw.rect(screen, next_piece.color,
                                     (start_x + j * cell, start_y + i * cell,
                                      cell, cell))

    def draw_level(self, screen, level):
        """dibuja el nivel en el panel lateral"""
        self._draw_label(screen, "LEVEL", MARGIN_TOP + 160)
        self._draw_value(screen, str(level), MARGIN_TOP + 188)

    def draw_score(self, screen, score):
        """dibuja la puntuación en el panel lateral con 8 cifras"""
        self._draw_label(screen, "SCORE", MARGIN_TOP + 250)
        self._draw_value(screen, f"{score:08d}", MARGIN_TOP + 278)

    def _draw_label(self, screen, text, y):
        label = get_font(26).render(text, True, LIGHT_GRAY)
        screen.blit(label, (PANEL_X + (PANEL_WIDTH - label.get_width()) // 2, y))

    def _draw_value(self, screen, text, y):
        value = get_font(34).render(text, True, WHITE)
        screen.blit(value, (PANEL_X + (PANEL_WIDTH - value.get_width()) // 2, y))

    def add_piece_to_board(self, piece, level):
        """fija la pieza en el tablero y verifica si la partida debe terminar"""
        for i, row in enumerate(piece.shape):
            for j, cell in enumerate(row):
                if cell:
                    grid_x = piece.x + j
                    grid_y = piece.y + i
                    if grid_y >= 0:
                        self.grid[grid_y][grid_x] = piece.color

        for x in range(self.columns):
            if self.grid[0][x] != 0:
                return True
        return False

    def clear_full_rows(self):
        """elimina las filas completas y devuelve cuantas se han eliminado"""
        new_grid = [row for row in self.grid if any(cell == 0 for cell in row)]
        lines_cleared = self.rows - len(new_grid)

        while len(new_grid) < self.rows:
            new_grid.insert(0, [0] * self.columns)

        self.grid = new_grid
        return lines_cleared

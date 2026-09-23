import pygame
from checkers2 import SQUARE_SIZE, GREY, WHITE
class Piece:
    # Padding ensures the piece is slightly smaller than the square it sits in
    PADDING = 15
    OUTLINE = 2

    def __init__(self, row, col, color):
        self.row = row
        self.col = col
        self.color = color
        self.king = False
        self.x = 0
        self.y = 0
        self.calc_pos()

    def calc_pos(self):
        """Calculates the center pixel coordinate of the square it occupies."""
        self.x = SQUARE_SIZE * self.col + SQUARE_SIZE // 2
        self.y = SQUARE_SIZE * self.row + SQUARE_SIZE // 2

    def make_king(self):
        self.king = True
        
    def draw(self, win):
        radius = SQUARE_SIZE // 2 - self.PADDING
        
        # 1. Draw a thin outline circle for better visual definition
        pygame.draw.circle(win, GREY, (self.x, self.y), radius + self.OUTLINE)
        # 2. Draw the actual piece
        pygame.draw.circle(win, self.color, (self.x, self.y), radius)
        
        # 3. If it's a king, draw a smaller gold/white circle in the center
        if self.king:
            pygame.draw.circle(win, WHITE, (self.x, self.y), radius // 3)

    def move(self, row, col):
        """Updates the grid position and recalculates pixels."""
        self.row = row
        self.col = col
        self.calc_pos()
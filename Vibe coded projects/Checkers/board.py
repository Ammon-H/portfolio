import pygame
from piece import Piece
from checkers2 import draw_squares, WIN, ROWS, COLS, SQUARE_SIZE, RED, GREY, WHITE

class Board:
    def __init__(self):
        self.board = []
        # NEW: Track the number of pieces left for win conditions
        self.red_left = 12
        self.grey_left = 12
        self.create_board()

    def create_board(self):
        """Initializes the 2D array and populates it with Piece objects."""
        for row in range(ROWS):
            self.board.append([])
            for col in range(COLS):
                if col % 2 == (row + 1) % 2:
                    if row < 3:
                        self.board[row].append(Piece(row, col, RED))
                    elif row > 4:
                        self.board[row].append(Piece(row, col, GREY))
                    else:
                        self.board[row].append(0) 
                else:
                    self.board[row].append(0)

    def draw(self, win, selected_piece=None, valid_moves=None):
        """Draws the squares first, then loops through the grid to draw pieces."""
        draw_squares(win) 
        for row in range(ROWS):
            for col in range(COLS):
                piece = self.board[row][col]
                if piece != 0:
                    piece.draw(win)
        
        if selected_piece:
            pygame.draw.circle(win, (0, 255, 0), (selected_piece.x, selected_piece.y), SQUARE_SIZE // 2, 4)
            
            if valid_moves:
                for row, col in valid_moves:
                    x = col * SQUARE_SIZE + SQUARE_SIZE // 2
                    y = row * SQUARE_SIZE + SQUARE_SIZE // 2
                    pygame.draw.circle(win, (0, 0, 255), (x, y), 15)

    def get_piece(self, row, col):
        """Returns the piece (or 0) at the given row and column."""
        return self.board[row][col]

    def move(self, piece, row, col):
        """Swaps the piece with the target square and updates the piece's internal position."""
        self.board[piece.row][piece.col], self.board[row][col] = self.board[row][col], self.board[piece.row][piece.col]
        piece.move(row, col)

        # NEW: King Logic - Promotes a piece if it reaches the opposite edge
        if row == 7 and piece.color == RED:
            piece.make_king()
        elif row == 0 and piece.color == GREY:
            piece.make_king()

    def remove(self, piece):
        """Removes a piece from the board by setting its cell to 0."""
        if piece != 0:
            self.board[piece.row][piece.col] = 0
            # NEW: Decrement the piece counter when a piece is captured
            if piece.color == RED:
                self.red_left -= 1
            elif piece.color == GREY:
                self.grey_left -= 1

    # NEW: Win Logic - Checks if a player has run out of pieces
    def winner(self):
        """Returns the winning color string, or None if the game is still going."""
        if self.red_left <= 0:
            return "GREY"
        elif self.grey_left <= 0:
            return "RED"
        return None

    def get_valid_moves(self, piece):
        """Returns a dictionary of legal moves and the pieces they capture."""
        valid_moves = {}
        directions = []

        if piece.color == RED or piece.king:
            directions.append(1)
        if piece.color == GREY or piece.king:
            directions.append(-1)

        for step in directions:
            # Check Normal Moves (1 Step Diagonal)
            target_row = piece.row + step
            if 0 <= target_row < ROWS:
                if piece.col - 1 >= 0:
                    if self.board[target_row][piece.col - 1] == 0:
                        valid_moves[(target_row, piece.col - 1)] = None
                if piece.col + 1 < COLS:
                    if self.board[target_row][piece.col + 1] == 0:
                        valid_moves[(target_row, piece.col + 1)] = None

            # Check Jump Moves (2 Steps Diagonal)
            jump_row = piece.row + (step * 2)
            if 0 <= jump_row < ROWS:
                if piece.col - 2 >= 0:
                    skipped_piece = self.board[piece.row + step][piece.col - 1]
                    landing_space = self.board[jump_row][piece.col - 2]
                    if skipped_piece != 0 and skipped_piece.color != piece.color and landing_space == 0:
                        valid_moves[(jump_row, piece.col - 2)] = skipped_piece
                
                if piece.col + 2 < COLS:
                    skipped_piece = self.board[piece.row + step][piece.col + 1]
                    landing_space = self.board[jump_row][piece.col + 2]
                    if skipped_piece != 0 and skipped_piece.color != piece.color and landing_space == 0:
                        valid_moves[(jump_row, piece.col + 2)] = skipped_piece

        return valid_moves
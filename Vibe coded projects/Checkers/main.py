import pygame
from checkers2 import draw_squares, WIN, ROWS, COLS, SQUARE_SIZE, RED, GREY, WHITE
import board

def get_row_col_from_mouse(pos):
    """Translates a pixel (x, y) mouse coordinate into a grid (row, col) coordinate."""
    x, y = pos
    row = y // SQUARE_SIZE
    col = x // SQUARE_SIZE
    return row, col

def main():
    run = True
    clock = pygame.time.Clock()
    game_board = board.Board() 
    
    selected_piece = None
    valid_moves = {} 
    turn = RED 

    while run:
        clock.tick(60)

        # NEW: Check for a winner at the start of every frame
        if game_board.winner() is not None:
            print(f"GAME OVER! {game_board.winner()} WINS!")
            run = False
            continue

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False

            if event.type == pygame.MOUSEBUTTONDOWN:
                pos = pygame.mouse.get_pos()
                row, col = get_row_col_from_mouse(pos)
                
                if selected_piece:
                    if (row, col) in valid_moves:
                        captured_piece = valid_moves[(row, col)]
                        if captured_piece:
                            game_board.remove(captured_piece)
                        
                        game_board.move(selected_piece, row, col)
                        
                        turn = GREY if turn == RED else RED
                        selected_piece = None 
                        valid_moves = {}
                        
                    elif game_board.get_piece(row, col) != 0 and game_board.get_piece(row, col).color == turn:
                        selected_piece = game_board.get_piece(row, col)
                        valid_moves = game_board.get_valid_moves(selected_piece)
                    else:
                        selected_piece = None
                        valid_moves = {}
                else:
                    piece = game_board.get_piece(row, col)
                    if piece != 0 and piece.color == turn:
                        selected_piece = piece
                        valid_moves = game_board.get_valid_moves(selected_piece)

        game_board.draw(WIN, selected_piece, valid_moves)
        pygame.display.update()

    pygame.quit()

if __name__ == "__main__":
    main()
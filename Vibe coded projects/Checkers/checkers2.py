import pygame

pygame.init()
WIDTH, HEIGHT = 800, 800
ROWS, COLS = 8, 8
SQUARE_SIZE = WIDTH // COLS

WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Checkers")

# RGB Colors
RED = (255, 0, 0)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREY = (128, 128, 128)

def draw_squares(win):
    win.fill(BLACK) 
    for row in range(ROWS):
        for col in range(row % 2, COLS, 2):
            # FIX: Swapped 'col' and 'row' so X and Y map correctly to the screen
            pygame.draw.rect(win, WHITE, (col * SQUARE_SIZE, row * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE))

def main():
    run = True
    clock = pygame.time.Clock()

    while run:
        clock.tick(60)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False

        # Draw the board
        draw_squares(WIN)
        pygame.display.update()

    pygame.quit()

if __name__ == "__main__":
    main()
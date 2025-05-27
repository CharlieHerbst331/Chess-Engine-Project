#file handles user input and displays gameState
#will convert into a web application later
import pygame as p
import ChessEngine

WIDTH = HEIGHT = 512 # 400 is another option
DIMENSION = 8
SQ = HEIGHT//DIMENSION
MAX_FPS = 15
IMAGES = {}

# Creating a function to initialize a dictionary of images

def load_images():
    pieces = ['wP', 'bP', 'bR', 'bN', 'bB', 'bQ', 'bK', 'bB', 'bN', 'bR', 
              'wR', 'wN', 'wB', 'wQ', 'wK', 'wB', 'wN', 'wR']
    for piece in pieces:
        IMAGES[piece] = p.transform.scale(p.image.load('pieces/' + piece + '.svg'), (SQ, SQ))
    # we can access any image from the dictionary IMAGES

#main driver, will handle user input and updating the graphics

def main():
    p.init()
    screen = p.display.set_mode((WIDTH, HEIGHT))
    clock = p.time.Clock()
    screen.fill(p.Color('white'))
    gs = ChessEngine.GameState()
    load_images()

    valid_moves = gs.get_valid_moves()
    move_made = False #flag variable to reduce computation of calculating valid_moves every frame
    sq_selected = ()
    player_clicks = [] #keeps track fo the players clicks
    running = True
    while running:
        for e in p.event.get():
            if e.type == p.QUIT:
                running = False
            #mouse handlers
            elif e.type == p.MOUSEBUTTONDOWN:
                location = p.mouse.get_pos()
                col = location[0] // SQ
                row = location[1] // SQ
                if sq_selected == (row, col):
                    sq_selected = ()
                    player_clicks = []
                else:
                    sq_selected = (row, col)
                    player_clicks.append(sq_selected)
                if len(player_clicks) == 2:
                    move = ChessEngine.Move(player_clicks[0], player_clicks[1], gs.board)
                    print(move.get_chess_notation())
                    print(gs.board.shape)
                    if move in valid_moves:
                        gs.make_move(move)
                        move_made = True
                        sq_selected = ()
                        player_clicks = []
                    else:
                        player_clicks = [sq_selected]
            elif e.type == p.KEYDOWN:
                if e.key == p.K_z:
                    gs.undo_move()
                    move_made = True

        if move_made:
            valid_moves = gs.get_valid_moves()
            move_made = False
        
        draw_game_state(screen, gs)    
        clock.tick(MAX_FPS)
        p.display.flip()
            
def draw_game_state(screen, gs):
    draw_board(screen)

    draw_pieces(screen, gs.board)
#draws the squares on the board
def draw_board(screen):
    colors = [p.Color('beige'), p.Color('brown')]

    for r in range(DIMENSION):
        for c in range(DIMENSION):
            color = colors[(r+c) % 2]
            p.draw.rect(screen, color, p.Rect(c*SQ, r*SQ, SQ, SQ))


#draws the pieces on the board using the current gamestate variable
def draw_pieces(screen, board):
    for r in range(DIMENSION):
        for c in range(DIMENSION):
            piece = board[r][c]
            if piece != '--':
                screen.blit(IMAGES[piece], p.Rect(c*SQ, r*SQ, SQ, SQ))

if __name__ == '__main__':
    main()

import numpy as np
#responsible for storing information about the current state of the chess game
#responsible for determining the valid moves at the current state
#responsible for keeping a move log

class GameState():
    def __init__(self):
        #the board is an 8X8 np.array, each square has a string of len 2
        #the first char represents the color of the piece and the second represents the type of piece
        self.board = np.array([['bR', 'bN', 'bB', 'bQ', 'bK', 'bB', 'bN', 'bR'],
                              ['bP', 'bP', 'bP', 'bP', 'bP', 'bP', 'bP', 'bP'],
                              ['--', '--', '--', '--', '--', '--', '--', '--'],
                              ['--', '--', '--', '--', '--', '--', '--', '--'],
                              ['--', '--', '--', '--', '--', '--', '--', '--'],
                              ['--', '--', '--', '--', '--', '--', '--', '--'],
                              ['wP', 'wP', 'wP', 'wP', 'wP', 'wP', 'wP', 'wP'],
                              ['wR', 'wN', 'wB', 'wQ', 'wK', 'wB', 'wN', 'wR']])
        self.white_to_move = True
        self.move_log = []
        self.move_functions = {'P' : self.get_pawn_moves, 'R': self.get_rook_moves, 'N': self.get_knight_moves, 'B' : self.get_bishop_moves, 'Q': self.get_queen_moves, 'K' : self.get_king_moves}

        self.w_king_loc = (7, 4)
        self.b_king_loc = (0, 4)

    #doesnt work for en pessant, castling, pawn promotion
    def make_move(self, move):
        self.board[move.start_row][move.start_col] = '--'
        self.board[move.end_row][move.end_col] = move.piece_moved
        self.move_log.append(move)
        if move.piece_moved[1] == 'K':
            if move.piece_moved[0] == 'w':
                self.w_king_loc = (move.end_row, move.end_col)
            else:
                self.b_king_loc = (move.end_row, move.end_col)
        self.white_to_move = not self.white_to_move
    
    def undo_move(self):
        if len(self.move_log):
            move = self.move_log.pop()
            self.board[move.start_row][move.start_col] = move.piece_moved
            self.board[move.end_row][move.end_col] = move.piece_captured
            if move.piece_moved[1] == 'K':
                if move.piece_moved[0] == 'w':
                    self.w_king_loc = (move.start_row, move.start_col)
                else:
                    self.b_king_loc = (move.start_row, move.start_col)
            self.white_to_move = not self.white_to_move

    # checking if a piece is under attack
    def square_under_attack(self, r, c, by_color):
        """
        Returns True if square (r, c) is under attack by any piece of color `by_color` ('w' or 'b').
        Uses consistent self.board[row][col] indexing throughout.
        """
        # 1) Sliding pieces: Rooks/Queens on orthogonals, Bishops/Queens on diagonals
        directions_and_attackers = [
            # (list of (dr,dc), string of piece-letters to check)
            ([(-1, 0), (1, 0), (0, -1), (0, 1)],   'RQ'),
            ([(-1, -1), (-1, 1), (1, -1), (1, 1)], 'BQ'),
        ]
        for dirs, attacker_pieces in directions_and_attackers:
            for dr, dc in dirs:
                row, col = r + dr, c + dc
                while 0 <= row < 8 and 0 <= col < 8:
                    sq = self.board[row][col]
                    if sq != '--':
                        # occupied: if it's the right color & piece type, it's attacking
                        if sq[0] == by_color and sq[1] in attacker_pieces:
                            return True
                        # otherwise blocked
                        break
                    row += dr
                    col += dc

        # 2) Knight attacks
        knight_offsets = [
            (-2, -1), (-2,  1), (-1, -2), (-1,  2),
            ( 1, -2), ( 1,  2), ( 2, -1), ( 2,  1)
        ]
        for dr, dc in knight_offsets:
            row, col = r + dr, c + dc
            if 0 <= row < 8 and 0 <= col < 8:
                sq = self.board[row][col]
                if sq[0] == by_color and sq[1] == 'N':
                    return True

        # 3) Pawn attacks
        if by_color == 'w':
            pawn_dirs = [(1, -1), (1, 1)]
            pawn_char = 'wP'
        else:
            pawn_dirs = [(-1, -1), (-1, 1)]
            pawn_char = 'bP'
        for dr, dc in pawn_dirs:
            row, col = r + dr, c + dc
            if 0 <= row < 8 and 0 <= col < 8:
                if self.board[row][col] == pawn_char:
                    return True

        # 4) King adjacency
        for dr in (-1, 0, 1):
            for dc in (-1, 0, 1):
                if dr == 0 and dc == 0:
                    continue
                row, col = r + dr, c + dc
                if 0 <= row < 8 and 0 <= col < 8:
                    sq = self.board[row][col]
                    if sq[0] == by_color and sq[1] == 'K':
                        return True

        # Nothing attacks this square
        return False
    #checks if the king of the person who's move it is in check
    def in_check(self):
        if self.white_to_move:
            return self.square_under_attack(self.w_king_loc[0], self.w_king_loc[1], 'b')
        return self.square_under_attack(self.b_king_loc[0], self.b_king_loc[1], 'w')
        

    #all moves considering checks

    def get_valid_moves(self):
        moves = self.get_possible_moves()
        i = 0
        while i < len(moves):
            self.make_move(moves[i])
            self.white_to_move = not self.white_to_move # temporarily switch turn to see the in_check paramtert
            if self.in_check():
                moves.pop(i)
            else: 
                i += 1   
            self.undo_move()
            self.white_to_move = not self.white_to_move
        return moves
                
        

    #all moves w/o considering checks of any kind

    def get_possible_moves(self):
        moves = []
        for r in range(self.board.shape[0]):
            for c in range(self.board.shape[1]):
                turn = self.board[r][c][0]
                # is b if blacks piece, w if white piece, - if no piece
                if (turn == 'w' and self.white_to_move) or (turn == 'b' and not self.white_to_move):
                    piece = self.board[r][c][1]
                    self.move_functions[piece](r, c, moves)
        return moves
    
    # all moves for the piece of each type located at board[r][c]
    def get_pawn_moves(self, r, c, moves):
        if self.white_to_move:
            if self.board[r-1][c] == '--': # 1 sqare pawn advance
                moves.append(Move((r, c), (r-1, c), self.board))
                if r == 6 and self.board[r-2][c] == '--': # 2 sqaure pawn advance
                    moves.append(Move((r, c), (r-2, c), self.board))
            if c-1 >= 0:
                if self.board[r-1][c-1][0] == 'b': #captures to the left
                    moves.append(Move((r, c), (r-1, c-1), self.board))
            if c+1 <= 7:
                if self.board[r-1][c+1][0] == 'b': #captures to the right
                    moves.append(Move((r, c), (r-1, c+1), self.board))

        else:
            if self.board[r+1][c] == '--': # 1 sqare pawn advance
                moves.append(Move((r, c), (r+1, c), self.board))
                if r == 1 and self.board[r+2][c] == '--': # 2 sqaure pawn advance
                    moves.append(Move((r, c), (r+2, c), self.board))
            if c-1 >= 0:
                if self.board[r+1][c-1][0] == 'w': #captures to the left
                    moves.append(Move((r, c), (r+1, c-1), self.board))
            if c+1 <= 7:
                if self.board[r+1][c+1][0] == 'w': #captures to the right
                    moves.append(Move((r, c), (r+1, c+1), self.board))

            
    def get_rook_moves(self, r, c, moves):
        directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]
        own_color = self.board[r][c][0]
        for dr, dc in directions:
            row, col = r + dr, c + dc
            while 0 <= row < 8 and 0 <= col < 8:
                square = self.board[row][col]
                if square != '--':
                    # if it’s an enemy piece, you can capture
                    if square[0] != own_color:
                        moves.append(Move((r, c), (row, col), self.board))
                    # then stop scanning further in this direction
                    break
                else:
                    # empty square — valid move, keep going
                    moves.append(Move((r, c), (row, col), self.board))
                row += dr
                col += dc
    
    def get_knight_moves(self, r, c, moves):
            # all eight possible knight offsets
        knight_offsets = [(-2, -1), (-2,  1),
                      (-1, -2), (-1,  2),
                      ( 1, -2), ( 1,  2),
                      ( 2, -1), ( 2,  1)]
        own_color = self.board[r, c][0]
        for dr, dc in knight_offsets:
            row, col = r + dr, c + dc
            # stay on board
            if 0 <= row < 8 and 0 <= col < 8:
                target = self.board[row, col]
                # empty square or enemy piece
                if target == '--' or target[0] != own_color:
                    moves.append(Move((r, c), (row, col), self.board))
    def get_bishop_moves(self, r, c, moves):
        directions = [(-1, -1), (-1,  1), (1, -1), (1,  1)]
        own_color = self.board[r, c][0]
        for dr, dc in directions:
            row, col = r + dr, c + dc
            while 0 <= row < 8 and 0 <= col < 8:
                square = self.board[row, col]
                # if it’s occupied
                if square != '--':
                    # if it’s an enemy, you can capture
                    if square[0] != own_color:
                        moves.append(Move((r, c), (row, col), self.board))
                    # either way, stop this ray
                    break
                # empty square, legal move
                moves.append(Move((r, c), (row, col), self.board))
                # step further along the same diagonal
                row += dr
                col += dc
       


    def get_queen_moves(self, r, c, moves):
        self.get_rook_moves(r, c, moves)
        self.get_bishop_moves(r, c, moves)
    def get_king_moves(self, r, c, moves):
        """
        Adds all legal king moves (one square in any direction, no castling)
        for the king at (r,c) into the moves list.
        """
        own_color = self.board[r][c][0]
        # all eight directions around the king
        for dr in (-1, 0, 1):
            for dc in (-1, 0, 1):
                if dr == 0 and dc == 0:
                    continue
                row, col = r + dr, c + dc
                if 0 <= row < 8 and 0 <= col < 8:
                    target = self.board[row][col]
                    # empty square or enemy piece
                    if target == '--' or target[0] != own_color:
                        moves.append(Move((r, c), (row, col), self.board))

                    



        

class Move():
    rank_to_row = {'1' : 7, '2' : 6, '3' : 5, '4' : 4, '5' : 3, '6' : 2, '7' : 1, '8' : 0}
    row_to_rank = {v: k for k, v in rank_to_row.items()}
    file_to_col = {'a' : 0, 'b' : 1, 'c': 2, 'd' : 3, 'e' : 4, 'f' : 5, 'g' : 6, 'h' : 7}
    col_to_file = {v: k for k, v in file_to_col.items()}
    def __init__(self, start_sq, end_sq, board):
        self.start_row = start_sq[0]
        self.start_col = start_sq[1]
        self.end_row = end_sq[0]
        self.end_col = end_sq[1]
        self.piece_moved = board[self.start_row][self.start_col]
        self.piece_captured = board[self.end_row][self.end_col]
        self.move_ID = self.start_row*1000 + self.start_col *100 + self.end_row*10 + self.end_col

    #overriding the equals method

    def __eq__(self, other):
        if isinstance(other, Move):
            return self.move_ID == other.move_ID
        return False

    def get_chess_notation(self):
        return self.get_rank_file(self.start_row, self.start_col) + self.get_rank_file(self.end_row, self.end_col)
    
    def get_rank_file(self, r, c):
        return self.col_to_file[c] + self.row_to_rank[r]
        
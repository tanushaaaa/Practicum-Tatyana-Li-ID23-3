a = (input("В какую игру вы хотите сыграть (шашки/шахматы)?: "))
if a == "шашки":
    import pygame

    WIDTH, HEIGHT = 800, 800
    ROWS, COLS = 8, 8
    SQUARE_SIZE = WIDTH // COLS

    RED = (255, 0, 0)
    WHITE = (255, 255, 255)
    BLACK = (0, 0, 0)
    BLUE = (0, 0, 255)
    GREY = (128, 128, 128)

    CROWN = pygame.transform.scale(pygame.image.load('assets/images/black-queen.png'), (44, 25))


    class Board:
        def __init__(self):
            self.board = []
            self.red_left = self.white_left = 12
            self.red_kings = self.white_kings = 0
            self.create_board()

        def draw_squares(self, win):
            win.fill(BLACK)
            for row in range(ROWS):
                for col in range(row % 2, COLS, 2):
                    pygame.draw.rect(win, RED, (row * SQUARE_SIZE, col * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE))

        def move(self, piece, row, col):
            self.board[piece.row][piece.col], self.board[row][col] = self.board[row][col], self.board[piece.row][
                piece.col]
            piece.move(row, col)

            if row == ROWS - 1 or row == 0:
                piece.make_king()
                if piece.color == WHITE:
                    self.white_kings += 1
                else:
                    self.red_kings += 1

        def get_piece(self, row, col):
            return self.board[row][col]

        def create_board(self):
            for row in range(ROWS):
                self.board.append([])
                for col in range(COLS):
                    if col % 2 == ((row + 1) % 2):
                        if row < 3:
                            self.board[row].append(Piece(row, col, WHITE))
                        elif row > 4:
                            self.board[row].append(Piece(row, col, RED))
                        else:
                            self.board[row].append(0)
                    else:
                        self.board[row].append(0)

        def draw(self, win):
            self.draw_squares(win)
            for row in range(ROWS):
                for col in range(COLS):
                    piece = self.board[row][col]
                    if piece != 0:
                        piece.draw(win)

        def remove(self, pieces):
            for piece in pieces:
                self.board[piece.row][piece.col] = 0
                if piece != 0:
                    if piece.color == RED:
                        self.red_left -= 1
                    else:
                        self.white_left -= 1

        def winner(self):
            if self.red_left <= 0:
                return WHITE
            elif self.white_left <= 0:
                return RED

            return None

        def get_valid_moves(self, piece):
            moves = {}
            left = piece.col - 1
            right = piece.col + 1
            row = piece.row

            if piece.color == RED or piece.king:
                moves.update(self._traverse_left(row - 1, max(row - 3, -1), -1, piece.color, left))
                moves.update(self._traverse_right(row - 1, max(row - 3, -1), -1, piece.color, right))
            if piece.color == WHITE or piece.king:
                moves.update(self._traverse_left(row + 1, min(row + 3, ROWS), 1, piece.color, left))
                moves.update(self._traverse_right(row + 1, min(row + 3, ROWS), 1, piece.color, right))

            return moves

        def _traverse_left(self, start, stop, step, color, left, skipped=[]):
            moves = {}
            last = []
            for r in range(start, stop, step):
                if left < 0:
                    break

                current = self.board[r][left]
                if current == 0:
                    if skipped and not last:
                        break
                    elif skipped:
                        moves[(r, left)] = last + skipped
                    else:
                        moves[(r, left)] = last

                    if last:
                        if step == -1:
                            row = max(r - 3, 0)
                        else:
                            row = min(r + 3, ROWS)
                        moves.update(self._traverse_left(r + step, row, step, color, left - 1, skipped=last))
                        moves.update(self._traverse_right(r + step, row, step, color, left + 1, skipped=last))
                    break
                elif current.color == color:
                    break
                else:
                    last = [current]

                left -= 1

            return moves

        def _traverse_right(self, start, stop, step, color, right, skipped=[]):
            moves = {}
            last = []
            for r in range(start, stop, step):
                if right >= COLS:
                    break

                current = self.board[r][right]
                if current == 0:
                    if skipped and not last:
                        break
                    elif skipped:
                        moves[(r, right)] = last + skipped
                    else:
                        moves[(r, right)] = last

                    if last:
                        if step == -1:
                            row = max(r - 3, 0)
                        else:
                            row = min(r + 3, ROWS)
                        moves.update(self._traverse_left(r + step, row, step, color, right - 1, skipped=last))
                        moves.update(self._traverse_right(r + step, row, step, color, right + 1, skipped=last))
                    break
                elif current.color == color:
                    break
                else:
                    last = [current]

                right += 1

            return moves


    class Game:
        def __init__(self, win):
            self._init()
            self.win = win

        def update(self):
            self.board.draw(self.win)
            self.draw_valid_moves(self.valid_moves)
            pygame.display.update()

        def _init(self):
            self.selected = None
            self.board = Board()
            self.turn = RED
            self.valid_moves = {}

        def winner(self):
            return self.board.winner()

        def reset(self):
            self._init()

        def select(self, row, col):
            if self.selected:
                result = self._move(row, col)
                if not result:
                    self.selected = None
                    self.select(row, col)

            piece = self.board.get_piece(row, col)
            if piece != 0 and piece.color == self.turn:
                self.selected = piece
                self.valid_moves = self.board.get_valid_moves(piece)
                return True

            return False

        def _move(self, row, col):
            piece = self.board.get_piece(row, col)
            if self.selected and piece == 0 and (row, col) in self.valid_moves:
                self.board.move(self.selected, row, col)
                skipped = self.valid_moves[(row, col)]
                if skipped:
                    self.board.remove(skipped)
                self.change_turn()
            else:
                return False

            return True

        def draw_valid_moves(self, moves):
            for move in moves:
                row, col = move
                pygame.draw.circle(self.win, BLUE,
                                   (col * SQUARE_SIZE + SQUARE_SIZE // 2, row * SQUARE_SIZE + SQUARE_SIZE // 2), 15)

        def change_turn(self):
            self.valid_moves = {}
            if self.turn == RED:
                self.turn = WHITE
            else:
                self.turn = RED


    class Piece:
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
            self.x = SQUARE_SIZE * self.col + SQUARE_SIZE // 2
            self.y = SQUARE_SIZE * self.row + SQUARE_SIZE // 2

        def make_king(self):
            self.king = True

        def draw(self, win):
            radius = SQUARE_SIZE // 2 - self.PADDING
            pygame.draw.circle(win, GREY, (self.x, self.y), radius + self.OUTLINE)
            pygame.draw.circle(win, self.color, (self.x, self.y), radius)
            if self.king:
                win.blit(CROWN, (self.x - CROWN.get_width() // 2, self.y - CROWN.get_height() // 2))

        def move(self, row, col):
            self.row = row
            self.col = col
            self.calc_pos()

        def __repr__(self):
            return str(self.color)


    FPS = 60

    WIN = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption('Checkers')


    def get_row_col_from_mouse(pos):
        x, y = pos
        row = y // SQUARE_SIZE
        col = x // SQUARE_SIZE
        return row, col


    def main():
        run = True
        clock = pygame.time.Clock()
        game = Game(WIN)

        while run:
            clock.tick(FPS)

            if game.winner() != None:
                print(game.winner())
                run = False

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    run = False

                if event.type == pygame.MOUSEBUTTONDOWN:
                    pos = pygame.mouse.get_pos()
                    row, col = get_row_col_from_mouse(pos)
                    game.select(row, col)

            game.update()

        pygame.quit()


    main()

if a == "шахматы":
    import pygame

    pygame.init()

    WIDTH = 1000
    HEIGHT = 900
    screen = pygame.display.set_mode([WIDTH, HEIGHT])
    pygame.display.set_caption('Two-Player Pygame Chess!')
    font = pygame.font.Font('freesansbold.ttf', 20)
    medium_font = pygame.font.Font('freesansbold.ttf', 40)
    big_font = pygame.font.Font('freesansbold.ttf', 50)
    timer = pygame.time.Clock()
    fps = 60
    # game variables and images
    white_pieces = ['rook', 'knight', 'bishop', 'king', 'queen', 'bishop', 'knight', 'rook',
                    'pawn', 'pawn', 'pawn', 'pawn', 'pawn', 'pawn', 'pawn', 'pawn']
    white_locations = [(0, 0), (1, 0), (2, 0), (3, 0), (4, 0), (5, 0), (6, 0), (7, 0),
                       (0, 1), (1, 1), (2, 1), (3, 1), (4, 1), (5, 1), (6, 1), (7, 1)]
    black_pieces = ['rook', 'knight', 'bishop', 'king', 'queen', 'bishop', 'knight', 'rook',
                    'pawn', 'pawn', 'pawn', 'pawn', 'pawn', 'pawn', 'pawn', 'pawn']
    black_locations = [(0, 7), (1, 7), (2, 7), (3, 7), (4, 7), (5, 7), (6, 7), (7, 7),
                       (0, 6), (1, 6), (2, 6), (3, 6), (4, 6), (5, 6), (6, 6), (7, 6)]
    captured_pieces_white = []
    captured_pieces_black = []
    # 0 - whites turn no selection: 1-whites turn piece selected: 2- black turn no selection, 3 - black turn piece selected
    turn_step = 0
    selection = 100
    valid_moves = []
    # load in game piece images (queen, king, rook, bishop, knight, pawn) x 2
    black_queen = pygame.image.load('assets/images/black queen.png')
    black_queen = pygame.transform.scale(black_queen, (80, 80))
    black_queen_small = pygame.transform.scale(black_queen, (45, 45))
    black_king = pygame.image.load('assets/images/black king.png')
    black_king = pygame.transform.scale(black_king, (80, 80))
    black_king_small = pygame.transform.scale(black_king, (45, 45))
    black_rook = pygame.image.load('assets/images/black rook.png')
    black_rook = pygame.transform.scale(black_rook, (80, 80))
    black_rook_small = pygame.transform.scale(black_rook, (45, 45))
    black_bishop = pygame.image.load('assets/images/black bishop.png')
    black_bishop = pygame.transform.scale(black_bishop, (80, 80))
    black_bishop_small = pygame.transform.scale(black_bishop, (45, 45))
    black_knight = pygame.image.load('assets/images/black knight.png')
    black_knight = pygame.transform.scale(black_knight, (80, 80))
    black_knight_small = pygame.transform.scale(black_knight, (45, 45))
    black_pawn = pygame.image.load('assets/images/black pawn.png')
    black_pawn = pygame.transform.scale(black_pawn, (65, 65))
    black_pawn_small = pygame.transform.scale(black_pawn, (45, 45))
    white_queen = pygame.image.load('assets/images/white queen.png')
    white_queen = pygame.transform.scale(white_queen, (80, 80))
    white_queen_small = pygame.transform.scale(white_queen, (45, 45))
    white_king = pygame.image.load('assets/images/white king.png')
    white_king = pygame.transform.scale(white_king, (80, 80))
    white_king_small = pygame.transform.scale(white_king, (45, 45))
    white_rook = pygame.image.load('assets/images/white rook.png')
    white_rook = pygame.transform.scale(white_rook, (80, 80))
    white_rook_small = pygame.transform.scale(white_rook, (45, 45))
    white_bishop = pygame.image.load('assets/images/white bishop.png')
    white_bishop = pygame.transform.scale(white_bishop, (80, 80))
    white_bishop_small = pygame.transform.scale(white_bishop, (45, 45))
    white_knight = pygame.image.load('assets/images/white knight.png')
    white_knight = pygame.transform.scale(white_knight, (80, 80))
    white_knight_small = pygame.transform.scale(white_knight, (45, 45))
    white_pawn = pygame.image.load('assets/images/white pawn.png')
    white_pawn = pygame.transform.scale(white_pawn, (65, 65))
    white_pawn_small = pygame.transform.scale(white_pawn, (45, 45))
    white_images = [white_pawn, white_queen, white_king, white_knight, white_rook, white_bishop]
    white_promotions = ['bishop', 'knight', 'rook', 'queen']
    white_moved = [False, False, False, False, False, False, False, False,
                   False, False, False, False, False, False, False, False]
    small_white_images = [white_pawn_small, white_queen_small, white_king_small, white_knight_small,
                          white_rook_small, white_bishop_small]
    black_images = [black_pawn, black_queen, black_king, black_knight, black_rook, black_bishop]
    small_black_images = [black_pawn_small, black_queen_small, black_king_small, black_knight_small,
                          black_rook_small, black_bishop_small]
    black_promotions = ['bishop', 'knight', 'rook', 'queen']
    black_moved = [False, False, False, False, False, False, False, False,
                   False, False, False, False, False, False, False, False]
    piece_list = ['pawn', 'queen', 'king', 'knight', 'rook', 'bishop']
    # check variables/ flashing counter
    counter = 0
    winner = ''
    game_over = False
    white_ep = (100, 100)
    black_ep = (100, 100)
    white_promote = False
    black_promote = False
    promo_index = 100
    check = False
    castling_moves = []


    class Board:
        # draw main game board
        def draw_board():
            for i in range(32):
                column = i % 4
                row = i // 4
                if row % 2 == 0:
                    pygame.draw.rect(screen, 'light gray', [600 - (column * 200), row * 100, 100, 100])
                else:
                    pygame.draw.rect(screen, 'light gray', [700 - (column * 200), row * 100, 100, 100])
                pygame.draw.rect(screen, 'gray', [0, 800, WIDTH, 100])
                pygame.draw.rect(screen, 'gold', [0, 800, WIDTH, 100], 5)
                pygame.draw.rect(screen, 'gold', [800, 0, 200, HEIGHT], 5)
                status_text = ['White: Select a Piece to Move!', 'White: Select a Destination!',
                               'Black: Select a Piece to Move!', 'Black: Select a Destination!']
                screen.blit(big_font.render(status_text[turn_step], True, 'black'), (20, 820))
                for i in range(9):
                    pygame.draw.line(screen, 'black', (0, 100 * i), (800, 100 * i), 2)
                    pygame.draw.line(screen, 'black', (100 * i, 0), (100 * i, 800), 2)
                screen.blit(medium_font.render('FORFEIT', True, 'black'), (810, 830))
                if white_promote or black_promote:
                    pygame.draw.rect(screen, 'gray', [0, 800, WIDTH - 200, 100])
                    pygame.draw.rect(screen, 'gold', [0, 800, WIDTH - 200, 100], 5)
                    screen.blit(big_font.render('Select Piece to Promote Pawn', True, 'black'), (20, 820))

        # draw pieces onto board
        def draw_pieces():
            for i in range(len(white_pieces)):
                index = piece_list.index(white_pieces[i])
                if white_pieces[i] == 'pawn':
                    screen.blit(white_pawn, (white_locations[i][0] * 100 + 22, white_locations[i][1] * 100 + 30))
                else:
                    screen.blit(white_images[index],
                                (white_locations[i][0] * 100 + 10, white_locations[i][1] * 100 + 10))
                if turn_step < 2:
                    if selection == i:
                        pygame.draw.rect(screen, 'red',
                                         [white_locations[i][0] * 100 + 1, white_locations[i][1] * 100 + 1,
                                          100, 100], 2)

            for i in range(len(black_pieces)):
                index = piece_list.index(black_pieces[i])
                if black_pieces[i] == 'pawn':
                    screen.blit(black_pawn, (black_locations[i][0] * 100 + 22, black_locations[i][1] * 100 + 30))
                else:
                    screen.blit(black_images[index],
                                (black_locations[i][0] * 100 + 10, black_locations[i][1] * 100 + 10))
                if turn_step >= 2:
                    if selection == i:
                        pygame.draw.rect(screen, 'blue',
                                         [black_locations[i][0] * 100 + 1, black_locations[i][1] * 100 + 1,
                                          100, 100], 2)

        # function to check all pieces valid options on board
        def check_options(pieces, locations, turn):
            global castling_moves
            moves_list = []
            all_moves_list = []
            castling_moves = []
            for i in range((len(pieces))):
                location = locations[i]
                piece = pieces[i]
                if piece == 'pawn':
                    moves_list = Pawn.check_pawn(location, turn)
                elif piece == 'rook':
                    moves_list = Rook.check_rook(location, turn)
                elif piece == 'knight':
                    moves_list = Knight.check_knight(location, turn)
                elif piece == 'bishop':
                    moves_list = Bishop.check_bishop(location, turn)
                elif piece == 'queen':
                    moves_list = Queen.check_queen(location, turn)
                elif piece == 'king':
                    moves_list, castling_moves = King.check_king(location, turn)
                all_moves_list.append(moves_list)
            return all_moves_list

        # draw captured pieces on side of screen
        def draw_captured():
            for i in range(len(captured_pieces_white)):
                captured_piece = captured_pieces_white[i]
                index = piece_list.index(captured_piece)
                screen.blit(small_black_images[index], (825, 5 + 50 * i))
            for i in range(len(captured_pieces_black)):
                captured_piece = captured_pieces_black[i]
                index = piece_list.index(captured_piece)
                screen.blit(small_white_images[index], (925, 5 + 50 * i))

        # check for valid moves for just selected piece
        def check_valid_moves():
            if turn_step < 2:
                options_list = white_options
            else:
                options_list = black_options
            valid_options = options_list[selection]
            return valid_options

        # draw valid moves on screen
        def draw_valid(moves):
            if turn_step < 2:
                color = 'red'
            else:
                color = 'blue'
            for i in range(len(moves)):
                pygame.draw.circle(screen, color, (moves[i][0] * 100 + 50, moves[i][1] * 100 + 50), 5)

        # draw a flashing square around king if in check
        def draw_check():
            global check
            check = False
            if turn_step < 2:
                if 'king' in white_pieces:
                    king_index = white_pieces.index('king')
                    king_location = white_locations[king_index]
                    for i in range(len(black_options)):
                        if king_location in black_options[i]:
                            check = True
                            if counter < 15:
                                pygame.draw.rect(screen, 'dark red', [white_locations[king_index][0] * 100 + 1,
                                                                      white_locations[king_index][1] * 100 + 1, 100,
                                                                      100],
                                                 5)
            else:
                if 'king' in black_pieces:
                    king_index = black_pieces.index('king')
                    king_location = black_locations[king_index]
                    for i in range(len(white_options)):
                        if king_location in white_options[i]:
                            check = True
                            if counter < 15:
                                pygame.draw.rect(screen, 'dark blue', [black_locations[king_index][0] * 100 + 1,
                                                                       black_locations[king_index][1] * 100 + 1, 100,
                                                                       100],
                                                 5)

        def draw_game_over():
            pygame.draw.rect(screen, 'black', [200, 200, 400, 70])
            screen.blit(font.render(f'{winner} won the game!', True, 'white'), (210, 210))
            screen.blit(font.render(f'Press ENTER to Restart!', True, 'white'), (210, 240))

        # check en passant because people on the internet won't stop bugging me for it
        def check_ep(old_coords, new_coords):
            if turn_step <= 1:
                index = white_locations.index(old_coords)
                ep_coords = (new_coords[0], new_coords[1] - 1)
                piece = white_pieces[index]
            else:
                index = black_locations.index(old_coords)
                ep_coords = (new_coords[0], new_coords[1] + 1)
                piece = black_pieces[index]
            if piece == 'pawn' and abs(old_coords[1] - new_coords[1]) > 1:
                # if piece was pawn and moved two spaces, return EP coords as defined above
                pass
            else:
                ep_coords = (100, 100)
            return ep_coords

        # add castling
        def check_castling():
            # king must not currently be in check, neither the rook nor king has moved previously, nothing between
            # and the king does not pass through or finish on an attacked piece
            castle_moves = []  # store each valid castle move as [((king_coords), (castle_coords))]
            rook_indexes = []
            rook_locations = []
            king_index = 0
            king_pos = (0, 0)
            if turn_step > 1:
                for i in range(len(white_pieces)):
                    if white_pieces[i] == 'rook':
                        rook_indexes.append(white_moved[i])
                        rook_locations.append(white_locations[i])
                    if white_pieces[i] == 'king':
                        king_index = i
                        king_pos = white_locations[i]
                if not white_moved[king_index] and False in rook_indexes and not check:
                    for i in range(len(rook_indexes)):
                        castle = True
                        if rook_locations[i][0] > king_pos[0]:
                            empty_squares = [(king_pos[0] + 1, king_pos[1]), (king_pos[0] + 2, king_pos[1]),
                                             (king_pos[0] + 3, king_pos[1])]
                        else:
                            empty_squares = [(king_pos[0] - 1, king_pos[1]), (king_pos[0] - 2, king_pos[1])]
                        for j in range(len(empty_squares)):
                            if empty_squares[j] in white_locations or empty_squares[j] in black_locations or \
                                    empty_squares[j] in black_options or rook_indexes[i]:
                                castle = False
                        if castle:
                            castle_moves.append((empty_squares[1], empty_squares[0]))
            else:
                for i in range(len(black_pieces)):
                    if black_pieces[i] == 'rook':
                        rook_indexes.append(black_moved[i])
                        rook_locations.append(black_locations[i])
                    if black_pieces[i] == 'king':
                        king_index = i
                        king_pos = black_locations[i]
                if not black_moved[king_index] and False in rook_indexes and not check:
                    for i in range(len(rook_indexes)):
                        castle = True
                        if rook_locations[i][0] > king_pos[0]:
                            empty_squares = [(king_pos[0] + 1, king_pos[1]), (king_pos[0] + 2, king_pos[1]),
                                             (king_pos[0] + 3, king_pos[1])]
                        else:
                            empty_squares = [(king_pos[0] - 1, king_pos[1]), (king_pos[0] - 2, king_pos[1])]
                        for j in range(len(empty_squares)):
                            if empty_squares[j] in white_locations or empty_squares[j] in black_locations or \
                                    empty_squares[j] in white_options or rook_indexes[i]:
                                castle = False
                        if castle:
                            castle_moves.append((empty_squares[1], empty_squares[0]))
            return castle_moves

        def draw_castling(moves):
            if turn_step < 2:
                color = 'red'
            else:
                color = 'blue'
            for i in range(len(moves)):
                pygame.draw.circle(screen, color, (moves[i][0][0] * 100 + 50, moves[i][0][1] * 100 + 70), 8)
                screen.blit(font.render('king', True, 'black'), (moves[i][0][0] * 100 + 30, moves[i][0][1] * 100 + 70))
                pygame.draw.circle(screen, color, (moves[i][1][0] * 100 + 50, moves[i][1][1] * 100 + 70), 8)
                screen.blit(font.render('rook', True, 'black'),
                            (moves[i][1][0] * 100 + 30, moves[i][1][1] * 100 + 70))
                pygame.draw.line(screen, color, (moves[i][0][0] * 100 + 50, moves[i][0][1] * 100 + 70),
                                 (moves[i][1][0] * 100 + 50, moves[i][1][1] * 100 + 70), 2)

        # add pawn promotion
        def check_promotion():
            pawn_indexes = []
            white_promotion = False
            black_promotion = False
            promote_index = 100
            for i in range(len(white_pieces)):
                if white_pieces[i] == 'pawn':
                    pawn_indexes.append(i)
            for i in range(len(pawn_indexes)):
                if white_locations[pawn_indexes[i]][1] == 7:
                    white_promotion = True
                    promote_index = pawn_indexes[i]
            pawn_indexes = []
            for i in range(len(black_pieces)):
                if black_pieces[i] == 'pawn':
                    pawn_indexes.append(i)
            for i in range(len(pawn_indexes)):
                if black_locations[pawn_indexes[i]][1] == 0:
                    black_promotion = True
                    promote_index = pawn_indexes[i]
            return white_promotion, black_promotion, promote_index

        def draw_promotion():
            pygame.draw.rect(screen, 'dark gray', [800, 0, 200, 420])
            if white_promote:
                color = 'white'
                for i in range(len(white_promotions)):
                    piece = white_promotions[i]
                    index = piece_list.index(piece)
                    screen.blit(white_images[index], (860, 5 + 100 * i))
            elif black_promote:
                color = 'black'
                for i in range(len(black_promotions)):
                    piece = black_promotions[i]
                    index = piece_list.index(piece)
                    screen.blit(black_images[index], (860, 5 + 100 * i))
            pygame.draw.rect(screen, color, [800, 0, 200, 420], 8)

        def check_promo_select():
            mouse_pos = pygame.mouse.get_pos()
            left_click = pygame.mouse.get_pressed()[0]
            x_pos = mouse_pos[0] // 100
            y_pos = mouse_pos[1] // 100
            if white_promote and left_click and x_pos > 7 and y_pos < 4:
                white_pieces[promo_index] = white_promotions[y_pos]
            elif black_promote and left_click and x_pos > 7 and y_pos < 4:
                black_pieces[promo_index] = black_promotions[y_pos]


    class King:
        # check king valid moves
        def check_king(position, color):
            moves_list = []
            castle_moves = Board.check_castling()
            if color == 'white':
                enemies_list = black_locations
                friends_list = white_locations
            else:
                friends_list = black_locations
                enemies_list = white_locations
            # 8 squares to check for kings, they can go one square any direction
            targets = [(1, 0), (1, 1), (1, -1), (-1, 0), (-1, 1), (-1, -1), (0, 1), (0, -1)]
            for i in range(8):
                target = (position[0] + targets[i][0], position[1] + targets[i][1])
                if target not in friends_list and 0 <= target[0] <= 7 and 0 <= target[1] <= 7:
                    moves_list.append(target)
            return moves_list, castle_moves


    class Queen:
        # check queen valid moves
        def check_queen(position, color):
            moves_list = Bishop.check_bishop(position, color)
            second_list = Rook.check_rook(position, color)
            for i in range(len(second_list)):
                moves_list.append(second_list[i])
            return moves_list


    class Bishop:
        # check bishop moves
        def check_bishop(position, color):
            moves_list = []
            if color == 'white':
                enemies_list = black_locations
                friends_list = white_locations
            else:
                friends_list = black_locations
                enemies_list = white_locations
            for i in range(4):  # up-right, up-left, down-right, down-left
                path = True
                chain = 1
                if i == 0:
                    x = 1
                    y = -1
                elif i == 1:
                    x = -1
                    y = -1
                elif i == 2:
                    x = 1
                    y = 1
                else:
                    x = -1
                    y = 1
                while path:
                    if (position[0] + (chain * x), position[1] + (chain * y)) not in friends_list and \
                            0 <= position[0] + (chain * x) <= 7 and 0 <= position[1] + (chain * y) <= 7:
                        moves_list.append((position[0] + (chain * x), position[1] + (chain * y)))
                        if (position[0] + (chain * x), position[1] + (chain * y)) in enemies_list:
                            path = False
                        chain += 1
                    else:
                        path = False
            return moves_list


    class Rook:
        # check rook moves
        def check_rook(position, color):
            moves_list = []
            if color == 'white':
                enemies_list = black_locations
                friends_list = white_locations
            else:
                friends_list = black_locations
                enemies_list = white_locations
            for i in range(4):  # down, up, right, left
                path = True
                chain = 1
                if i == 0:
                    x = 0
                    y = 1
                elif i == 1:
                    x = 0
                    y = -1
                elif i == 2:
                    x = 1
                    y = 0
                else:
                    x = -1
                    y = 0
                while path:
                    if (position[0] + (chain * x), position[1] + (chain * y)) not in friends_list and \
                            0 <= position[0] + (chain * x) <= 7 and 0 <= position[1] + (chain * y) <= 7:
                        moves_list.append((position[0] + (chain * x), position[1] + (chain * y)))
                        if (position[0] + (chain * x), position[1] + (chain * y)) in enemies_list:
                            path = False
                        chain += 1
                    else:
                        path = False
            return moves_list


    class Pawn:
        # check valid pawn moves
        def check_pawn(position, color):
            moves_list = []
            if color == 'white':
                if (position[0], position[1] + 1) not in white_locations and \
                        (position[0], position[1] + 1) not in black_locations and position[1] < 7:
                    moves_list.append((position[0], position[1] + 1))
                    # indent the check for two spaces ahead, so it is only checked if one space ahead is also open
                    if (position[0], position[1] + 2) not in white_locations and \
                            (position[0], position[1] + 2) not in black_locations and position[1] == 1:
                        moves_list.append((position[0], position[1] + 2))
                if (position[0] + 1, position[1] + 1) in black_locations:
                    moves_list.append((position[0] + 1, position[1] + 1))
                if (position[0] - 1, position[1] + 1) in black_locations:
                    moves_list.append((position[0] - 1, position[1] + 1))
                # add en passant move checker
                if (position[0] + 1, position[1] + 1) == black_ep:
                    moves_list.append((position[0] + 1, position[1] + 1))
                if (position[0] - 1, position[1] + 1) == black_ep:
                    moves_list.append((position[0] - 1, position[1] + 1))
            else:
                if (position[0], position[1] - 1) not in white_locations and \
                        (position[0], position[1] - 1) not in black_locations and position[1] > 0:
                    moves_list.append((position[0], position[1] - 1))
                    # indent the check for two spaces ahead, so it is only checked if one space ahead is also open
                    if (position[0], position[1] - 2) not in white_locations and \
                            (position[0], position[1] - 2) not in black_locations and position[1] == 6:
                        moves_list.append((position[0], position[1] - 2))
                if (position[0] + 1, position[1] - 1) in white_locations:
                    moves_list.append((position[0] + 1, position[1] - 1))
                if (position[0] - 1, position[1] - 1) in white_locations:
                    moves_list.append((position[0] - 1, position[1] - 1))
                # add en passant move checker
                if (position[0] + 1, position[1] - 1) == white_ep:
                    moves_list.append((position[0] + 1, position[1] - 1))
                if (position[0] - 1, position[1] - 1) == white_ep:
                    moves_list.append((position[0] - 1, position[1] - 1))
            return moves_list


    class Knight:
        # check valid knight moves
        def check_knight(position, color):
            moves_list = []
            if color == 'white':
                enemies_list = black_locations
                friends_list = white_locations
            else:
                friends_list = black_locations
                enemies_list = white_locations
            # 8 squares to check for knights, they can go two squares in one direction and one in another
            targets = [(1, 2), (1, -2), (2, 1), (2, -1), (-1, 2), (-1, -2), (-2, 1), (-2, -1)]
            for i in range(8):
                target = (position[0] + targets[i][0], position[1] + targets[i][1])
                if target not in friends_list and 0 <= target[0] <= 7 and 0 <= target[1] <= 7:
                    moves_list.append(target)
            return moves_list


    # main game loop
    black_options = Board.check_options(black_pieces, black_locations, 'black')
    white_options = Board.check_options(white_pieces, white_locations, 'white')
    run = True
    while run:
        timer.tick(fps)
        if counter < 30:
            counter += 1
        else:
            counter = 0
        screen.fill('dark gray')
        Board.draw_board()
        Board.draw_pieces()
        Board.draw_captured()
        Board.draw_check()
        if not game_over:
            white_promote, black_promote, promo_index = Board.check_promotion()
            if white_promote or black_promote:
                Board.draw_promotion()
                Board.check_promo_select()
        if selection != 100:
            valid_moves = Board.check_valid_moves()
            Board.draw_valid(valid_moves)
            if selected_piece == 'king':
                Board.draw_castling(castling_moves)
        # event handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and not game_over:
                x_coord = event.pos[0] // 100
                y_coord = event.pos[1] // 100
                click_coords = (x_coord, y_coord)
                if turn_step <= 1:
                    if click_coords == (8, 8) or click_coords == (9, 8):
                        winner = 'black'
                    if click_coords in white_locations:
                        selection = white_locations.index(click_coords)
                        # check what piece is selected, so you can only draw castling moves if king is selected
                        selected_piece = white_pieces[selection]
                        if turn_step == 0:
                            turn_step = 1
                    if click_coords in valid_moves and selection != 100:
                        white_ep = Board.check_ep(white_locations[selection], click_coords)
                        white_locations[selection] = click_coords
                        white_moved[selection] = True
                        if click_coords in black_locations:
                            black_piece = black_locations.index(click_coords)
                            captured_pieces_white.append(black_pieces[black_piece])
                            if black_pieces[black_piece] == 'king':
                                winner = 'white'
                            black_pieces.pop(black_piece)
                            black_locations.pop(black_piece)
                            black_moved.pop(black_piece)
                        # adding check if en passant pawn was captured
                        if click_coords == black_ep:
                            black_piece = black_locations.index((black_ep[0], black_ep[1] - 1))
                            captured_pieces_white.append(black_pieces[black_piece])
                            black_pieces.pop(black_piece)
                            black_locations.pop(black_piece)
                            black_moved.pop(black_piece)
                        black_options = Board.check_options(black_pieces, black_locations, 'black')
                        white_options = Board.check_options(white_pieces, white_locations, 'white')
                        turn_step = 2
                        selection = 100
                        valid_moves = []
                    # add option to castle
                    elif selection != 100 and selected_piece == 'king':
                        for q in range(len(castling_moves)):
                            if click_coords == castling_moves[q][0]:
                                white_locations[selection] = click_coords
                                white_moved[selection] = True
                                if click_coords == (1, 0):
                                    rook_coords = (0, 0)
                                else:
                                    rook_coords = (7, 0)
                                rook_index = white_locations.index(rook_coords)
                                white_locations[rook_index] = castling_moves[q][1]
                                black_options = Board.check_options(black_pieces, black_locations, 'black')
                                white_options = Board.check_options(white_pieces, white_locations, 'white')
                                turn_step = 2
                                selection = 100
                                valid_moves = []
                if turn_step > 1:
                    if click_coords == (8, 8) or click_coords == (9, 8):
                        winner = 'white'
                    if click_coords in black_locations:
                        selection = black_locations.index(click_coords)
                        # check what piece is selected, so you can only draw castling moves if king is selected
                        selected_piece = black_pieces[selection]
                        if turn_step == 2:
                            turn_step = 3
                    if click_coords in valid_moves and selection != 100:
                        black_ep = Board.check_ep(black_locations[selection], click_coords)
                        black_locations[selection] = click_coords
                        black_moved[selection] = True
                        if click_coords in white_locations:
                            white_piece = white_locations.index(click_coords)
                            captured_pieces_black.append(white_pieces[white_piece])
                            if white_pieces[white_piece] == 'king':
                                winner = 'black'
                            white_pieces.pop(white_piece)
                            white_locations.pop(white_piece)
                            white_moved.pop(white_piece)
                        if click_coords == white_ep:
                            white_piece = white_locations.index((white_ep[0], white_ep[1] + 1))
                            captured_pieces_black.append(white_pieces[white_piece])
                            white_pieces.pop(white_piece)
                            white_locations.pop(white_piece)
                            white_moved.pop(white_piece)
                        black_options = Board.check_options(black_pieces, black_locations, 'black')
                        white_options = Board.check_options(white_pieces, white_locations, 'white')
                        turn_step = 0
                        selection = 100
                        valid_moves = []
                    # add option to castle
                    elif selection != 100 and selected_piece == 'king':
                        for q in range(len(castling_moves)):
                            if click_coords == castling_moves[q][0]:
                                black_locations[selection] = click_coords
                                black_moved[selection] = True
                                if click_coords == (1, 7):
                                    rook_coords = (0, 7)
                                else:
                                    rook_coords = (7, 7)
                                rook_index = black_locations.index(rook_coords)
                                black_locations[rook_index] = castling_moves[q][1]
                                black_options = Board.check_options(black_pieces, black_locations, 'black')
                                white_options = Board.check_options(white_pieces, white_locations, 'white')
                                turn_step = 0
                                selection = 100
                                valid_moves = []
            if event.type == pygame.KEYDOWN and game_over:
                if event.key == pygame.K_RETURN:
                    game_over = False
                    winner = ''
                    white_pieces = ['rook', 'knight', 'bishop', 'king', 'queen', 'bishop', 'knight', 'rook',
                                    'pawn', 'pawn', 'pawn', 'pawn', 'pawn', 'pawn', 'pawn', 'pawn']
                    white_locations = [(0, 0), (1, 0), (2, 0), (3, 0), (4, 0), (5, 0), (6, 0), (7, 0),
                                       (0, 1), (1, 1), (2, 1), (3, 1), (4, 1), (5, 1), (6, 1), (7, 1)]
                    white_moved = [False, False, False, False, False, False, False, False,
                                   False, False, False, False, False, False, False, False]
                    black_pieces = ['rook', 'knight', 'bishop', 'king', 'queen', 'bishop', 'knight', 'rook',
                                    'pawn', 'pawn', 'pawn', 'pawn', 'pawn', 'pawn', 'pawn', 'pawn']
                    black_locations = [(0, 7), (1, 7), (2, 7), (3, 7), (4, 7), (5, 7), (6, 7), (7, 7),
                                       (0, 6), (1, 6), (2, 6), (3, 6), (4, 6), (5, 6), (6, 6), (7, 6)]
                    black_moved = [False, False, False, False, False, False, False, False,
                                   False, False, False, False, False, False, False, False]
                    captured_pieces_white = []
                    captured_pieces_black = []
                    turn_step = 0
                    selection = 100
                    valid_moves = []
                    black_options = Board.check_options(black_pieces, black_locations, 'black')
                    white_options = Board.check_options(white_pieces, white_locations, 'white')

        if winner != '':
            game_over = True
            Board.draw_game_over()

        pygame.display.flip()
    pygame.quit()




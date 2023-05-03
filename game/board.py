from constant import *


class Board:
    def __init__(self, board=init_board, turn=Player.WHITE):
        self.player = None
        self.size = len(board)
        self.board = self.setting_board(board)
        self.turn = turn
        self.previous_move = None  # (Piece, end)

    def __str__(self):
        board_str = '-----------------\n'
        for row in self.board:
            board_str += '|'
            for col in row:
                board_str += str(col) + '|' if col else ' |'
            board_str += '\n'
        board_str += '-----------------\n'
        return board_str

    def setting_board(self, board):
        temp = [[None for _ in range(self.size)] for _ in range(self.size)]

        for i, col in enumerate(board):
            for j, sq in enumerate(col):
                if sq == ' ': continue
                player = Player.WHITE if sq.islower() else Player.BLACK
                sq = sq.lower()
                temp[i][j] = globals()[classname_of_pieces[sq]]((i, j), player)

        return temp

    def is_enemy(self, pos, player) -> bool:
        if self.is_empty(pos):
            return False
        return self.board[pos[0]][pos[1]].player != player

    def is_occupied(self, pos) -> bool:
        return self.board[pos[0]][pos[1]] is not None

    def is_empty(self, pos) -> bool:
        return self.board[pos[0]][pos[1]] is None

    def is_within_bounds(self, pos):
        return 0 <= pos[0] < self.size and 0 <= pos[1] < self.size

    def find_myk(self):

        for col in self.board:
            for row in col:
                if isinstance(row, King):
                    if row.player == Player.WHITE:
                        if self.turn == Player.WHITE:
                            return row.pos
                        elif self.turn == Player.BLACK:
                            break
                    elif row.player == Player.BLACK:
                        if self.turn == Player.WHITE:
                            break
                        elif self.turn == Player.BLACK:
                            return row.pos

    def find_opk(self):

        if self.turn == Player.WHITE:
            for col in self.board:
                for row in col:
                    if isinstance(row, King): # 왕 찾았어
                        if row.player == Player.WHITE:
                            return row.pos
                        if row.player == Player.BLACK: # 화이츠 차례에 왕이 블랙이면 위치를 보낸다 이거잖아
                            continue
        if self.turn == Player.BLACK:
            for col in self.board:
                for row in col:
                    if isinstance(row, King): # 왕 찾았어
                        if row.player == Player.BLACK:
                            return row.pos
                        if row.player == Player.WHITE: # 화이츠 차례에 왕이 블랙이면 위치를 보낸다 이거잖아
                            continue

    def move(self, start, end):
        c1, r1 = start
        c2, r2 = end
        piece = self.board[c1][r1]

        if not self.is_occupied(start):
            print("아무것도 없는 칸")
            return
        if piece.player != self.turn:
            print("플레이어의 기물 X.")
            return


        if isinstance(piece, Pawn):
            self.move_pawn(start, end)
        else:
            self.move_piece(start, end)

        if self.final_check(start, end):
            print("체크입니다~!!!!!!!!!!!!")
            return


        ## 폰 움직임 여기서 구현

    def move_pawn(self, start, end):
        c1, r1 = start
        c2, r2 = end
        piece = self.board[c1][r1]

        if not isinstance(piece, Pawn):
            print("error")
            return

        if end not in piece.get_legal_moves(self):
            print("가능한 수 X")
            return

        if piece.is_promotion_line():
            prom_val = c2
            nc = 0 if self.turn == Player.WHITE else 7
            ne = (nc, r2)
            prom_piece = globals()[classname_of_pieces[prom_val]](ne, self.turn)

            self.board[c1][r1] = None
            self.board[nc][r2] = prom_piece
            return

        if piece.enpassant(self):
            _, taked_pos = piece.enpassant(self)
            tc, tr = taked_pos
            tc -= piece.directions

            self.board[c2][r2] = self.board[c1][r1]
            self.board[c1][r1] = None
            self.board[tc][tr] = None

        else:
            self.board[c2][r2] = self.board[c1][r1]
            self.board[c1][r1] = None

        piece.set_position(end)
        self.previous_move = (piece, end)

        self.turn = Player.WHITE if self.turn == Player.BLACK else Player.BLACK

    def move_piece(self, start, end):
        c1, r1 = start
        c2, r2 = end
        piece = self.board[c1][r1]  # 이거는 초기에 말 확인하는거

        ## piece != None 이라는 것을 편집기한테 알려주기위해서
        if not isinstance(piece, Piece):
            print("아무것도 없는 칸")
            return

        if end not in piece.get_legal_moves(self):
            print("가능한 수 X")
            return

        self.board[c2][r2] = self.board[c1][r1]
        self.board[c1][r1] = None
        piece.set_position(end)
        self.previous_move = (piece, end)

        self.turn = Player.WHITE if self.turn == Player.BLACK else Player.BLACK

    def pre_check(self, start):
        c1, r1 = start
        ini_piece = self.board[c1][r1]
        k_col, k_row = self.find_myk()
        self.board[c1][r1] = None

        pieces = {
            'b': bishop_directions,
            'r': rook_directions,
            'q': queen_directions
        }

        for piece in pieces:

            for direction in pieces[piece]:
                ct, rt = k_col + direction[0], k_row + direction[1]

                while self.is_within_bounds((ct, rt)):
                    if isinstance(pieces[piece], Bishop):
                        if isinstance(self.board[ct][rt], Bishop):
                            self.board[c1][r1] = ini_piece
                            return True
                        if not self.is_empty((ct, rt)):
                            break

                    if isinstance(pieces[piece], Rook):
                        if isinstance(self.board[ct][rt], Rook):
                            self.board[c1][r1] = ini_piece
                            return True
                        if not self.is_empty((ct, rt)):
                            break

                    if isinstance(pieces[piece], Queen):
                        if isinstance(self.board[ct][rt], Queen):
                            self.board[c1][r1] = ini_piece
                            return True
                        if not self.is_empty((ct, rt)):
                            break
                    ct, rt = ct + direction[0], rt + direction[1]

        self.board[c1][r1] = ini_piece

        return False


    def final_check(self, start, end):
        c1, r1 = start
        c2, r2 = end
        opk_col, opk_row = self.find_opk()
        last_piece = self.board[c2][r2]
        ini_piece = self.board[c1][r1]
        self.board[c1][r1] = None

        pieces = {
            'b': bishop_directions,
            'r': rook_directions,
            'q': queen_directions,
        }

        if isinstance(self.board[c2][r2], Knight):  ##움직인 말이 나이트인 경우
            ##이 말의 움직임 결과에 이 좌표가 있으면 check

            for direction in knight_directions:
                ct, rt = opk_col + direction[0], opk_row + direction[1]
                print(ct, rt)
                if not self.is_within_bounds((ct, rt)):
                    continue

                if isinstance(self.board[ct][rt], Knight):
                    self.board[c1][r1] = ini_piece
                    return True

        if isinstance(last_piece, Pawn):

            pawn_directions = [(-1, -1), (-1, 1)]
            PAWN_directions = [(1, 1), (1, -1)]

            if self.turn == Player.BLACK:
                for direction in PAWN_directions:
                    ct, rt = opk_col + direction[0], opk_row + direction[1]
                    if not self.is_within_bounds((ct, rt)):
                        break

                    if (ct, rt) in (opk_col, opk_row):
                        self.board[c1][r1] = ini_piece
                        return True

            if self.turn == Player.WHITE:
                for direction in pawn_directions:
                    ct, rt = opk_col + direction[0], opk_row + direction[1]
                    if not self.is_within_bounds((ct, rt)):
                        continue

                    if (ct, rt) in (opk_col, opk_row):
                        self.board[c1][r1] = ini_piece
                        return True
        #움직인 말이 비숍, 룩, 퀸인 경우 또는 움직인 말에 의해 생성된 경로에 이 좌표가 있으면 check
        for piece in pieces:

            for direction in pieces[piece]:
                ct, rt = opk_col + direction[0], opk_row + direction[1]

                while self.is_within_bounds((ct, rt)):

                    if isinstance(pieces[piece], Bishop):
                        if isinstance(self.board[ct][rt], Bishop):
                            self.board[c1][r1] = ini_piece
                            return True
                        if not self.is_empty((ct, rt)):
                            break

                    if isinstance(pieces[piece], Rook):
                        if isinstance(self.board[ct][rt], Rook):
                            self.board[c1][r1] = ini_piece
                            return True
                        if not self.is_empty((ct, rt)):
                            break

                    if isinstance(pieces[piece], Queen):
                        if isinstance(self.board[ct][rt], Queen):
                            self.board[c1][r1] = ini_piece
                            return True
                        if not self.is_empty((ct, rt)):
                            break
                    ct, rt = ct + direction[0], rt + direction[1]


        self.board[c1][r1] = ini_piece
        return False


def get_classname(piece):
    return classname_of_pieces[piece.lower()]


def can_castling():
    pass


class Piece:
    ##player: boolean -> true=white / false=black
    def __init__(self, pos: tuple, player: Player, directions):
        self.pos = pos
        self.player = player
        self.directions = directions

    def set_position(self, _pos: tuple):
        self.pos = _pos

    def get_position(self):
        return self.pos

    def get_player(self):
        return self.player

    def get_legal_moves(self, b: Board):
        col, row = self.pos
        legal_moves = []

        if isinstance(self, King) or isinstance(self, Knight):
            for direction in self.directions:
                new_col = col + direction[0]
                new_row = row + direction[1]
                new_pos = (new_col, new_row)
                if not b.is_within_bounds(new_pos):
                    continue

                if b.is_empty(new_pos):
                    legal_moves.append(new_pos)
                elif b.is_enemy(new_pos, self.player):
                    legal_moves.append(new_pos)

        elif isinstance(self, Queen) or isinstance(self, Bishop) or isinstance(self, Rook):
            for direction in self.directions:
                new_col = col + direction[0]
                new_row = row + direction[1]
                new_pos = (new_col, new_row)

                while b.is_within_bounds(new_pos):
                    if b.is_empty(new_pos):
                        legal_moves.append(new_pos)
                        new_pos = (new_pos[0] + direction[0], new_pos[1] + direction[1])
                    elif b.is_enemy(new_pos, self.player):
                        legal_moves.append(new_pos)
                        break
                    else:
                        break
        print(legal_moves)

        return legal_moves

    def __str__(self):
        return f"Class Piece"


class Pawn(Piece):
    def __init__(self, pos: tuple, player: Player):
        super().__init__(pos, player, -1 if player == Player.WHITE else 1)

    def __str__(self):
        return 'p' if self.player == Player.WHITE else 'P'

    def _get_promotion_cases(self, r):
        return [('q', r), ('r', r), ('n', r), ('b', r)] if self.player == Player.WHITE else \
            [('Q', r), ('R', r), ('N', r), ('B', r)]

    def get_legal_moves(self, b: Board):
        c1, r1 = self.pos
        legal_moves = []
        first = self.player == Player.WHITE and c1 == 6 \
                or self.player == Player.BLACK and c1 == 1
        promotion_line = self.player == Player.WHITE and c1 == 1 \
                         or self.player == Player.BLACK and c1 == 6

        if first:
            for d in range(1, 3):
                temp = (c1 + self.directions * d, r1)
                if b.is_empty(temp):
                    legal_moves.append(temp)
                else:
                    break

        else:
            temp = (c1 + self.directions, r1)
            if b.is_empty(temp):
                if self.is_promotion_line():
                    legal_moves.extend(self._get_promotion_cases(temp[1]))
                else:
                    legal_moves.append(temp)

        for d in [-1, 1]:
            temp = (c1 + self.directions, r1 + d)
            if b.is_within_bounds(temp) and b.is_enemy(temp, self.player):
                if self.is_promotion_line():
                    legal_moves.extend(self._get_promotion_cases(temp[1]))
                else:
                    legal_moves.append(temp)

        if self.enpassant(b):
            _, enpassant_end = self.enpassant(b)
            legal_moves.append(enpassant_end)

        print(legal_moves)

        return legal_moves

    def is_promotion_line(self):
        c1, r1 = self.pos
        return self.player == Player.WHITE and c1 == 1 \
            or self.player == Player.BLACK and c1 == 6

    def enpassant(self, b: Board):
        c, r = self.pos
        if b.previous_move is not None:
            prev_piece, prev_move = b.previous_move
            if isinstance(prev_piece, Pawn):
                prev_c, prev_r = prev_move
                white = self.player == Player.WHITE
                return (white and c == prev_c == 3) or (not white and c == prev_c == 4) \
                       and abs(prev_r - r) == 1, (c + self.directions, prev_r)

        return False


class Knight(Piece):
    def __init__(self, pos: tuple, player: Player):
        super().__init__(pos, player, knight_directions)

    def __str__(self):
        return 'n' if self.player == Player.WHITE else 'N'


class Bishop(Piece):
    def __init__(self, pos: tuple, player: Player):
        super().__init__(pos, player, bishop_directions)

    def __str__(self):
        return 'b' if self.player == Player.WHITE else 'B'


class Rook(Piece):
    def __init__(self, pos: tuple, player: Player):
        super().__init__(pos, player, rook_directions)
        self.move = False  ## 캐슬링

    def __str__(self):
        return 'r' if self.player == Player.WHITE else 'R'


class Queen(Piece):
    def __init__(self, pos: tuple, player: Player):
        super().__init__(pos, player, queen_directions)

    def __str__(self):
        return 'q' if self.player == Player.WHITE else 'Q'


class King(Piece):
    def __init__(self, pos: tuple, player: Player):
        super().__init__(pos, player, king_directions)
        self.move = False  ## 캐슬링

    def __str__(self):
        return 'k' if self.player == Player.WHITE else 'K'

    def get_legal_moves(self, b: Board):
        col, row = self.pos
        legal_moves = super().get_legal_moves(b)

        ##TODO 캐슬링 구현
        can_castling()

        return legal_moves

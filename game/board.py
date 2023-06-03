from constant import *

class Board:
    def __init__(self, board=init_board, turn=Player.WHITE):
        self.size = len(board)
        self.all_pieces = []
        self.king = {Player.WHITE : None, Player.BLACK : None}
        self.board = self.setting_board(board)
        self.turn = turn
        self.previous_move = None
        self.state_castle = 'kqKQ'
        self.turn_count = 2
        self.done = Done.ing
        
    def __str__(self):
        board_str = '-----------------\n'
        for row in self.board:
            board_str += '|'
            for col in row:
                board_str += str(col) + '|' if col else ' |'
            board_str += '\n'
        board_str += '-----------------\n'
        return board_str

    def is_white_move(self):
        return self.turn == Player.WHITE

    def right_turn(self, player):
        return self.turn == player

    def piece_at(self, pos):
        return self.board[pos[0]][pos[1]]

    def opp_color(self):
        return Player.WHITE if self.turn == Player.BLACK else Player.BLACK

    def is_enemy(self, pos, player) -> bool:
        if self.is_empty(pos):
            return False
        return self.board[pos[0]][pos[1]].player != player

    def is_ally(self, pos, player):
        return not self.is_enemy(pos, player) and not self.is_empty(pos)

    def is_occupied(self, pos) -> bool:
        return self.board[pos[0]][pos[1]] is not None

    def is_empty(self, pos) -> bool:
        return self.board[pos[0]][pos[1]] is None

    def is_within_bounds(self, pos):
        return 0 <= pos[0] < self.size and 0 <= pos[1] < self.size

    def find_king(self, color):
        return self.king[color].pos

    def col_SAN(self, c):
        return str(self.size - c)

    @staticmethod
    def row_SAN(r):
        return str(chr(r + ord('a')))

    def get_SAN(self, pos):
        c, r = pos
        return self.col_SAN(c), self.row_SAN(r)

    ## 배열 좌표형식을 uci인지 뭔지 하는 표기법으로 변환
    def convert_sq_uci(self, pos):
        c, r = pos
        return f"{self.row_SAN(r)}{self.col_SAN(c)}"

    def convert_move_uci(self, start, end):
        return f"{self.convert_sq_uci(start)}{self.convert_sq_uci(end)}"

    def _remove_for_castling(self, kq):
        print(self.state_castle.replace(kq, ''))
        return self.state_castle.replace(kq, '') if kq in self.state_castle else self.state_castle

    def setting_board(self, board):
        temp = [[None for _ in range(self.size)] for _ in range(self.size)]

        for i, col in enumerate(board):
            for j, sq in enumerate(col):
                if sq == ' ': continue
                player = Player.WHITE if sq.islower() else Player.BLACK
                sq = sq.lower()
                temp[i][j] = globals()[classname_of_pieces[sq]]((i, j), player)
                self.all_pieces.append(temp[i][j])
                if isinstance(temp[i][j], King):
                    self.king[player] = temp[i][j]

        return temp

    def convert_to_FEN(self):
        fen = ""
        for c in self.board:
            cnt = 0
            for piece in c:
                if isinstance(piece, Piece):
                    fen += f"{cnt}{str(piece)}" if cnt != 0 else str(piece)
                    cnt = 0
                else:
                    cnt += 1

            fen += f"{cnt}/" if cnt != 0 else "/"
        fen = fen[:-1]
        turn = "w" if self.turn == Player.WHITE else "b"
        self.castling_state()
        castle = self.state_castle
        count = str(self.turn_count // 2)
        enp = "-"
        if self.can_enpassant():
            enp = self.can_enpassant()
            enp = self.convert_sq_uci(enp)
            print(enp)

        return " ".join([fen, turn, castle, enp, count])
        # return fen + turn + castle + str(count)

    def castling_state(self):

        if self.state_castle == '-':
            return

        if self.king[Player.BLACK].moved:
            self.state_castle = self._remove_for_castling('K')
            self.state_castle = self._remove_for_castling('Q')
        else:  # 킹이 안움직였으면
            if isinstance(self.board[0][0], Rook):
                if self.board[0][0].moved:
                    self.state_castle = self._remove_for_castling('Q')
            else:
                self.state_castle = self._remove_for_castling('Q')

            if isinstance(self.board[0][7], Rook):
                if self.board[0][7].moved:
                    self.state_castle = self._remove_for_castling('K')

            else:
                self.state_castle = self._remove_for_castling('K')

        if self.king[Player.WHITE].moved:
            self.state_castle = self._remove_for_castling('k')
            self.state_castle = self._remove_for_castling('q')
        else:  # 킹이 안움직였으면
            if isinstance(self.board[7][0], Rook):
                if self.board[7][0].moved:
                    self.state_castle = self._remove_for_castling('q')

            else:
                self.state_castle = self._remove_for_castling('q')

            if isinstance(self.board[7][7], Rook):
                if self.board[7][7].moved:
                    self.state_castle = self._remove_for_castling('k')

            else:
                self.state_castle = self._remove_for_castling('k')

        if len(self.state_castle) == 0:
            self.state_castle = '-'


    def convert_to_SAN(self, start, end):
        c1, r1 = start
        c2, r2 = end
        piece = self.board[c1][r1]
        san = ""
        c1san, r1san = self.get_SAN(start)
        c2san, r2san = self.get_SAN(end)
        start_san = r1san + c1san
        end_san = r2san + c2san

        _take = isinstance(self.board[c2][r2], Piece)

        if not isinstance(piece, Piece):
            print("ERROR")
            exit(-1)

        if isinstance(piece, Pawn):
            san += r1san
            _take = _take or piece.is_enpassant(end, self)

            if _take:
                san += 'x' + end_san
            else:
                san += c2san

        elif isinstance(piece, King):
            if piece.castling(self):
                side = piece.is_castling(start, end)
                if side == -1:
                    return 'O-O-O'
                elif side == 1:
                    return 'O-O'
            san += str(piece)
            san += 'x' + end_san if _take else end_san

        else:
            pass

        return san


    def get_all_moves(self):
        results = {}
        for col in self.board:
            for row in col:
                if isinstance(row, Piece) and self.right_turn(row.player):
                    results[row] = row.get_legal_moves(self)
        return results

    def is_mate(self):
        all_legal_moves = self.get_all_moves()

        for pos in all_legal_moves:
            if not all_legal_moves[pos]:
                continue
            else:
                return False

        return True

    def move(self, start, end):
        c1, r1 = start
        piece = self.board[c1][r1]

        if not self.is_occupied(start):
            # print("아무것도 없는 칸")
            return False
        if piece.player != self.turn:
            # print("플레이어의 기물 X.")
            return False

        if isinstance(piece, Pawn):
            if not self.move_pawn(start, end):
                return False
        else:
            if not self.move_piece(start, end):
                return False

        check = False
        if self.final_check():
            check = True
            print("체크")

        piece.set_position(end)
        self.previous_move = (piece, start, end)
        self.turn = self.opp_color()

        if self.is_mate():
            if check:
                self.done = Done.white if is_white(self.opp_color()) else Done.black
                print(f"체크메이트, {self.opp_color()} 승")
            else:
                self.done = Done.draw
                print("스테일메이트, 무승부")

        self.turn_count += 1

        return True

    def move_pawn(self, start, end):
        c1, r1 = start
        c2, r2 = end
        piece = self.board[c1][r1]

        if not isinstance(piece, Pawn):
            print("error")
            return False

        if end not in piece.get_legal_moves(self):
            # print("가능한 수 X")
            return False


        if piece.is_promotion_line():
            prom_val = c2
            nc = 0 if self.turn == Player.WHITE else 7
            ne = (nc, r2)
            prom_piece = globals()[classname_of_pieces[prom_val]](ne, self.turn)

            self.board[c1][r1] = None
            self.board[nc][r2] = prom_piece
            return True

        if piece.is_enpassant(end, self):
            taked_pos = piece.enpassant(self)
            tc, tr = taked_pos
            tc -= piece.directions

            self.board[c2][r2] = self.board[c1][r1]
            self.board[c1][r1] = None
            self.board[tc][tr] = None

        else:
            self.board[c2][r2] = self.board[c1][r1]
            self.board[c1][r1] = None

        return True

    def move_piece(self, start, end):
        c1, r1 = start
        c2, r2 = end
        piece = self.board[c1][r1]  # 이거는 초기에 말 확인하는거

        ## piece != None 이라는 것을 편집기한테 알려주기위해서
        if not isinstance(piece, Piece):
            print("아무것도 없는 칸")
            return False

        if end not in piece.get_legal_moves(self):
            print("가능한 수 X")
            return False

        ## 캐슬링 움직임 처리
        if isinstance(piece, King):
            _col = 7 if is_white(piece.player) else 0
            ## [룩의 원래 위치, 룩이 갈 위치, 왕이 갈 위치]
            temp = {-1: [0, 3, 2], 1: [7, 5, 6]}

            case = piece.is_castling(start, end)
            ki = 4
            if case != 0:
                ri, rf, kf = temp[case]
                _rook = self.board[_col][ri]
                if not isinstance(_rook, Rook):
                    print("알수없는 오류")
                    return False
                _rook.set_position((_col, rf))
                self.board[_col][rf] = self.board[_col][ri]
                self.board[_col][kf] = self.board[_col][ki]
                self.board[_col][ri] = None
                self.board[_col][ki] = None
                return True

        self.board[c2][r2] = self.board[c1][r1]
        self.board[c1][r1] = None

        return True

    def pre_check(self, start, end):
        c1, r1 = start
        c2, r2 = end
        ini_piece = self.board[c1][r1]
        final_piece = self.board[c2][r2]

        self.board[c1][r1] = None
        self.board[c2][r2] = ini_piece
        k_col, k_row = end if isinstance(ini_piece, King) else self.find_king(self.turn)

        pieces = {
            'n': knight_directions,
            'k': king_directions
        }

        for piece in pieces:
            curr_piece = globals()[classname_of_pieces[piece]]
            for direction in pieces[piece]:
                ct, rt = k_col + direction[0], k_row + direction[1]
                if not self.is_within_bounds((ct, rt)):
                    continue

                if self.is_enemy((ct, rt), self.turn) and isinstance(self.board[ct][rt], curr_piece):
                    self.board[c1][r1] = ini_piece
                    self.board[c2][r2] = final_piece
                    return True

        pawn_directions = [(-1, -1), (-1, 1)] if self.turn == Player.WHITE else [(1, 1), (1, -1)]

        for direction in pawn_directions:
            ct, rt = k_col + direction[0], k_row + direction[1]
            if not self.is_within_bounds((ct, rt)):
                continue

            if self.is_enemy((ct, rt), self.turn) and isinstance(self.board[ct][rt], Pawn):
                self.board[c1][r1] = ini_piece
                self.board[c2][r2] = final_piece
                return True

        pieces = {
            'b': bishop_directions,
            'r': rook_directions,
            'q': queen_directions
        }

        for piece in pieces:
            curr_piece = globals()[classname_of_pieces[piece]]
            for direction in pieces[piece]:
                ct, rt = k_col + direction[0], k_row + direction[1]
                while self.is_within_bounds((ct, rt)):
                    if self.is_enemy((ct, rt), self.turn) and isinstance(self.board[ct][rt], curr_piece):
                        self.board[c1][r1] = ini_piece
                        self.board[c2][r2] = final_piece
                        return True

                    if not self.is_empty((ct, rt)):
                        break

                    ct, rt = ct + direction[0], rt + direction[1]

        self.board[c1][r1] = ini_piece
        self.board[c2][r2] = final_piece
        return False

    def final_check(self):
        _color = self.opp_color()
        opk_col, opk_row = self.find_king(_color)

        pieces = {
            'b': bishop_directions,
            'r': rook_directions,
            'q': queen_directions,
        }

        for direction in knight_directions:
            ct, rt = opk_col + direction[0], opk_row + direction[1]
            if not self.is_within_bounds((ct, rt)):
                continue

            if self.is_enemy((ct, rt), _color) and isinstance(self.board[ct][rt], Knight):
                return True

        pawn_directions = [(-1, -1), (-1, 1)] if self.turn == Player.BLACK else [(1, 1), (1, -1)]

        for direction in pawn_directions:
            ct, rt = opk_col + direction[0], opk_row + direction[1]
            if not self.is_within_bounds((ct, rt)):
                continue

            if self.is_enemy((ct, rt), _color) and isinstance(self.board[ct][rt], Pawn):
                return True

        # 움직인 말이 비숍, 룩, 퀸인 경우 또는 움직인 말에 의해 생성된 경로에 이 좌표가 있으면 check

        for piece in pieces:
            curr_piece = globals()[classname_of_pieces[piece]]
            for direction in pieces[piece]:
                ct, rt = opk_col + direction[0], opk_row + direction[1]
                while self.is_within_bounds((ct, rt)):
                    if self.is_enemy((ct, rt), _color) and isinstance(self.board[ct][rt], curr_piece):
                        return True
                    if not self.is_empty((ct, rt)):
                        break

                    ct, rt = ct + direction[0], rt + direction[1]

        return False

    def can_enpassant(self):
        if self.previous_move is None:
            return False
        piece, start, end = self.previous_move
        if not isinstance(piece, Pawn):
            return False
        sc, sr = start
        ec, er = end

        if abs(sc - ec) == 2:
            return (2, sr) if self.is_white_move() else (5, sr)

        return False


def get_classname(piece):
    return classname_of_pieces[piece.lower()]

def is_white(player):
    return player == Player.WHITE


class Piece:
    def __init__(self, pos: tuple, player: Player, directions):
        self.pos = pos
        self.came_from = pos
        self.player = player
        self.directions = directions
        self.moved = False

    def set_position(self, _pos: tuple):
        self.pos = _pos
        self.moved = True

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

                if b.is_ally(new_pos, self.player):
                    continue

                if b.pre_check(self.pos, new_pos):
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
                    if b.is_ally(new_pos, self.player):
                        break

                    if b.pre_check(self.pos, new_pos):
                        new_pos = (new_pos[0] + direction[0], new_pos[1] + direction[1])
                        continue

                    if b.is_empty(new_pos):
                        legal_moves.append(new_pos)
                        new_pos = (new_pos[0] + direction[0], new_pos[1] + direction[1])
                    elif b.is_enemy(new_pos, self.player):
                        legal_moves.append(new_pos)
                        break
                    else:
                        break

        return legal_moves

    def __str__(self):
        return f"Class Piece"


class Pawn(Piece):
    def __init__(self, pos: tuple, player: Player):
        super().__init__(pos, player, -1 if is_white(player) else 1)

    def __str__(self):
        return 'p' if is_white(self.player) else 'P'

    def _get_promotion_cases(self, r):
        return [('q', r), ('r', r), ('n', r), ('b', r)] if is_white(self.player) else \
            [('Q', r), ('R', r), ('N', r), ('B', r)]

    def get_legal_moves(self, b: Board):
        c1, r1 = self.pos
        legal_moves = []
        first = self.player == Player.WHITE and c1 == 6 \
                or self.player == Player.BLACK and c1 == 1

        if first:
            for d in range(1, 3):
                temp = (c1 + self.directions * d, r1)
                if b.is_empty(temp) and not b.pre_check(self.pos, temp):
                    legal_moves.append(temp)
                else:
                    break

        else:
            temp = (c1 + self.directions, r1)
            if b.is_empty(temp) and not b.pre_check(self.pos, temp):
                if self.is_promotion_line():
                    legal_moves.extend(self._get_promotion_cases(temp[1]))
                else:
                    legal_moves.append(temp)

        for d in [-1, 1]:
            temp = (c1 + self.directions, r1 + d)
            if not b.is_within_bounds(temp):
                continue
            if not b.is_ally(temp, self.player) and b.pre_check(self.pos, temp):
                continue

            if b.is_within_bounds(temp) and b.is_enemy(temp, self.player):
                if self.is_promotion_line():
                    legal_moves.extend(self._get_promotion_cases(temp[1]))
                else:
                    legal_moves.append(temp)

        enpassant_end = self.enpassant(b)
        if enpassant_end:
            if not b.pre_check(self.pos, enpassant_end):
                legal_moves.append(enpassant_end)

        return legal_moves

    def is_promotion_line(self):
        c, r = self.pos
        return self.player == Player.WHITE and c == 1 \
               or self.player == Player.BLACK and c == 6

    def enpassant(self, b: Board):
        c, r = self.pos

        if b.previous_move:
            prev_piece, prev_start, prev_end = b.previous_move
            if isinstance(prev_piece, Pawn):
                prev_c1, prev_r1 = prev_start
                prev_c2, prev_r2 = prev_end
                white = is_white(self.player)

                if white and prev_c1 == 1 and prev_c2 == 3 and c == 3 and abs(prev_r2 - r) == 1:
                    return c + self.directions, prev_r2
                elif prev_c1 == 6 and prev_c2 == 4 and c == 4 and abs(prev_r2 - r) == 1:
                    return c + self.directions, prev_r2

    def is_enpassant(self, end, b: Board):
        c2, r2 = end

        if b.previous_move:
            prev_piece, prev_start, prev_end = b.previous_move
            if isinstance(prev_piece, Pawn):
                prev_c2, prev_r2 = prev_end

                return self.enpassant(b) and prev_r2 == r2

        return False


class Knight(Piece):
    def __init__(self, pos: tuple, player: Player):
        super().__init__(pos, player, knight_directions)

    def __str__(self):
        return 'n' if is_white(self.player) else 'N'


class Bishop(Piece):
    def __init__(self, pos: tuple, player: Player):
        super().__init__(pos, player, bishop_directions)

    def __str__(self):
        return 'b' if is_white(self.player) else 'B'


class Rook(Piece):
    def __init__(self, pos: tuple, player: Player):
        super().__init__(pos, player, rook_directions)

    def __str__(self):
        return 'r' if is_white(self.player) else 'R'


class Queen(Piece):
    def __init__(self, pos: tuple, player: Player):
        super().__init__(pos, player, queen_directions)

    def __str__(self):
        return 'q' if is_white(self.player) else 'Q'


class King(Piece):
    def __init__(self, pos: tuple, player: Player):
        super().__init__(pos, player, king_directions)

    def __str__(self):
        return 'k' if is_white(self.player) else 'K'

    def get_legal_moves(self, b: Board):
        col, row = self.pos
        legal_moves = super().get_legal_moves(b)

        castle = self.castling(b)
        if castle:
            legal_moves.extend(castle)

        return legal_moves

    def castling(self, b: Board):
        _col = 7 if is_white(self.player) else 0
        if self.moved or self.pos != (_col, 4):
            return False

        info = {0: (2, [4, 3, 2]), 7: (6, [4, 5, 6])}
        results = []

        for i in info:
            rook = b.board[_col][i]
            _row = info[i][0]
            way = info[i][1]
            if isinstance(rook, Rook):
                if not rook.moved:
                    can = True
                    for row in way:
                        temp = (_col, row)
                        if not b.is_empty(temp) and temp != self.pos:
                            can = False
                            break
                        if b.pre_check(self.pos, temp):
                            can = False
                            break
                    if i == 0 and not b.is_empty((_col, 1)):
                        can = False
                    if can:
                        results.append((_col, _row))

        return results

    ## -1: left / 0: castling X / 1: right
    ## 캐슬링이 가능한 경우인지 이미 확인한 후에, 고른 움직임이 캐슬링인지 확인하는 메소드
    def is_castling(self, start, end):
        _col = 7 if is_white(self.player) else 0
        if start == (_col, 4) and end == (_col, 2):
            return -1
        if start == (_col, 4) and end == (_col, 6):
            return 1

        return 0


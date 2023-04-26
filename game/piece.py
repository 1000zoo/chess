from constant import *
from board import Board


##TODO 모든 움직임에 대해서 체크 확인

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
                elif b.is_enemy(self.pos, self.player):
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

        return legal_moves

    def __str__(self):
        return f"Class Piece"


class Pawn(Piece):
    def __init__(self, pos: tuple, player: Player):
        super().__init__(pos, player, -1 if player == Player.WHITE else 1)

    def __str__(self):
        return 'p' if self.player == Player.WHITE else 'P'

    def _promotion(self, r):
        return [('q', r), ('r', r), ('n', r), ('b', r)] if self.player == Player.WHITE else \
                [('Q', r), ('R', r), ('N', r), ('B', r)]

    def get_legal_moves(self, b: Board):
        c1, r1 = self.pos
        legal_moves = []
        first = self.player == Player.WHITE and c1 == 6 \
                   or self.player ==Player.BLACK and c1 == 1
        promotion_line = self.player == Player.WHITE and c1 == 1 \
                         or self.player == Player.BLACK and c1 == 6

        if first:
            for d in range(1,3):
                temp = (c1 + self.directions * d, r1)
                if b.is_empty(temp):
                    legal_moves.append(temp)
                else:
                    break

        else:
            temp = (c1 + self.directions, r1)
            if b.is_empty(temp):
                legal_moves.append(temp)
                if promotion_line:
                    legal_moves.extend(self._promotion(temp[1]))
                else:
                    legal_moves.append(temp)

        for d in [-1, 1]:
            temp = (c1 + self.directions, r1 + d)
            if b.is_within_bounds(temp) and b.is_enemy(temp, self.player):
                if promotion_line:
                    legal_moves.extend(self._promotion(temp[1]))
                else:
                    legal_moves.append(temp)

        ## 앙파상
        prev_piece, prev_move = b.previous_move
        if isinstance(prev_piece, Pawn):
            prev_c, prev_r = prev_move
            if prev_c == c1 and abs(prev_r - r1) == 1:
                legal_moves.append((c1 + self.directions, prev_r))
                # move에 앙파상으로 잡았다는 것을 어떻게 알릴 것인지

        return legal_moves

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

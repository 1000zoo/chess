import constant as c
from constant import Player
from board import Board


##TODO 모든 움직임에 대해서 체크 확인

def get_classname(piece):
    return c.classname_of_pieces[piece.lower()]


class Piece:
    ##player: boolean -> true=white / false=black
    def __init__(self, pos: tuple, player: Player):
        self.pos = pos
        self.player = player

    def set_position(self, _pos: tuple):
        self.pos = _pos

    def get_position(self):
        return self.pos

    def get_player(self):
        return self.player

    def __str__(self):
        return f"Class Piece"


class Pawn(Piece):
    def __init__(self, pos: tuple, player: Player):
        super().__init__(pos, player)

    def __str__(self):
        return 'p' if self.player == Player.WHITE else 'P'

    def get_legal_moves(self):
        """
        TODO 폰움직임 앙파상 프로모션 구현
        """
        pass


class Knight(Piece):
    def __init__(self, pos: tuple, player: Player):
        super().__init__(pos, player)
        self.directions = c.knight_directions

    def __str__(self):
        return 'n' if self.player == Player.WHITE else 'N'

    def get_legal_moves(self, board: Board):
        col, row = self.pos
        legal_moves = []  ##((col, row), take) => take: bool 잡았다 못잡았다.

        for direction in self.directions:
            new_col = col + direction[0]
            new_row = row + direction[1]
            new_pos = (new_col, new_row)
            if not board.is_within_bounds(new_pos):
                continue

            if board.is_empty(new_pos):
                legal_moves.append((new_pos, False))
            elif board.is_enemy(self.pos, self.player):
                legal_moves.append((new_pos, True))

        return legal_moves


class Bishop(Piece):
    def __init__(self, pos: tuple, player: Player):
        super().__init__(pos, player)
        self.directions = c.bishop_directions

    def __str__(self):
        return 'b' if self.player == Player.WHITE else 'B'

    def get_legal_moves(self, board: Board):
        col, row = self.pos
        legal_moves = []  ##((col, row), take) => take: bool 잡았다 못잡았다.

        for direction in self.directions:
            new_col = col + direction[0]
            new_row = row + direction[1]
            new_pos = (new_col, new_row)

            while board.is_within_bounds(new_pos):
                if board.is_empty(new_pos):
                    legal_moves.append((new_pos, False))
                    new_pos = (new_pos[0] + direction[0], new_pos[1] + direction[1])
                elif board.is_enemy(new_pos, self.player):
                    legal_moves.append((new_pos, True))
                    break
                else:
                    break

        return legal_moves


class Rook(Piece):
    def __init__(self, pos: tuple, player: Player):
        super().__init__(pos, player)
        self.directions = c.rook_directions
        self.move = False  ## 캐슬링

    def __str__(self):
        return 'r' if self.player == Player.WHITE else 'R'

    def get_legal_moves(self, board: Board):
        col, row = self.pos
        legal_moves = []  ##((col, row), take) => take: bool 잡았다 못잡았다.

        for direction in self.directions:
            new_col = col + direction[0]
            new_row = row + direction[1]
            new_pos = (new_col, new_row)

            while board.is_within_bounds(new_pos):
                if board.is_empty(new_pos):
                    legal_moves.append((new_pos, False))
                    new_pos = (new_pos[0] + direction[0], new_pos[1] + direction[1])
                elif board.is_enemy(new_pos, self.player):
                    legal_moves.append((new_pos, True))
                    break
                else:
                    break

        return legal_moves


class Queen(Piece):
    def __init__(self, pos: tuple, player: Player):
        super().__init__(pos, player)
        self.directions = c.queen_directions

    def __str__(self):
        return 'q' if self.player == Player.WHITE else 'Q'

    def get_legal_moves(self, board: Board):
        col, row = self.pos
        legal_moves = []  ##((col, row), take) => take: bool 잡았다 못잡았다.

        for direction in self.directions:
            new_col = col + direction[0]
            new_row = row + direction[1]
            new_pos = (new_col, new_row)

            while board.is_within_bounds(new_pos):
                if board.is_empty(new_pos):
                    legal_moves.append((new_pos, False))
                    new_pos = (new_pos[0] + direction[0], new_pos[1] + direction[1])
                elif board.is_enemy(new_pos, self.player):
                    legal_moves.append((new_pos, True))
                    break
                else:
                    break

        return legal_moves


##TODO 캐슬링 구현
class King(Piece):
    def __init__(self, pos: tuple, player: Player):
        super().__init__(pos, player)
        self.directions = c.king_directions
        self.move = False  ## 캐슬링

    def __str__(self):
        return 'k' if self.player == Player.WHITE else 'K'

    def get_legal_moves(self, board: Board):
        col, row = self.pos
        legal_moves = []  ##((col, row), take) => take: bool 잡았다 못잡았다.

        for direction in self.directions:
            new_col = col + direction[0]
            new_row = row + direction[1]
            new_pos = (new_col, new_row)

            if not board.is_within_bounds(new_pos):
                continue

            if board.is_empty(new_pos):
                legal_moves.append((new_pos, False))
            elif board.is_enemy(new_pos, self.player):
                legal_moves.append((new_pos, True))

        return legal_moves

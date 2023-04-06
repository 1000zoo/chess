import constant as c
from constant import Player


def get_classname(piece):
    return c.classname_of_pieces[piece.lower()]

"""
color: boolean -> true=white / false=black
"""
class Piece:
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




class Knight(Piece):
    def __init__(self, pos: tuple, player: Player):
        super().__init__(pos, player)

    def __str__(self):
        return 'n' if self.player == Player.WHITE else 'N'


class Bishop(Piece):
    def __init__(self, pos: tuple, player: Player):
        super().__init__(pos, player)

    def __str__(self):
        return 'p' if self.player == Player.WHITE else 'P'


class Rook(Piece):
    def __init__(self, pos: tuple, player: Player):
        super().__init__(pos, player)
        self.move = False   ## 캐슬링

    def __str__(self):
        return 'r' if self.player == Player.WHITE else 'R'


class Queen(Piece):
    def __init__(self, pos: tuple, player: Player):
        super().__init__(pos, player)

    def __str__(self):
        return 'q' if self.player == Player.WHITE else 'Q'


class King(Piece):
    def __init__(self, pos: tuple, player: Player):
        super().__init__(pos, player)
        self.move = False   ## 캐슬링

    def __str__(self):
        return 'k' if self.player == Player.WHITE else 'K'

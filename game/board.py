import constant as c
from constant import Player
import piece as p
from enum import Enum


class Board:
    def __init__(self, board=c.board, turn=Player.WHITE):
        self.player = None
        self.size = len(board)
        self.board = self.setting_board(board)
        self.turn = turn

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
                temp[i][j] = getattr(p, p.get_classname(sq))((i, j), player)

        return temp

    def is_enemy(self, pos, player) -> bool:
        if self.is_empty(pos):
            return False
        return self.board[pos[0]][pos[1]].player != player

    def is_occupied(self, pos) -> bool:
        return self.board[pos[0]][pos[1]] is not None

    def is_empty(self, pos) -> bool:
        return self.board[pos[0]][pos[1]] is None

    ## 위치관련 조건문에 항상 맨 앞에 있어야댐
    def is_within_bounds(self, pos):
        return 0 <= pos[0] < self.size and 0 <= pos[1] < self.size


    ##TODO 움직이면 board 변경
    def move_piece(self, start, end):
        c1, r1 = start
        c2, r2 = end
        piece = self.board[c1][r1] #이거는 초기에 말 확인하는거

        if not self.is_occupied(self.board):
            return

        if not isinstance(piece, p.Piece):
            print("not piece")
            return

        if piece.player != self.turn:
            return

        if end not in piece.get_legal_moves(self):
            return

        self.board[c2][r2] = self.board[c1][r1]
        self.board[c1][r1] = None

        self.turn = Player.WHITE if self.player == Player.BLACK else Player.BLACK
if __name__ == "__main__":
    b = Board()
    print(b)
    print(b.board[0][4].get_legal_moves(b))

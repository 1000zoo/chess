from board import *
from constant import Player

if __name__ == '__main__':
    b = Board(turn=Player.WHITE)
    print(b)
    while True:
        print(b.turn)
        _s = tuple(map(lambda x: int(x), input("start:")))
        p = b.board[_s[0]][_s[1]]
        if isinstance(p, Piece):
            p.get_legal_moves(b)
        _e = tuple(map(lambda x: int(x), input("end:")))
        _wrong_input = False

        if len(_s) != 2 and len(_e) != 2:
            print("잘못된 입력")
            continue

        if _wrong_input:
            continue

        b.move(_s, _e)
        print(b)

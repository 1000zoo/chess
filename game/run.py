from board import *
from constant import Player

if __name__ == '__main__':
    b = Board()
    print(b)
    while True:
        print(b.turn)
        _s = tuple(map(lambda x: int(x), input("start:")))
        p = b.board[_s[0]][_s[1]]
        print(p)
        if isinstance(p, Piece):
            p.get_legal_moves(b)
        else:
            print("빈 칸 입니다.")
            continue

        _e = tuple(map(lambda x: int(x), input("end:")))

        if (_s[0] == 1 and b.turn == Player.WHITE)\
            or (_s[0] == 6 and b.turn == Player.BLACK):
            prom = input("promotion to (qrbn) => ")
            _e = (prom, _e[1])
            pass

        _wrong_input = False

        if len(_s) != 2 and len(_e) != 2:
            print("잘못된 입력")
            continue

        if _wrong_input:
            continue

        b.move(_s, _e)
        print(b)

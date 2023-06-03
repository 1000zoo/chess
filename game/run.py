from board import *
from constant import Player

if __name__ == '__main__':
    b = Board()
    while True:
        print(b)
        print(b.turn)
        try:
            _s = tuple(map(lambda x: int(x), input("start:")))
            if len(_s) != 2:
                print("잘못된 입력입니다.")
                continue

        except ValueError as e:
            print("잘못된 입력입니다.")
            continue

        p = b.board[_s[0]][_s[1]]
        if isinstance(p, Piece):
            if p.player != b.turn:
                print("선택한 기물의 턴이 아닙니다.")
                continue
            print(p.get_legal_moves(b))
        else:
            print("빈 칸 입니다.")
            continue
        try:
            _e = tuple(map(lambda x: int(x), input("end:")))
            if len(_e) != 2:
                print("잘못된 입력입니다.")
                continue

        except ValueError as e:
            print("잘못된 입력입니다.")
            continue

        if ((_s[0] == 1 and b.turn == Player.WHITE)
            or (_s[0] == 6 and b.turn == Player.BLACK)) and isinstance(p, Pawn):
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
        print(b.convert_to_FEN())
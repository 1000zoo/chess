from board import *

if __name__ == '__main__':
    b = Board()
    print(b)
    while True:
        print(b.turn)
        _s = tuple(map(lambda x: int(x), input("start:")))
        _e = tuple(map(lambda x: int(x), input("end:")))
        _wrong_input = False

        if len(_s) != 2 and len(_e) != 2:
            print("잘못된 입력")
            continue

        if _wrong_input:
            continue

        b.move_piece(_s, _e)
        print(b)

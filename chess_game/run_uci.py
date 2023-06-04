from board import *
from constants.constant import *

if __name__ == '__main__':
    b = Board()
    while not b.done:
        print(b)
        print(b.convert_to_FEN())
        print(b.get_all_moves())

        action = input("uci-> ")
        b.push_uci(action)

    print(b.winner)
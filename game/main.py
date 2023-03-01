

class Piece:
    def __init__(self, p_type, color):
        self.p_type = p_type
        self.color = color
        self.possible_move = []
        self.price = 0

class Board:
    def __init__(self, size = 8):
        self._size = size
        self.board = [['R', 'N', 'B', 'Q', 'K', 'B', 'N', 'R'],
                      ['P', 'P', 'P', 'P', 'P', 'P', 'P', 'P'],
                      [' ', ' ', ' ', ' ', ' ', ' ', ' ', ' '],
                      [' ', ' ', ' ', ' ', ' ', ' ', ' ', ' '],
                      [' ', ' ', ' ', ' ', ' ', ' ', ' ', ' '],
                      [' ', ' ', ' ', ' ', ' ', ' ', ' ', ' '],
                      ['p', 'p', 'p', 'p', 'p', 'p', 'p', 'p'],
                      ['r', 'n', 'b', 'q', 'k', 'b', 'n', 'r']]
        self.turn = 'white'
        self.move_history = []
        self.piece_pos = {
            'r' : [],
            'n' : [],
            'b' : [],
            'q' : [],
            'k' : [],
            'p' : [],
        }

    def __str__(self):
        board_str = '-----------------\n'
        for row in self.board:
            board_str += '|'
            for col in row:
                board_str += col + '|'
            board_str += '\n'
        board_str += '-----------------\n'
        return board_str

    def board_to_array(self, pos : str) -> tuple:
        row = ord(pos[0]) - ord('a')
        col = self._size - int(pos[1])
        return col, row

    def col_process(self, c):
        return str(self._size - c)

    @staticmethod
    def row_process(r):
        return str(chr(r + ord('a')))

    def array_to_board(self, start, end, take, promotion, sameline, check, mate):
        c1, r1 = start
        c2, r2 = end
        piece = self.board[c1][r1].upper()

        if piece == 'P':
            ret = self.row_process(r1)
            if take:
                ret += 'x' + self.row_process(r2) + self.col_process(c2)
            else:
                ret += self.col_process(c2)

            if promotion != '':
                ret += '=Q'

        else:
            ret = piece
            if take:
                ret += 'x' + self.row_process(r2) + self.col_process(c2)
            else:
                ret += self.row_process(r2) + self.col_process(c2)
            # TODO 룩이나 나이트, 프로모션 한 퀸, 비숍이 같은 목적지를 향할 경우 처리해야함
            # if sameline:
            #     pass
        if check:
            ret += '+'

        if mate:
            ret += '#'

        self.move_history.append(ret)

    def move(self, start, end):
        # c1, r1 = self.board_to_array(start)
        # c2, r2 = self.board_to_array(end)
        c1, r1 = start
        c2, r2 = end
        piece = self.board[c1][r1]
        _take = False
        _promotion = ''
        _sameline = False
        _check = False
        _mate = False

        if piece == ' ':
            print("No piece in start position.")
            return

        if (self.turn == 'white' and piece.isupper()) or (self.turn == 'black' and piece.islower()):
            print("Not your piece")
            return

        if start == end:
            return

        if self.board[c2][r2] != ' ':
            _take = True

        if piece.islower() == 'p' and (self.turn == 'white' and r2 == 0 or self.turn == 'black' and r2 == 7):
            _promotion = 'q' if self.turn == 'white' else 'Q'

        self.array_to_board(start, end, _take, _promotion, _sameline, _check, _mate)
        self.board[c1][r1] = ' '
        self.board[c2][r2] = piece
        self.turn = 'white' if self.turn == 'black' else 'black'
        print(self)


if __name__ == '__main__':
    b = Board()
    b.move((6,3), (4,3))
    b.move((1,4), (3,4))
    b.move((4,3), (3,4))
    b.move((0,1), (2,2))
    b.move((7,6), (5,5))
    b.move((2,2), (3,4))
    print(b.move_history)
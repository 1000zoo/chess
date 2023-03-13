import constant as c

class Board:
    def __init__(self, board = c.board):
        self.board = board
        self._size = 8
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
                ret += '=' + promotion.upper()

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
        if not (self.check_boundary(start) and self.check_boundary(end)):
            print("wrong input")
            return
        c1, r1 = start
        c2, r2 = end
        piece = self.board[c1][r1]
        _take = False
        _promotion = ''
        _sameline = False
        _check = False
        _mate = False

        if start == end:
            return

        if piece == ' ':
            print("No piece in start position.")
            return

        if (self.turn == 'white' and piece.isupper()) or (self.turn == 'black' and piece.islower()):
            print("Not your piece")
            return

        if not self.check_legal_move(start, end):
            print("it's legal move")
            return

        if self.board[c2][r2] != ' ':
            _take = True

        if piece.lower() == 'p' and (self.turn == 'white' and c2 == 0 or self.turn == 'black' and c2 == 7):
            prom = input("promotion to: ").lower()
            while not self.check_promotion(prom):
                print("wrong input")
                prom = input("promotion to: ").lower()
            _promotion = prom
            piece = prom if self.turn == 'white' else prom.upper()

        self.array_to_board(start, end, _take, _promotion, _sameline, _check, _mate)
        self.board[c1][r1] = ' '
        self.board[c2][r2] = piece
        self.turn = 'white' if self.turn == 'black' else 'black'
        print(self)

    @staticmethod
    def check_promotion(prom):
        return prom == 'r' or prom == 'q' or prom == 'b' or prom == 'n'

    def check_legal_move(self, start, end):
        c1, r1 = start
        c2, r2 = end
        piece = self.board[c1][r1].lower()

        if piece== 'p':
            return (c2, r2) in self.pawn_moves(start)

        elif piece == 'n':
            return (c2, r2) in self.knight_move(start)

        elif piece == 'k':
            return (c2, r2) in self.king_move(start)

        elif piece == 'b':
            return (c2, r2) in self.bishop_move(start)

        elif piece == 'r':
            return (c2, r2) in self.rook_move(start)

        elif piece == 'q':
            return (c2, r2) in self.queen_move(start)

        else:
            return False

        ## R B N Q K 추가

    def pawn_moves(self, start):
        c1, r1 = start
        piece = self.board[c1][r1]
        possible_moves = []

        if piece.islower():
            if c1 == 6:
                if self.isEmptySpace((c1 - 1, r1)):
                    possible_moves.append((c1 - 1, r1))
                    if self.isEmptySpace((c1 - 2, r1)):
                        possible_moves.append((c1 - 2, r1))
            else:
                if self.isEmptySpace((c1 - 1, r1)):
                    possible_moves.append((c1 - 1, r1))
            if not self.isEmptySpace((c1 - 1, r1 - 1)) and self.isEnemy(start, (c1 - 1, r1 - 1)):
                possible_moves.append((c1 - 1, r1 - 1))
            if not self.isEmptySpace((c1 - 1, r1 + 1)) and self.isEnemy(start, (c1 - 1, r1 + 1)):
                possible_moves.append((c1 - 1, r1 + 1))

        else:
            if c1 == 1:
                if self.isEmptySpace((c1 + 1, r1)):
                    possible_moves.append((c1 + 1, r1))
                if self.isEmptySpace((c1 + 2, r1)):
                    possible_moves.append((c1 + 2, r1))
            if self.isEmptySpace((c1 + 1, r1)):
                possible_moves.append((c1 + 1, r1))
            if not self.isEmptySpace((c1 + 1, r1 - 1)) and self.isEnemy(start, (c1 + 1, r1 - 1)):
                possible_moves.append((c1 + 1, r1 - 1))
            if not self.isEmptySpace((c1 + 1, r1 + 1)) and self.isEnemy(start, (c1 + 1, r1 + 1)):
                possible_moves.append((c1 + 1, r1 + 1))

        return possible_moves

    def knight_move(self, start):
        c1, r1 = start
        directions = [(2,1), (1,2), (-2,1), (-1,2), (2,-1), (1,-2), (-2,-1),(-1,-2)]
        possible_moves = []

        for direction in directions:
            c2 = c1 + direction[0]
            r2 = r1 + direction[1]
            pos = (c2, r2)
            if self.isEmptySpace(pos) or self.isEnemy(start, pos):
                possible_moves.append(pos)

        return possible_moves

    def king_move(self, start):
        c1, r1 = start
        directions = [(1,1), (1,-1), (-1,1), (-1,-1), (1,0), (-1,0), (0,1), (0,-1)]
        possible_moves = []

        for direction in directions:
            c2 = c1 + direction[0]
            r2 = r1 + direction[1]
            pos = (c2, r2)
            if self.isEmptySpace(pos) or self.isEnemy(start, pos):
                possible_moves.append(pos)

        return possible_moves

    def bishop_move(self, start):
        c1, r1 = start
        directions = [(1,1), (1,-1), (-1,1), (-1,-1)]
        possible_moves = []

        for direction in directions:
            current = (c1 + direction[0], r1 + direction[1])

            while self.check_boundary(current):
                if self.isEmptySpace(current) or self.isEnemy(start, current):
                    possible_moves.append(current)
                    current = (current[0] + direction[0], current[1] + direction[1])
                else:
                    break

        return possible_moves

    def rook_move(self, start):
        c1, r1 = start
        directions = [(1,0), (0,1), (-1,0), (0,-1)]
        possible_moves = []

        for direction in directions:
            current = (c1 + direction[0], r1 + direction[1])

            while self.check_boundary(current):
                if self.isEmptySpace(current) or self.isEnemy(start, current):
                    possible_moves.append(current)
                    current = (current[0] + direction[0], current[1] + direction[1])
                else:
                    break

        return possible_moves

    def queen_move(self, start):
        c1, r1 = start
        directions = [(1,0), (0,1), (-1,0), (0,-1), (1,1), (1,-1), (-1,1), (-1,-1)]
        possible_moves = []

        for direction in directions:
            current = (c1 + direction[0], r1 + direction[1])

            while self.check_boundary(current):
                if self.isEmptySpace(current) or self.isEnemy(start, current):
                    possible_moves.append(current)
                    current = (current[0] + direction[0], current[1] + direction[1])
                else:
                    break

        return possible_moves


    def check_boundary(self, pos):
        return 0 <= pos[0] < self._size and 0 <= pos[1] < self._size

    def isEmptySpace(self, pos):
        return self.check_boundary(pos) and self.board[pos[0]][pos[1]] == ' '

    def isEnemy(self, start, end):
        c1, r1 = start
        c2, r2 = end
        return self.check_boundary(end) and self.board[c1][r1].islower() ^ self.board[c2][r2].islower()



if __name__ == '__main__':
    _board = [['R', ' ', 'B', 'Q', 'K', 'B', 'N', 'R'],
              [' ', 'p', ' ', 'P', 'P', 'P', 'P', 'P'],
              ['N', ' ', 'P', ' ', ' ', ' ', ' ', ' '],
              ['P', ' ', ' ', ' ', ' ', ' ', ' ', ' '],
              [' ', ' ', ' ', ' ', ' ', ' ', ' ', ' '],
              [' ', ' ', ' ', ' ', ' ', ' ', ' ', ' '],
              ['p', ' ', 'p', 'p', 'p', 'p', 'p', 'p'],
              ['r', 'n', 'b', 'q', 'k', 'b', 'n', 'r']
              ]
    b = Board(_board)
    print(b)
    while True:
        _s = tuple(map(lambda x: int(x), input("start:")))
        _e = tuple(map(lambda x: int(x), input("end:")))
        _wrong_input = False

        if len(_s) != 2 and len(_e) != 2:
            print("잘못된 입력")
            continue

        if _wrong_input:
            continue

        b.move(_s, _e)
        print(b.move_history)
    # b.move((1,5),(2,5))


import constant as c

class Board:
    def __init__(self, board = c.board, turn = 'white'):
        self.board = board
        self.size = len(board)
        self.turn = turn
        self.move_history = []
        self.current_pos = {}
        self.legal_moves = {
            'r' : [],
            'n' : [],
            'b' : [],
            'q' : [],
            'k' : [],
            'p' : [],
        }
        self.set_current_pos()
        self.pre_move = None

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
        col = self.size - int(pos[1])
        return col, row

    def col_process(self, c):
        return str(self.size - c)

    @staticmethod
    def row_process(r):
        return str(chr(r + ord('a')))

    def reset_current_pos(self):
        self.current_pos = {'white': {'p': [],'n': [],'b': [],'r': [],'q': [],'k': []},
                            'black': {'p': [],'n': [],'b': [],'r': [],'q': [],'k': []}}

    def set_current_pos(self):
        self.reset_current_pos()
        for i, col in enumerate(self.board):
            for j, row in enumerate(col):
                piece = row
                if piece != ' ':
                    turn = 'white' if piece.islower() else 'black'
                    self.current_pos[turn][piece.lower()].append((i, j))


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

        if not self.is_legal_move(start, end):
            print("it's legal move")
            return

        ##TODO 앙파상의 경우 _take 처리

        ## 체크인지 확인하기 위해 일시적으로 말 이동
        self.board[c1][r1] = ' '
        temp = self.board[c2][r2]
        self.board[c2][r2] = piece
        if not self.is_king_safe(self.turn):
            print("King is not safe")
            self.board[c1][r1] = piece
            self.board[c2][r2] = ' '
            return

        self.board[c1][r1] = piece
        self.board[c2][r2] = temp

        if self.board[c2][r2] != ' ':
            _take = True

        if piece.lower() == 'p' and (self.turn == 'white' and c2 == 0 or self.turn == 'black' and c2 == 7):
            prom = input("promotion to: ").lower()
            while not self.check_promotion(prom):
                print("wrong input")
                prom = input("promotion to: ").lower()
            _promotion = prom
            piece = prom if self.turn == 'white' else prom.upper()

        _check = not self.is_king_safe('black' if self.turn == 'white' else 'white')

        self.array_to_board(start, end, _take, _promotion, _sameline, _check, _mate)
        self.board[c1][r1] = ' '
        self.board[c2][r2] = piece
        self.pre_move = (start, end)
        self.set_current_pos()
        self.turn = 'white' if self.turn == 'black' else 'black'
        print(self)

    @staticmethod
    def check_promotion(prom):
        return prom == 'r' or prom == 'q' or prom == 'b' or prom == 'n'

    def is_king_safe(self, color):
        k_col, k_row = self.current_pos[color]['k'][0]
        pieces = {
            'b' : c.bishop_directions,
            'r' : c.rook_directions,
            'q' : c.queen_directions
        }
        ## 폰의 경우
        pawn_case = [(-1, 1), (-1, -1)] if color == 'white' else [(1, -1), (1, 1)]

        opp = 'P' if color == 'white' else 'p'
        for move in pawn_case:
            ct, rt = k_col + move[0], k_row + move[1]
            if not self.check_boundary((ct, rt)):
                continue

            if self.board[ct][rt] == opp:
                return False

        ## 나이트의 경우
        opp = 'N' if color == 'white' else 'n'
        for move in c.knight_directions:
            ct, rt = k_col + move[0], k_row + move[1]
            if not self.check_boundary((ct, rt)):
                continue

            if self.board[ct][rt] == opp:
                return False


        for piece in pieces:
            opp = piece.upper() if color == 'white' else piece

            for direction in pieces[piece]:
                ct, rt = k_col + direction[0], k_row + direction[1]

                while self.check_boundary((ct, rt)):
                    if self.board[ct][rt] == opp:
                        return False
                    if not self.is_empty_space((ct, rt)):
                        break
                    ct, rt = ct + direction[0], rt + direction[1]

        return True



    def is_legal_move(self, start, end):
        c1, r1 = start
        c2, r2 = end
        piece = self.board[c1][r1].lower()

        if piece== 'p':
            return (c2, r2) in self.pawn_moves(start)

        elif piece == 'n':
            return (c2, r2) in self.knight_moves(start)

        elif piece == 'k':
            return (c2, r2) in self.king_moves(start)

        elif piece == 'b':
            return (c2, r2) in self.bishop_moves(start)

        elif piece == 'r':
            return (c2, r2) in self.rook_moves(start)

        elif piece == 'q':
            return (c2, r2) in self.queen_moves(start)

        else:
            return False


    def pawn_moves(self, start):
        c1, r1 = start
        piece = self.board[c1][r1]
        size = self.size
        possible_moves = []
        direction = -1 if piece.islower() else 1    # 색에 따라 달라지는 폰의 방향
        two_step = piece.islower() and c1 == 6 or piece.isupper() and c1 == 1   # 첫 줄에 있는지 판단

        def _enpassant():
            if not self.pre_move:
                return None
            cases = [r1 - 1, r1 + 1]
            ps, pe = self.pre_move

            for case in cases:
                if case < 0 or case >= size:
                    continue
                if ps == (c1 + 2 * direction, case) and pe == (c1, case):
                    return c1 + direction, case

            return None

        # 첫줄에 있을 때
        if two_step:
            # 바로 앞이 비었는 지 확인
            if self.is_empty_space((c1 + direction, r1)):
                possible_moves.append((c1 + direction, r1))
                # 바로 앞이 비었다면, 두 칸 앞도 비었는 지 확인
                if self.is_empty_space((c1 + 2 * direction, r1)):
                    possible_moves.append((c1 + 2 * direction, r1))

        # 첫줄이 아닐 때
        else:
            if self.is_empty_space((c1 + direction, r1)):
                possible_moves.append((c1 + direction, r1))

        # 대각선에 적이 있을 때
        if not self.is_empty_space((c1 + direction, r1 - 1)) and self.is_enemy(start, (c1 + direction, r1 - 1)):
            possible_moves.append((c1 + direction, r1 - 1))
        if not self.is_empty_space((c1 + direction, r1 + 1)) and self.is_enemy(start, (c1 + direction, r1 + 1)):
            possible_moves.append((c1 + direction, r1 + 1))

        if _enpassant():
            end = _enpassant()
            self.board[end[0] - direction][end[1]] = ' '
            possible_moves.append(_enpassant())

        print(possible_moves)
        return possible_moves

    def knight_moves(self, start):
        c1, r1 = start
        directions = c.knight_directions
        possible_moves = []

        for direction in directions:
            c2 = c1 + direction[0]
            r2 = r1 + direction[1]
            pos = (c2, r2)
            if self.is_empty_space(pos) or self.is_enemy(start, pos):
                possible_moves.append(pos)

        return possible_moves

    def bishop_moves(self, start):
        c1, r1 = start
        directions = c.bishop_directions
        possible_moves = []

        for direction in directions:
            current = (c1 + direction[0], r1 + direction[1])

            while self.check_boundary(current):
                if self.is_empty_space(current) or self.is_enemy(start, current):
                    possible_moves.append(current)
                    current = (current[0] + direction[0], current[1] + direction[1])
                else:
                    break

        return possible_moves

    def rook_moves(self, start):
        c1, r1 = start
        directions = c.rook_directions
        possible_moves = []

        for direction in directions:
            current = (c1 + direction[0], r1 + direction[1])

            while self.check_boundary(current):
                if self.is_empty_space(current) or self.is_enemy(start, current):
                    possible_moves.append(current)
                    current = (current[0] + direction[0], current[1] + direction[1])
                else:
                    break

        return possible_moves

    def queen_moves(self, start):
        c1, r1 = start
        directions = c.queen_directions
        possible_moves = []

        for direction in directions:
            current = (c1 + direction[0], r1 + direction[1])

            while self.check_boundary(current):
                if self.is_empty_space(current) or self.is_enemy(start, current):
                    possible_moves.append(current)
                    current = (current[0] + direction[0], current[1] + direction[1])
                else:
                    break

        return possible_moves

    def king_moves(self, start):
        c1, r1 = start
        directions = c.king_directions
        possible_moves = []

        for direction in directions:
            c2 = c1 + direction[0]
            r2 = r1 + direction[1]
            pos = (c2, r2)
            if self.is_empty_space(pos) or self.is_enemy(start, pos):
                possible_moves.append(pos)

        return possible_moves

    # 인덱스 범위 확인
    def check_boundary(self, pos):
        return 0 <= pos[0] < self.size and 0 <= pos[1] < self.size

    # 빈 칸인지 확인
    def is_empty_space(self, pos):
        return self.check_boundary(pos) and self.board[pos[0]][pos[1]] == ' '

    # 해당 말이 적인지 확인
    def is_enemy(self, start, end):
        c1, r1 = start
        c2, r2 = end
        return self.check_boundary(end) and self.board[c1][r1].islower() ^ self.board[c2][r2].islower()



if __name__ == '__main__':
    # _board = [['r', ' ', ' ', 'Q', 'K', 'B', 'N', 'R'],
    #           [' ', ' ', ' ', 'P', 'P', 'P', 'P', 'P'],
    #           [' ', ' ', 'P', ' ', ' ', ' ', ' ', ' '],
    #           ['P', ' ', ' ', ' ', ' ', ' ', ' ', ' '],
    #           [' ', 'N', ' ', ' ', ' ', ' ', ' ', ' '],
    #           [' ', ' ', ' ', ' ', ' ', ' ', ' ', ' '],
    #           ['p', ' ', 'p', 'p', 'p', 'p', 'p', 'p'],
    #           ['r', 'n', 'b', 'q', 'k', 'b', 'n', 'r']
    #           ]
    # b = Board(_board, turn='black')
    b = Board()
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


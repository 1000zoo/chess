import pygame
import sys
from board import *

SIZE = width, height = 512, 512
SQUARE_SIZE = SW, SH = width / 8, height / 8
# INDICATOR_SIZE = IW, IH = SW / 1.5, SH / 1.5
MBD = pygame.MOUSEBUTTONDOWN


class Square:
    def __init__(self, col, row, x, y, size, callback=None):
        self.col = col
        self.row = row
        self.x = x
        self.y = y
        self.size = size
        self.callback = callback

    def draw(self, surface, color):
        rect = pygame.Rect(self.x, self.y, self.size, self.size)
        pygame.draw.rect(surface, color, rect)

    def is_clicked(self, pos):
        x, y = pos
        return self.x <= x <= self.x + self.size and self.y <= y <= self.y + self.size

    def handle_event(self, event):
        if event == MBD:
            pos = pygame.mouse.get_pos()
            if self.is_clicked(pos):
                if self.callback:
                    return self.callback(self.col, self.row)


class SquareMatrix:
    def __init__(self, _board):
        self.board = _board
        self.matrix = []
        self.create_squares()
        ...

    def create_squares(self, x_offset=0, y_offset=0, square_size=SW):
        for row in range(8):
            for col in range(8):
                x = x_offset + col * square_size
                y = y_offset + row * square_size
                square = Square(row, col, x, y, square_size, self.on_square_clicked)
                self.matrix.append(square)

    def draw(self, surface):
        for square in self.matrix:
            square.draw(surface, square.color)
            if square.piece:
                square.piece.draw(surface)

    @staticmethod
    def on_square_clicked(col, row):
        return col, row

    def handle_event(self, event):
        for square in self.matrix:
            temp = square.handle_event(event)
            if temp:
                return temp

def draw_board(main_board, images, screen):
    for row in range(8):
        for col in range(8):
            x = col * SH
            y = row * SW

            piece = main_board.piece_at((row, col))
            if isinstance(piece, Piece):
                _color = 'w' if is_white(piece.player) else 'b'
                _pname = str(piece).lower()
                img = images[f"{_color}{_pname}"]
                screen.blit(img, (x, y))

def hub(x, y):
    return x, y

def reset_board(screen, board_img):
    screen.blit(board_img, (0, 0))
    return False

def main():
    # 초기화
    pygame.init()

    main_board = Board()

    screen = pygame.display.set_mode(SIZE)
    pygame.display.set_caption("Chess")


    # 체스말 이미지 로드
    images = {}
    for color in ["w", "b"]:
        for name in ["p", "r", "n", "b", "q", "k"]:
            filename = f"asset/img/{color}{name}.png"
            piece_image = pygame.image.load(filename)
            piece_image = pygame.transform.scale(piece_image, SQUARE_SIZE)
            images[f"{color}{name}"] = piece_image

    board_img = pygame.image.load('asset/img/000.png')
    board_img = pygame.transform.scale(board_img, SIZE)

    indicator = pygame.image.load("asset/img/001.png")
    indicator = pygame.transform.scale(indicator, SQUARE_SIZE)

    sm = SquareMatrix(main_board)
    screen.blit(board_img, (0, 0))

    # 게임 루프
    while True:
        lm_square = []
        # 보드 그리기
        draw_board(main_board, images, screen)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == MBD:
                screen.blit(board_img, (0, 0))
                start = c1, r1 = sm.handle_event(MBD)
                selected_piece = main_board.board[c1][r1]

                if isinstance(selected_piece, Piece) and \
                        main_board.right_turn(selected_piece.player):
                    lm = selected_piece.get_legal_moves(main_board)

                    loop_on2 = True
                    while loop_on2:
                        draw_board(main_board, images, screen)

                        for _c, _r in lm:
                            y = _c * SH
                            x = _r * SH
                            screen.blit(indicator, (x, y))
                            tsc = Square(_c, _r, x, y, SH, lambda __x, __y: hub(__x, __y))
                            lm_square.append(tsc)

                        for event2 in pygame.event.get():
                            if event2.type == pygame.QUIT:
                                pygame.quit()
                                sys.exit()

                            if event2.type == MBD and event2.button == 1:
                                for _lm in lm_square:
                                    end = _lm.handle_event(MBD)
                                    if end:
                                        main_board.move(start, end)

                                    loop_on2 = reset_board(screen, board_img)


                            if event2.type == MBD and event2.button == 3:
                                loop_on2 = reset_board(screen, board_img)

                        pygame.display.update()

                    draw_board(main_board, images, screen)

        pygame.display.update()


if __name__=="__main__":
    main()
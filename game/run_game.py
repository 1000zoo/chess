import pygame
import sys

from board import *

class Square:
    def __init__(self, row, col, x, y, size, callback=None):
        self.row = row
        self.col = col
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
        if event.type == pygame.MOUSEBUTTONDOWN:
            pos = pygame.mouse.get_pos()
            if self.is_clicked(pos):
                if self.callback:
                    self.callback(self.row, self.col)


class SquareMatrix:
    def __init__(self):
        self.board = ...
        self.matrix = []
        ...

    def create_squares(self, x_offset, y_offset, square_size):
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

    def on_square_clicked(self, row, col):
        # 해당 칸이 클릭되었을 때 호출될 함수
        pass

    def handle_event(self, event):
        for square in self.matrix:
            square.handle_event(event)


def main():
    # 초기화
    pygame.init()
    SIZE = width, height = 512, 512
    SQUARE_SIZE = SW, SH = width / 8, height / 8
    # INDICATOR_SIZE = IW, IH = SW / 1.5, SH / 1.5

    screen = pygame.display.set_mode(SIZE)
    pygame.display.set_caption("Chess")

    # 보드 생성
    board = Board()

    # 체스말 이미지 로드
    images = {}
    for color in ["w", "b"]:
        for name in ["p", "r", "n", "b", "q", "k"]:
            filename = f"asset/img/{color}{name}.png"
            piece_image = pygame.image.load(filename)
            piece_image = pygame.transform.scale(piece_image, SQUARE_SIZE)
            images[f"{color}{name}"] = piece_image

    indicator = pygame.image.load("asset/img/001.png")
    indicator = pygame.transform.scale(indicator, SQUARE_SIZE)

    # 게임 루프
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        board_img = pygame.image.load('asset/img/000.png')
        board_img = pygame.transform.scale(board_img, SIZE)
        screen.blit(board_img, (0,0))

        # 보드 그리기
        for row in range(8):
            for col in range(8):
                x = col * SH
                y = row * SW

                piece = board.piece_at((row, col))
                if isinstance(piece, Piece):
                    _color = 'w' if is_white(piece.player) else 'b'
                    _pname = str(piece).lower()
                    img = images[f"{_color}{_pname}"]
                    screen.blit(img, (x, y))

        pygame.display.flip()


if __name__=="__main__":
    main()
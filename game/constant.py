from enum import Enum

board = [['R', 'N', 'B', 'Q', 'K', 'B', 'N', 'R'],
          ['P', 'P', 'P', 'P', 'P', 'P', 'P', 'P'],
          [' ', ' ', ' ', ' ', ' ', ' ', ' ', ' '],
          [' ', ' ', ' ', ' ', ' ', ' ', ' ', ' '],
          [' ', ' ', ' ', ' ', ' ', ' ', ' ', ' '],
          [' ', ' ', ' ', ' ', ' ', ' ', ' ', ' '],
          ['p', 'p', 'p', 'p', 'p', 'p', 'p', 'p'],
          ['r', 'n', 'b', 'q', 'k', 'b', 'n', 'r']]

# board = ["R       ",
#          " PPPPPPP",
#          "        ",
#          "        ",
#          "        ",
#          "        ",
#          "pppppppp",
#          "rnbqkbnr"
#          ]

classname_of_pieces = {
    'p' : 'Pawn',
    'n' : 'Knight',
    'b' : 'Bishop',
    'r' : 'Rook',
    'q' : 'Queen',
    'k' : 'King'
}

class Player(Enum):
    WHITE = 0
    BLACK = 1

knight_directions = [(2,1), (1,2), (-2,1), (-1,2), (2,-1), (1,-2), (-2,-1),(-1,-2)]
bishop_directions = [(1,1), (1,-1), (-1,1), (-1,-1)]
rook_directions = [(1,0), (0,1), (-1,0), (0,-1)]
queen_directions = bishop_directions + rook_directions
king_directions = queen_directions


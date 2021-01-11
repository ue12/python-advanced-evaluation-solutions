"""
this module exports the Board class
"""

# https://introcs.cs.princeton.edu/java/assignments/8puzzle.html

from pathlib import Path

### constants
# default target board
PLAIN = [1, 2, 3, 4, 5, 6, 7, 8, 0]

def replace_hole(s):
    return s.replace('.', '0').replace('-', '0')

class Board:
    """
    a board instance is modelled as a permutation,
    i.e. a list of the 9 first integers 0..8
    0 is used to denote the hole

    it can be built from a permutation, a string, or a Path
    and by default, it is the target board
    """
    def __init__(self, permutation=None):
        if permutation is None:
            permutation = PLAIN
        if isinstance(permutation, Path):
            with permutation.open() as feed:
                permutation = feed.read()
        if isinstance(permutation, str):
            permutation = replace_hole(permutation)
            permutation = [int(x) for x in permutation.split() if x]
        self.permutation = list(permutation)

    def __eq__(self, other):
        return self.permutation == other.permutation

    def __repr__(self):
        """
        returns a 3-line string
        """
        def c(n):
            # return one char per slot
            return str(n) if n!= 0 else "-"
        def line(l3):
            "l3 is a line of 3 ints"
            return " ".join(c(n) for n in l3)
        return "\n".join(line(self.permutation[3*i:3*(i+1)]) for i in range(3))

    def copy(self):
        return Board(self.permutation[:])

    def neighbours(self):
        """
        generator that yields Board instances
        corresponding to the possible moves from here
        """
        # find the hole
        hole = self.permutation.index(0)
        hx, hy = hole % 3, hole // 3
        DIRECTIONS = ((0, 1), (0, -1), (1, 0), (-1, 0))
        for dx, dy in DIRECTIONS:
            # new hole
            nhx, nhy = hx+dx, hy+dy
            # is it in the board ?
            if (0 <= nhx <= 2) and (0 <= nhy <= 2):
                move = self.copy()
                new_hole = 3*nhy + nhx
                p = move.permutation
                p[hole], p[new_hole] = p[new_hole], p[hole]
                yield move


    def hamming(self, other):
        """
        count 1 for each tile that has moved between the 2 positions
        xxx not quite exactly what the papers suggests,
        since here the hole is counted as well
        """
        return sum(x != y for (x, y) in zip(self.permutation, other.permutation))

    # here we could have defined this utility as a local function
    # inside manhattan; it is also possible to define it like this
    # a staticmethod behaves like a regular function, it does not
    # expect a 'self' reference as its first parameter
    @staticmethod
    def distance(i1, i2):
        """
        given two indices in the permutation,
        return the distance between them, counted as the number
        of horizontal / vertical moves to go from one to the other
        """
        x1, y1 = i1 % 3, i1 // 3
        x2, y2 = i2 % 3, i2 // 3
        return abs(x1-x2) + abs(y1-y2)

    def manhattan(self, other):
        result = 0
        for value in range(9):
            i1 = self.permutation.index(value)
            i2 = other.permutation.index(value)
            result += self.distance(i1, i2)
        return result


    def solvable(self):
        """
        a board is solvable iff:
        1. if 0 is on the diagonals: local permutation must be EVEN
        2. if 0 is on the edges: permutation must be ODD

        more specifically, if we paint the tiles like this
        x o x
        o x o
        x o x
        1. is when the hole is on either of the crosses and
        2. is when the hole is on a circle
        """
        hole = self.permutation.index(0)
        hx, hy = hole % 3, hole // 3
        expected_parity = (hx+hy) % 2

        def parity(L):
            swaps = 0
            size = len(L)
            for i in range(size):
                for j in range(i+1, size):
                    if L[j] < L[i]:
                        swaps += 1
            return swaps % 2

        return expected_parity == parity(self.permutation)

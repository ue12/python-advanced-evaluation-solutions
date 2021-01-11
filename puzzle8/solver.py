"""
this module exports the Solver class

it also defines the State function that is used internally by the solver
"""

import itertools
import heapq
import time
import json

from .board import Board

# the type hint that describes a priority function
# this is what a Solver instance expects
from typing import Callable
Priority = Callable[["Board", "Board"], int]


class State:
    """
    in this class, priority is an integer
    """
    def __init__(self, board, nb_moves, previous: "State", priority: int):
        self.board = board
        self.nb_moves = nb_moves
        self.previous = previous
        self.priority = priority

    def __repr__(self):
        b = " | ".join(repr(self.board).split("\n"))
        return f"{b} / {self.nb_moves} away / prio {self.priority}"

    # here we check for a loop of any length,
    # not just of length 2 as suggested in the assignment
    def anti_loop(self, board):
        """
        return True if board was already in this state or one of its
        (previous) ancestors
        """
        scanner = self
        while True:
            if scanner.board == board:
                return True
            if scanner.previous:
                scanner = scanner.previous
            else:
                break

    # we define an order on the State instances
    # which is required for the priority queue to do its job properly
    def __lt__(self, other):
        return self.priority < other.priority


class Solver:
    """
    in this class priority is a method on the Board class
    i.e. priority: Board x Board -> int
    """
    def __init__(self, start_board, *,
                 priority: Priority = Board.manhattan):
        self.start_board = start_board
        self.priority = priority
        # untested, but in theory we could aim at any position
        # xxx the reachable thingy probably needs more care for that feature
        self.target = Board()


    # it makes sense sometimes to allow for late debugging
    def solve(self, debug=False):
        """
        returns a dictionary
          reachable: bool
          iterations: int
          moves: List[Board]
          duration: float

        if reachable is False, moves is None and iterations is 0
        """
        start = time.time()

        # unsovable
        if not self.start_board.solvable():
            return dict(reachable=False, iterations=0,
                        moves=None, duration = time.time()-start)

        # here the unsolvable case is out of the way
        priority = self.priority(self.start_board, self.target)
        initial_state = State(self.start_board, 0, None, priority)
        if debug:
            print(f"{initial_state=}")
        queue = []
        heapq.heappush(queue, initial_state)
        # keeping track of the number of iterations
        for iteration in itertools.count(1):
            if debug:
                # a little tedious: show a glance on the queue on one line
                print(f"iteration #{iteration} - {len(queue)} states - [", end="")
                for s in queue[:10]:
                    print(s.priority, end=" ")
                print(']' if len(queue) <= 10 else "...]")
            state = heapq.heappop(queue)

            # found it !
            if state.board == self.target:
                # rebuild path
                moves = []
                while state:
                    moves.append(state.board)
                    state = state.previous
                return dict(reachable=True, iterations=iteration,
                            moves=moves, duration=time.time()-start)

            # otherwise let's just apply the A* logic
            for move in state.board.neighbours():
                # skip move if already in the chain
                if state.anti_loop(move):
                    continue
                # compute priority
                priority = self.priority(move, self.target) + state.nb_moves
                next_state = State(move, state.nb_moves+1, state, priority)
                # this call here will keep the queue sorted, 
                # and will run in O(log(n))
                heapq.heappush(queue, next_state)

            # safety net, just in case
            if iteration == 100_000:
                if debug:
                   print(f"EMERGENCY BRAKE")
                return dict(reachable=False, iterations=iteration,
                            moves=None, duration=time.time()-start)


    def store_result(self, solved, writer: 'File'):
        """
        a utility to store the result in the requested format
        """
        c = solved.copy()
        c['priority'] = self.priority.__name__
        if solved['reachable']:
            print("\n\n".join(str(b) for b in reversed(solved['moves'])),
                  file=writer)
            c['nb_moves'] = len(solved['moves'])-1
        else:
            print(self.start_board, file=writer)
            c['nb_moves'] = 0
        print("---", file=writer)
        del c['moves']
        print(json.dumps(c), file=writer)

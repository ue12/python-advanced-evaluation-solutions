"""
the entry point for the command line tool
"""

from pathlib import Path

from puzzle8.board import Board
from puzzle8.solver import Solver

def main():
    # argument parsing
    from argparse import ArgumentParser
    parser = ArgumentParser()
    # the --debug option will allow to run the solver in debug mode
    parser.add_argument("-d", "--debug", action='store_true', default=False)
    # default is to use manhattan, with --hamming we can test the other one
    parser.add_argument("--hamming", action='store_true', default=False)
    parser.add_argument("puzzle")
    parser.add_argument("chain")
    args = parser.parse_args()

    # the priority
    priority = Board.manhattan if not args.hamming else Board.hamming


    # input file
    input_path = Path(args.puzzle)
    if not input_path.exists():
        print(f"{input_path} not found")
        # terminate the program in this case
        exit(1)

    # create a board from the file contents
    board = Board(input_path)

    # prepare the output
    result_path = Path(args.chain)
    with result_path.open('w') as writer:
        s = Solver(board, priority=priority)
        # propagate the --debug flag if set
        solved = s.solve(debug=args.debug)
        s.store_result(solved, writer)
        print(f"{input_path} -> {solved['iterations']} iterations")


# the below idiom allows for importation of this module
if __name__ == '__main__':
    main()

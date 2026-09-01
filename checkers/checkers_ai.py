import argparse
import copy
import sys
import time
from typing import List, Optional

cache = {}  # you can use this to implement state caching


class State:
    # This class is used to represent a state.
    # board : a list of lists that represents the 8*8 board
    def __init__(self, board: list[list[str]], turn: str) -> None:

        self.board = board

        self.width = 8
        self.height = 8

        self.turn = turn

    def __hash__(self) -> int:
        """
        Return a hash of the board and the current player's turn.
        This allows the state to be used as a key in dictionaries.
        """
        return hash((tuple(tuple(row) for row in self.board), self.turn))

    def display(self) -> None:
        for i in self.board:
            for j in i:
                print(j, end="")
            print("")
        print("")

    def get_next_turn(self) -> str:
        """
        Return the string of the next turn.
        """
        if self.turn == 'player_red':
            return 'player_black'
        else:
            return 'player_red'

    def get_current_player_pieces(self) -> list[str]:
        """
        Return the current player's types of pieces.
        """
        if self.turn == 'player_red':
            return ['r', 'R']
        else:
            return ['b', 'B']

    def get_opposite_player_pieces(self) -> list[str]:
        """
        Return the opposite player's types of pieces.
        """
        if self.turn == 'player_red':
            return ['b', 'B']
        else:
            return ['r', 'R']


def generate_jumps(state: State, piece: tuple[int, int]) -> List[State]:
    """Generate all possible jump moves for a given piece and return resulting states."""
    results = []
    piece_location_i, piece_location_j = piece[0], piece[1]
    player = state.board[piece_location_i][piece_location_j]
    directions = []

    if player.isupper():  # Kings can jump in all directions
        directions.extend([(1, -1), (1, 1), (-1, -1), (-1, 1)])
    else:   # Soldiers can only jump forward
        if player == 'r':
            directions.extend([(-1, -1), (-1, 1)])
        else:
            directions.extend([(1, -1), (1, 1)])

    # Check for possible jumps in each direction
    for direction_i, direction_j in directions:
        destination_i, destination_j = piece_location_i + direction_i * 2, piece_location_j + direction_j * 2
        if 0 <= destination_i < 8 and 0 <= destination_j < 8:
            # Check if there's an opponent's piece in (ni, nj) and empty square beyond it
            if state.board[piece_location_i + direction_i][piece_location_j + direction_j] in state.get_opposite_player_pieces() and state.board[destination_i][destination_j] == '.':
                new_state = copy.deepcopy(state)
                new_state.board[piece_location_i][piece_location_j] = '.'
                new_state.board[piece_location_i + direction_i][piece_location_j + direction_j] = '.'
                new_state.board[destination_i][destination_j] = player
                # Promote to king if applicable
                if player == 'r' and destination_i == 0 or player == 'b' and destination_i == 7:
                    new_state.board[destination_i][destination_j] = player.upper()
                    new_state.turn = new_state.get_next_turn()
                    results.append(new_state)
                else:
                    results.extend(generate_jumps(new_state, (destination_i, destination_j)))
                    if not results:
                        new_state.turn = new_state.get_next_turn()
                        results.append(new_state)

    return results


def generate_simple_moves(state: State, piece: tuple[int, int]) -> List[State]:
    """Generate all possible simple moves for a given piece and return resulting states."""
    results = []
    piece_location_i, piece_location_j = piece[0], piece[1]
    player = state.board[piece_location_i][piece_location_j]
    directions = []

    if player.isupper():  # Kings can move in all directions
        directions.extend([(1, -1), (1, 1), (-1, -1), (-1, 1)])
    else:   # Soldiers can only move forward
        if player == 'r':
            directions.extend([(-1, -1), (-1, 1)])  # Red moves up the board
        else:
            directions.extend([(1, -1), (1, 1)])  # Black moves down the board

    # Check for possible simple moves in each direction
    for direction_i, direction_j in directions:
        destination_i, destination_j = piece_location_i + direction_i, piece_location_j + direction_j
        if 0 <= destination_i < 8 and 0 <= destination_j < 8:
            # Check if the destination is an empty square
            if state.board[destination_i][destination_j] == '.':
                new_state = copy.deepcopy(state)
                new_state.board[piece_location_i][piece_location_j] = '.'  # Move the piece
                new_state.board[destination_i][destination_j] = player
                # Promote to king if applicable
                if player == 'r' and destination_i == 0 or player == 'b' and destination_i == 7:
                    new_state.board[destination_i][destination_j] = player.upper()  # Promote to king
                new_state.turn = new_state.get_next_turn()
                results.append(new_state)

    return results


def get_possible_moves(curr_state: State) -> list[State]:
    # Get all the pieces of the player of the turn.
    pieces = []

    for i in range(8):
        for j in range(8):
            if curr_state.board[i][j] in curr_state.get_current_player_pieces():
                pieces.append((i, j))

    results = []

    for piece in pieces:
        # check if the piece can make any jumps or multi-jumps, be careful with the difference of a soldier and a king.
        # record the board in a state after jumping, remember to change the turn
        results.extend(generate_jumps(curr_state, piece))

    if results:
        return results

    for piece in pieces:
        # check if the piece can make any simple moves, be careful with the difference of a soldier and a king.
        # record the board in a state after making simple moves, remember to change the turn
        results.extend(generate_simple_moves(curr_state, piece))

    return results


def terminal(curr_state: State) -> bool:
    """
    Check if one side has no pieces left.
    """
    board = curr_state.board
    no_red = True
    no_black = True
    for i in range(8):
        for j in range(8):
            if board[i][j] in ['r', 'R']:
                no_red = False
            if board[i][j] in ['b', 'B']:
                no_black = False
    return no_red or no_black


def evaluation_function(state: State) -> int:
    """
    Evaluate the current board state and return a utility score.
    A higher score is better for red (maximizer), a lower score is better for black (minimizer).
    """
    red_score = 0
    black_score = 0

    for i in range(8):
        for j in range(8):
            piece = state.board[i][j]
            if piece == 'r':  # Red normal piece
                red_score += 1
            elif piece == 'R':  # Red king
                red_score += 2
            elif piece == 'b':  # Black normal piece
                black_score += 1
            elif piece == 'B':  # Black king
                black_score += 2

    # The utility for the state will be the red score minus the black score
    return red_score - black_score


def utility(curr_state: State) -> int:
    if evaluation_function(curr_state) >= 0:
        return sys.maxsize
    return -sys.maxsize - 1


def depth_first_mini_max_search_with_alpha_beta_pruning(curr_state: State, alpha: int, beta: int, depth: int, cutoff_depth: int) -> tuple[Optional[State], int]:
    """
    Version 3: with cutoff test and evaluation function
    """
    state_hash = hash(curr_state)
    if state_hash in cache:
        data = cache[state_hash]
        if data[2] <= depth:
            return data[0], data[1]

    if terminal(curr_state):
        cache[state_hash] = (curr_state, utility(curr_state), depth)
        return curr_state, utility(curr_state)

    # Check for depth limit
    if depth >= cutoff_depth:
        cache[state_hash] = (curr_state, evaluation_function(curr_state), depth)
        return curr_state, evaluation_function(curr_state)

    best_move = None
    # treat player red as maximizer and player black as minimizer
    best_move_value = -sys.maxsize - 1 if curr_state.turn == "player_red" else sys.maxsize

    moves_with_vals = [(move, evaluation_function(move)) for move in get_possible_moves(curr_state)]
    sorted_moves_with_vals = sorted(moves_with_vals, key=lambda x: x[1], reverse=(curr_state.turn == "player_red"))

    for move, move_value in sorted_moves_with_vals:
        next_move, next_move_value = depth_first_mini_max_search_with_alpha_beta_pruning(move, alpha, beta, depth + 1, cutoff_depth)

        if not best_move:
            best_move, best_move_value = move, next_move_value

        if curr_state.turn == "player_red":  # Maximizer's turn
            if best_move_value < next_move_value:
                best_move, best_move_value = move, next_move_value
            if best_move_value >= beta:
                cache[state_hash] = (best_move, best_move_value, depth)
                return best_move, best_move_value
            alpha = max(alpha, best_move_value)

        if curr_state.turn == "player_black":  # Minimizer's turn
            if best_move_value > next_move_value:
                best_move, best_move_value = move, next_move_value
            if best_move_value <= alpha:
                cache[state_hash] = (best_move, best_move_value, depth)
                return best_move, best_move_value
            beta = min(beta, best_move_value)

    cache[state_hash] = (best_move, best_move_value, depth)
    return best_move, best_move_value


def read_from_file(filename):

    f = open(filename)
    lines = f.readlines()
    board = [[str(x) for x in l.rstrip()] for l in lines]
    f.close()

    return board


if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--inputfile",
        type=str,
        required=True,
        help="The input file that contains the puzzles."
    )
    parser.add_argument(
        "--outputfile",
        type=str,
        required=True,
        help="The output file that contains the solution."
    )
    args = parser.parse_args()

    try:
        # redirect the standard output to the opened file
        sys.stdout = open(args.outputfile, 'w')

        initial_board = read_from_file(args.inputfile)
        state = State(initial_board, 'player_red')
        state.display()
        while not terminal(state):
            state = depth_first_mini_max_search_with_alpha_beta_pruning(state, -sys.maxsize - 1, sys.maxsize, 0, 13)[0]
            if not state:
                break
            state.display()

    except (IOError, OSError) as e:
        print(f"Error with opening the files: {e}")

    finally:
        # recover the standard output
        if sys.stdout:
            sys.stdout.close()
        sys.stdout = sys.__stdout__

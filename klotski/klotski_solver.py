import argparse
import heapq
import sys

char_single = '2'


class Piece:
    """
    This represents a piece on the Hua Rong Dao puzzle.
    """

    def __init__(self, is_2_by_2, is_single, coord_x, coord_y, orientation):
        """
        :param is_2_by_2: True if the piece is a 2x2 piece and False otherwise.
        :type is_2_by_2: bool
        :param is_single: True if this piece is a 1x1 piece and False otherwise.
        :type is_single: bool
        :param coord_x: The x coordinate of the top left corner of the piece.
        :type coord_x: int
        :param coord_y: The y coordinate of the top left corner of the piece.
        :type coord_y: int
        :param orientation: The orientation of the piece (one of 'h' or 'v')
            if the piece is a 1x2 piece. Otherwise, this is None
        :type orientation: str
        """

        self.is_2_by_2 = is_2_by_2
        self.is_single = is_single
        self.coord_x = coord_x
        self.coord_y = coord_y
        self.orientation = orientation

    def set_coords(self, coord_x, coord_y):
        """
        Move the piece to the new coordinates.

        :param coord: The new coordinates after moving.
        :type coord: int
        """

        self.coord_x = coord_x
        self.coord_y = coord_y

    def __repr__(self):
        return '{} {} {} {} {}'.format(self.is_2_by_2, self.is_single, \
            self.coord_x, self.coord_y, self.orientation)

    # added helper functions
    def can_move_up(self, board) -> bool:
        """
        Attempt to move the piece up on the board.
        Return True if successful, False otherwise.
        """
        blanks = board.blanks  # find all blanks
        y, x = self.coord_y, self.coord_x  # coords

        # check border
        if y - 1 < 0:
            return False

        # 2x2 chunk or 2x1 chunk (horizontal)
        if self.is_2_by_2 or (self.orientation == 'h'):
            # the space above the chunk is empty
            if (y - 1, x) in blanks and (y - 1, x + 1) in blanks:
                return True

        # 1x1 chunk or 1x2 chunk (vertical)
        if self.is_single or (self.orientation == 'v'):
            if (y - 1, x) in blanks:
                return True

        return False

    def can_move_down(self, board) -> bool:
        """
        Attempt to move the piece down on the board.
        Return True if successful, False otherwise.
        """
        blanks = board.blanks  # find all blanks
        y, x = self.coord_y, self.coord_x  # current coordinates

        # check border
        if self.is_2_by_2 or (self.orientation == 'v'):
            if y + 2 >= board.height:
                return False
        else:
            if y + 1 >= board.height:
                return False

        # 2x2 chunk
        if self.is_2_by_2:
            # the space below the chunk must be empty
            if (y + 2, x) in blanks and (y + 2, x + 1) in blanks:
                return True

        # 2x1 chunk (horizontal)
        if self.orientation == 'h':
            # the space below the chunk must be empty
            if (y + 1, x) in blanks and (y + 1, x + 1) in blanks:
                return True

        # 1x1 chunk
        if self.is_single:
            if (y + 1, x) in blanks:
                return True

        # 1x2 chunk (vertical)
        if self.orientation == 'v':
            if (y + 2, x) in blanks:
                return True

        return False

    def can_move_left(self, board) -> bool:
        """
        Attempt to move the piece left on the board.
        Return True if successful, False otherwise.
        """
        blanks = board.blanks  # find all blanks
        y, x = self.coord_y, self.coord_x  # current coordinates

        # check border
        if x - 1 < 0:
            return False

        # 2x2 chunk or 2x1 chunk (vertical)
        if self.is_2_by_2 or (self.orientation == 'v'):
            # the space to the left of the chunk must be empty
            if (y, x - 1) in blanks and (y + 1, x - 1) in blanks:
                return True

        # 1x1 chunk or 1x2 chunk (horizontal)
        if self.is_single or (self.orientation == 'h'):
            if (y, x - 1) in blanks:
                return True

        return False

    def can_move_right(self, board) -> bool:
        """
        Attempt to move the piece right on the board.
        Return True if successful, False otherwise.
        """
        blanks = board.blanks  # find all blanks
        y, x = self.coord_y, self.coord_x  # current coordinates

        # check border
        if self.is_2_by_2 or (self.orientation == 'h'):
            if x + 2 >= board.width:
                return False
        else:
            if x + 1 >= board.width:
                return False

        # 2x2 chunk
        if self.is_2_by_2:
            # the space to the right of the chunk must be empty
            if (y, x + 2) in blanks and (y + 1, x + 2) in blanks:
                return True

        # 1x1 chunk
        if self.is_single:
            if (y, x + 1) in blanks:
                return True

        # 2x1 chunk (vertical)
        if self.orientation == 'v':
            # the space to the right of the chunk must be empty
            if (y, x + 1) in blanks and (y + 1, x + 1) in blanks:
                return True

        # 1x2 chunk (horizontal)
        if self.orientation == 'h':
            if (y, x + 2) in blanks:
                return True

        return False


class Board:
    """
    Board class for setting up the playing board.
    """

    def __init__(self, height, pieces):
        """
        :param pieces: The list of Pieces
        :type pieces: List[Piece]
        """
        self.width = 4
        self.height = height
        self.pieces = pieces

        # self.grid is a 2-d (size * size) array automatically generated
        # using the information on the pieces when a board is being created.
        # A grid contains the symbol for representing the pieces on the board.
        self.grid = []
        self.__construct_grid()
        self.blanks = []
        for y in range(self.height):
            for x in range(self.width):
                if self.grid[y][x] == '.':  # find empty spaces
                    self.blanks.append((y, x))  # record

    # customized eq for object comparison.
    def __eq__(self, other):
        if isinstance(other, Board):
            return self.grid == other.grid
        return False

    def __hash__(self):
        """
        Hashes the board by converting the grid to a tuple of tuples (which is hashable).
        """
        return hash(tuple(tuple(y) for y in self.grid))

    def __construct_grid(self):
        """
        Called in __init__ to set up a 2-d grid based on the piece location information.
        """
        for i in range(self.height):
            line = []
            for j in range(self.width):
                line.append('.')
            self.grid.append(line)

        for piece in self.pieces:
            if piece.is_2_by_2:
                self.grid[piece.coord_y][piece.coord_x] = '1'
                self.grid[piece.coord_y][piece.coord_x + 1] = '1'
                self.grid[piece.coord_y + 1][piece.coord_x] = '1'
                self.grid[piece.coord_y + 1][piece.coord_x + 1] = '1'
            elif piece.is_single:
                self.grid[piece.coord_y][piece.coord_x] = char_single
            else:
                if piece.orientation == 'h':
                    self.grid[piece.coord_y][piece.coord_x] = '<'
                    self.grid[piece.coord_y][piece.coord_x + 1] = '>'
                elif piece.orientation == 'v':
                    self.grid[piece.coord_y][piece.coord_x] = '^'
                    self.grid[piece.coord_y + 1][piece.coord_x] = 'v'

    def display(self):
        """
        Print out the current board.
        """
        for i, line in enumerate(self.grid):
            for ch in line:
                print(ch, end='')
            print()


class State:
    """
    State class wrapping a Board with some extra current state information.
    Note that State and Board are different. Board has the locations of the pieces.
    State has a Board and some extra information that is relevant to the search:
    heuristic function, f value, current depth and parent.
    """

    def __init__(self, board, hfn, depth, parent=None):
        """
        :param board: The board of the state.
        :type board: Board
        :param hfn: The heuristic function.
        :type hfn: Optional[Heuristic]
        :param f: The f value of current state.
        :type f: int
        :param depth: The depth of current state in the search tree.
        :type depth: int
        :param parent: The parent of current state.
        :type parent: Optional[State]
        """
        self.board = board
        self.hfn = hfn
        self.f = depth
        if hfn:
            self.f += hfn(board)
        self.depth = depth
        self.parent = parent
        self.child = None  # update the attribute after the solution is found

    def generate_successors(self):
        """
        Generate all valid successor states from the current state.
        Return a list of new states.
        """
        successors = []

        for piece in self.board.pieces:
            if piece.can_move_up(self.board):
                new_piece = Piece(piece.is_2_by_2, piece.is_single, piece.coord_x, piece.coord_y - 1, piece.orientation)
                new_pieces = [new_piece if p is piece else p for p in self.board.pieces]
                new_board = Board(self.board.height, new_pieces)
                new_state = State(new_board, self.hfn, self.depth + 1, self)
                successors.append(new_state)

            if piece.can_move_down(self.board):
                new_piece = Piece(piece.is_2_by_2, piece.is_single, piece.coord_x, piece.coord_y + 1, piece.orientation)
                new_pieces = [new_piece if p is piece else p for p in self.board.pieces]
                new_board = Board(self.board.height, new_pieces)
                new_state = State(new_board, self.hfn, self.depth + 1, self)
                successors.append(new_state)

            if piece.can_move_left(self.board):
                new_piece = Piece(piece.is_2_by_2, piece.is_single, piece.coord_x - 1, piece.coord_y, piece.orientation)
                new_pieces = [new_piece if p is piece else p for p in self.board.pieces]
                new_board = Board(self.board.height, new_pieces)
                new_state = State(new_board, self.hfn, self.depth + 1, self)
                successors.append(new_state)

            if piece.can_move_right(self.board):
                new_piece = Piece(piece.is_2_by_2, piece.is_single, piece.coord_x + 1, piece.coord_y, piece.orientation)
                new_pieces = [new_piece if p is piece else p for p in self.board.pieces]
                new_board = Board(self.board.height, new_pieces)
                new_state = State(new_board, self.hfn, self.depth + 1, self)
                successors.append(new_state)

        return successors


def read_from_file(filename):
    """
    Load initial board from a given file.

    :param filename: The name of the given file.
    :type filename: str
    :return: A loaded board
    :rtype: Board
    """

    puzzle_file = open(filename, "r")

    line_index = 0
    pieces = []
    final_pieces = []
    final = False
    found_2by2 = False
    finalfound_2by2 = False
    height_ = 0

    for line in puzzle_file:
        height_ += 1
        if line == '\n':
            if not final:
                height_ = 0
                final = True
                line_index = 0
            continue
        if not final: #initial board
            for x, ch in enumerate(line):
                if ch == '^': # found vertical piece
                    pieces.append(Piece(False, False, x, line_index, 'v'))
                elif ch == '<': # found horizontal piece
                    pieces.append(Piece(False, False, x, line_index, 'h'))
                elif ch == char_single:
                    pieces.append(Piece(False, True, x, line_index, None))
                elif ch == '1':
                    if found_2by2 == False:
                        pieces.append(Piece(True, False, x, line_index, None))
                        found_2by2 = True
        else: #goal board
            for x, ch in enumerate(line):
                if ch == '^': # found vertical piece
                    final_pieces.append(Piece(False, False, x, line_index, 'v'))
                elif ch == '<': # found horizontal piece
                    final_pieces.append(Piece(False, False, x, line_index, 'h'))
                elif ch == char_single:
                    final_pieces.append(Piece(False, True, x, line_index, None))
                elif ch == '1':
                    if finalfound_2by2 == False:
                        final_pieces.append(Piece(True, False, x, line_index, None))
                        finalfound_2by2 = True
        line_index += 1

    puzzle_file.close()
    board = Board(height_, pieces)
    goal_board = Board(height_, final_pieces)
    return board, goal_board


def grid_to_string(grid):
    string = ""
    for i, line in enumerate(grid):
        for ch in line:
            string += ch
        string += "\n"
    return string


def backtrack_solution(state: State):
    """
    Backtrack from the goal state to record the complete path.
    """
    curr = state
    parent = curr.parent
    while parent:
        parent.child = curr
        curr = parent
        parent = curr.parent
    return curr


def df_search(init_state: State):
    frontier = [init_state]
    explored = set()

    while frontier:
        curr_state = frontier.pop()

        if curr_state.board in explored:
            continue

        explored.add(curr_state.board)

        if curr_state.board == goal_board:
            return curr_state

        for s in curr_state.generate_successors():
            frontier.append(s)

    return None


def a_star_search(init_state: State):
    """
    Perform A* search to find the optimal path from the initial state to the goal state.
    """
    frontier = []  # Priority queue (min-heap)
    heapq.heappush(frontier, (init_state.f, id(init_state), init_state))  # Add initial state to the frontier
    explored = set()

    while frontier:
        # Get the state with the lowest f value
        _, _, curr_state = heapq.heappop(frontier)

        # If the current state is explored
        if curr_state.board in explored:
            continue

        # Add the current state to explored
        explored.add(curr_state.board)

        # If we have reached the goal state, return the solution
        if curr_state.board == goal_board:
            return curr_state

        # Generate all valid successors
        for s in curr_state.generate_successors():
            # Enqueue the successor into the priority queue
            heapq.heappush(frontier, (s.f, id(s), s))

    return None  # If no solution is found


def manhattan_distance_heuristic(curr_board: Board) -> int:
    """
    Compute the Manhattan distance heuristic for the current board compared to the goal board.
    """
    total_distance = 0
    for curr_piece in curr_board.pieces:
        smallest_distance = sys.maxsize
        for goal_piece in goal_board.pieces:
            if curr_piece.is_2_by_2 and goal_piece.is_2_by_2:
                # Manhattan distance = abs(x1 - x2) + abs(y1 - y2)
                smallest_distance = min(smallest_distance, abs(curr_piece.coord_x - goal_piece.coord_x) + abs(curr_piece.coord_y - goal_piece.coord_y))
            elif curr_piece.is_single and goal_piece.is_single:
                # Manhattan distance = abs(x1 - x2) + abs(y1 - y2)
                smallest_distance = min(smallest_distance, abs(curr_piece.coord_x - goal_piece.coord_x) + abs(curr_piece.coord_y - goal_piece.coord_y))
            elif curr_piece.orientation == 'h' and goal_piece.orientation == 'h':
                # Manhattan distance = abs(x1 - x2) + abs(y1 - y2)
                smallest_distance = min(smallest_distance, abs(curr_piece.coord_x - goal_piece.coord_x) + abs(curr_piece.coord_y - goal_piece.coord_y))
            elif curr_piece.orientation == 'v' and goal_piece.orientation == 'v':
                # Manhattan distance = abs(x1 - x2) + abs(y1 - y2)
                smallest_distance = min(smallest_distance, abs(curr_piece.coord_x - goal_piece.coord_x) + abs(curr_piece.coord_y - goal_piece.coord_y))
        total_distance += smallest_distance

    return total_distance


if __name__ == "__main__":
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
    parser.add_argument(
        "--algo",
        type=str,
        required=True,
        choices=['astar', 'dfs'],
        help="The searching algorithm."
    )
    args = parser.parse_args()

    # read the board from the file
    board, goal_board = read_from_file(args.inputfile)

    solution_state = None
    # select search algorithm
    if args.algo == 'dfs':
        # convert board to state type
        initial_state = State(board, hfn=None, depth=0)
        # run the search
        solution_state = df_search(initial_state)
    elif args.algo == 'astar':
        # convert board to state type
        initial_state = State(board, hfn=manhattan_distance_heuristic, depth=0)
        # run the search
        solution_state = a_star_search(initial_state)

    # if a solution is found, backtrack
    if solution_state:
        solution_path = backtrack_solution(solution_state)
        with open(args.outputfile, 'w') as f:
            while solution_path:
                f.write(grid_to_string(solution_path.board.grid))
                f.write('\n')
                solution_path = solution_path.child
    else:
        with open(args.outputfile, 'w') as f:
            f.write("No solution\n")

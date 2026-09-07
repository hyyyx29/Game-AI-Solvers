# Game-AI-Solvers

Two classic game AIs implemented from scratch in pure Python — nothing beyond the standard library.

| Solver | Technique |
|--------|-----------|
| [Klotski sliding-puzzle solver](klotski/) | A* search with a Manhattan-distance heuristic (plus a DFS mode) |
| [Checkers agent](checkers/) | Minimax with alpha-beta pruning and state caching |

## Klotski solver (`klotski/`)

Solves **Klotski / Hua Rong Dao** (华容道), the classic sliding-block puzzle: maneuver the 2×2 block through a packed 4×5 board. A* explores board states with a Manhattan-distance heuristic and returns an optimal move sequence; a DFS mode is included for comparison.

```bash
cd klotski
python klotski_solver.py --inputfile sample_puzzle.txt --outputfile solution.txt --algo astar
```

The input file holds the start board and the goal board, separated by a blank line:

```
^11^        1  the 2×2 block (four cells)
v11v        ^v the top/bottom halves of a vertical 1×2 piece
^<>^        <> a horizontal 1×2 piece
v22v        2  a single 1×1 piece
2..2        .  empty
```

The output file lists every intermediate board from start to goal.

## Checkers agent (`checkers/`)

Plays checkers under standard rules — forced captures, chained multi-jumps, and king promotion — using **minimax with alpha-beta pruning**, a depth cutoff, and a cache of evaluated states. Given a position, it plays out the game and writes the sequence of boards.

```bash
cd checkers
python checkers_ai.py --inputfile sample_endgame.txt --outputfile moves.txt
```

Board format: eight lines of eight characters — `r`/`b` for red/black men, `R`/`B` for kings, `.` for an empty square. Red moves first.

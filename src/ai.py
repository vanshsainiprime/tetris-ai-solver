from board import Board
from simulator import simulate_move

def get_column_heights(board):
    heights = []

    for column in range(Board.WIDTH):
        height = 0

        for row in range(Board.HEIGHT):
            if board.grid[row][column] != 0:
                height = Board.HEIGHT - row
                break

        heights.append(height)

    return heights

def count_holes(board):
    holes = 0

    for column in range(Board.WIDTH):
        block_found = False

        for row in range(Board.HEIGHT):
            if board.grid[row][column] != 0:
                block_found = True

            elif block_found:
                holes += 1

    return holes


def get_aggregate_height(board):
    return sum(get_column_heights(board))


def get_bumpiness(board):
    heights = get_column_heights(board)

    bumpiness = 0

    for i in range(Board.WIDTH - 1):
        bumpiness += abs(
            heights[i] - heights[i + 1]
        )

    return bumpiness


def evaluate_board(board, lines_cleared=0):
    aggregate_height = get_aggregate_height(board)
    holes = count_holes(board)
    bumpiness = get_bumpiness(board)

    score = (
        (lines_cleared * 10)
        - (aggregate_height * 0.5)
        - (holes * 5)
        - (bumpiness * 0.3)
    )

    return score


def search_future(
    board,
    piece_queue,
    depth=0
):
    """
    Recursively evaluate the future pieces.

    piece_queue contains:
        current piece
        next piece
        next piece
        ...

    Returns the best score obtainable from this state.
    """

    if depth >= len(piece_queue):
        return 0

    rotations = piece_queue[depth]

    best_score = float("-inf")

    for piece in rotations:

        for column in range(Board.WIDTH):

            result = simulate_move(
                board,
                piece,
                column
            )

            if result is None:
                continue

            new_board, lines_cleared = result

            immediate_score = evaluate_board(
                new_board,
                lines_cleared
            )

            future_score = search_future(
                new_board,
                piece_queue,
                depth + 1
            )

            total_score = (
                immediate_score
                + future_score * 0.7
            )

            if total_score > best_score:
                best_score = total_score

    return best_score


def find_best_move(
    board,
    current_rotations,
    next_rotations_list
):
    """
    Find the best move using the current piece
    and the detected NEXT queue.

    Example:

        current = T
        next = [S, I, T]

    Search:

        T -> S -> I -> T
    """

    piece_queue = [
        current_rotations
    ]

    for rotations in next_rotations_list:
        piece_queue.append(rotations)

    best_move = None
    best_score = float("-inf")

    for rotation_index, current_piece in enumerate(
        current_rotations
    ):

        for column in range(Board.WIDTH):

            result = simulate_move(
                board,
                current_piece,
                column
            )

            if result is None:
                continue

            new_board, lines_cleared = result

            immediate_score = evaluate_board(
                new_board,
                lines_cleared
            )

            future_score = search_future(
                new_board,
                piece_queue,
                depth=1
            )

            total_score = (
                immediate_score
                + future_score * 0.7
            )

            if total_score > best_score:

                best_score = total_score

                best_move = {
                    "rotation": rotation_index,
                    "column": column,
                    "score": total_score
                }

    return best_move
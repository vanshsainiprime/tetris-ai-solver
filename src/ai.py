from board import Board
from simulator import simulate_move


SEARCH_NODES = 0

FULL_ROW = (1 << Board.WIDTH) - 1



# PIECE PLACEMENT PRECOMPUTATION


def build_placements(rotations):
    """
    Precompute every legal horizontal placement of
    every rotation.

    Each placement stores:

        column
        row_masks

    row_masks contains the exact bit pattern occupied
    by the piece for each local piece row.
    """

    placements = []

    for rotation_index, piece in enumerate(rotations):

        max_column = max(
            column
            for row, column in piece
        )

        max_row = max(
            row
            for row, column in piece
        )

        width = max_column + 1

        rotation_placements = []

        for column in range(
            Board.WIDTH - width + 1
        ):

            row_masks = [0] * (max_row + 1)

            for piece_row, piece_column in piece:

                row_masks[piece_row] |= (
                    1 << (
                        column
                        + piece_column
                    )
                )

            rotation_placements.append(
                (
                    column,
                    tuple(row_masks)
                )
            )

        placements.append(
            rotation_placements
        )

    return placements



# PRECOMPUTED PLACEMENT CACHE


_PLACEMENT_CACHE = {}


def get_placements(rotations):
    """
    Cache precomputed placements for a rotation set.
    """

    key = tuple(
        tuple(piece)
        for piece in rotations
    )

    placements = _PLACEMENT_CACHE.get(key)

    if placements is None:

        placements = build_placements(
            rotations
        )

        _PLACEMENT_CACHE[key] = placements

    return placements



# BOARD CONVERSION


def board_to_bitboard(board):
    """
    Convert the 20x10 grid into 20 integer row masks.
    """

    rows = []

    for row in board.grid:

        mask = 0

        for column, cell in enumerate(row):

            if cell:
                mask |= 1 << column

        rows.append(mask)

    return tuple(rows)



# FAST COLLISION


def placement_collides(
    rows,
    row_masks,
    start_row
):
    """
    Check collision between a precomputed piece
    placement and the board.
    """

    for offset, piece_mask in enumerate(
        row_masks
    ):

        board_row = start_row + offset

        if board_row >= Board.HEIGHT:
            return True

        if rows[board_row] & piece_mask:
            return True

    return False



# FAST DROP


def find_drop_row(
    rows,
    row_masks
):
    """
    Find the lowest valid row for a precomputed
    placement.

    This preserves the original simulator's
    top-to-bottom drop behaviour.
    """

    row = 0

    if placement_collides(
        rows,
        row_masks,
        row
    ):
        return None

    while True:

        next_row = row + 1

        if placement_collides(
            rows,
            row_masks,
            next_row
        ):
            return row

        row = next_row



# FAST SIMULATION


def simulate_placement(
    rows,
    row_masks
):
    """
    Place a precomputed piece and clear lines.
    """

    row = find_drop_row(
        rows,
        row_masks
    )

    if row is None:
        return None

    new_rows = list(rows)

    for offset, piece_mask in enumerate(
        row_masks
    ):

        new_rows[
            row + offset
        ] |= piece_mask

    # Remove full rows.
    remaining = []

    for board_row in new_rows:

        if board_row != FULL_ROW:
            remaining.append(
                board_row
            )

    lines_cleared = (
        Board.HEIGHT
        - len(remaining)
    )

    if lines_cleared:

        remaining = (
            [0] * lines_cleared
            + remaining
        )

    return (
        tuple(remaining),
        lines_cleared
    )



# BOARD ANALYSIS


def analyze_bitboard(rows):
    """
    Exact equivalent of analyze_board() in ai.py.
    """

    heights = [0] * Board.WIDTH
    holes = 0

    for column in range(Board.WIDTH):

        bit = 1 << column
        block_found = False

        for row in range(Board.HEIGHT):

            occupied = (
                rows[row] & bit
            ) != 0

            if occupied:

                if not block_found:

                    heights[column] = (
                        Board.HEIGHT - row
                    )

                    block_found = True

            elif block_found:

                holes += 1

    aggregate_height = sum(heights)

    bumpiness = 0

    for column in range(
        Board.WIDTH - 1
    ):

        bumpiness += abs(
            heights[column]
            - heights[column + 1]
        )

    return (
        aggregate_height,
        holes,
        bumpiness
    )



# BOARD EVALUATION


def evaluate_bitboard(
    rows,
    lines_cleared=0
):

    (
        aggregate_height,
        holes,
        bumpiness
    ) = analyze_bitboard(rows)

    return (
        (lines_cleared * 10)
        - (aggregate_height * 0.5)
        - (holes * 5)
        - (bumpiness * 0.3)
    )



# COMPATIBILITY HELPERS (LEGACY GRID & TESTS)


def analyze_board(board):
    """
    Analyze the board using the 20x10 grid representation.
    """

    heights = [0] * Board.WIDTH
    holes = 0

    for column in range(Board.WIDTH):

        block_found = False

        for row in range(Board.HEIGHT):

            if board.grid[row][column] != 0:

                if not block_found:
                    heights[column] = (
                        Board.HEIGHT - row
                    )
                    block_found = True

            elif block_found:
                holes += 1

    aggregate_height = sum(heights)

    bumpiness = 0

    for column in range(Board.WIDTH - 1):
        bumpiness += abs(
            heights[column]
            - heights[column + 1]
        )

    return (
        aggregate_height,
        holes,
        bumpiness
    )


def get_column_heights(board):
    heights = [0] * Board.WIDTH

    for column in range(Board.WIDTH):

        for row in range(Board.HEIGHT):

            if board.grid[row][column] != 0:
                heights[column] = (
                    Board.HEIGHT - row
                )
                break

    return heights


def count_holes(board):
    return analyze_board(board)[1]


def get_aggregate_height(board):
    return analyze_board(board)[0]


def get_bumpiness(board):
    return analyze_board(board)[2]


def evaluate_board(board, lines_cleared=0):
    (
        aggregate_height,
        holes,
        bumpiness
    ) = analyze_board(board)

    return (
        (lines_cleared * 10)
        - (aggregate_height * 0.5)
        - (holes * 5)
        - (bumpiness * 0.3)
    )


def board_key(board):
    """
    Represent each row as a 10-bit integer.
    """

    return tuple(
        sum(
            (1 << column)
            for column, cell in enumerate(row)
            if cell
        )
        for row in board.grid
    )



# MOVE GENERATION


def generate_moves(
    rows,
    rotations
):
    """
    Generate all legal moves using precomputed
    placements.

    Returns:

        (
            rotation_index,
            column,
            new_rows,
            lines_cleared
        )
    """

    all_placements = get_placements(
        rotations
    )

    moves = []

    for rotation_index, placements in enumerate(
        all_placements
    ):

        for column, row_masks in placements:

            result = simulate_placement(
                rows,
                row_masks
            )

            if result is None:
                continue

            new_rows, lines_cleared = result

            moves.append(
                (
                    rotation_index,
                    column,
                    new_rows,
                    lines_cleared
                )
            )

    return moves



# FUTURE SEARCH


def search_future(
    rows,
    piece_queue,
    depth=0,
    cache=None
):
    global SEARCH_NODES

    SEARCH_NODES += 1

    if depth >= len(piece_queue):
        return 0

    cache_key = (
        rows,
        depth
    )

    cached = cache.get(cache_key)

    if cached is not None:
        return cached

    rotations = piece_queue[depth]

    best_score = float("-inf")

    moves = generate_moves(
        rows,
        rotations
    )

    for (
        _rotation,
        _column,
        new_rows,
        lines_cleared
    ) in moves:

        immediate_score = evaluate_bitboard(
            new_rows,
            lines_cleared
        )

        future_score = search_future(
            new_rows,
            piece_queue,
            depth + 1,
            cache
        )

        total_score = (
            immediate_score
            + future_score * 0.7
        )

        if total_score > best_score:
            best_score = total_score

    cache[cache_key] = best_score

    return best_score



# BEST MOVE


def find_best_move(
    board,
    current_rotations,
    next_rotations_list
):
    global SEARCH_NODES

    SEARCH_NODES = 0

    rows = board_to_bitboard(
        board
    )

    piece_queue = [
        current_rotations
    ]

    for rotations in next_rotations_list:

        piece_queue.append(
            rotations
        )

    cache = {}

    best_move = None
    best_score = float("-inf")

    current_moves = generate_moves(
        rows,
        current_rotations
    )

    for (
        rotation_index,
        column,
        new_rows,
        lines_cleared
    ) in current_moves:

        immediate_score = evaluate_bitboard(
            new_rows,
            lines_cleared
        )

        future_score = search_future(
            new_rows,
            piece_queue,
            depth=1,
            cache=cache
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

    print(
        f"SEARCH NODES: {SEARCH_NODES}"
    )

    return best_move

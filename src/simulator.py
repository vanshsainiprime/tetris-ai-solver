from board import Board


def copy_board(board):
    new_board = Board()

    for row in range(Board.HEIGHT):
        new_board.grid[row] = board.grid[row].copy()

    return new_board


def simulate_move(board, piece, column):
    """
    Simulate dropping a piece onto a board.

    Returns:
        (new_board, lines_cleared)

    or:
        None if the move is invalid.
    """


    # FIND DROP POSITION


    row = 0

    if not board.can_place(
        piece,
        row,
        column
    ):
        return None

    while board.can_place(
        piece,
        row + 1,
        column
    ):
        row += 1


    # COPY BOARD


    new_board = copy_board(board)


    # PLACE PIECE


    for piece_row, piece_column in piece:

        board_row = row + piece_row
        board_column = column + piece_column

        new_board.grid[
            board_row
        ][
            board_column
        ] = 1


    # CLEAR LINES


    lines_cleared = 0
    new_grid = []

    for board_row in new_board.grid:

        if all(board_row):
            lines_cleared += 1
        else:
            new_grid.append(board_row)

    if lines_cleared:

        empty_rows = [
            [0] * Board.WIDTH
            for _ in range(lines_cleared)
        ]

        new_grid = (
            empty_rows
            + new_grid
        )

    new_board.grid = new_grid

    return new_board, lines_cleared
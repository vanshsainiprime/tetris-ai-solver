from board import Board


def copy_board(board):
    """
    Create an independent copy of a board.
    """

    new_board = Board()

    for row in range(Board.HEIGHT):
        for column in range(Board.WIDTH):
            new_board.grid[row][column] = board.grid[row][column]

    return new_board


def simulate_move(board, piece, column):
    """
    Simulate dropping a piece onto a board.

    Returns:
        (new_board, lines_cleared)

    Returns:
        None if the move is invalid.
    """

    new_board = copy_board(board)

    # The piece must fit at the starting position.
    if not new_board.can_place(piece, 0, column):
        return None

    # Find the lowest position.
    drop_row = new_board.get_drop_row(piece, column)

    # Place the piece.
    new_board.place_piece(piece, drop_row, column)

    # Clear completed lines.
    lines_cleared = new_board.clear_lines()

    return new_board, lines_cleared
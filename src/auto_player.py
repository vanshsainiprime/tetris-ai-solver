from phone import capture_screen
from vision import (
    load_screen,
    detect_board,
    detect_current_piece,
    remove_current_piece,
    detect_next_queue
)
from pieces import PIECES
from board import Board
from ai import find_best_move

from controller import (
    create_action_plan,
    print_action_plan
)
from adb_controller import ADBController

def convert_to_board(detected_board):
    """
    Convert vision output into our Board object.
    """

    board = Board()

    for row in range(Board.HEIGHT):
        for column in range(Board.WIDTH):

            if detected_board[row][column] != ".":
                board.set_cell(
                    row,
                    column,
                    1
                )

    return board


def get_current_column(current_cells):
    """
    Get the leftmost column occupied by
    the currently falling piece.
    """

    if not current_cells:
        return None

    return min(
        column
        for row, column in current_cells
    )


def main():

    print()
    print("=" * 50)
    print("ONE-PIECE AUTO PLAYER")
    print("=" * 50)

    # IMPORTANT:
    #
    # True  = simulation only
    # False = actually control the phone
    #
    # We are using False because this is the
    # controlled one-piece live test.
    controller = ADBController(
        dry_run=False
    )


    # Capture immediately
    print("Capturing screen...")

    filename = capture_screen(
        "auto_screen.png"
    )

    image = load_screen(
        filename
    )

    # Detect board

    raw_board = detect_board(
        image
    )

    current_piece_type, current_cells = (
        detect_current_piece(
            raw_board
        )
    )

    if current_piece_type not in PIECES:

        print(
            "ERROR: Could not identify current piece."
        )

        return

    current_column = get_current_column(
        current_cells
    )

    if current_column is None:

        print(
            "ERROR: Could not determine current column."
        )

        return


    # Remove falling piece from board
    settled_board = remove_current_piece(
        raw_board,
        current_cells
    )

    board = convert_to_board(
        settled_board
    )

    # Detect NEXT queue
    next_queue = detect_next_queue(
        image
    )

    print(
        f"Current piece: {current_piece_type}"
    )

    print(
        f"Current column: {current_column}"
    )

    print(
        f"Next queue: {next_queue}"
    )

    # Convert NEXT queue into rotation lists
    next_rotations = []

    for piece_type in next_queue:

        if piece_type in PIECES:

            next_rotations.append(
                PIECES[piece_type]
            )

 
    # AI
    best_move = find_best_move(
        board,
        PIECES[current_piece_type],
        next_rotations
    )

    if best_move is None:

        print(
            "ERROR: AI could not find a move."
        )

        return

    print()
    print("AI DECISION")
    print("-" * 30)

    print(
        f"Rotation: {best_move['rotation']}"
    )

    print(
        f"Target column: {best_move['column']}"
    )

    print(
        f"Score: {best_move['score']:.2f}"
    )

    # Create actions
    actions = create_action_plan(
        current_piece_type,
        best_move["rotation"],
        best_move["column"],
        current_column
    )

    print_action_plan(
        current_piece_type,
        best_move["rotation"],
        best_move["column"],
        current_column,
        actions
    )


    # EXECUTE IMMEDIATELY

    print()
    print("EXECUTING...")
    print()

    controller.execute_plan(
        actions
    )

    # STOP
  
    print()
    print("=" * 50)
    print("ONE PIECE COMPLETE")
    print("=" * 50)


if __name__ == "__main__":
    main()

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

    if not current_cells:
        return None

    columns = [
        column
        for row, column in current_cells
    ]

    return min(columns)


def main():

    print()
    print("=" * 45)
    print("MULTI-PIECE AI TEST")
    print("=" * 45)

    # SAFE TEST MODE
    controller = ADBController(
        dry_run=True
    )

    from phone import capture_screen

    filename = capture_screen(
        "live_screen.png"
    )

    image = load_screen(
        filename
    )

   
    # Detect board


    raw_board = detect_board(
        image
    )

    
    # Detect current piece


    current_piece_type, current_cells = (
        detect_current_piece(
            raw_board
        )
    )

    if current_piece_type not in PIECES:

        print(
            "Could not identify current piece."
        )

        return

    current_column = get_current_column(
        current_cells
    )

    if current_column is None:

        print(
            "Could not determine current piece column."
        )

        return

    # Remove falling piece
 

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

    print()
    print(
        f"Current piece: {current_piece_type}"
    )

    print(
        f"Current column: {current_column}"
    )

    print(
        f"Next queue: {next_queue}"
    )


    # Convert queue to rotations


    next_rotations_list = []

    for piece_type in next_queue:

        if piece_type in PIECES:

            next_rotations_list.append(
                PIECES[piece_type]
            )

  
    # AI SEARCH


    best_move = find_best_move(
        board,
        PIECES[current_piece_type],
        next_rotations_list
    )

    if best_move is None:

        print(
            "AI could not find a valid move."
        )

        return

    # Create controller actions
 

    actions = create_action_plan(
        current_piece_type,
        best_move["rotation"],
        best_move["column"],
        current_column
    )

  
    # Display result


    print()
    print(
        f"AI rotation: {best_move['rotation']}"
    )

    print(
        f"AI target column: {best_move['column']}"
    )

    print(
        f"AI score: {best_move['score']:.2f}"
    )

    print_action_plan(
        current_piece_type,
        best_move["rotation"],
        best_move["column"],
        current_column,
        actions
    )

    print()
    print("DRY RUN ONLY")
    print(
        "Nothing will be sent to the phone."
    )

    controller.execute_plan(
        actions
    )


if __name__ == "__main__":
    main()
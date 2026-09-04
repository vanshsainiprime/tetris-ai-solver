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


def convert_to_board(detected_board):
    """
    Convert the vision board into our Board object.
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


def main():

    # Load screenshot
   

    image = load_screen(
        "phone_screen.png"
    )


    # Vision


    raw_board = detect_board(
        image
    )

    current_piece_type, current_cells = (
        detect_current_piece(
            raw_board
        )
    )

    settled_board = remove_current_piece(
        raw_board,
        current_cells
    )

    next_queue = detect_next_queue(
        image
    )


    # Validate current piece


    if current_piece_type not in PIECES:

        print(
            "Could not identify current piece."
        )

        return


 
    # Convert board

    board = convert_to_board(
        settled_board
    )


    # Next piece
    if next_queue:

        next_piece_type = next_queue[0]

    else:

        next_piece_type = current_piece_type


    if next_piece_type not in PIECES:

        next_piece_type = current_piece_type


    # AI


    best_move = find_best_move(
        board,
        PIECES[current_piece_type],
        PIECES[next_piece_type]
    )


    if best_move is None:

        print(
            "AI could not find a valid move."
        )

        return


    # Action planner


    actions = create_action_plan(
        current_piece_type,
        best_move["rotation"],
        best_move["column"]
    )


 
    # Print state


    print()
    print("=" * 45)
    print("AI GAME STATE")
    print("=" * 45)

    print(
        f"Current piece: {current_piece_type}"
    )

    print(
        f"Next queue: {next_queue}"
    )

    print(
        f"AI next piece: {next_piece_type}"
    )

    print()

    print("AI RESULT:")

    print(
        f"Rotation: {best_move['rotation']}"
    )

    print(
        f"Column: {best_move['column']}"
    )

    print(
        f"Score: {best_move['score']:.2f}"
    )



    # Print action plan


    print_action_plan(
        current_piece_type,
        best_move["rotation"],
        best_move["column"],
        actions
    )


if __name__ == "__main__":
    main()
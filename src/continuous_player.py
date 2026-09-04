import time

from phone import capture_screen

from vision import (
    load_screen,
    detect_board,
    detect_current_piece,
    remove_current_piece,
    detect_next_queue
)

from board import Board
from pieces import PIECES
from planner import RollingPlanner
from controller import create_action_plan
from adb_controller import ADBController


MAX_PIECES = 20
STATE_CHECK_DELAY = 0.25


def convert_to_board(detected_board):
    board = Board()

    for row in range(Board.HEIGHT):
        for column in range(Board.WIDTH):
            if detected_board[row][column] != ".":
                board.set_cell(row, column, 1)

    return board


def get_current_column(current_cells):
    if not current_cells:
        return None

    return min(
        column
        for row, column in current_cells
    )


def boards_match(board_a, board_b):
    """
    Compare two board states.
    """

    for row in range(Board.HEIGHT):
        for column in range(Board.WIDTH):

            if (
                board_a.grid[row][column]
                != board_b.grid[row][column]
            ):
                return False

    return True


def detect_game_state():
    """
    Capture and analyze the current phone screen.
    """

    filename = capture_screen(
        "continuous_screen.png"
    )

    image = load_screen(
        filename
    )

    raw_board = detect_board(
        image
    )

    current_piece_type, current_cells = (
        detect_current_piece(
            raw_board
        )
    )

    if current_piece_type not in PIECES:
        return None

    current_column = get_current_column(
        current_cells
    )

    if current_column is None:
        return None

    settled_board = remove_current_piece(
        raw_board,
        current_cells
    )

    board = convert_to_board(
        settled_board
    )

    next_queue = detect_next_queue(
        image
    )

    return {
        "board": board,
        "current_piece": current_piece_type,
        "current_column": current_column,
        "next_queue": next_queue
    }


def print_predictions(predictions):
    print()
    print("PREDICTION CACHE")

    for index, prediction in enumerate(
        predictions,
        start=1
    ):

        print(
            f"{index}. "
            f"{prediction['piece']} → "
            f"column {prediction['column']} | "
            f"rotation {prediction['rotation']} | "
            f"score {prediction['score']:.2f}"
        )


def main():

    print()
    print("=" * 60)
    print("TETRIS AI - ROLLING PREDICTION PLAYER")
    print("=" * 60)

    controller = ADBController(
        dry_run=True
    )

    planner = RollingPlanner()

    previous_prediction = None

    for piece_number in range(
        1,
        MAX_PIECES + 1
    ):

        print()
        print(
            f"READING PIECE {piece_number}..."
        )

        state = detect_game_state()

        if state is None:
            print(
                "Could not reliably detect game state."
            )
            print("STOPPING.")
            break

        print(
            f"Current: {state['current_piece']}"
        )

        print(
            f"Current column: "
            f"{state['current_column']}"
        )

        print(
            f"NEXT: "
            f"{state['next_queue']}"
        )

 
        # Check whether we can reuse the cached prediction
        cached_prediction = (
            planner.get_current_prediction()
        )

        can_reuse = False

        if cached_prediction is not None:

            if (
                cached_prediction["piece"]
                == state["current_piece"]
            ):

                if boards_match(
                    state["board"],
                    cached_prediction["board_before"]
                ):
                    can_reuse = True

        if can_reuse:

            print()
            print(
                "REUSING CACHED PREDICTION"
            )

            current_prediction = (
                planner.consume_current_prediction()
            )

            # The cached prediction already has
            # its action plan.
        else:

            print()
            print(
                "CACHE INVALID OR EMPTY"
            )

            print(
                "CALCULATING NEW PREDICTIONS..."
            )

            planner.build_predictions(
                state["board"],
                state["current_piece"],
                state["current_column"],
                state["next_queue"]
            )

            current_prediction = (
                planner.consume_current_prediction()
            )

        if current_prediction is None:

            print(
                "Planner could not find a move."
            )

            print("STOPPING.")

            break

        print_predictions(
            planner.get_predictions()
        )

        print()
        print("CURRENT MOVE")

        print(
            f"Piece: "
            f"{current_prediction['piece']}"
        )

        print(
            f"Rotation: "
            f"{current_prediction['rotation']}"
        )

        print(
            f"Target column: "
            f"{current_prediction['column']}"
        )

        print(
            f"Actions: "
            f"{current_prediction['actions']}"
        )

        # Execute current move
        print()
        print("EXECUTING...")

        controller.execute_plan(
            current_prediction["actions"]
        )

        time.sleep(
            STATE_CHECK_DELAY
        )

        print(
            "Move complete."
        )

    print()
    print("=" * 60)
    print("ROLLING PLAYER COMPLETE")
    print("=" * 60)


if __name__ == "__main__":
    main()
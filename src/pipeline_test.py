import time
from concurrent.futures import ProcessPoolExecutor
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
from controller import create_action_plan
from adb_controller import ADBController
from background_worker import calculate_prediction


MAX_PIECES = 5


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


def detect_game_state():
    filename = capture_screen(
        "pipeline_screen.png"
    )

    image = load_screen(filename)

    raw_board = detect_board(image)

    current_piece, current_cells = (
        detect_current_piece(raw_board)
    )

    if current_piece not in PIECES:
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

    next_queue = detect_next_queue(image)

    return {
        "board": board,
        "current_piece": current_piece,
        "current_column": current_column,
        "next_queue": next_queue
    }


def start_background_prediction(
    executor,
    state
):
    print(
        "Starting background calculation..."
    )

    future = executor.submit(
        calculate_prediction,
        (
            state["board"],
            state["current_piece"],
            state["next_queue"]
        )
    )

    return future


def main():

    print()
    print("=" * 60)
    print("TETRIS AI - TRUE PIPELINE TEST")
    print("=" * 60)

    controller = ADBController(
        dry_run=False
    )

    executor = ProcessPoolExecutor(
        max_workers=1
    )

    try:

     
        # Read first state

        state = detect_game_state()

        if state is None:
            print("Could not detect game state.")
            return

        print(
            f"Current: {state['current_piece']}"
        )

        print(
            f"Column: {state['current_column']}"
        )

        print(
            f"NEXT: {state['next_queue']}"
        )

   
        # Start first calculation

        future = start_background_prediction(
            executor,
            state
        )

        for piece_number in range(
            1,
            MAX_PIECES + 1
        ):

            print()
            print(
                "-" * 60
            )

            print(
                f"PIECE {piece_number}"
            )

            # Wait for current prediction

            print(
                "Waiting for AI prediction..."
            )

            best_move = future.result()

            if best_move is None:
                print(
                    "AI could not find a move."
                )
                break

            print(
                "Prediction ready:"
            )

            print(
                f"Rotation: "
                f"{best_move['rotation']}"
            )

            print(
                f"Target: "
                f"{best_move['column']}"
            )

            print(
                f"Score: "
                f"{best_move['score']:.2f}"
            )

            # Build current actions

            actions = create_action_plan(
                state["current_piece"],
                best_move["rotation"],
                best_move["column"],
                state["current_column"]
            )

            print(
                f"Actions: {actions}"
            )

            # Execute current move
       
            print()
            print(
                "EXECUTING CURRENT MOVE..."
            )

            controller.execute_plan(
                actions
            )

            # While the move has been sent to the
            # phone, we can start preparing the
            # NEXT state only after it is detected.
            #
            # This test measures that transition.
            print()
            print(
                "Move commands finished."
            )

            time.sleep(0.25)

            new_state = detect_game_state()

            if new_state is None:
                print(
                    "Could not detect next state."
                )
                break

            print(
                f"New current: "
                f"{new_state['current_piece']}"
            )

            print(
                f"New NEXT: "
                f"{new_state['next_queue']}"
            )

            # Immediately start next calculation.


            future = start_background_prediction(
                executor,
                new_state
            )

            state = new_state

            print(
                "Next AI calculation is now running "
                "in the background."
            )

    finally:

        executor.shutdown(
            wait=True
        )

    print()
    print("=" * 60)
    print("PIPELINE TEST COMPLETE")
    print("=" * 60)


if __name__ == "__main__":
    main()

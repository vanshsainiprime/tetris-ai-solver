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

MAX_PIECES = 10

STABLE_CHECK_DELAY = 0.10
MAX_STABILITY_ATTEMPTS = 8

STATE_VERIFY_DELAY = 0.08
MAX_STATE_VERIFY_ATTEMPTS = 3


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


def detect_stable_game_state():
    """
    Detect the current piece twice consecutively.

    This prevents accepting a frame during the
    transition between two pieces.
    """

    last_piece = None
    last_state = None

    for attempt in range(
        1,
        MAX_STABILITY_ATTEMPTS + 1
    ):

        state = detect_game_state()

        if state is None:
            time.sleep(
                STABLE_CHECK_DELAY
            )
            continue

        piece = state["current_piece"]

        print(
            f"Stability check "
            f"{attempt}/{MAX_STABILITY_ATTEMPTS}: "
            f"{piece}"
        )

        if (
            last_state is not None
            and piece == last_piece
        ):
            print(
                f"Stable piece detected: {piece}"
            )

            return state

        last_piece = piece
        last_state = state

        time.sleep(
            STABLE_CHECK_DELAY
        )

    return last_state


def make_state_signature(state):
    """
    Create a compact identity for the current game state.

    We intentionally use:

    - current piece
    - current column
    - NEXT queue
    - settled board

    The falling piece itself is removed from the board
    before this signature is created.
    """

    board_data = tuple(
        tuple(row)
        for row in state["board"].grid
    )

    next_queue = tuple(
        state["next_queue"]
    )

    return (
        state["current_piece"],
        state["current_column"],
        next_queue,
        board_data
    )


def quick_state_signature(state):
    """
    Lightweight signature used immediately before execution.

    The settled board is included, but the main focus is
    whether the current piece/queue has changed.
    """

    board_data = tuple(
        tuple(row)
        for row in state["board"].grid
    )

    return (
        state["current_piece"],
        state["current_column"],
        tuple(state["next_queue"]),
        board_data
    )


def states_match(state_a, state_b):
    return (
        make_state_signature(state_a)
        == make_state_signature(state_b)
    )


def start_background_prediction(
    executor,
    state
):
    print(
        "Starting background calculation..."
    )

    started_at = time.perf_counter()

    future = executor.submit(
        calculate_prediction,
        (
            state["board"],
            state["current_piece"],
            state["next_queue"]
        )
    )

    return future, started_at


def get_prediction(future, started_at):

    result = future.result()

    elapsed = (
        time.perf_counter()
        - started_at
    )

    print(
        f"AI calculation time: "
        f"{elapsed:.3f}s"
    )

    return result, elapsed


def verify_before_execution(
    expected_state
):
    """
    Capture the phone again immediately before executing
    the AI move.

    If the game has already advanced, reject the prediction.
    """

    for attempt in range(
        1,
        MAX_STATE_VERIFY_ATTEMPTS + 1
    ):

        actual_state = detect_game_state()

        if actual_state is None:
            time.sleep(
                STATE_VERIFY_DELAY
            )
            continue

        same_piece = (
            actual_state["current_piece"]
            == expected_state["current_piece"]
        )

        same_column = (
            actual_state["current_column"]
            == expected_state["current_column"]
        )

        same_queue = (
            actual_state["next_queue"]
            == expected_state["next_queue"]
        )

        print(
            f"Execution check "
            f"{attempt}/{MAX_STATE_VERIFY_ATTEMPTS}: "
            f"piece={same_piece}, "
            f"column={same_column}, "
            f"queue={same_queue}"
        )

        if (
            same_piece
            and same_column
            and same_queue
        ):
            return actual_state

        print(
            "STATE CHANGED - prediction is stale."
        )

        time.sleep(
            STATE_VERIFY_DELAY
        )

    return None


def main():

    print()
    print("=" * 60)
    print("TETRIS AI - STATE-SAFE REAL PLAYER")
    print("=" * 60)

    controller = ADBController(
        dry_run=False
    )

    executor = ProcessPoolExecutor(
        max_workers=1
    )

    future = None
    future_started_at = None

    try:


        # INITIAL STATE
      

        print()
        print(
            "READING INITIAL GAME STATE..."
        )

        state = detect_stable_game_state()

        if state is None:
            print(
                "Could not detect initial state."
            )
            return

        print()
        print(
            f"Current: "
            f"{state['current_piece']}"
        )

        print(
            f"Column: "
            f"{state['current_column']}"
        )

        print(
            f"NEXT: "
            f"{state['next_queue']}"
        )

        # START INITIAL AI
    

        future, future_started_at = (
            start_background_prediction(
                executor,
                state
            )
        )


        # MAIN LOOP
  

        piece_number = 1

        while piece_number <= MAX_PIECES:

            print()
            print("-" * 60)
            print(
                f"PIECE {piece_number}"
            )
            print("-" * 60)

            # WAIT FOR AI
 

            print(
                "Waiting for AI prediction..."
            )

            best_move, ai_time = (
                get_prediction(
                    future,
                    future_started_at
                )
            )

            if best_move is None:
                print(
                    "AI could not find a move."
                )
                break

            print()
            print(
                "Prediction ready:"
            )

            print(
                f"Piece: "
                f"{state['current_piece']}"
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

            # VERIFY STATE BEFORE EXECUTION
            print()
            print(
                "VERIFYING STATE BEFORE EXECUTION..."
            )

            verified_state = (
                verify_before_execution(
                    state
                )
            )

            if verified_state is None:

                print()
                print(
                    "OLD PREDICTION DISCARDED."
                )

                print(
                    "Reading fresh state..."
                )

                state = detect_stable_game_state()

                if state is None:
                    print(
                        "Could not recover game state."
                    )
                    break

                print(
                    f"Recovered current: "
                    f"{state['current_piece']}"
                )

                print(
                    f"Recovered NEXT: "
                    f"{state['next_queue']}"
                )

                future, future_started_at = (
                    start_background_prediction(
                        executor,
                        state
                    )
                )

                continue

            # Use the freshly verified column.
            state = verified_state

            # BUILD ACTIONS
      
            actions = create_action_plan(
                state["current_piece"],
                best_move["rotation"],
                best_move["column"],
                state["current_column"]
            )

            print()
            print(
                f"Actions: {actions}"
            )

            # FINAL SAFETY CHECK
            final_state = detect_game_state()

            if final_state is None:
                print(
                    "Final state check failed."
                )
                continue

            if not states_match(
                state,
                final_state
            ):
                print()
                print(
                    "STATE CHANGED BEFORE EXECUTION."
                )

                print(
                    "Prediction discarded."
                )

                state = detect_stable_game_state()

                if state is None:
                    break

                future, future_started_at = (
                    start_background_prediction(
                        executor,
                        state
                    )
                )

                continue

            # EXECUTE
            print()
            print(
                "EXECUTING CURRENT MOVE..."
            )

            move_started_at = time.perf_counter()

            controller.execute_plan(
                actions
            )

            move_time = (
                time.perf_counter()
                - move_started_at
            )

            print(
                f"Move execution time: "
                f"{move_time:.3f}s"
            )


            # WAIT FOR NEW PIECE
            print()
            print(
                "WAITING FOR STABLE NEXT PIECE..."
            )

            new_state = (
                detect_stable_game_state()
            )

            if new_state is None:
                print(
                    "Could not detect next state."
                )
                break

            print()
            print(
                f"New current: "
                f"{new_state['current_piece']}"
            )

            print(
                f"New column: "
                f"{new_state['current_column']}"
            )

            print(
                f"New NEXT: "
                f"{new_state['next_queue']}"
            )

            # START NEXT AI IMMEDIATELY
     
            future, future_started_at = (
                start_background_prediction(
                    executor,
                    new_state
                )
            )

            state = new_state

            print(
                "Next AI calculation is running "
                "in the background."
            )

            piece_number += 1

    finally:

        executor.shutdown(
            wait=True
        )

    print()
    print("=" * 60)
    print("STATE-SAFE PLAYER COMPLETE")
    print("=" * 60)


if __name__ == "__main__":
    main()
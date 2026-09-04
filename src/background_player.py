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
from controller import create_action_plan
from adb_controller import ADBController
from background_worker import BackgroundPlanner


MAX_PIECES = 10
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


def detect_game_state():
    filename = capture_screen(
        "background_screen.png"
    )

    image = load_screen(filename)

    raw_board = detect_board(image)

    current_piece_type, current_cells = (
        detect_current_piece(raw_board)
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

    next_queue = detect_next_queue(image)

    return {
        "board": board,
        "current_piece": current_piece_type,
        "current_column": current_column,
        "next_queue": next_queue
    }


def main():

    print()
    print("=" * 60)
    print("TETRIS AI - PIPELINED BACKGROUND PLAYER")
    print("=" * 60)

    controller = ADBController(
        dry_run=True
    )

    planner = BackgroundPlanner()

    try:

     
        # INITIAL STATE


        print()
        print("READING INITIAL GAME STATE...")

        state = detect_game_state()

        if state is None:
            print("Could not detect game state.")
            return

        print(
            f"Current: {state['current_piece']}"
        )

        print(
            f"Current column: "
            f"{state['current_column']}"
        )

        print(
            f"NEXT: {state['next_queue']}"
        )

 
        # START FIRST AI CALCULATION
        print()
        print("STARTING AI IN BACKGROUND...")

        planner.start(
            state["board"],
            state["current_piece"],
            state["next_queue"]
        )


        # MAIN LOOP

        for piece_number in range(
            1,
            MAX_PIECES + 1
        ):

            print()
            print("-" * 60)
            print(
                f"PIECE {piece_number}"
            )
            print("-" * 60)

            # Wait only for the CURRENT move's calculation.
     
            while not planner.ready():

                print(
                    "AI calculating...",
                    end="\r"
                )

                time.sleep(0.05)

            best_move = planner.get_result()

            if best_move is None:
                print(
                    "AI could not find a move."
                )
                break

            print()
            print("CURRENT AI RESULT")

            print(
                f"Rotation: "
                f"{best_move['rotation']}"
            )

            print(
                f"Target column: "
                f"{best_move['column']}"
            )

            print(
                f"Score: "
                f"{best_move['score']:.2f}"
            )

            actions = create_action_plan(
                state["current_piece"],
                best_move["rotation"],
                best_move["column"],
                state["current_column"]
            )

            print(
                f"Actions: {actions}"
            )

   
            # Execute CURRENT move.

            print()
            print("EXECUTING CURRENT MOVE...")

            controller.execute_plan(actions)

            # IMPORTANT:
            #
            # While the phone is performing the move,
            # we immediately start preparing the next
            # state AFTER the move.
            #
            # This is where the pipeline begins.


            print()
            print(
                "Waiting for piece to settle..."
            )

            time.sleep(
                STATE_CHECK_DELAY
            )

   
            # Capture ACTUAL new phone state.
            print(
                "READING NEW PHONE STATE..."
            )

            new_state = detect_game_state()

            if new_state is None:
                print(
                    "Could not detect new game state."
                )
                break

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

            # Start calculating the NEW current piece
            # immediately.
            #
            # We don't calculate it before detecting the
            # actual state because the board may have
            # changed differently from our simulation.

            print()
            print(
                "STARTING NEXT AI CALCULATION..."
            )

            planner.start(
                new_state["board"],
                new_state["current_piece"],
                new_state["next_queue"]
            )

            # Update state.

            state = new_state

            print(
                "Next calculation running in background."
            )

    finally:

        planner.shutdown()

    print()
    print("=" * 60)
    print("PIPELINED PLAYER COMPLETE")
    print("=" * 60)


if __name__ == "__main__":
    main()
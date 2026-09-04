from board import Board
from pieces import PIECES
from background_worker import BackgroundPlanner

def main():
    board = Board()

    planner = BackgroundPlanner()

    print("Starting background AI calculation...")

    planner.start(
        board,
        "T",
        ["S", "I", "O"]
    )

    print("AI is calculating in the background...")
    while not planner.ready():
        pass

    result = planner.get_result()

    print()
    print("BACKGROUND RESULT")
    print(result)

    planner.shutdown()

if __name__ == "__main__":
    main()

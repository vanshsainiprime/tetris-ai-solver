from concurrent.futures import ProcessPoolExecutor


def calculate_prediction(args):
    """
    Run AI calculation in a separate process.

    This keeps heavy AI computation away from
    the main game-control loop.
    """

    from ai import find_best_move
    from pieces import PIECES

    board, current_piece, next_queue = args

    future_rotations = []

    for piece_type in next_queue:
        if piece_type in PIECES:
            future_rotations.append(
                PIECES[piece_type]
            )

    return find_best_move(
        board,
        PIECES[current_piece],
        future_rotations
    )


class BackgroundPlanner:

    def __init__(self):
        self.executor = ProcessPoolExecutor(
            max_workers=1
        )

        self.future = None

    def start(
        self,
        board,
        current_piece,
        next_queue
    ):
        """
        Start AI calculation in the background.
        """

        self.future = self.executor.submit(
            calculate_prediction,
            (
                board,
                current_piece,
                next_queue
            )
        )

    def ready(self):
        """
        Check whether the calculation is finished.
        """

        if self.future is None:
            return False

        return self.future.done()

    def get_result(self):
        """
        Get the calculated AI move.
        """

        if self.future is None:
            return None

        if not self.future.done():
            return None

        return self.future.result()

    def shutdown(self):
        """
        Stop the background worker.
        """

        self.executor.shutdown(
            wait=True
        )

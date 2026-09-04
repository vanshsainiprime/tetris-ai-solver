from ai import find_best_move
from controller import create_action_plan
from pieces import PIECES
from simulator import simulate_move
from board import Board


class RollingPlanner:

    def __init__(self):
        self.predictions = []

    def clear(self):
        self.predictions = []

    def _copy_board(self, board):
        new_board = Board()

        for row in range(Board.HEIGHT):
            for column in range(Board.WIDTH):
                new_board.grid[row][column] = (
                    board.grid[row][column]
                )

        return new_board

    def _simulate_move(
        self,
        board,
        piece_type,
        rotation,
        column
    ):
        piece = PIECES[piece_type][rotation]

        result = simulate_move(
            board,
            piece,
            column
        )

        if result is None:
            return None

        new_board, lines_cleared = result

        return new_board

    def _calculate_move(
        self,
        board,
        piece_type,
        future_queue
    ):
        if piece_type not in PIECES:
            return None

        future_rotations = []

        for next_piece in future_queue:

            if next_piece in PIECES:
                future_rotations.append(
                    PIECES[next_piece]
                )

        return find_best_move(
            board,
            PIECES[piece_type],
            future_rotations
        )

    def build_predictions(
        self,
        board,
        current_piece,
        current_column,
        next_queue
    ):
        """
        Build a predicted chain:

        Current -> NEXT1 -> NEXT2 -> NEXT3

        Every prediction stores:

        - piece
        - rotation
        - target column
        - score
        - actions
        - predicted board after the move
        """

        self.clear()
        predicted_board = self._copy_board(
            board
        )
        sequence = [
            current_piece
        ]

        for piece_type in next_queue:

            if piece_type in PIECES:
                sequence.append(
                    piece_type
                )

        for index, piece_type in enumerate(
            sequence
        ):

            future_queue = sequence[
                index + 1:
            ]
            best_move = self._calculate_move(
                predicted_board,
                piece_type,
                future_queue
            )
            if best_move is None:
                break

            if index == 0:
                spawn_column = current_column
            else:
                # Future pieces are assumed to start
                # from the normal center spawn position.
                piece = PIECES[piece_type][0]
                piece_columns = [
                    column
                    for row, column in piece
                ]

                piece_width = (
                    max(piece_columns) + 1
                )

                spawn_column = (
                    Board.WIDTH - piece_width
                ) // 2

            actions = create_action_plan(
                piece_type,
                best_move["rotation"],
                best_move["column"],
                spawn_column
            )

            predicted_board_after_move = (
                self._simulate_move(
                    predicted_board,
                    piece_type,
                    best_move["rotation"],
                    best_move["column"]
                )
            )

            if predicted_board_after_move is None:
                break

            prediction = {
                "piece": piece_type,
                "rotation": best_move["rotation"],
                "column": best_move["column"],
                "score": best_move["score"],
                "actions": actions,
                "board_before": self._copy_board(
                    predicted_board
                ),
                "board_after": self._copy_board(
                    predicted_board_after_move
                )
            }

            self.predictions.append(
                prediction
            )

            predicted_board = (
                predicted_board_after_move
            )

        return self.predictions

    def get_current_prediction(self):

        if not self.predictions:
            return None

        return self.predictions[0]

    def consume_current_prediction(self):

        if not self.predictions:
            return None

        return self.predictions.pop(0)

    def get_predictions(self):

        return self.predictions
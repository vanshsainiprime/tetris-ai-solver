class Board:
    WIDTH = 10
    HEIGHT = 20

    def __init__(self):
        self.grid = [
            [0 for _ in range(self.WIDTH)]
            for _ in range(self.HEIGHT)
        ]

    def print_board(self):
        for row in self.grid:
            print(
                " ".join(
                    "⬛" if cell else "⬜"
                    for cell in row
                )
            )

    def set_cell(self, row, column, value=1):
        self.grid[row][column] = value

    def can_place(self, piece, row, column):
        """
        Check whether a piece can be placed
        at the specified position.
        """

        for piece_row, piece_column in piece:

            board_row = row + piece_row
            board_column = column + piece_column

            # Outside left/right
            if board_column < 0 or board_column >= self.WIDTH:
                return False

            # Outside top/bottom
            if board_row < 0 or board_row >= self.HEIGHT:
                return False

            # Collision with existing block
            if self.grid[board_row][board_column] != 0:
                return False

        return True

    def get_drop_row(self, piece, column):
        """
        Find the lowest valid row for a piece.
        """

        row = 0

        while self.can_place(piece, row + 1, column):
            row += 1

        return row

    def place_piece(self, piece, row, column):
        """
        Place a piece onto the board.
        """

        if not self.can_place(piece, row, column):
            return False

        for piece_row, piece_column in piece:

            board_row = row + piece_row
            board_column = column + piece_column

            self.grid[board_row][board_column] = 1

        return True

    def clear_lines(self):
        """
        Remove every completely filled row.

        Returns:
            int: Number of lines cleared.
        """

        new_grid = []
        lines_cleared = 0

        for row in self.grid:

            # If every cell is occupied,
            # this row is complete.
            if all(cell != 0 for cell in row):
                lines_cleared += 1

            else:
                new_grid.append(row)

        # Add empty rows at the top
        while len(new_grid) < self.HEIGHT:
            new_grid.insert(0, [0] * self.WIDTH)

        self.grid = new_grid

        return lines_cleared
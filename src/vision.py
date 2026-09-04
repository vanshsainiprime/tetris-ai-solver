import cv2
import numpy as np


# BOARD CALIBRATION


REFERENCE_WIDTH = 917
REFERENCE_HEIGHT = 2048

REFERENCE_LEFT = 167
REFERENCE_TOP = 518
REFERENCE_RIGHT = 750
REFERENCE_BOTTOM = 1659

BOARD_WIDTH = 10
BOARD_HEIGHT = 20


LEFT_RATIO = REFERENCE_LEFT / REFERENCE_WIDTH
TOP_RATIO = REFERENCE_TOP / REFERENCE_HEIGHT
RIGHT_RATIO = REFERENCE_RIGHT / REFERENCE_WIDTH
BOTTOM_RATIO = REFERENCE_BOTTOM / REFERENCE_HEIGHT


# NEXT QUEUE CALIBRATION


# Approximate NEXT panel in the reference screenshot.

NEXT_LEFT = 776
NEXT_RIGHT = 885

NEXT_TOP = 620
NEXT_BOTTOM = 915


# SCREEN

def load_screen(filename):
    """
    Load a phone screenshot.
    """

    image = cv2.imread(filename)

    if image is None:
        raise FileNotFoundError(
            f"Could not load image: {filename}"
        )

    return image


def get_screen_size(image):
    """
    Return screen width and height.
    """

    height, width = image.shape[:2]

    return width, height


def get_board_coordinates(image):
    """
    Calculate board coordinates for the actual
    screenshot resolution.
    """

    height, width = image.shape[:2]

    left = int(width * LEFT_RATIO)
    top = int(height * TOP_RATIO)

    right = int(width * RIGHT_RATIO)
    bottom = int(height * BOTTOM_RATIO)

    return left, top, right, bottom


# BOARD GEOMETRY


def get_board(image):
    """
    Crop the Tetris board.
    """

    left, top, right, bottom = (
        get_board_coordinates(image)
    )

    return image[
        top:bottom,
        left:right
    ]


def get_cell_bounds(image, row, column):
    """
    Get pixel boundaries of one board cell.
    """

    left, top, right, bottom = (
        get_board_coordinates(image)
    )

    board_width = right - left
    board_height = bottom - top

    cell_width = board_width / BOARD_WIDTH
    cell_height = board_height / BOARD_HEIGHT

    x0 = int(
        left + column * cell_width
    )

    x1 = int(
        left + (column + 1) * cell_width
    )

    y0 = int(
        top + row * cell_height
    )

    y1 = int(
        top + (row + 1) * cell_height
    )

    return x0, y0, x1, y1


def get_cell_region(image, row, column):
    """
    Get the central portion of a board cell.
    """

    x0, y0, x1, y1 = get_cell_bounds(
        image,
        row,
        column
    )

    width = x1 - x0
    height = y1 - y0

    margin_x = int(width * 0.25)
    margin_y = int(height * 0.25)

    return image[
        y0 + margin_y:y1 - margin_y,
        x0 + margin_x:x1 - margin_x
    ]


# COLOR DETECTION


def get_cell_hsv(image, row, column):
    """
    Get the median HSV values from a cell.
    """

    cell = get_cell_region(
        image,
        row,
        column
    )

    hsv = cv2.cvtColor(
        cell,
        cv2.COLOR_BGR2HSV
    )

    h = float(
        np.median(hsv[:, :, 0])
    )

    s = float(
        np.median(hsv[:, :, 1])
    )

    v = float(
        np.median(hsv[:, :, 2])
    )

    return h, s, v


def classify_color(hue):
    """
    Convert OpenCV hue into a Tetris piece type.
    """

    if hue < 8 or hue >= 170:
        return "Z"

    if 8 <= hue < 20:
        return "L"

    if 20 <= hue < 40:
        return "O"

    if 40 <= hue < 85:
        return "S"

    if 85 <= hue < 105:
        return "I"

    if 105 <= hue < 130:
        return "J"

    if 130 <= hue < 170:
        return "T"

    return "?"


def get_cell_type(image, row, column):
    """
    Detect the piece type inside one board cell.
    """

    hue, saturation, brightness = get_cell_hsv(
        image,
        row,
        column
    )

    if brightness < 170:
        return "."

    if saturation < 80:
        return "."

    return classify_color(hue)



# BOARD DETECTION


def detect_board(image):
    """
    Detect every colored cell on the board.
    """

    board = []

    for row in range(BOARD_HEIGHT):

        board_row = []

        for column in range(BOARD_WIDTH):

            piece_type = get_cell_type(
                image,
                row,
                column
            )

            board_row.append(
                piece_type
            )

        board.append(
            board_row
        )

    return board


# CURRENT PIECE

def find_colored_components(board):
    """
    Find connected groups of colored cells.
    """

    visited = set()
    components = []

    for row in range(BOARD_HEIGHT):

        for column in range(BOARD_WIDTH):

            if board[row][column] == ".":
                continue

            if (row, column) in visited:
                continue

            queue = [
                (row, column)
            ]

            visited.add(
                (row, column)
            )

            component = []

            while queue:

                current_row, current_column = (
                    queue.pop(0)
                )

                component.append(
                    (
                        current_row,
                        current_column
                    )
                )

                neighbors = [
                    (
                        current_row - 1,
                        current_column
                    ),
                    (
                        current_row + 1,
                        current_column
                    ),
                    (
                        current_row,
                        current_column - 1
                    ),
                    (
                        current_row,
                        current_column + 1
                    )
                ]

                for nr, nc in neighbors:

                    if not (
                        0 <= nr < BOARD_HEIGHT
                        and
                        0 <= nc < BOARD_WIDTH
                    ):
                        continue

                    if (nr, nc) in visited:
                        continue

                    if board[nr][nc] == ".":
                        continue

                    visited.add(
                        (nr, nc)
                    )

                    queue.append(
                        (nr, nc)
                    )

            components.append(
                component
            )

    return components


def detect_current_piece(board):
    """
    Detect the uppermost colored component as
    the current falling piece.
    """

    components = find_colored_components(
        board
    )

    if not components:
        return None, []

    components.sort(
        key=lambda component: min(
            row
            for row, column in component
        )
    )

    current_component = components[0]

    piece_types = []

    for row, column in current_component:

        piece_types.append(
            board[row][column]
        )

    piece_type = max(
        set(piece_types),
        key=piece_types.count
    )

    return piece_type, current_component


def remove_current_piece(
    board,
    current_component
):
    """
    Remove the current falling piece.
    """

    result = [
        row.copy()
        for row in board
    ]

    for row, column in current_component:

        result[row][column] = "."

    return result


# NEXT QUEUE

def get_next_region(image):
    """
    Crop the NEXT queue area.
    """

    height, width = image.shape[:2]

    scale_x = width / REFERENCE_WIDTH
    scale_y = height / REFERENCE_HEIGHT

    left = int(NEXT_LEFT * scale_x)
    right = int(NEXT_RIGHT * scale_x)

    top = int(NEXT_TOP * scale_y)
    bottom = int(NEXT_BOTTOM * scale_y)

    return image[
        top:bottom,
        left:right
    ]


def detect_next_queue(image):
    """
    Detect the 3 upcoming Tetris pieces.

    The game displays three NEXT pieces.

    Most pieces can be identified directly from their hue.
    J is special because it is blue, very similar to the
    blue NEXT background. If no other piece color is found
    inside a slot, that slot is treated as J.
    """

    region = get_next_region(image)

    hsv = cv2.cvtColor(
        region,
        cv2.COLOR_BGR2HSV
    )

    height, width = region.shape[:2]

    # Divide the NEXT panel into 3 slots.

    slot_height = height / 3

    pieces = []

    for slot_index in range(3):

        y0 = int(
            slot_index * slot_height
        )

        y1 = int(
            (slot_index + 1) * slot_height
        )

        slot = hsv[
            y0:y1,
            :
        ]

        if slot.size == 0:
            pieces.append("?")
            continue

        hue = slot[:, :, 0]
        saturation = slot[:, :, 1]
        brightness = slot[:, :, 2]

        # Ignore the blue background by looking for the
        # characteristic hue of every NON-J piece.
        #
        # We don't require high brightness because the
        # upcoming pieces can be dimmed.

        color_masks = {

            "Z": (
                (
                    (hue < 8)
                    |
                    (hue >= 170)
                )
                &
                (saturation > 100)
            ),

            "L": (
                (hue >= 8)
                &
                (hue < 20)
                &
                (saturation > 100)
            ),

            "O": (
                (hue >= 20)
                &
                (hue < 40)
                &
                (saturation > 100)
            ),

            "S": (
                (hue >= 40)
                &
                (hue < 85)
                &
                (saturation > 100)
            ),

            "I": (
                (hue >= 85)
                &
                (hue < 105)
                &
                (saturation > 100)
            ),

            "T": (
                (hue >= 130)
                &
                (hue < 170)
                &
                (saturation > 100)
            )
        }

        # Count pixels for each non-blue piece color.

        scores = {}

        for piece_type, mask in color_masks.items():

            scores[piece_type] = int(
                np.count_nonzero(mask)
            )

        # Find strongest non-blue color.

        best_piece = max(
            scores,
            key=scores.get
        )

        best_score = scores[best_piece]


        # If a meaningful non-blue color exists, use it.

        if best_score >= 20:

            pieces.append(
                best_piece
            )

        else:

            # No recognizable non-blue color.
            #
            # In this game the remaining blue Tetrimino
            # is J.


            pieces.append("J")

    return pieces

# PRINTING


def print_detected_board(board):
    """
    Print a board.
    """

    print()
    print("BOARD")
    print("-" * 22)

    for row in board:

        print(
            "|"
            + "".join(row)
            + "|"
        )

    print("-" * 22)


def print_piece(piece_type, cells):
    """
    Print the current piece.
    """

    print()
    print("CURRENT PIECE")

    if piece_type is None:
        print("None")
        return

    print("Type:", piece_type)
    print("Cells:", cells)


def print_next_queue(pieces):
    """
    Print the detected NEXT queue.
    """

    print()
    print("NEXT QUEUE")

    if not pieces:

        print("None detected")
        return

    for index, piece in enumerate(
        pieces,
        start=1
    ):

        print(
            f"{index}: {piece}"
        )


def print_legend():
    """
    Print the color legend.
    """

    print()
    print("Legend:")
    print(". = empty")
    print("I = cyan")
    print("O = yellow")
    print("T = purple")
    print("S = green")
    print("Z = red")
    print("J = blue")
    print("L = orange")
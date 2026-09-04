from pieces import PIECES


def calculate_horizontal_moves(
    current_column,
    target_column
):
    """
    Move from the detected current column
    directly toward the AI target column.
    """

    difference = target_column - current_column

    if difference < 0:
        return "LEFT", abs(difference)

    if difference > 0:
        return "RIGHT", difference

    return "NONE", 0


def get_rotation_taps(
    piece_type,
    rotation
):
    """
    Convert AI rotation index into counter-clockwise
    taps used by the actual game.
    """

    rotations = PIECES[piece_type]

    count = len(rotations)

    if count == 1:
        return 0

    return (-rotation) % count


def create_action_plan(
    piece_type,
    rotation,
    target_column,
    current_column
):
    """
    Convert an AI decision into game actions.
    """

    rotations = PIECES[piece_type]

    if rotation < 0 or rotation >= len(rotations):
        raise ValueError(
            "Invalid rotation index."
        )

    actions = []

    # Rotation
    rotation_taps = get_rotation_taps(
        piece_type,
        rotation
    )

    for _ in range(rotation_taps):
        actions.append("ROTATE")

    # Horizontal movement
    direction, amount = calculate_horizontal_moves(
        current_column,
        target_column
    )

    for _ in range(amount):
        actions.append(direction)

    # Drop
    actions.append("DROP")

    return actions


def print_action_plan(
    piece_type,
    rotation,
    target_column,
    current_column,
    actions
):
    print()
    print("=" * 45)
    print("ACTION PLAN")
    print("=" * 45)

    print(
        f"Piece: {piece_type}"
    )

    print(
        f"Current column: {current_column}"
    )

    print(
        f"Target column: {target_column}"
    )

    print(
        f"AI rotation: {rotation}"
    )

    print()

    for number, action in enumerate(
        actions,
        start=1
    ):
        print(
            f"{number}. {action}"
        )

    print("=" * 45)
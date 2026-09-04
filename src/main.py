from vision import (
    load_screen,
    detect_board,
    detect_current_piece,
    remove_current_piece,
    detect_next_queue,
    print_detected_board,
    print_piece,
    print_next_queue,
    print_legend
)

# LOAD SCREENSHOT
filename = "phone_screen.png"

image = load_screen(filename)


# DETECT BOARD

raw_board = detect_board(
    image
)



# DETECT CURRENT PIECE


current_piece, current_cells = (
    detect_current_piece(
        raw_board
    )
)



# REMOVE CURRENT PIECE


settled_board = remove_current_piece(
    raw_board,
    current_cells
)


# DETECT NEXT QUEUE


next_queue = detect_next_queue(
    image
)

# PRINT RESULTS

print_detected_board(
    raw_board
)

print_piece(
    current_piece,
    current_cells
)

print_detected_board(
    settled_board
)

print_next_queue(
    next_queue
)

print_legend()
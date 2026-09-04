from phone import capture_screen
from vision import load_screen, detect_next_queue


def main():
    print("Capturing fresh phone screen...")

    filename = capture_screen(
        "live_screen.png"
    )

    image = load_screen(
        filename
    )

    next_queue = detect_next_queue(
        image
    )
    print()
    print("FRESH NEXT QUEUE")
    print("=" * 30)

    for index, piece in enumerate(
        next_queue,
        start=1
    ):
        print(
            f"{index}: {piece}"
        )

    print("=" * 30)


if __name__ == "__main__":
    main()
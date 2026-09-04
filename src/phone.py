import subprocess


def capture_screen(output_file="phone_screen.png"):
    """
    Capture the Android phone's current screen
    and save it as an image.
    """

    command = [
        "adb",
        "exec-out",
        "screencap",
        "-p"
    ]

    with open(output_file, "wb") as file:
        subprocess.run(
            command,
            stdout=file,
            check=True
        )
    return output_file
import subprocess
import time


class ADBController:

    def __init__(self, dry_run=True):
        self.dry_run = dry_run

    def run_adb(self, *args):

        command = ["adb", *args]

        if self.dry_run:

            print(
                "[DRY RUN]",
                " ".join(command)
            )

            return

        subprocess.run(
            command,
            check=True
        )

    def left(self):

        self.run_adb(
            "shell",
            "input",
            "swipe",
            "540",
            "1200",
            "440",
            "1200",
            "250"
        )

    def right(self):

        self.run_adb(
            "shell",
            "input",
            "swipe",
            "440",
            "1200",
            "540",
            "1200",
            "250"
        )

    def rotate(self):

        self.run_adb(
            "shell",
            "input",
            "tap",
            "540",
            "700"
        )

    def drop(self):

        self.run_adb(
            "shell",
            "input",
            "swipe",
            "540",
            "700",
            "540",
            "1200",
            "250"
        )

    def wait(self, seconds=0.15):

        time.sleep(seconds)

    def execute_action(self, action):

        if action == "LEFT":

            self.left()

        elif action == "RIGHT":

            self.right()

        elif action == "ROTATE":

            self.rotate()

        elif action == "DROP":

            self.drop()

        else:

            raise ValueError(
                f"Unknown action: {action}"
            )

    def execute_plan(self, actions):

        for action in actions:

            self.execute_action(
                action
            )

            self.wait(0.15)
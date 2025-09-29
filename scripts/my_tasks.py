from fireworks import Firework, FWorker, LaunchPad
from fireworks.core.rocket_launcher import launch_rocket, rapidfire
from tasks import ImageTask, ImageToPDFTask
from fireworks.fw_config import USER_PACKAGES
import os
from pathlib import Path

if __name__ == "__main__":
    launchpad = LaunchPad(
        host=os.getenv("MONGODB_OCR_DEVELOPMENT_CONN_STRING"),
        name="fireworks",
        uri_mode=True,
    )
    launchpad.reset("")
    raw_dir = Path("./data/raw")

    for dir in raw_dir.iterdir():
        if dir.is_dir():  # only process directories
            firework = Firework(
                [ImageTask(), ImageToPDFTask()],
                spec={"barcode_dir": str(dir.resolve())},  # full absolute path
                name="OCR Pipeline",
            )

            # Store workflow and launch it locally
            launchpad.add_wf(firework)
    rapidfire(launchpad, FWorker())

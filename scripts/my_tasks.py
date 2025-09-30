import os
from pathlib import Path

from fireworks import Firework, FWorker, LaunchPad
from fireworks.core.rocket_launcher import rapidfire
from fireworks.queue import queue_adapter
from digitask import ImageTask, ImageToPDFTask

if __name__ == "__main__":
    launchpad = LaunchPad(
        host=os.getenv("MONGODB_OCR_DEVELOPMENT_CONN_STRING"),
        name="fireworks",
        uri_mode=True,
    )
    launchpad.reset("")
    raw_dir = Path("./data/raw")
    q = queue_adapter.QScriptTemplate()
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

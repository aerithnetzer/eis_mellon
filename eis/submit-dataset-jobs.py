import glob
import os
from pathlib import Path

import typer

app = typer.Typer()

SCRATCH_DIR = Path("/your/scratch/dir")  # replace with your actual path


def main(parent_dir: str):
    yml_file_paths = glob.iglob(str(SCRATCH_DIR / "**/meta.yml"), recursive=True)

    for f in yml_file_paths:
        parent_abs = os.path.abspath(os.path.dirname(f))
        print("Absolute path of parent directory:", parent_abs)


if __name__ == "__main__":
    app()

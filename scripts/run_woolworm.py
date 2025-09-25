from argparse import ArgumentParser
from pathlib import Path
import subprocess
import sys

from loguru import logger
from woolworm import Woolworm

parser = ArgumentParser(prog="Woolworm on a bunch o' stuff.")
parser.add_argument("barcode_dir", help="Parent directory containing a JP2000 subdirectory")
args = parser.parse_args()
barcode_dir = Path(args.barcode_dir)


def run_woolworm_job(barcode_dir: Path):
    """Process all JP2s in the JP2000 directory, then run MARKER."""
    jp2000_directory = barcode_dir / "JP2000"
    if not jp2000_directory.exists() or not jp2000_directory.is_dir():
        logger.error(f"{jp2000_directory} does not exist or is not a directory")
        sys.exit(1)

    output_dir = barcode_dir.parent / "WOOLWORM_OUTPUT"
    output_dir.mkdir(exist_ok=True)

    jp2_files = sorted(jp2000_directory.glob("*.jp2"))
    if not jp2_files:
        logger.warning(f"No JP2 files in {jp2000_directory}")
        return

    logger.info(f"Running Woolworm on {len(jp2_files)} images in {jp2000_directory}")
    for jp2_file in jp2_files:
        out_file = output_dir / f"{jp2_file.stem}.jpg"
        Woolworm.Pipelines.process_image(
            input_file_path=str(jp2_file),
            output_file_path=str(out_file),
        )

    logger.info(f"Running MARKER on {output_dir}")
    subprocess.run(["marker", str(output_dir)], check=True)


if __name__ == "__main__":
    run_woolworm_job(barcode_dir)

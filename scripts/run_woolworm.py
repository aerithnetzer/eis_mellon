from argparse import ArgumentParser
import glob
import os
from pathlib import Path
import sys

from loguru import logger
from PIL import Image
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

    # Get sorted list of all .jpg files in current directory
    jpg_files = sorted(glob.glob("*.jpg"))

    # Open images and convert to RGB (needed for PDF)
    images = [Image.open(f).convert("RGB") for f in jpg_files]

    if images:
        # Save first image and append the rest as pages
        pdf_path = os.path.join(output_dir, "WOOLWORM.pdf")
        images[0].save(pdf_path, save_all=True, append_images=images[1:])
        print(f"PDF saved as {pdf_path}")
    else:
        print("No .jpg files found in current directory.")


if __name__ == "__main__":
    run_woolworm_job(barcode_dir)

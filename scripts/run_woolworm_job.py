import os
import sys
from pathlib import Path
import subprocess
from woolworm import Woolworm
from loguru import logger


def run_woolworm_job(jp2_dir: Path):
    """Process all JP2s in one JP2000 directory, then run MARKER."""
    if not jp2_dir.exists() or not jp2_dir.is_dir():
        logger.error(f"{jp2_dir} does not exist or is not a directory")
        sys.exit(1)

    work_dir = jp2_dir.parent
    output_dir = work_dir / "WOOLWORM_OUTPUT"
    output_dir.mkdir(exist_ok=True)

    jp2_files = sorted(jp2_dir.glob("*.jp2"))
    if not jp2_files:
        logger.warning(f"No JP2 files in {jp2_dir}")
        return

    logger.info(f"Running Woolworm on {len(jp2_files)} images in {jp2_dir}")
    for jp2_file in jp2_files:
        out_file = output_dir / f"{jp2_file.stem}.jpg"
        Woolworm.Pipelines.ProcessImage(input_file=str(jp2_file), output_file=str(out_file))

    logger.info(f"Running MARKER on {output_dir}")
    subprocess.run(["marker", str(output_dir)], check=True)


if __name__ == "__main__":
    jp2_dir = Path(sys.argv[1])
    run_woolworm_job(jp2_dir)

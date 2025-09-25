import os
import argparse
import subprocess
from loguru import logger


def hyperprint():
    parser = argparse.ArgumentParser(description="Batch process JP2 with woolworm and run marker")
    parser.add_argument("parent_dir", help="Parent directory containing barcode subdirectories")
    parser.add_argument("--account", required=True, help="SLURM account name")
    args = parser.parse_args()

    parent_dir = args.parent_dir
    if not os.path.exists(parent_dir):
        raise FileNotFoundError(f"Parent directory {parent_dir} does not exist.")
    logger.info(f"Parent directory is {parent_dir}")
    for i, name in enumerate(os.listdir(parent_dir)):
        barcode_dir = os.path.join(parent_dir, name)
        logger.info(f"barcode_dir directory is {barcode_dir}")
        if not os.path.isdir(barcode_dir):
            continue

        jp2_dir = os.path.join(barcode_dir, "JP2000")
        if not os.path.exists(jp2_dir):
            print(f"Skipping {barcode_dir}, no JP2000 directory found")
            continue

        woolworm_output_dir = os.path.join(barcode_dir, "WOOLWORM_OUTPUT")
        marker_output_dir = os.path.join(barcode_dir, "MARKER_OUTPUT")

        logger.info(f"Woolworm output dir {woolworm_output_dir}")
        logger.info(f"Marker output dir {marker_output_dir}")
        os.makedirs(woolworm_output_dir, exist_ok=True)
        os.makedirs(marker_output_dir, exist_ok=True)

        # Count JP2s for SLURM time estimate
        jp2_files = [f for f in os.listdir(jp2_dir) if f.lower().endswith(".jp2")]
        logger.info(f"{len(jp2_files)} found.")
        total_seconds = len(jp2_files) * 45
        hours = total_seconds // 3600
        minutes = (total_seconds % 3600) // 60
        seconds = total_seconds % 60
        slurm_time = f"{hours}:{minutes:02}:{seconds:02}"
        print(f"Slurm time is: {slurm_time}")
        # SLURM script runs Woolworm then Marker
        SLURM_TEMPLATE = rf"""#!/bin/bash
#SBATCH --account={args.account}
#SBATCH --partition=gengpu
#SBATCH --gres=gpu:1
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=4
#SBATCH --job-name=Hyperprint-{i:05d}
#SBATCH --time={slurm_time}
#SBATCH --mem=16GB
#SBATCH --output=output-%j.out
#SBATCH --error=error-%j.err

module purge

echo "Running Woolworm on JP2 files"
uv run ./scripts/run_woolworm.py {parent_dir}

echo "Running Marker on Woolworm output"

uv run marker "{woolworm_output_dir}" --output_dir="{marker_output_dir}"
"""

        script_path = f"submit_{name}.sh"
        with open(script_path, "w") as f:
            f.write(SLURM_TEMPLATE)

        subprocess.run(["sbatch", script_path])
        os.remove(script_path)


if __name__ == "__main__":
    hyperprint()

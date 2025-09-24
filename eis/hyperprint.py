import argparse
import os
import subprocess


def hyperprint():
    parser = argparse.ArgumentParser(description="Batch submit woolworm jobs")
    parser.add_argument("parent_dir", help="Parent directory containing barcode subdirectories")
    args = parser.parse_args()

    parent_dir = args.parent_dir
    if not os.path.exists(parent_dir):
        raise FileNotFoundError(f"Parent directory {parent_dir} does not exist.")

    for i, name in enumerate(os.listdir(parent_dir)):
        barcode_dir = os.path.join(parent_dir, name)
        if not os.path.isdir(barcode_dir):
            continue

        jp2_dir = os.path.join(barcode_dir, "JP2000")
        if not os.path.exists(jp2_dir):
            print(f"Skipping {barcode_dir}, no JP2000 directory found")
            continue

        # Count JPGs
        jp2_count = sum(
            len([f for f in files if f.endswith(".jpg")]) for _, _, files in os.walk(jp2_dir)
        )
        total_seconds = jp2_count * 30
        hours = total_seconds // 3600
        minutes = (total_seconds % 3600) // 60
        seconds = total_seconds % 60
        slurm_time = f"{hours}:{minutes:02}:{seconds:02}"

        marker_output_dir = os.path.join(barcode_dir, "MARKER_OUTPUT")

        # Raw f-string to preserve bash $/{} syntax
        SLURM_TEMPLATE = rf"""#!/bin/bash
#SBATCH --partition=gengpu
#SBATCH --gres=gpu:1
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=4
#SBATCH --job-name=Hyperprint-{i:05d}
#SBATCH --time={slurm_time}
#SBATCH --mem=16GB
#SBATCH --output=output-%j.out
#SBATCH --error=error-%j.err

NUM_DEVICES=1
NUM_WORKERS=8
module purge
uv run marker "{jp2_dir}" --output_dir="{marker_output_dir}"
"""

        script_path = f"submit_{name}.sh"
        with open(script_path, "w") as f:
            f.write(SLURM_TEMPLATE)

        subprocess.run(["sbatch", script_path])
        os.remove(script_path)


if __name__ == "__main__":
    hyperprint()

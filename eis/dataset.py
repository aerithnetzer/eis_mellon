from pathlib import Path
import shutil
import subprocess

import boto3
from loguru import logger
from tqdm import tqdm
import typer

app = typer.Typer()

SCRATCH_DIR = Path("/scratch/ysc4337/eis_mellon")  # adjust as needed


def list_all_s3_objects(s3_client, bucket: str, prefix: str = "") -> list[str]:
    """Recursively list all object keys in the S3 bucket under prefix."""
    keys = []
    paginator = s3_client.get_paginator("list_objects_v2")
    for page in paginator.paginate(Bucket=bucket, Prefix=prefix):
        for obj in page.get("Contents", []):
            keys.append(obj["Key"])
    return keys


def sync_to_scratch(bucket: str, s3_dir: str) -> Path:
    """Sync the S3 directory to local scratch and prepare PROCESSED_JP2000."""
    local_path = SCRATCH_DIR / s3_dir.strip("/")
    local_path.mkdir(parents=True, exist_ok=True)

    cmd = ["aws", "s3", "sync", f"s3://{bucket}/{s3_dir}", str(local_path)]
    logger.info(f"Syncing {s3_dir} to {local_path}")
    subprocess.run(cmd, check=True)

    # Create PROCESSED_JP2000 directory
    processed_dir = local_path / "PROCESSED_JP2000"
    processed_dir.mkdir(exist_ok=True)

    # Copy JP2000 contents if exists
    jp2000_dir = local_path / "JP2000"
    if jp2000_dir.exists() and jp2000_dir.is_dir():
        for item in jp2000_dir.iterdir():
            dest = processed_dir / item.name
            if item.is_dir():
                shutil.copytree(item, dest, dirs_exist_ok=True)
            else:
                shutil.copy2(item, dest)
        logger.info(f"Copied contents of {jp2000_dir} to {processed_dir}")

    return local_path


def run_workflow(local_path: Path):
    logger.info(f"Running workflow for {local_path}...")


@app.command()
def main(bucket: str, root_prefix: str = ""):
    """
    Recursively scan S3 bucket for meta.yml files.
    For each meta.yml, treat its parent directory as the barcode.
    Sync barcode directory to scratch if JP2000 exists,
    create PROCESSED_JP2000, and copy JP2000 contents into it.
    """
    s3_client = boto3.client("s3")
    all_keys = list_all_s3_objects(s3_client, bucket, root_prefix)

    # Filter for meta.yml files
    meta_keys = [k for k in all_keys if k.endswith("meta.yml")]
    logger.info(f"Found {len(meta_keys)} meta.yml files.")

    for meta_key in tqdm(meta_keys, desc="Processing works"):
        barcode_dir = str(Path(meta_key).parent)  # parent directory is the barcode
        jp2000_key_prefix = f"{barcode_dir}/JP2000"

        # Check if JP2000 exists
        if any(k.startswith(jp2000_key_prefix) for k in all_keys):
            local_path = sync_to_scratch(bucket, barcode_dir)
            run_workflow(local_path)
        else:
            logger.warning(f"No JP2000 found for barcode {barcode_dir}, skipping.")


if __name__ == "__main__":
    app()

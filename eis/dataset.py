from pathlib import Path
from woolworm import Woolworm
from loguru import logger
import typer
import os
from tqdm import tqdm

app = typer.Typer()


@app.command()
def main(input_path: Path):
    try:
        assert os.path.isdir(input_path)
    except AssertionError:
        logger.critical("Input path is not a directory!")
        raise ValueError("Input path is not a directory")

    logger.info("Starting job")
    jp2_dir = os.path.join(input_path, "JP2000")
    logger.info(f"JP2 Directory: {jp2_dir}")

    jp2_files = sorted(Path(jp2_dir).glob("*.jpg"))
    logger.info(f"Found {len(jp2_files)} JP2 files")

    for f in tqdm(jp2_files, desc="Transforming documents"):
        # create parallel WOOLWORM dir
        o = Path(str(f).replace("JP2000", "WOOLWORM")).with_suffix(".png")
        os.makedirs(o.parent, exist_ok=True)

        Woolworm.Pipelines.process_image(str(f), str(o))

        # sanity check
        if not o.exists() or o.stat().st_size == 0:
            logger.error(f"Output file not created properly: {o}")
            continue

        text = Woolworm.ocr(str(o))
        text = str(text)

        md_out = o.with_suffix(".md")
        with open(md_out, "w", encoding="utf-8") as mdfile:
            mdfile.write(text)

    logger.info("Processing complete")


if __name__ == "__main__":
    app()

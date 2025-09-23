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
    except ValueError:
        logger.critical("Input path is not a directory!")
        raise ValueError
    logger.info("Starting job")
    jp2_dir = os.path.join(input_path, "JP2000")
    jp2_files = os.listdir(jp2_dir)
    jp2_files = sorted(jp2_files)
    for f in tqdm(jp2_files, desc="Transforming documents"):
        o = f.replace("JP2000", "WOOLWORM")
        o = f.replace(".jp2", ".png")
        os.makedirs(o, exist_ok=True)
        Woolworm.Pipelines.process_image(f, o)
        text = Woolworm.ocr(o)
        text = str(text)
        o = o.replace(".png", ".md")
        with open(o, "w", encoding="utf-8") as f:
            f.write(text)

    pass


if __name__ == "__main__":
    app()

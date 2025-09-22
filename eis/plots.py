from pathlib import Path
from loguru import logger
from tqdm import tqdm
import typer
import woolworm
from eis.config import DATA_DIR, FIGURES_DIR

app = typer.Typer()


@app.command()
def main(
    # ---- REPLACE DEFAULT PATHS AS APPROPRIATE ----
    input_path: Path = DATA_DIR / "dataset.csv",
    output_path: Path = FIGURES_DIR / "plot.png",
    # -----------------------------------------
):
    w = woolworm.Woolworm()  # Create a woolworm object
    img = w.load((DATA_DIR / ""))
    # ---- REPLACE THIS WITH YOUR OWN CODE ----
    logger.info("Generating Hough Line Representation")
    # -----------------------------------------


if __name__ == "__main__":
    app()

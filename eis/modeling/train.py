import os
import matplotlib.pyplot as plt
import glob
from pathlib import Path
import textnets as tn
from loguru import logger
from PIL import Image
import pytesseract
import spacy
from spacy_llm.util import assemble
import typer
from woolworm import Woolworm

from eis.config import MODELS_DIR, PROCESSED_DATA_DIR, RAW_DATA_DIR

app = typer.Typer()


def get_project_location():
    pass


@app.command()
def main(
    # ---- REPLACE DEFAULT PATHS AS APPROPRIATE ----
    features_path: Path = (RAW_DATA_DIR / "p1074_35556030758452/003.jpg"),
    labels_path: Path = PROCESSED_DATA_DIR / "labels.csv",
    model_path: Path = MODELS_DIR / "model.pkl",
    # -----------------------------------------
):
    files_1 = glob.glob(str(RAW_DATA_DIR / "p1074_35556030758452/*.jpg"))
    files_2 = glob.glob(str(RAW_DATA_DIR / "p1074_35556031825029/*.jpg"))
    files_1 = sorted(files_1)
    files_2 = sorted(files_2)
    logger.info(files_1)
    corpora = [files_1, files_2]
    data = {}
    for i, c in enumerate(corpora):
        files = c[:10]
        c_data = ""
        for j, f in enumerate(files):
            logger.info(f"Converting {f} to text.")
            string = Woolworm.ocr(f, method="tesseract")
            string = str(string).replace("\n", " ")
            c_data += string
        data[str(i)] = c_data  # use index as key, not f.index

    corpus = tn.Corpus.from_dict(data, lang="en")
    t = tn.Textnet(corpus.tokenized(), min_docs=1)
    fig, ax = plt.subplots(figsize=(8, 8))
    t.plot(label_nodes=True, show_clusters=True, ax=ax)
    plt.savefig("textnet.png")
    plt.show()


if __name__ == "__main__":
    app()

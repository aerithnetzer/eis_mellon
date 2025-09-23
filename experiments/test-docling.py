import json
import logging
import os
from pathlib import Path
import time

from docling.datamodel.base_models import InputFormat
from docling.datamodel.pipeline_options import (
    EasyOcrOptions,
    PdfPipelineOptions,
)
from docling.document_converter import DocumentConverter, ImageFormatOption

from eis.config import PROCESSED_DATA_DIR, RAW_DATA_DIR

_log = logging.getLogger(__name__)


def main():
    logging.basicConfig(level=logging.INFO)
    input_doc_path = RAW_DATA_DIR / "p1074_35556031825029/JP2000/"
    output_doc_path = PROCESSED_DATA_DIR / "p1074_35556031825029/JP2000/"

    pipeline_options = PdfPipelineOptions()
    pipeline_options.do_ocr = True
    pipeline_options.do_table_structure = True
    pipeline_options.table_structure_options.do_cell_matching = True
    ocr_options = EasyOcrOptions(force_full_page_ocr=False)
    pipeline_options.ocr_options = ocr_options

    fs = [os.path.join(input_doc_path, f) for f in os.listdir(input_doc_path) if f.endswith("jpg")]
    fs = sorted(fs)
    fs = fs[:10]
    doc_converter = DocumentConverter(format_options={InputFormat.IMAGE: ImageFormatOption()})
    for f in fs:
        start_time = time.time()
        conv_result = doc_converter.convert(f)
        end_time = time.time() - start_time

        _log.info(f"Document converted in {end_time:.2f} seconds.")

        ## Export results
        output_dir = Path(output_doc_path)
        output_dir.mkdir(parents=True, exist_ok=True)
        doc_filename = conv_result.input.file.stem

        # Export Docling document JSON format:
        with (output_dir / f"{doc_filename}.json").open("w", encoding="utf-8") as fp:
            fp.write(json.dumps(conv_result.document.export_to_dict(), indent=4))

        # Export Text format (plain text via Markdown export):
        with (output_dir / f"{doc_filename}.txt").open("w", encoding="utf-8") as fp:
            fp.write(conv_result.document.export_to_markdown(strict_text=True))

        # Export Markdown format:
        with (output_dir / f"{doc_filename}.md").open("w", encoding="utf-8") as fp:
            fp.write(conv_result.document.export_to_markdown())

        # Export Document Tags format:
        with (output_dir / f"{doc_filename}.doctags").open("w", encoding="utf-8") as fp:
            fp.write(conv_result.document.export_to_document_tokens())


if __name__ == "__main__":
    main()

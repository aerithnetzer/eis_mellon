from fireworks import FWAction
from PIL import Image
import os
from woolworm import Woolworm
from pathlib import Path
from fireworks.core.firework import FiretaskBase
import loguru

logger = loguru.logger


class ImageTask(FiretaskBase):
    _fw_name = "digitask.ImageTask"

    def run_task(self, fw_spec):
        input_directory = Path(fw_spec["barcode_dir"])
        jpeg_dir = input_directory / "JPEG"
        jpeg_dir.mkdir(parents=True, exist_ok=True)  # create parent(s) + JPEG folder

        jp2_dir = input_directory / "JP2000"

        jp2_files = []
        jpg_files = []
        i = 0
        for f in sorted(jp2_dir.iterdir()):
            if f.is_file() and f.suffix.lower() == ".jp2":
                in_file = f.resolve()  # absolute input path

                # Output filename in JPEG dir
                out_filename = f.name.replace("JP2000", "JPEG").replace(".jp2", ".jpg")
                out_file = jpeg_dir / out_filename

                try:
                    w = Woolworm()
                    w.Pipelines.process_image(str(in_file), str(out_file))
                    jp2_files.append(str(in_file))
                    jpg_files.append(str(out_file.resolve()))
                except Exception as e:
                    print(f"Error processing {f.name}: {e}")

        len_input_directory = len(list(input_directory.iterdir()))
        print(f"Length of input directory is {len_input_directory}")

        return FWAction(
            stored_data={
                "_jp2_files": sorted(jp2_files),
                "_jpg_files": sorted(jpg_files),
            },
            mod_spec=[{"_push": {"_jpg_files": jpg_files}}],
        )


class ImageToPDFTask(FiretaskBase):
    _fw_name = "digitask.ImageToPDFTask"

    def run_task(self, fw_spec):
        jpg_files = sorted(fw_spec["_jpg_files"])
        input_directory = Path(fw_spec["barcode_dir"])
        jpeg_dir = Path(input_directory) / "JPEG"
        outpath_file = Path(input_directory) / "WOOLWORM.PDF"
        jpeg_dir.mkdir(exist_ok=True)
        logger.debug(f"Value of jpg_files[0]: {jpg_files[0], type(jpg_files[0])}")
        jpg_files = sorted(jpg_files[0])

        first_image = Image.open(jpg_files[0]).convert("RGB")

        # Open the rest and convert to RGB
        rest_images = [Image.open(p).convert("RGB") for p in jpg_files[1:]]

        # Save all into a single PDF
        first_image.save(outpath_file, save_all=True, append_images=rest_images)
        return FWAction(
            stored_data={
                "_jpg_files": jpg_files,
                "_pdf_file": outpath_file,
            },
            mod_spec=[{"_push": {"_jpg_files": jpg_files, "_pdf_file": outpath_file}}],
        )


class MarkerTask(FiretaskBase):
    _fw_name = "digitas.MarkerTask"

    def run_task(self, fw_spec):
        jpg_files = sorted(fw_spec["_jpg_files"])
        input_directory = Path(fw_spec["barcode_dir"])
        jpeg_dir = Path(input_directory) / "JPEG"
        outpath_file = Path(input_directory) / "WOOLWORM.PDF"
        jpeg_dir.mkdir(exist_ok=True)
        logger.debug(f"Value of jpg_files[0]: {jpg_files[0], type(jpg_files[0])}")
        jpg_files = sorted(jpg_files[0])

        first_image = Image.open(jpg_files[0]).convert("RGB")

        # Open the rest and convert to RGB
        rest_images = [Image.open(p).convert("RGB") for p in jpg_files[1:]]

        # Save all into a single PDF
        first_image.save(outpath_file, save_all=True, append_images=rest_images)
        return FWAction(
            stored_data={
                "_jpg_files": jpg_files,
                "_pdf_file": outpath_file,
            },
            mod_spec=[{"_push": {"_jpg_files": jpg_files, "_pdf_file": outpath_file}}],
        )

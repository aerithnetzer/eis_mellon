import argparse
import os
from pathlib import Path
from fireworks import LaunchPad
from jobflow.managers.fireworks import flow_to_workflow
from jobflow.core.flow import Flow
from jobflow.core.job import job
from fireworks.core.rocket_launcher import rapidfire
from loguru import logger
from PIL import Image
from woolworm import Woolworm


parser = argparse.ArgumentParser()
parser.add_argument("barcode_dir", help="Path to barcode directory (e.g. P0491XXXXX)")
parser.add_argument("--launcher-root", default="~/fw_launchers", help="Where launcher_* dirs go")
args = parser.parse_args()

barcode_dir = Path(args.barcode_dir).resolve()
launcher_root = Path(os.path.expanduser(args.launcher_root)).resolve()
launcher_root.mkdir(parents=True, exist_ok=True)


@job
def jp2s_to_jpgs(barcode_dir: Path):
    barcode_dir = Path(barcode_dir).resolve()
    input_dir = Path(barcode_dir) / "JP2000"  # <-- fixed name
    if not input_dir.exists():
        raise FileNotFoundError(f"Missing JP2000 dir: {input_dir}")

    jpeg_dir = Path(barcode_dir) / "JPEG"
    jpeg_dir.mkdir(parents=True, exist_ok=True)

    w = Woolworm()
    output_paths = []

    for i, f in enumerate(sorted(input_dir.glob("*.jp2"))):
        try:
            g = jpeg_dir / f.with_suffix(".jpg").name
            logger.debug(f"Now converting {i + 1}/20: {f} -> {g}")
            w.Pipelines.process_image(f, g)
            output_paths.append(g)
        except Exception as e:
            logger.error(f"Failed on file {f}: {e}")
            break  # or continue, depending on desired behavior
        logger.debug(f"Output paths: {output_paths}, of type {type(output_paths)}")
    return output_paths


@job
def jpgs_to_pdf(jpg_paths: list[Path], barcode_dir: Path):
    if not jpg_paths:
        raise ValueError("No JPEG files provided")

    jpg_paths = sorted(jpg_paths, key=str)
    images = [Image.open(p).convert("RGB") for p in jpg_paths]

    output_pdf = Path(barcode_dir).resolve() / "WOOLWORM.PDF"
    images[0].save(output_pdf, save_all=True, append_images=images[1:])
    logger.debug(f"Putting PDF in {output_pdf}")

    return output_pdf


@job
def marker_on_pdf(pdf_path: str | os.PathLike):
    pdf_path = Path(pdf_path).resolve()  # Make absolute
    from marker.converters.pdf import PdfConverter
    from marker.models import create_model_dict
    from marker.output import save_output

    converter = PdfConverter(artifact_dict=create_model_dict())
    rendered = converter(str(pdf_path))  # Ensure string path
    output_dir = Path(pdf_path).parent.resolve()
    save_output(rendered, str(output_dir), Path(pdf_path).resolve().stem)
    return True


# -------------------------------
# 3. Flow definition
# -------------------------------
jpgs = jp2s_to_jpgs(barcode_dir)
pdf = jpgs_to_pdf(jpgs.output, barcode_dir)
marker_pdf = marker_on_pdf(pdf.output)

flow = Flow([jpgs, pdf, marker_pdf])

# -------------------------------
# 4. FireWorks launcher location
# -------------------------------
os.chdir(launcher_root)  # <<-- keep launcher_* dirs in ~/fw_launchers

# Configure the workflow to not restart
wf = flow_to_workflow(flow)
wf.metadata = {"_prevent_auto_restart": True}

# Or set longer timeouts
for fw in wf.fws:
    fw.spec.update(
        {
            "_timeout": 3600,  # 1 hour timeout
            "_prevent_auto_restart": True,
        }
    )
lpad = LaunchPad.auto_load()
lpad.reset("", require_password=False)
lpad.add_wf(wf)
rapidfire(lpad)

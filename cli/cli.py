# This CLI takes as input a single barcode directory, expecting a subdirectory titled "JP2000"
# It then loops over all JP2 files in the JP2000 directory, transforming each of them to normal jpg, and putting them
# in a subdir called <barcode>/JPEG
# It then will create a PDF file from these images, and put it in a path called <barcode>/WOOLWORM.PDF
# Finally, it runs `marker` on the file.
from argparse import ArgumentParser
from woolworm import Woolworm

parser = ArgumentParser(prog="Run the tasks as a single firework.")

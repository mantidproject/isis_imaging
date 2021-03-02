import subprocess
import pathlib

FILTER_SIZES = [3, 4, 5]
ARR_SIZES = [100, 500, 1000]
N_IMAGES = [100, 500, 1000]

FOLDER_PATH = str(pathlib.Path(__file__).parent.absolute())
OUTLIER_PATH = FOLDER_PATH + "/outlierprofiler.py"

for filter_size in FILTER_SIZES:
    for arr_size in ARR_SIZES:
        for n_images in N_IMAGES:
            subprocess.Popen(
                f"nvprof --unified-memory-profiling off python {OUTLIER_PATH} --filter_size {filter_size} --arr_size {arr_size} --n_images {n_images}",
                shell=True)
            break

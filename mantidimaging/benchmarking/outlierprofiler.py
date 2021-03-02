import numpy as np
import cupy as cp
import argparse

from mantidimaging.core.gpu import utility

parser = argparse.ArgumentParser()
parser.add_argument("--filter_size", default=3, type=int)
parser.add_argument("--arr_size", default=100, type=int)
parser.add_argument("--n_images", default=100, type=int)
args = parser.parse_args()


class DummyProgress:
    def update(self):
        pass

    def mark_complete(self):
        pass


class OutlierProfiler:
    def __init__(self):
        self.dtype = "float32"
        self.cuda = utility.CudaExecuter(self.dtype)
        self.mode = "bright"
        self.progress = DummyProgress()
        self.diff = 0.5

    def run_outliers(self, filter_size: int, n_images: int, arr_size: int):
        data = np.random.rand((n_images, arr_size, arr_size))
        with cp.cuda.profile():
            self.cuda.remove_outlier(data, self.diff, filter_size, self.mode, self.progress)


op = OutlierProfiler()
op.run_outliers(args.filter_size, args.n_images, args.arr_size)

from logging import getLogger

from mantidimaging import helper as h
from mantidimaging.core.utility.progress_reporting import Progress


def fool_my_own_sanity_check(data):
    try:
        h.check_data_stack(data)
    except ValueError:
        h.check_data_stack(data, expected_dims=2)


def execute(data, cores=None, chunksize=None, progress=None):
    getLogger(__name__).warn("This only implement gap filling code. "
                             "NO CODE FOR SHIFTING THE CHIPS IS CURRENTLY "
                             "IMPLEMENTED!")

    progress = Progress.ensure_instance(progress, task_name='MCP Corrections')

    fool_my_own_sanity_check(data)

    # regions to mask, in order [left, top, right, bottom],
    # the order for the coordinates is also left, top, right, bottom
    # filter_width = 0 could use this for arbitrary filter value
    x1 = 254
    x2 = 258
    left_chip_region = [1, x1, 255, x2]
    right_chip_region = [257, x1, 511, x2]
    top_chip_region = [x1, 1, x2, 255]
    bottom_chip_region = [x1, 257, x2, 511]

    vertical_chip_regions = [top_chip_region, bottom_chip_region]
    horizontal_chip_regions = [left_chip_region, right_chip_region]

    with progress:
        progress.update(msg="MCP corrections")
        # 1st way -> set all of the coordinates to 0 in a for loop per region
        for region in vertical_chip_regions:
            left = region[0]
            top = region[1]
            right = region[2]
            bottom = region[3]
            if data.ndim == 3:
                for image in data:
                    do_vertical_magic(image, left, top, right, bottom)
            else:
                do_vertical_magic(data, left, top, right, bottom)

        for region in horizontal_chip_regions:
            left = region[0]
            top = region[1]
            right = region[2]
            bottom = region[3]
            if data.ndim == 3:
                for image in data:
                    do_horizontal_magic(image, left, top, right, bottom)
            else:
                do_horizontal_magic(data, left, top, right, bottom)

    # 2nd way -> create a mask of 512, 512 filled with 1, set the coordinates
    # to 1e-9 and then multiply all images by that mask!
    fool_my_own_sanity_check(data)

    return data


def do_horizontal_magic(image, left, top, right, bottom):
    # get column on left of values we'll interpolate
    left_val = image[top - 1:top, left:right]
    # get column on right of values we'll interpolate
    right_val = image[bottom:bottom + 1, left:right]
    fill_value = (left_val + right_val) / 2
    image[top:bottom, left:right] = fill_value


def do_vertical_magic(image, left, top, right, bottom):
    # get column on left of values we'll interpolate
    left_val = image[top:bottom, left - 1:left]
    # get column on right of values we'll interpolate
    right_val = image[top:bottom, right:right + 1]
    # generate the interpolation
    fill_value = (left_val + right_val) / 2
    # this makes each column of the matrix to equal the vector
    image[top:bottom, left:right] = fill_value

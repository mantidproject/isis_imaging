#!/usr/bin/env python
import argparse
import atexit
import logging
import warnings

from mantidimaging import helper as h
from mantidimaging.core.parallel import utility
from mantidimaging.core.utility.optional_imports import safe_import

formatwarning_orig = warnings.formatwarning
warnings.formatwarning = lambda message, category, filename, lineno, line=None: formatwarning_orig(
    message, category, filename, lineno, line="")


def startup_checks():
    tomopy = safe_import("tomopy")
    if tomopy is not None:
        ver = tomopy.__version__
        if "1.7" not in ver:
            raise RuntimeError("Unexpected TomoPy version {}, " "please update Conda environment".format(ver))


def parse_args():
    parser = argparse.ArgumentParser(description="Mantid Imaging GUI")

    parser.add_argument(
        "--log-level",
        type=str,
        default="INFO",
        help="Log verbosity level. "
        "Available options are: TRACE, DEBUG, INFO, WARN, CRITICAL",
    )

    parser.add_argument("--version", action="store_true", help="Print version number and exit.")

    return parser.parse_args()


def main():
    import SharedArray as sa

    def free_all():
        for arr in sa.list():
            sa.delete(arr.name.decode("utf-8"))

    atexit.register(free_all)
    args = parse_args()
    # Print version number and exit
    if args.version:
        from mantidimaging import __version__ as version_no

        print(version_no)
        return

    h.initialise_logging(logging.getLevelName(args.log_level))
    startup_checks()
    free_all()

    from mantidimaging import gui
    gui.execute()


if __name__ == "__main__":
    main()

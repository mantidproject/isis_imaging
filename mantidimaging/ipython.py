#!/usr/bin/env python


def main():
    import sys
    import IPython

    # Put a \n at the start so that we are below iPython's default message
    print("\nMantidImaging iPython, starting from ipython.py located in", sys.path[0])

    # setting end to empty string  means that the `Done` will be printed on the
    # same line
    print("Importing mantidimaging... ", end="")

    # import after the path has been corrected
    import mantidimaging  # noqa

    print("Done")

    IPython.embed()


if __name__ == "__main__":
    main()

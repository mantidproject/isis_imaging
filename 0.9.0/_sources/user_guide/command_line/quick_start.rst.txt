Quick Start
===========

Printing the help
-----------------

The help can be printed by passing the :code:`-h` flag.

:code:`mantidimaging -h`

This will print out the whole help, containing each available command line
parameter that can be passed.

Loading Data
------------

Specifying Sample data
^^^^^^^^^^^^^^^^^^^^^^

:code:`mantidimaging -i /some/path/to/sample`

Loading Sample, Flat and Dark at once
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

* Only Sample can be loaded, but you can't load just Flat or just Dark images.
  Both Flat and Dark must be specified at the same time.

:code:`mantidimaging -i /some/path/to/sample -F /some/path/to/flat -D
/some/path/to/dark`

Running a filter
^^^^^^^^^^^^^^^^

Available filters can be listed using the help command :code:`mantidimaging -h`.
This example will show how to run a median filter on the loaded images.

From the :code:`mantidimaging -h` we can see that the Median filter has the
following commands:

:code:`--median-size <number>` and :code:`--median-mode <string>`

The one we are interested in :code:`--median-size`.

To run the median filter we want to load a stack with `-i` and then append the
:code:`--median-size` flag. The full command line will look like this:

:code:`mantidimaging -i /some/path/ --median-size 3`

This will load in the data, execute median filter and do nothing else.

Saving pre-processed images
^^^^^^^^^^^^^^^^^^^^^^^^^^^

If we want to save out the pre-processed images we need to provide the one of
the following flags:

:code:`-s` or :code:`--save-preproc`

If they are not specified the data will be processed, and then **the result will
be discarded**. However this also requires an output path specified. Please
refer to `Specifying output folder`_.

Specifying output folder
^^^^^^^^^^^^^^^^^^^^^^^^

If we want anything saved out we need to specify the output path. This can be
done via one of the following flags:

:code:`-o folder_name` or :code:`--output-path folder_name`

Customising pre-processed folder
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

By default the pre-processing will be saved out in a folder called
:code:`pre_processed`. This can be customised using one of the following flags:

:code:`-p folder_name` or :code:`--preproc-subdir folder_name`

Specifying indices to be processed
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The package supports specifying only certain indices to be processed, for faster
testing and execution. This functionality can be accessed with:

:code:`--indices <start> <stop> <step>`

The flag also supports a few additional usages:

:code:`--indices <stop>` - This will assume the start is 0, and step is 1

:code:`--indices <start> <stop` - This will assume the step is 1

Example usage on the command line:

    - :code:`mantidimaging -i /some/data --indices 100 --median-size 3`

    - :code:`mantidimaging -i /some/data --indices 0 100 --median-size 3`

    - :code:`mantidimaging -i /some/data --indices 0 100 1 --median-size 3`

These 3 specify the same thing, and show off the different ways to use
:code:`--indices`.

Saving out sinograms
^^^^^^^^^^^^^^^^^^^^

Finding the Center of Rotation and reconstructing a dataset requires the images
to be converted to Sinograms first.

This can be done in anything that involves saving images out, meaning that the
images can be converted after being applied a filter:

:code:`mantidimaging -i /some/path/ --median-size 3 --swap-axes -o /some/path
-s`

For converting images that have already been saved out, use the following
command:

:code:`mantidimaging -i /some/path/ -o /output/path --convert --swap-axes`


Automatic Finding COR
^^^^^^^^^^^^^^^^^^^^^

- Note: This expects images as sinograms. Please refer to `Saving out
  sinograms`_.

To run one of the Tomopy's automatic COR finding algorithms use:

:code:`--imopr cor --indices 10`

This will run the automatic COR algorithm on the first 10 slices.

Manual Finding COR
^^^^^^^^^^^^^^^^^^

- Note: This expects images as sinograms. Please refer to `Saving out
  sinograms`_.

If the algorithm is not accurate you can use the manual approach:

:code:`--imopr <cor_start> <cor_end> <cor_step> corwrite -o /some/path --indices
10`

:code:`--imopr`'s :code:`corwrite` allows to manually specify CORs, reconstruct
the slices with those CORs and save them out.

The functionality is extended to provide a way for multiple slices in one go.

:code:`mantidimaging -i /some/sinogrmas --imopr 200 300 1 corwrite -o /some/path
--indices 10`

This will reconstruct the first 10 slices (from :code:`--indices 10`) and will
use the CORs in range 200 to 300, with a step of 1 (from :code:`--imopr 200 300
1 corwrite`).

Then it will save them out to the path specified by :code:`-o`.

Running reconstruction
^^^^^^^^^^^^^^^^^^^^^^

When the correct CORs have been found you can run the reconstruction.

The :code:`--reconstruction` flag must be specified, which also requires the
:code:`--cor-slices --cors` to be specified.

:code:`--cors`

Specifies the COR for each slice. If a single COR is passed, it will be assumed
all slices have the same COR.

:code:`--cor-slices`

Specifies which are the slices for which the CORs are specified with the
:code:`--cors` flag. This must have the same number of arguments as
:code:`--cors`.

If only a single COR is passed into :code:`--cors` you **must not** specify this
flag.

Example command line:

:code:`mantidimaging -i /some/sinograms/ --cor-slices 100 200 300 --cors 340 341
342 --reconstruction -o /some/output/path`

This specifies that slice 100 has COR of 340, slice 200 has a COR of 341, and
slice 300 has a COR of 342. The CORs between the slices will be interpolated
based on the ones that are passed in.

Selecting tool and algorithm
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The tool used can be specified with:

:code:`-t` or :code:`--tool`

The algorithm can be specified with:

:code:`-a` or :code:`--algorithm`

For available tools and algorithms please refer to the `Printing the help`_.

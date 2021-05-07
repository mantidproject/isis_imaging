Execution Splitter
==================

Sometimes the datasets are too large to handle in a single run even on a 32GB
machine. This is the reason the :code:`execution_splitter` was added.

The :code:`execution_splitter` is part of the :code:`algorithms` package. It
will calculate the expected size, depending on whether we are doing a
reconstruction (the memory usage will double, to allocate memory for the
reconstructed volume) or just image processing (no doubling expected). Based on
that it tries to have a ratio of expected size to available memory under 1,
meaning we don't run out of memory during execution.

It will then split the indices in however many steps are needed to not run out
of memory (let's say split in 2, so each run will use half the original memory).
If we have 1500 images, on the first run we will process the first [0-750), and
on the second run we will process the [750-1500) (last index not included). Any
associated centers of rotation will also be split according to the indices.

The actual call to the :code:`execution_splitter` package happens in
:code:`main.py`, if the :code:`--split` flag is detected, we go onto a different
branch of execution.

The reason we can split the data like that, is that nearly all filters are
atomic operations on an image, and it does not matter what happens to the other
images, or whether they are present at all. This is also true for a
reconstruction, we only reconstruct a sinogram and do not care about the others.

The exception to that is the Region of Interest normalisation filter, because we
use the sums of _all_ provided images to calculate our scalar, meaning that if
we process half, we calculate the number from only half the images, and the
second half will be multiplied by a different number. This has not been found to
be an issue, and the results are pretty much the same regardless of whether we
process all of the images, half, a third, or even less. The reason for that is
that most of the time only a very small number of images will actually have a
contrast that's different from the rest.

--------------------
Associated CLI flags
--------------------

    - :code:`--split`

      This will activate the aforementioned functionality.

    - :code:`--reconstruction`

      Specifies whether this is a reconstruction or not. This is not a specific
      flag to :code:`execution_splitter`, but it will activate all
      reconstruction branches in the package. See the :code:`default_run.py`
      file to see more of what happens due to this flag.

    - :code:`--max-ratio`

      The maximum allowed ratio of expected size to available memory.

    - :code:`--max-memory`

      The maximum allowed memory.

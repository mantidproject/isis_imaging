Rotate Stack
============

Rotates an image (or each image in a stack) clockwise by a multiple of 90
degrees.

Through the Python API the flat and dark images can also be provided to process
them in a single call to :code:`execute()`.

Command line examples
---------------------

  - :code:`mantidimaging -i /some/data -r 1`

  - :code:`mantidimaging -i /some/data --rotation 1`

Python API
----------

.. autofunction:: mantidimaging.core.filters.rotate_stack.execute

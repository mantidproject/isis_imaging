Clip Values
===========

This filter restricts the range of pixel values in an image, replacing the value
of any pixels that have a value outside of a given range.

Command line examples
---------------------

  - :code:`mantidimaging -i /some/data/ --clip-min -120 --clip-max 42`

Python API
----------

.. autofunction:: mantidimaging.core.filters.clip_values.execute

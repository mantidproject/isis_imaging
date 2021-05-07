Crop Coordinates
================

This filter crops an image to a region of interest (ROI) using the extents of
the region.

The extents are expected in the order :code:`left top right bottom`.

Command line examples
---------------------

  - :code:`mantidimaging -i /some/data -R 134 203 170 250`

  - :code:`mantidimaging -i /some/data --region-of-interest 134 203 170 250`

Python API
----------

.. autofunction:: mantidimaging.core.filters.crop_coords.execute

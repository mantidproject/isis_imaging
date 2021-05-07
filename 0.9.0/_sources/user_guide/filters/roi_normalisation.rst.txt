ROI Normalisation
=================

Normalise by beam intensity by selecting a region (the air region) of the image
which is outside of the detector area affected by the sample (i.e. in an area
that is receiving full beam intensity).

The workflow of this filter is:

  - For each image the sum of pixel intensities within the air region is
    calculated, giving an array of summed intensities for the air region of each
    image

  - The array of air region summed intensities is normalised by dividing it by
    its largest element

  - For each image the pixel intensities of the entire image are divided by the
    normalised air region for that image

Command line examples
---------------------

  - :code:`mantidimaging -i /some/data -A 134 203 170 250`

  - :code:`mantidimaging -i /some/data --air-region 134 203 170 250`

Python API
----------

.. autofunction:: mantidimaging.core.filters.roi_normalisation.execute

Background Correction and Normalisation
=======================================

Performs normalisation of sample and flat field images using summed intensity in
a given open air region then performs a correction for pixel specific intensity
variances over the range of intensities.

Operates on a stack of sample images, :math:`I_{s}` using flat, :math:`I_{f}`
(full intensity) and dark, :math:`I_{d}` (zero intensity) images.

The normalisation factors for sample images, :math:`N_{s}` and flat field
images, :math:`N_{f}` are calculated by summing the pixel intensities in a given
region of interest (which should be an area of open beam not close to the
sample), normalising them then taking their inverse.

.. math::
    D &= \frac{\sum{I_{d}}}{|I_{d}|} \\
    F &= \frac{\sum{N_{f}I_{f}}}{|I_{f}|} \\
    S &= \frac{N_{s}I_{s} - D}{F - D}

Python API
----------

.. autofunction:: mantidimaging.core.filters.background_correction_and_normalisation.execute

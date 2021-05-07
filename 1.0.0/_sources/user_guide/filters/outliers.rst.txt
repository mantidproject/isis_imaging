Outliers
========

.. important::

    This filter requires TomoPy to be available.

Removes bright or dark spots (outliers) from an image (or stack of images).

This uses the TomoPy implementation (:code:`tomopy.misc.corr.remove_outlier`)
(docs_).

Python API
----------

.. autofunction:: mantidimaging.core.filters.outliers.execute

.. _docs: http://tomopy.readthedocs.io/en/latest/api/tomopy.misc.corr.html#tomopy.misc.corr.remove_outlier

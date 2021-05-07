Outliers
========

.. important::

    This filter requires TomoPy to be available.

Removes bright or dark spots (outliers) from an image (or stack of images).

This uses the TomoPy implementation (:code:`tomopy.misc.corr.remove_outlier`)
(docs_).

Command line examples
---------------------

  - :code:`mantidimaging -i /some/data --outliers 1`

  - :code:`mantidimaging -i /some/data --outliers 1 --outliers-radius 4`

Python API
----------

.. autofunction:: mantidimaging.core.filters.outliers.execute

.. _docs: http://tomopy.readthedocs.io/en/latest/api/tomopy.misc.corr.html#tomopy.misc.corr.remove_outlier

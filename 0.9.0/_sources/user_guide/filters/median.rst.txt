Median
======

Applies SciPy's median filter (:code:`scipy.ndimage.filters.median_filter`)
(docs_).

Command line examples
---------------------

  - :code:`mantidimaging -i /some/data --median-size 3`

  - :code:`mantidimaging -i /some/data --median-size 3 --median-mode 'nearest'`

Python API
----------

.. autofunction:: mantidimaging.core.filters.median_filter.execute

.. _docs: https://docs.scipy.org/doc/scipy-0.16.1/reference/generated/scipy.ndimage.filters.median_filter.html

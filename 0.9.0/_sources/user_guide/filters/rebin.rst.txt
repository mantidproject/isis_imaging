Rebin
=====

Reshapes an image (or stack of images) using SciPy's :code:`scipy.misc.imresize`
(docs_).

Command line examples
---------------------

  - :code:`mantidimaging -i /some/data --rebin 0.5 --rebin-mode 'nearest'`

Python API
----------

.. autofunction:: mantidimaging.core.filters.rebin.execute

.. _docs: https://docs.scipy.org/doc/scipy-0.16.1/reference/generated/scipy.misc.imresize.html

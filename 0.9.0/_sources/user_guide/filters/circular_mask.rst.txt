Circular Mask
=============

.. important::

    This filter requires TomoPy to be available.

Applies TomoPy's circular mask filter (:code:`tomopy.misc.corr.circ_mask`)
(docs_).

Takes a radius as a ratio of the smallest image dimension and a value to apply
to all pixels outside this radius.

Command line examples
---------------------

  - :code:`mantidimaging -i /some/data/ --circular-mask 0.75 --circular-mask-val
    0`

Python API
----------

.. autofunction:: mantidimaging.core.filters.circular_mask.execute

.. _docs: http://tomopy.readthedocs.io/en/latest/api/tomopy.misc.corr.html#tomopy.misc.corr.circ_mask

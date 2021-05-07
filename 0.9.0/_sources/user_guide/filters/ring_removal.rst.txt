Ring Removal
============

.. important::

    This filter requires TomoPy to be available.

This filter removes ring artefacts in a reconstructed volume.

This uses the TomoPy implementation (:code:`tomopy.misc.corr.remove_ring`)
(docs_).

Command line examples
---------------------

  - :code:`mantidimaging -i /some/data/ --ring-removal --ring-removal-x 140
    --ring-removal-x 128`

Python API
----------

.. autofunction:: mantidimaging.core.filters.ring_removal.execute

.. _docs: http://tomopy.readthedocs.io/en/latest/api/tomopy.misc.corr.html#tomopy.misc.corr.remove_ring

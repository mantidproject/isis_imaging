Ring Removal
============

.. important::

    This filter requires TomoPy to be available.

This filter removes ring artefacts in a reconstructed volume.

This uses the TomoPy implementation (:code:`tomopy.misc.corr.remove_ring`)
(docs_).

Python API
----------

.. autofunction:: mantidimaging.core.filters.ring_removal.execute

.. _docs: http://tomopy.readthedocs.io/en/latest/api/tomopy.misc.corr.html#tomopy.misc.corr.remove_ring

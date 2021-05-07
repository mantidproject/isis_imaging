Minus Log
=========

.. important::

    This filter requires TomoPy to be available.

This filter applies the :math:`-ln(x)` operation to the intensity of each pixel
in an image.

This uses the TomoPy implementation (:code:`tomopy.prep.normalize.minus_log`)
(docs_).

This is used to convert from a transmission image (i.e. high intensity
indicating transmission through the sample) to attenuation images (i.e. high
intensity indicating attenuation by the sample).

Command line examples
---------------------

  - :code:`mantidimaging -i /some/data --minus-log`

Python API
----------

.. autofunction:: mantidimaging.core.filters.minus_log.execute

.. _docs: http://tomopy.readthedocs.io/en/latest/api/tomopy.prep.normalize.html#tomopy.prep.normalize.minus_log

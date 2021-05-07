Stripe Removal
==============

.. important::

    This filter requires TomoPy to be available.

Performs stripe removal using one of three methods provided by TomoPy:
    - `Fourier-Wavelet <http://tomopy.readthedocs.io/en/latest/api/tomopy.prep.stripe.html#tomopy.prep.stripe.remove_stripe_fw>`_
    - `Titarenko <http://tomopy.readthedocs.io/en/latest/api/tomopy.prep.stripe.html#tomopy.prep.stripe.remove_stripe_ti>`_
    - `Smoothing filter <http://tomopy.readthedocs.io/en/latest/api/tomopy.prep.stripe.html#tomopy.prep.stripe.remove_stripe_sf>`_

Command line examples
---------------------

  - :code:`mantidimaging -i /some/data --stripe-removal-wf level=1`

  - :code:`mantidimaging -i /some/data --stripe-removal-wf level=3 pad=False`

  - :code:`mantidimaging -i /some/data --stripe-removal-wf level=3 pad=False
    wname=db5`

  - :code:`mantidimaging -i /some/data --stripe-removal-wf level=3 pad=False
    wname=db5 sigma=2`

  - :code:`mantidimaging -i /some/data --stripe-removal-ti nblock=3`

  - :code:`mantidimaging -i /some/data --stripe-removal-ti nblock=3 alpha=2`

  - :code:`mantidimaging -i /some/data --stripe-removal-sf size=3`

Python API
----------

.. autofunction:: mantidimaging.core.filters.stripe_removal.execute

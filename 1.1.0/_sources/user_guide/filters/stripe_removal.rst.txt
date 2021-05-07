Stripe Removal
==============

.. important::

    This filter requires TomoPy to be available.

Performs stripe removal using one of three methods provided by TomoPy:
    - `Fourier-Wavelet <http://tomopy.readthedocs.io/en/latest/api/tomopy.prep.stripe.html#tomopy.prep.stripe.remove_stripe_fw>`_
    - `Titarenko <http://tomopy.readthedocs.io/en/latest/api/tomopy.prep.stripe.html#tomopy.prep.stripe.remove_stripe_ti>`_
    - `Smoothing filter <http://tomopy.readthedocs.io/en/latest/api/tomopy.prep.stripe.html#tomopy.prep.stripe.remove_stripe_sf>`_

Python API
----------

.. autofunction:: mantidimaging.core.filters.stripe_removal.execute

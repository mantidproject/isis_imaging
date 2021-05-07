Troubleshooting
===============

Solutions to (hopefully not very) common issues.

Intel MKL errors
----------------

If when starting the package you receive errors relating to Intel MKL the
easiest remedy is to use non-MKL versions of NumPy and SciPy.

This is done using the following commands from the Anaconda environment in which
you have the package installed.

.. code::

   conda install nomkl numpy scipy scikit-learn numexpr
   conda remove mkl mkl-service

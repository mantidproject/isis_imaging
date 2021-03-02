GPU Mode
=============

.. important::

    The GPU mode will only work if :code:`cupy` is installed and working on your system.

The Median and Remove Outlier filters have the option of being run on the GPU.
This works by having the :code:`cupy` library import the CUDA module so that
Python can be used to compile it, run it, and retrieve the results. Transferring
data to and from the GPU is quite time-consuming, so the degree of speed
improvement you observe (or don't observe) depends on:

- the size of the data
- the float precision
- the number of floating point operations that the algorithm has to perform

Depending on these factors, the cost of data transfer may outweigh the GPU
processing improvement. As a consequence of this, using the CPU is the better
option in some cases. In the
case of the median and remove outlier filters, using a larger filter size
increases the number of floating point operations required to obtain a result.
This means that if a speed improvement is observed for a filter size of 3,
filter sizes greater than 3 will produce an even larger speed improvement.

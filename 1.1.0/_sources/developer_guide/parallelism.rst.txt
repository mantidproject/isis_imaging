Parallelism in Python
=====================

In order to process data in parallel using the Python's built-in module
:code:`multiprocessing`, the data needs to be put into a :code:`shared array`,
which is created using the :code:`multiprocessing.sharedctypes` module. This is
all abstracted away inside the :code:`parallel.utility` module, specifically the
:code:`create_shared_array` function.

What happens if we don't use a shared array?
--------------------------------------------

If we do not use a shared array, each image is first copied to the spawned
process' memory, and then processed and returned, then copied again in the main
process' memory. We want to avoid these copies because they waste time. The way
to avoid them is to use a shared array, so that each child process can do the
processing in-place.

Is in-place processing safe?
----------------------------

Yes, each process gets a whole image, and only processes that image. It does not
try to read and change data of other processes, therefore we do not have
race-conditions or undefined behaviour.

How is parallel processing done right now?
------------------------------------------

Parallel processing is all funnelled through the :code:`parallel` package. It
uses function decorating to forward parameters, because there is no native way
of doing that in Python 2.7. There might be a way of changing that in Python
3.x.

It all goes down to using a parallel pool with worker as much as cores the
process has been given. We then do an :code:`pool.imap` and execute the function
that's already been decorated with the rest of the parameters, and provide the
data as a first parameter. The reason we don't decorate the function with the
data reference is then the data might be copied.

The :code:`two_shared_mem` package forwards 2 parameters to the decorated
function because some filters require the data and another array to use, for
example doing background correction, we need a second array to subtract and then
divide.

Using :code:`pool.imap` means that the main thread will briefly be returned to,
and that is when we increment the progress bar. There has been no performance
penalty found for using :code:`pool.imap`, which briefly returns to the main
thread, over :code:`pool.map` which doesn't return to the main thread, thus we
will lose the ability to increment the progress bar.

Python <=3.6 Performance Issues
===============================

Up to Python 3.6 a change has been made to how the shared memory is allocated.
It was moved to using a shared file, instead of mapping to RAM. The reason for
that is to support different ways to start subprocesses. More information can be
found at this issue thread http://bugs.python.org/issue30919.

This, is a breaking change to these scripts, because IO is not nearly fast
enough as we want it to be. There is a fix and the performance testing that has
been done with it (copied the code from Python 3.7) seems to give the same
performance as the Python 2.7. It will not be available with the default
distribution until Python 3.7.

The behaviour is monkey-patched at runtime, to have the Python 3.7 code, in the
:code:`parallel` package's :code:`__init__.py` file. There is more explanation
of what is being done in the file and why.

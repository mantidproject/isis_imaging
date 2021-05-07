IO package
==========

The :code:`io` module provides easy modules to load and save stacks of data.

Loading data
------------

The :code:`core.io.loader` module provides a :code:`load` method, that takes a
path, and :code:`img_format` (the default is :code:`tiff`, if different it needs
to be specified) and will load **all** of the images in that folder.

Saving data
-----------

The :code:`core.io.saver` module provides a :code:`save` method, that takes a
Numpy :code:`ndarray` and a path, and will save out all the images in the path.
The function also has additional parameters to specify output image format.

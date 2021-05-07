Converting images
=================

This mode is simply to convert from one file format to another which might be
more convenient.

An example when it might be desired is converting from **fits** to **tiff**
images.

The python fits reader (pyfits) flips the images vertically, so some selections
of regions of interest might be inaccurate.

Example usage:

:code:`mantidimaging -i /some/data/ -o /some/output/ --in-format <img_format>
--out-format <img_format>`

This will load all images from :code:`/some/data` and save them out in
:code:`/some/output` with the format specified by :code:`--out-format`.

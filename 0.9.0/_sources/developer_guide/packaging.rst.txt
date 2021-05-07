Packaging
=========

The preferred method of packaging the package is as a Conda package.

This is most likely to be the simplest way to distribute the package; for users
Anaconda Cloud is the simplest way to obtain dependencies (for instance,
TomoPy), for clusters a Conda package is one of the less painful ways of
deploying something (so I am told).

TL;DR
-----

Building:

   1. :code:`cd buildscripts/conda/`
   2. :code:`./build.sh`

Installing:

   1. :code:`conda config --add channel dgursoy` (once)
   2. :code:`conda install -c file:///tmp/mantidimaging-conda/linux-64 mantidimaging`

Building the package
--------------------

Before you go any further make sure you have :code:`conda-build` installed, this
should be as simple as :code:`conda install conda-build`.

The metadata is in :code:`buildscripts/conda/mantidimaging` and a script to
start the build is included in the :code:`buildscripts/conda` directory, all
this really does is call :code:`conda-build`.

The :code:`build.sh` script defaults the output directory to
:code:`/tmp/mantidimaging-conda`, this is to get around the issue where
encrypted volumes under Linux have longer file paths (or at least that's the
error :code:`conda-build` gives you), regardless it fails if the output
directory is on an encrypted volume.

Conda packages are created for both Python 2.7 and Python 3.5.

Installing the package
----------------------

Before installing the Conda package the channel from which TomoPy will be
installed must be added to the local Conda configuration. This is done with the
command: :code:`conda config --add channels dgursoy`. This only has to be done
once per machine.

The package can be installed from a local build using: :code:`conda install -c
file:///tmp/mantidimaging-conda/linux-64 mantidimaging` (assuming the package is
still in the directory it was built).

Here you are essentially using a directory as a channel, don't try to install
directly from the archive as it will not resolve dependencies.

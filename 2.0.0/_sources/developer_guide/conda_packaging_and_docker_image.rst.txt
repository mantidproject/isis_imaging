Conda Packaging and Docker images
=================================

The preferred method of packaging the package is as a Conda package.

This is most likely to be the simplest way to distribute the package;
Anaconda Cloud is the simplest way to obtain dependencies (for instance,
TomoPy).

TL;DR
-----

Building:

   1. :code:`make build-conda-package`. This will automatically try to install the build requirements by calling the make target :code:`install-build-requirements`

Installing:

   1. :code:`conda install -c file:///tmp/mantidimaging-conda/linux-64 -c conda-forge  mantidimaging`

Building the package
--------------------

This can now be done in a Github Action as a more convenient way. This still works as well.

Before you go any further make sure you have the build requirements installed.
This can be done via :code:`make install-build-requirements`.

The metadata is in :code:`conda/meta.yaml`. This generates a package based
on the environment and an installation using :code:`setup.py`.

Note that you may have issues if the Conda root directory is on an encrypted
volume, in this case you may use the :code:`--croot` option to set a root
directory that is on a "normal" volume.

The command to build the package is (and the specific command can be found in the Makefile):

   1. :code:`make build-conda-package`

Installing the package
----------------------

Before installing the Conda package, these commands will set the channels in the correct priority order:

   1. :code:`conda config --prepend channels conda-forge`
   2. :code:`conda config --prepend channels anaconda`
   3. :code:`conda config --prepend channels defaults`

This makes the priority in order of :code:`defaults > anaconda > conda-forge`, and is necessary due to packages having different versions in the different repositories.
This only has to be done once per machine.

The package can be installed from a local build using: :code:`conda install -c
file:///tmp/mantidimaging-conda/linux-64 mantidimaging` (assuming the package is
still in the directory it was built).

Here you are essentially using a directory as a channel.

Caution: installing directly from the archive as it will not resolve dependencies!

Uploading the package
---------------------

After it is built, the package can be uploaded to the upstream repository. This is done automatically if the conda automatic upload is yes, set via :code:`conda config --set anaconda_upload yes`.

Two environment variables are necessary: the :code:`$UPLOAD_USER`, and the :code:`$ANACONDA_API_TOKEN`.
You can specify your own username and API key to build the conda package in your own conda repository.
If you want to push a package to the original repository please contact the Mantid development team for more information.

Building the Docker image
-------------------------

The Docker image is currently used as a setup for the test environment. The configuration is stored in the :code:`docker/Dockerfile`, and a :code:`make` helper command is provided for building it:

   1. :code:`cd docker && make`

The default tags used are :code:`centos7`, :code:`ubuntu18` and :code:`latest`, where :code:`$UPLOAD_USER` is the environment variable.
You can provide a custom one to build it to your Docker hub repository, or contact the Mantid development team if you need to push to the official one.

Pushing the Docker image
------------------------

The command to push the Docker image to Docker hub does not have a :code:`make` shortcut provided, and is as follows:

   1. :code:`cd docker && make push`

This assumes the Makefile command was used to create the image, and the :code:`$UPLOAD_USER` is still present in the environment. You can replace :code:`$UPLOAD_USER/mantidimaging:travis-ci-2019.10` with anything, including your own Docker hub account.
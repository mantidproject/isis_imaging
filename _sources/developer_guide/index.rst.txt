Developer Guide
===============

Getting Started
---------------

You will need conda, CUDA and gcc installed, see the :ref:`Installation` instructions.

First download the Mantid Imaging source code using Git.

:code:`git clone https://github.com/mantidproject/mantidimaging.git`

If you have a github account you can use ssh access:

:code:`git clone git@github.com:mantidproject/mantidimaging.git`

To set up a developer environment, from with in the cloned directory run:

:code:`conda env create -f environment-dev.yml`

This will create a conda environment containing all the packages needed to run and develop Mantid Imaging. The activate command will activate the environment.

Afterwards the environment can be activated by running:

:code:`conda activate mantidimaging-dev`

(Note: This method will also install the mantidimaging package in the environment. Be aware that if you run `python -m mantidimaging` from outside the source directory it will use the installed version).

To check that the set up was successful, try running the tests from the source directory:

:code:`python -m pytest`

.. toctree::
   :maxdepth: 1
   :caption: Contents:

   documentation
   developer_conventions
   conda_packaging_and_docker_image
   release
   testing

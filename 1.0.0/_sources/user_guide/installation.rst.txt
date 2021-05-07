Installation
============

Installing
----------

The simplest way to install the toolkit is via the `packages
<https://anaconda.org/mantid/mantidimaging>`_ published to Anaconda Cloud, this
can be done with an existing Amaconda or Miniconda distribution if you already
have one on your machine.

1. Download and install `Miniconda 3 <https://conda.io/miniconda.html>`_
2. Create a Python 3.5 virtual environment: :code:`conda create --name mantidimaging python=3.5`
3. Activate the newly created environment: :code:`conda activate mantidimaging`
4. Install mantidimaging: :code:`conda install -c conda-forge -c mantid mantidimaging`

Alternatively you may also use this command at step 4 to install a "nightly"
version of the package: :code:`conda install -c mantid/label/nightly mantidimaging`.
This version will contain the latest features buy may be less stable than the
released versions.

Note that the name of the environment used here (`mantidimaging`) is only an
example and can be changed to whatever name you like.

Running
-------

1. Activate the environment created in the installation step: :code:`conda activate mantidimaging`
2. Run using one of the following commands:

  - GUI: :code:`mantidimaging`
  - IPython: :code:`mantidimaging-ipython`

Updating
--------

To update to the latest version of the toolkit use the command: :code:`conda
update mantidimaging`.

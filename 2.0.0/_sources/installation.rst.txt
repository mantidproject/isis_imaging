.. _Installation:

Installation
============
Installing
----------

The simplest way to install the toolkit is via the packages_ published to Anaconda Cloud, this
can be done with an existing Anaconda or Miniconda distribution if you already
have one on your machine.

.. _packages: https://anaconda.org/mantid/mantidimaging/


1. These dependencies must be present on your system before installing the Mantid Imaging environment.
Please look for instructions specific to your OS on how to do that:

  - Qt5 - https://doc.qt.io/qt-5/gettingstarted.html
  - CUDA Runtime version 10.2 - https://developer.nvidia.com/cuda-10.2-download-archive


2. Download and install `Miniconda 3 <https://conda.io/miniconda.html>`_
3. Make sure :code:`conda` is available on your PATH
4. Run the install script:

  - :code:`source <(curl -s https://raw.githubusercontent.com/mantidproject/mantidimaging/master/install.sh)`


5. This creates an environment called :code:`mantidimaging` that you can activate via :code:`conda activate mantidimaging`

Running the source
------------------

1. Activate the environment created in the installation step: :code:`conda activate mantidimaging`
2. Run using one of the following commands:

  - From the root of the repository run with :code:`python -m mantidimaging`


Running the package
-------------------

1. Activate the environment created in the installation step: :code:`conda activate mantidimaging`
2. Run using one of the following commands:

  - GUI: :code:`mantidimaging`
  - IPython: :code:`mantidimaging-ipython`

Updating
--------
To update to the latest version of Mantid Imaging run:

:code:`conda activate mantidimaging && conda update mantidimaging`

If you see any issues with package compatibility, the fastest solution is reinstalling the environment - see below.

Reinstalling the environment
----------------------------
To completely delete the Mantid Imaging environment follow these steps:

- :code:`conda deactivate`

  - to exit out of the conda Mantid Imaging environment

- :code:`conda remove -n mantidimaging --all`

  - and press :code:`y` to confirm

- Follow steps 3 and 4 from Installing_.

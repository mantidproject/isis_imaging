.. _Troubleshooting:

Troubleshooting
===============

Updating Mantid Imaging on IDAaaS
---------------------------------

Updating Unstable package
#########################

To update the unstable package please copy and run this command in a terminal:

.. code-block:: bash

    source /opt/miniconda/bin/activate /opt/miniconda && ENVIRONMENT_NAME=mantidimaging_unstable REPO_LABEL=unstable source <(curl -s https://raw.githubusercontent.com/mantidproject/mantidimaging/master/install.sh)

Updating Release package
########################

To update the release package please copy and run this command in a terminal:

.. code-block:: bash

    source /opt/miniconda/bin/activate /opt/miniconda && source <(curl -s https://raw.githubusercontent.com/mantidproject/mantidimaging/master/install.sh)

Updating when not on IDAaaS
###########################

When updating the package, and not on IDAaaS, you will have to:

- Open a terminal which has the :code:`base` Anaconda environment activated, or
- replace the :code:`/opt/miniconda/` paths in :code:`source /opt/miniconda/bin/activate /opt/miniconda`
command with the path where :code:`conda` is installed on your system.

Afterwards run the remainder of the command to update the environment:

- For Unstable

.. code-block:: bash

    ENVIRONMENT_NAME=mantidimaging_unstable REPO_LABEL=unstable source <(curl -s https://raw.githubusercontent.com/mantidproject/mantidimaging/master/install.sh)


- For Release

.. code-block:: bash

    source <(curl -s https://raw.githubusercontent.com/mantidproject/mantidimaging/master/install.sh)



Can't reconstruct with FBP_CUDA and SIRT_CUDA
---------------------------------------------

These algorithms have 2 requirements:

- Having a CUDA-compatible graphics card (GPU)
- Having the CUDA Runtime 10.2 libraries installed


Having a CUDA-compatible graphics card
######################################

Please check that your GPU is on the list of compatible GPUs https://developer.nvidia.com/cuda-gpus

Having the CUDA Runtime 10.2 libraries installed
################################################

Please install the CUDA Runtime version 10.2 binaries from https://developer.nvidia.com/cuda-10.2-download-archive

Reinstalling CUDA on Linux can be quickly done with this script


.. code-block:: bash

    # uninstall nvidia driver and cuda driver
    nvidia-uninstall && /usr/local/cuda/bin/cuda-uninstaller

    # download the CUDA installer
    wget http://developer.download.nvidia.com/compute/cuda/10.2/Prod/local_installers/cuda_10.2.89_440.33.01_linux.run ~/Downloads/cuda_10.2.89_440.33.01_linux.run

    # install GPU driver and CUDA Toolkit from CLI silently
    sudo bash ~/Downloads/cuda_10.2.89_440.33.01_linux.run --silent --driver --toolkit


Specific Errors
===============


SystemError: <built-in function connectSlotsByName> returned a result with an error set
---------------------------------------------------------------------------------------

This means that the PyQt package is missing or an old version (it must be newer than PyQt5==5.13.2)

Suggested Fix
#############

Install PyQt5 and pyqtgraph with :code:`pip install pyqt5==5.15 pyqtgraph==0.11`



qt.qpa.plugin: Could not load the Qt platform plugin "xcb" in "" even though it was found.
----------------------------------------------------------------------------------------------

This might mean some system libraries are missing

Suggested Fix
#############

Try installing :code:`apt install libxcb-xinerama0`

qt.qpa.xcb: could not connect to display...
-------------------------------------------

Missing :code:`DISPLAY` variable. This means the application cannot find the display to show itself on.


Suggested Fix
#############

You can set this via :code:`export DISPLAY=:N` where :code:`:N` should be the number of your display
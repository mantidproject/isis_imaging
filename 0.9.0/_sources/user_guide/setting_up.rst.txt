Setting up
==========

Obtaining the package
---------------------

A copy of the :code:`mantidimaging` package can be obtained by either cloning
the Git repository:

:code:`git clone https://github.com/mantidproject/mantidimaging.git`

Or downloading a Zip archive of the repository contents:

:code:`wget https://github.com/mantidproject/mantidimaging/archive/master.zip`
:code:`unzip mantidimaging-master.zip`

Prerequisites
-------------

MantidImaging requires you to have an Anaconda distribution setup. If you do not
already have one then install Miniconda.

Environment
-----------

Create a virtual environment to run MantidImaging within using the command:
:code:`conda create -n mantidimaging python=3.5 anaconda` (note that you can
replace :code:`mantidimaging` with whatever name you would prefer).

The virtual environment can then be activated using the command :code:`source
activate mantidimaging`, this must be done before the :code:`mantidimaging`
package can be used (even after installation).

Installing the package
----------------------

The package can be installed using the following command inside the
:code:`mantidimaging` directory:

:code:`python setup.py install`

Alternatively, it can be useful to install in development mode if you plan on
frequently updating or modifying the package:

:code:`python setup.py develop`

Starting the package
--------------------

Once the package is installed it can be launched via either of the following
commands:

    - Command line: :code:`mantidimaging.sh <args...>`
    - IPython: :code:`mantidimaging-ipython.sh <args...>`
    - GUI: :code:`mantidimaging-gui.sh <args...>`

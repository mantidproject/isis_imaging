Documentation
=============

The documents are written in RST and generated with Sphinx, the build is
performed via the Sphinx integration with setuptools.

The most recent release of Sphinx can be installed from PyPI via :code:`pip
install sphinx` (the version available via the Ubuntu repositories does not
include all extensions that are required to build the documentation).

The documentation is version controlled along with the code, therefore it is
beneficial to make relevant changes to the documentation as the code is
modified.

Getting Started
---------------

TL;DR :code:`conda create -n mantidimaging -c conda-forge -c mantid/label/deps --only-deps mantidimaging && conda activate mantidimaging`

Setting up the correct environment requires installing a "deps" or dependencies
package, hosted in the Anaconda repository. This requires using the channel and the label :code:`deps`.
Additionally the channel :code:`conda-forge` is needed to supply some of the dependencies.

The command for that is as follows:

:code:`conda create -n mantidimaging -c conda-forge -c mantid/label/deps --only-deps mantidimaging`

This will create an environment called :code:`mantidimaging`, with the :code:`-n mantidimaging` flag.
It also specifies the :code:`conda-forge` channel, and the :code:`deps` label using :code:`-c mantid/label/deps`.
It will only install the dependencies by using the :code:`--only-deps` flag.

Afterwards the environment needs to be activated. This is done with:

:code:`conda activate mantidimaging`


Workflow
--------

TL;DR of building the documentation.

Run the commands:

.. code::

   python setup.py docs_api
   python setup.py docs
   python setup.py docs -b qthelp

If you also want to publish the docs:

.. code::

   python setup.py docs_publish


API Documentation
-----------------

The API documentation must be generated prior to building the documentation.
This is done with the command: :code:`python setup.py docs_api`.

HTML
----

The HTML pages can be built using :code:`python setup.py docs`, which will build
the documentation in :code:`docs/build.html`.

There is a setuptools command configured to deploy the documentation to GitHub
Pages where it will be visible at https://mantidproject.github.io/mantidimaging

This can be done via the command :code:`python setup.py docs_publish`.  This
assumes you are using SSH as your Git push protocol, if you are not you may
specify an alternative remote URL using the :code:`-r` argument.

QtHelp
------

It is also possible to use Sphinx to build the documentation as a Qt Help
project.

This can be done  with the command: :code:`python setup.py docs -b qthelp`.

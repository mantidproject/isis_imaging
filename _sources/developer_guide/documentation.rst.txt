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


Workflow
--------

TL;DR of building the documentation.

Run the commands:

.. code::

   python setup.py docs

This will create the documentation in the docs/build/html directory.

If you also want to publish the docs (note this is normally done as an automated process):

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


Release Notes
-------------

Release notes should be continuously updated during developement. Almost all pull requests should have an update to the relivent file and section in :file:`docs/release_notes`

If the next release name is not yet chosen this will be :file:`next.rts`, and renamed closer to release.

When fixes are backported to a release branch, they can be added to the notes for that release, in an updates section.

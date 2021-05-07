Testing
=======

Mantid imaging uses unit tests, static analysis and GUI approval testing

The full test suite can be run using:

.. code ::

    make check

Tests are run automatically on pull requests on GitHub using actions, but should also be run during development.

Unit testing
------------

Unit tests can be run using `pytest <https://docs.pytest.org/>`_, e.g.

.. code::

    python -m pytest

For options such as running a subset of tests, see `PyTest Docs <https://docs.pytest.org/en/stable/usage.html>`_


Static analysis
---------------

Mantid Imaging uses `mypy <http://mypy-lang.org/>`_, `flake8 <https://flake8.pycqa.org/>`_ and `yapf <https://github.com/google/yapf>`_ for static analysis and formatting. They are run by :code:`make check`, or can be run individually, e.g. :code:`make mypy`.


GUI Testing
-----------

Mantid Imaging uses `Applitools Eyes <https://applitools.com/products-eyes/>`_ for GUI approval testing. Screenshots of windows are uploaded and compared to known good baseline images. This is run in the github action on pull requests.

Appplitools requires an API key to use, which can be found on via a Applitools web interface. On a developer machine this can be passed as an environment variable. E.g.

.. code::

    APPLITOOLS_API_KEY=XXXXXXXXXX xvfb-run --auto-servernum pytest -p no:xdist -p no:randomly -p no:repeat -p no:cov mantidimaging/eyes_tests

Differences between uploaded and baseline images can be examined and approved or rejected from the Applitools web interface.

To run without a key or to prevent uploads, set ``APPLITOOLS_API_KEY`` to ``local`` and choose a directory to save the screenshots. Note that this does not check for changes, and will always pass. e.g.

.. code::

    mkdir /tmp/gui_test
    APPLITOOLS_API_KEY=local APPLITOOLS_IMAGE_DIR=/tmp/gui_test xvfb-run --auto-servernum pytest -p no:xdist -p no:randomly -p no:repeat -p no:cov mantidimaging/eyes_tests

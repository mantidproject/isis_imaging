Developer Conventions
=====================

Dependencies
------------

Mantid imaging makes use of a number of python modules. To ensure that these get installed for users they can be listed as dependencies.

Dependencies are categorised by when they are needed:

* Runtime: Needed to run Mantid Imaging.
* Development: Only needed during development.

and how they are installed:

* Conda: suitable version available in the conda repository. Preferred.
* Pip: suitable version available in the PyPI repository.

Conda runtime dependencies can be specified in `conda/meta.yaml`. These will be tracked automatically by conda and installed when ever the mantidimaging package installed.

Pip runtime dependencies can't be tracked automatically and so must be installed as part of the environment. These should be listed in `environment.yml`. Due to technical limitations they must also be duplicated in the pip section of `environment-dev.yml`.

Development dependencies should be listed in `environment-dev.yml`, with conda and pip dependencies placed in the correct place.
Creating a Release
==================

This is a checklist for creating a new release.

Releases are created from the ``master`` branch.

The version number is expected to be in SemVer format and will be referred to as
``M.m.p``, adjust this as appropriate.

- Update version numbers in:
  - ``setup.py``
  - ``mantidimaging/__init__.py``
- Create Git tag from ``master``: ``git tag M.m.p --sign``
- Push the tag to the repository: ``git push M.m.p``
- (optional) Add release notes in GitHub
- Start the `mantidimaging-master
  <http://builds.mantidproject.org/view/Imaging/job/mantidimaging-master/>`_
  CI job
- Download and extract the `build artefacts
  <http://builds.mantidproject.org/view/Imaging/job/mantidimaging-master/lastSuccessfulBuild/artifact/>`_
- Upload the Conda package to Anaconda Cloud: ``anaconda upload -u mantid
  --force mantidimaging-M.m.p-py35_0.tar.bz2`` (``--force`` is required as the
  CI job will have already uploaded this package with the ``nightly`` label)
- Build the API documentation: ``python setup.py docs_api``
- Build the documentation: ``python setup.py docs``
- Upload the documentation: ``python setup.py docs_publish``

Creating a Release
==================

This is a checklist for creating a new release.

Releases are created from the ``master`` branch.

The version number is expected to be in SemVer format and will be referred to as
``M.m.p``, adjust this as appropriate.

- Create a new release branch
- Update version numbers in:
   - ``setup.py``
   - ``mantidimaging/__init__.py``
   - ``docs/conf.py``
- Go to https://github.com/mantidproject/mantidimaging/releases
- Draft a new release, with the appropriate version number, targetting the new release branch
- Perform the necessary testing or merge necessary bug fixes in the release branch
- (optional) Add release notes in the docs GitHub
- Go to the release draft and publish it
- Once published the tag will be available for Conda to use, but a package with a :code:`main` label is not created automatically
  - To manually publish a package please follow :ref:`Conda Packaging and Docker images`
Mantid Imaging next release
===========================

This contains changes for the next not yet released Mantid Imaging versions.


New features
------------

- #927 : ROI norm: use averaged view in ROI selector
- #925 : Jenks / Otsu everywhere

Fixes
-----

- #939 : median: NameError: name 'cp' is not defined
- #957 : Crop Coordinates ROI not changing
- #961 :  Test failure: ImportError: libcuda.so.1

Developer Changes
-----------------

- #917 : Intermittent failure of StripeRemovalTest.test_memory_executed_wf
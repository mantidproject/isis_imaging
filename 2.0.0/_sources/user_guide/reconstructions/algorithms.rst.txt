.. _Reconstruction Algorithms:

Reconstruction Algorithms
=========================

FBP_CUDA and SIRT_CUDA
----------------------
These filters are used from the ASTRA Toolbox package.

`Link to the original documentation for FBP_CUDA <http://www.astra-toolbox.com/docs/algs/FBP_CUDA.html>`_.

`Link to the original documentation for SIRT_CUDA <http://www.astra-toolbox.com/docs/algs/SIRT_CUDA.html>`_.

This is an implementation of the algorithms for 2D data sets. They require a CUDA-compatible graphics card.

The creation of a projector and geometry is automated inside Mantid Imaging, and parallel beam geometry is assumed.

The geometry used is the parallel beam vector geometry, which allows tilt to be taken into account via the
centres of rotation for each slice. This means manual rotation of the images to correct the tilt shouldn't be necessary.

The vector creation code was re-used from `ToMoBAR <https://github.com/dkazanc/ToMoBAR/blob/master/src/Python/tomobar/supp/astraOP.py#L20-L70>`_.

FBP_CUDA
--------
This algorithm has the option to use different filters to improve reconstruction quality.

For an evaluation of the filters please go to the :ref:`Reconstruction Filters` page.

SIRT_CUDA
---------
Instead of filters for improving the reconstruction quality, this filter uses number of iterations.

Have a look at our refine iterations tool on the Reconstruct tab of the Reconstruction window that
should assist you in finding the optimal number of rotations for your data.

gridrec
-------
This filter is from the TomoPy package.

The original documentation for gridrec can be found `here <https://tomopy.readthedocs.io/en/latest/api/tomopy.recon.algorithm.html#module-tomopy.recon.algorithm>`_.

This is a CPU filter, and does not require a CUDA graphics card to run.

From the TomoPy documentation, these are the paper references for this filter:

- Dowd BA, Campbell GH, Marr RB, Nagarkar VV, Tipnis SV, Axe L, and Siddons DP. Developments in synchrotron x-ray computed microtomography at the national synchrotron light source. In Proc. SPIE, volume 3772, 224–236. 1999.
- Rivers ML. Tomorecon: high-speed tomography reconstruction on workstations using multi-threading. In Proc. SPIE, volume 8506, 85060U–85060U–13. 2012.

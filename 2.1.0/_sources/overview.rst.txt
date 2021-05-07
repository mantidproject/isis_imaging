Overview
========

Mantid Imaging contains tools for loading data from neutron imaging experiments, preprocessing to enhance images and tomographic reconstruction into 3 dimensional data that can be output for further analysis.

Mantid Imaging makes use of a range of algorithms, some from external tools including `Astra <http://www.astra-toolbox.com/>`_ and `Tomopy <https://tomopy.readthedocs.io/en/latest/>`_. Many of these are optimised for multithreading and GPU computing.

Mantid Imaging is written in Python and requires a CUDA capable GPU for full functionality. It runs on Linux. See :ref:`Installation` for more details.

See the :ref:`User Guide` for an example taking data from a set of images to full reconstruction.

Features
--------

Operations
^^^^^^^^^^

The Operations Window provides a selection of tools and filters to process and enhance the 2D images before running the reconstruction.

* Crop Coordinates
* Flat-fielding
* Remove Outliers
* ROI Normalisation

* Circular Mask
* Clip Values
* Divide
* Gaussian
* Median
* Monitor Normalisation
* Rebin
* Rescale
* Ring Removal
* Rotate Stack

* Remove all stripes
* Remove dead stripes
* Remove large stripes
* Stripe Removal
* Remove stripes with filtering
* Remove stripes with sorting and fitting

More details on using these are available in the :ref:`API Reference` and :ref:`User Guide`.


Reconstruction
^^^^^^^^^^^^^^

Mantid Imaging offers several reconstruction algorithms

* FBP_CUDA - Filtered Backprojection
* SIRT_CUDA - Simultaneous Iterative Reconstruction Technique
* gridrec

Glossary
--------

COR
   Centre of Rotation.

Dataset
   Consists of images stacks plus additional files or metadata, such as flat and dark frames, and log files.

Image
   A single 2D recorded by the experiment. Typically loaded from TIFF files.

Image Stack
   A set of multiple related images, for example images of the same object from a range of angles.

Projection
   The original image formed by the unscattered/unabsorbed neutrons reaching the imaging detector.

ROI
   Region of Interest. A cropped part of an image.

Sinogram
   A projection of all rotations of a single slice through an object. Each point in the slice becomes a sinusoidal line. Also known as a Radon transform.

Tomography
   The process of creating a 3D model if an object from a series 2D images taken at a range angles through it.


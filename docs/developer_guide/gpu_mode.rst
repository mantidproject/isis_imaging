GPU Notes
#########

Current GPU Configuration / Limitations
***************************************

- To minimise the occurence of memory problems, the
  :code:`MAX_CUPY_MEMORY_FRACTION` has been set to 0.8. This means that
  :code:`cupy` will assume it has access to no more than 80% of the GPU memory.
- The :code:`MAX_GPU_SLICES` variable determines how many images are stored on
  the GPU at any one time. This is currently set to 100 and does not take image
  dimensions or precision into account. This is not the most efficient solution
  but does at least work for managing asynchronous execution.
- The median and outlier GPU operations only work for input arrays of type
  float32 or float64 in numpy.
- The :code:`cupy` functions are recompiled every time the GPU filters are used.
- The GPU checkbox is visible and enabled regardless of whether :code:`cupy` is
  installed and working on the system.
- The function simply returns without having made any changes to the input array
  if :code:`cupy` encouters an :code:`OutOfMemoryError`.

Creating and Using GPU Algorithms
*********************************

Block and Grid Dimensions
=========================

Block and grid dimensions are used to determine how work is partitioned on a
GPU. These are set in the :code:`_create_block_and_grid_args` function using
the following formulas.

.. math::
    \textrm{Block size} = (N,N,N) \\
    \textrm{Grid size} = (\left\lceil{\frac{X}{N}}\right\rceil,\left\lceil{\frac{Y}{N}}\right\rceil,\left\lceil{\frac{Z}{N}}\right\rceil)

*N* is presently hard-coded as 10. *X*, *Y*, and *Z* denote the dimensions of
the input array being processed on the GPU.

Importing CUDA Kernels in Cupy
==============================

Once defined, CUDA functions can be used from Python in the following way

.. code-block:: Python

    imaging_filter_module = cp.RawModule(code=loaded_from_source)
    single_image_median_filter = imaging_filter_module.get_function("two_dimensional_median_filter")
    single_image_median_filter(
        grid_size,
        block_size,
        (
            input_data,
            padded_data,
            input_data.shape[0],
            input_data.shape[1],
            filter_size,
        ),
    )

where :code:`loaded_from_source` contains a CUDA kernel in the form of a Python
string. Note that the first arguments are the grid size and block size, with the
actual CUDA function arguments being given last in a tuple.

Warming-up Functions
====================

Upon creating a working CUDA function, it is advisable to run it on a smaller
array prior to running it with real data. In the case of the median and remove
outlier filters this takes place in the :code:`_warm_up` function in the
:code:`CudaExecuter` class. This is called from the initialiser.

CUDA Function Overview
**********************

Both the median and remove outlier filters work by using an insertion sort
to obtain the median value of the neighbouring pixels in a 2D image. They can
only be used on a stack of 2D images with each image being passed to the
functions individually. This allows for asynchronous execution.

2D Median Filter
================

.. code-block:: C

    __global__ void two_dimensional_median_filter(float *data_array,
                                                  const float *padded_array,
                                                  const int X, const int Y,
                                                  const int filter_size) {


The arguments passed to the median filter are a single 2D image array from the
stack, the padded image array, the *X* and *Y* dimensions of the image array,
and the filter size. All arguments besides the original data array are required
to be constant as the original data array is the only value that is overwritten.

The :code:`__global__` keyword indicates that this function can be called from
the CPU.

.. code-block:: C

      unsigned int id_x = blockIdx.x * blockDim.x + threadIdx.x;
      unsigned int id_y = blockIdx.y * blockDim.y + threadIdx.y;

      if ((id_x >= X) || (id_y >= Y))
        return;

The program begins by obtaining the :code:`id_x` and :code:`id_y` values that
determine pixel for which the median will be found. If this is outside the
boundaries of the array then the function returns without doing anything.

.. code-block:: C

      unsigned int index = (id_x * Y) + id_y;
      unsigned int padded_img_width = Y + filter_size - 1;

If the :code:`id_x` and :code:`id_y` values are acceptable, then the program
translates this to an index in the row-major array and calculates the width of
the padded image.

.. code-block:: C

      data_array[index] = find_neighbour_median(padded_array, padded_img_width,
                                                id_x, id_y, filter_size);

Finally, a helper method is called for finding the median value of a pixel in a
2D image. The result overwrites the pixel in the array located at :code:`index`.
The helper methods have the :code:`__device__` keyword in their header as they
are called solely from the GPU.

The complete function is shown below:

.. code-block:: C

    __global__ void two_dimensional_median_filter(float *data_array,
                                                  const float *padded_array,
                                                  const int X, const int Y,
                                                  const int filter_size) {
      unsigned int id_x = blockIdx.x * blockDim.x + threadIdx.x;
      unsigned int id_y = blockIdx.y * blockDim.y + threadIdx.y;

      if ((id_x >= X) || (id_y >= Y))
        return;

      unsigned int index = (id_x * Y) + id_y;
      unsigned int padded_img_width = Y + filter_size - 1;

      data_array[index] = find_neighbour_median(padded_array, padded_img_width,
                                                id_x, id_y, filter_size);
    }

2D Remove Outlier Filter
========================

The remove outlier filters work in a similar way to the median filter. Upon
finding the median, rather than place this in the array right away, a check is
carried out to see if the original value is much higher or much lower than the
median based on the value of the :code:`diff` argument. The original value is
only overwritten if this condition is true.

Slicing Algorithm
*****************

The Python code determines how many images from the stack will be on the GPU
at once. Upon finding the "slice limit" *L*, the program sends the first L
images from the stack and the first L padded images to the GPU. If the number of
images in the stack *N* falls below the hard-coded :code:`GPU_SLICE_LIMIT` then
the entire image stack is sent to the GPU.

The algorithm is illustrated in the following psuedocode:

.. code-block::

    Function ImagingFilter(ImageStack[][][], FilterSize, Args)

        N = |ImageStack|
        L = GetSliceLimit(N)

        Streams[] = CreateStreams(N)

        PaddedImageStack = CreatePaddedImages(ImageStack, FilterSize)

        GPUImages[][][] = SendDataToGPU(First L Elements of ImageStack, Streams)
        GPUPaddedImages[][][] = SendDataToGPU(First L Elements of
        PaddedImageStack, Streams)

        BlockSize, GridSize = GetBlockAndGridSizes(N)

        For i in N:

            Use Streams[i]

            If i >= L:
                Overwrite GPUImages[i][][] with ImageStack[i][][]
                Overwrite GPUPaddedImages[i][][] with
                PaddedImageStack[i][][]

            Synchronise Streams[i]

            GPUImagingAlgorithm(GPUImages[i][][], GPUPaddedImages[i][][],
            BlockSize, GridSize, Streams[i], Args)

            Synchronise Streams[i]

            Overwrite ImageStack[i][][] with GPUImageStack[i][][]

In essence, the data is processed as if it were on a ferris wheel consisting of
*L* cabins where the images are the *N* people who form the queue. The cabins
represent the limit of images on the GPU and the streams allocated to those
images. A person in the queue entering a cabin is a transfer from CPU to GPU
while a person exiting a cabin at the end of their ride is a transfer from GPU
to CPU. If *N* > *L* then at least one of the cabins will be used more than
once.

Development Pitfalls
********************

The filter was only peformed on part of the array or the filter works on small arrays then gets the wrong result for larger arrays
==================================================================================================================================
This may mean that the grid and dimension sizes do not account for the
entire array.

Float parameters become 0 in CUDA
=================================
This indicates the value was not converted to a numpy :code:`float` or
:code:`single` prior to being passed to the kernel.

:code:`cupy` objects appear to forget what they are
===================================================
If you find calling :code:`stream.sychronize` or some other method results in an
error because this is not part of the Stream class, it may due to having
created an array in CUDA and failing to free it. As the number of un-freed
arrays accumulates, this scrambles the pointer addresses which leads to this
behaviour.

Further Work
************

Intelligent Management of :code:`OutOfMemoryError`
==================================================
Presently, the median and remove outlier GPU filters give up when this
error is encoutered. In the future, it may be worth finding a way to
reattempt the operation under different conditions so as to not fill the
GPU.

Intelligent Management of Maximum Number of GPU Slices
======================================================
Ideally, the number of images on a stack that are transferred to a GPU would
depend on their size and the capacity of the GPU being used
rather than simply being a fixed number. This may be a more suitable long-term
solution for avoiding memory problems and would also be better suited for
running the algorithms on different hardware with minimal manual tinkering.

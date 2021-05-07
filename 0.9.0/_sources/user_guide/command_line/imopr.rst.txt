Immage Operator (imopr) mode
============================

This mode helps find the COR of a sample.

It also only operates on sinograms! If your images a radiograms, use the
:code:`--convert --swap-axes` option, which will convert the data to sinograms.

There are 2 main ways to find CORs on a sample; automatic and manual.

Automatic
---------

Automatic COR finding using :code:`--imopr <start_slice> <end_slice> <step>
cor`.

This will automatically find the COR guess on each of the slices you have
specified.

Example usage:

:code:`mantidimaging -i /some/data/ --imopr 100 500 50 cor`

This will find the COR for every 50 slices, and print it out on the screen.

Manual
------

Manual COR finding using :code:`corwrite`, for this mode
:code:`-o/--output-path` **MUST** be specified:

  - For a single slice: :code:`--imopr <slice_index> <start_cor> <end_cor>
    <step_for_cor> corwrite`

  - For multiple slices: :code:`--imopr <slice_start> <slice_end> <slice_step>
    <start_cor> <end_cor> <step_for_cor> corwrite`

Example usages:

- Single slice:

  :code:`mantidimaging -i /some/data -o /some/data --imopr 42 250 350 10
  corwrite`

This will reconstruct slice 42, with CORs starting from 250 up to 350, with a
step of 10.

The output will be a single folder with the name of the angle number (in this
case it will be a folder with name :code:`42`), and inside it will save a
reconstructed image for every COR.

- Multiple slices:

  :code:`mantidimaging -i /some/data -o /some/data --imopr 100 500 50 250 350 10
  corwrite`

This will reconstruct every 50 slices between 100 and 500, with the same COR
range as the single slice: starting from 250 to 350, with a step of 10.

The output will be a folder for *each* angle, with an image for *each* COR.

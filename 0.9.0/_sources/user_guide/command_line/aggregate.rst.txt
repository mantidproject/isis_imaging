Aggregating images
==================

This mode gives you the ability to aggregate images with different energy
levels.

Currently only one file structure is supported:

.. code::

  └── data (folder with all angles)
      ├── angle0 (folder per angle)
      │   ├── some_images_here_0.img_format
      │   ├── some_images_here_1.img_format
      │   ├── some_images_here_2.img_format
      │   ├── some_images_here_N.img_format
      ├── angle2
      │   ├── some_images_here_0.img_format
      │   ├── some_images_here_1.img_format
      │   ├── some_images_here_2.img_format
      │   ├── some_images_here_N.img_format
      ├── angleN
      │   ├── some_images_here_0.img_format
      │   ├── some_images_here_1.img_format
      │   ├── some_images_here_2.img_format
      │   ├── some_images_here_N.img_format

.. image:: ../../_static/aggregate.png
    :alt: Aggregate Directory Structure

For usage of this mode the following arguments are available:

`--aggregate`
-------------

Syntax: :code:`--aggregate <start_energy> <end_energy>... <mode:{sum/avg}>`

This flag will activate the mode, it requires an even number of inputs, which
should correspond to start and end energy levels. The final argument must be
either **sum** (sum of ALL of the images) or **avg** (mean of ALL of the images)
specifying the method used to create the aggregated image.

- Using avg as an aggregation mode produces images with pixel values range that
  are closer to the original images
- Using sum will produce images with very large pixel values

Example usage:

:code:`mantidimaging -i /some/data/ --aggregate 0 10 -o /some/directory`

:code:`mantidimaging -i /some/data/ --aggregate 150 435 -o /some/directory`

`--aggregate-angles`
--------------------

Syntax: :code:`--aggregate-angles <start_angle> <end_angle>`

This flag allows to select only certain angles for aggregation _within_ the
input folder.

The :code:`--aggregate ...` command **MUST** be passed otherwise this flag will be
ignored.

Example usage:

:code:`mantidimaging -i /some/data/ --aggregate 0 10 --aggregate-angles 0 10 -o
/some/directory`

:code:`mantidimaging -i /some/data/ --aggregate 0 10 --aggregate-angles 3 4 -o
/some/directory`

The default output directory structure will create a folder for each angle, and
inside this folder there will be an image for each range of energy levels
selected.

This command line :code:`mantidimaging -i /data/ --aggregate 0 10 avg -o
aggregate/` creates the following structure:

.. code::

  aggregate/
  ├── angle_avg0
  │   └── out_avg0_10.tiff
  ├── angle_avg1
  │   └── out_avg0_10.tiff
  ├── angle_avg10
  │   └── out_avg0_10.tiff
  ├── angle_avg2
  │   └── out_avg0_10.tiff
  ├── angle_avg3
  │   └── out_avg0_10.tiff
  ├── angle_avg4
  │   └── out_avg0_10.tiff
  ├── angle_avg5
  │   └── out_avg0_10.tiff
  ├── angle_avg6
  │   └── out_avg0_10.tiff
  ├── angle_avg7
  │   └── out_avg0_10.tiff
  ├── angle_avg8
  │   └── out_avg0_10.tiff
  └── angle_avg9
      └── out_avg0_10.tiff

Each of the input angles has a folder, the method used is appended to the name,
as well as the angle number.

Inside the folders the images contain the energy levels which were aggregated.

`--aggregate-single-folder-output`
----------------------------------

This command gives the option to **not** create the structure above.

This command line :code:`mantidimaging -i /data/ --aggregate 0 100 avg -o
aggregate/ --aggregate-single-folder-output` creates the following file
structure:

.. code::

  aggregate/
  ├── out_avg_0_100_0.tiff
  ├── out_avg_0_100_1.tiff
  ├── out_avg_0_100_2.tiff
  ├── out_avg_0_100_3.tiff
  ├── out_avg_0_100_4.tiff
  ├── out_avg_0_100_5.tiff
  ├── out_avg_0_100_6.tiff
  ├── out_avg_0_100_7.tiff
  ├── out_avg_0_100_8.tiff
  ├── out_avg_0_100_9.tiff
  └── out_avg_0_100_10.tiff

Each image has the range of energy levels it aggregated (0-100 in this case),
and the angle it corresponds to. The angle is appended last because it allows
for easy sorting of the files by this and other imaging software.

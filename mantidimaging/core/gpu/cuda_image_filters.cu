extern "C" {
/**
  Prints a float array. Can be helpful for debugging.

  @param array     The float array.
  @param N         The size of the array.
 */
__device__ void print_float_array(const float *array, const int N) {
  for (int i = 0; i < N; i++)
    printf("%.3f ", array[i]);
  printf("\n");
}
/**
  Prints the neighbour elements of a pixel in a 2D array. Can be helpful for
  debugging.

  @param padded_array        The padded data array.
  @param padded_img_width    The width of the padded image.
  @param id_x                The x index of the current pixel.
  @param id_y                The y index of the current pixel.
  @param filter_size         The size of the filter.
 */
__device__ void print_neighbour_elements_in_two_dimensional_array(
    const float *padded_array, const int padded_img_width, const int id_x,
    const int id_y, const int filter_size) {
  for (int i = id_x; i < id_x + filter_size; i++)
    for (int j = id_y; j < id_y + filter_size; j++)
      printf("%.3f ", padded_array[(i * padded_img_width) + j]);
  printf("\n");
}
/**
  Insertion sorts a 1D array and returns its median.
  Helper function for the 2D median and 2D remove outlier filters.

  @param array     The float array.
  @param N         The size of the array.
  @return          The median of the array.
 */
__device__ float find_median_in_neighbour_array(float *neighbour_array,
                                                const int N) {
  int i, j;
  float key;

  for (i = 1; i < N; i++) {
    key = neighbour_array[i];
    j = i - 1;

    while (j >= 0 && neighbour_array[j] > key) {
      neighbour_array[j + 1] = neighbour_array[j];
      j = j - 1;
    }
    neighbour_array[j + 1] = key;
  }

  return neighbour_array[N / 2];
}
/**
  Returns the median of a pixel's neighbours in a 2D array.
  Helper function for the 2D median and 2D remove outlier filters.

  @param padded_array        The padded data array.
  @param padded_img_width    The width of the padded image.
  @param id_x                The x index of the current pixel.
  @param id_y                The y index of the current pixel.
  @param filter_size         The size of the filter.
  @return                    The median of the pixel's neighbourhood.
 */
__device__ float find_neighbour_median(const float *padded_array,
                                       const int padded_img_width,
                                       const int id_x, const int id_y,
                                       const int filter_size) {
  float *neighbour_array = new float[filter_size * filter_size];
  int n_counter = 0;

  for (int i = id_x; i < id_x + filter_size; i++) {
    for (int j = id_y; j < id_y + filter_size; j++) {
      neighbour_array[n_counter] = padded_array[(i * padded_img_width) + j];
      n_counter += 1;
    }
  }

  float median = find_median_in_neighbour_array(neighbour_array,
                                                filter_size * filter_size);
  free(neighbour_array);
  return median;
}
/**
  Applies a median filter to all the pixels in a 2D array.
  This function should be used asynchronously with a stack of 2D images.

  @param data_array       The original data array.
  @param padded_array     The padded data array.
  @param X                The height of the image.
  @param Y                The width of the image.
  @param filter_size      The size of the filter.
 */
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
/**
  Applies a remove bright outliers filter to all the pixels in a 2D array.
  This function should be used asynchronously with a stack of 2D images.

  @param data_array       The original data array.
  @param padded_array     The padded data array.
  @param X                The height of the image.
  @param Y                The width of the image.
  @param filter_size      The size of the filter.
  @param diff             The difference required to replace the original pixel
                          value with the median.
 */
__global__ void two_dimensional_remove_bright_outliers(
    float *data_array, const float *padded_array, const int X, const int Y,
    const int filter_size, const float diff) {
  unsigned int id_x = blockIdx.x * blockDim.x + threadIdx.x;
  unsigned int id_y = blockIdx.y * blockDim.y + threadIdx.y;

  if ((id_x >= X) || (id_y >= Y))
    return;

  unsigned int index = (id_x * Y) + id_y;
  unsigned int padded_img_width = Y + filter_size - 1;

  float median = find_neighbour_median(padded_array, padded_img_width, id_x,
                                       id_y, filter_size);

  if (data_array[index] - median >= diff)
    data_array[index] = median;
}
/**
  Applies a remove dark outliers filter to all the pixels in a 2D array.
  This function should be used asynchronously with a stack of 2D images.

  @param data_array       The original data array.
  @param padded_array     The padded data array.
  @param X                The height of the image.
  @param Y                The width of the image.
  @param filter_size      The size of the filter.
  @param diff             The difference required to replace the original pixel
                          value with the median.
 */
__global__ void two_dimensional_remove_dark_outliers(float *data_array,
                                                     const float *padded_array,
                                                     const int X, const int Y,
                                                     const int filter_size,
                                                     const float diff) {
  unsigned int id_x = blockIdx.x * blockDim.x + threadIdx.x;
  unsigned int id_y = blockIdx.y * blockDim.y + threadIdx.y;

  if ((id_x >= X) || (id_y >= Y))
    return;

  unsigned int index = (id_x * Y) + id_y;
  unsigned int padded_img_width = Y + filter_size - 1;

  float median = find_neighbour_median(padded_array, padded_img_width, id_x,
                                       id_y, filter_size);

  if (data_array[index] - median <= diff)
    data_array[index] = median;
}
}

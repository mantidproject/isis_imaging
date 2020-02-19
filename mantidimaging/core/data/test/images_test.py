import unittest

import numpy as np
from six import StringIO

from mantidimaging.core.data import Images


class ImagesTest(unittest.TestCase):
    def test_to_string_empty(self):
        imgs = Images(np.array([1]))
        self.assertEquals(str(imgs), 'Image Stack: sample=(1,), flat=None, dark=None, |properties|=0')

    def test_to_string_with_sample(self):
        sample = np.ndarray(shape=(2, 64, 64))
        imgs = Images(sample)
        self.assertEquals(str(imgs), 'Image Stack: sample=(2, 64, 64), flat=None, dark=None, ' '|properties|=0')

    def test_parse_metadata_file(self):
        json_file = StringIO('{"a_int": 42, "a_string": "yes", "a_arr": ["one", "two", '
                             '"three"], "a_float": 3.65e-05, "a_bool": true}')

        imgs = Images([1])
        imgs.load_metadata(json_file)

        def validate_prop(k, v):
            self.assertEquals(imgs.metadata[k], v)

        validate_prop('a_bool', True)
        validate_prop('a_string', 'yes')
        validate_prop('a_int', 42)
        validate_prop('a_arr', ['one', 'two', 'three'])

    def test_record_parameters_in_metadata(self):
        imgs = Images([1])
        self.assertFalse(imgs.has_history)

        imgs.record_operation('test_func',
                              'A pretty name',
                              56,
                              9002,
                              np.ndarray((800, 1024, 1024)),
                              'yes',
                              False,
                              this=765,
                              that=495.0,
                              roi=(1, 2, 3, 4))

        self.assertTrue(imgs.has_history)

        self.assertEquals(
            imgs.metadata, {
                'operation_history': [{
                    'name': 'test_func',
                    'display_name': 'A pretty name',
                    'args': [56, 9002, None, 'yes', False],
                    'kwargs': {
                        'this': 765,
                        'that': 495.0,
                        'roi': (1, 2, 3, 4)
                    },
                }]
            })

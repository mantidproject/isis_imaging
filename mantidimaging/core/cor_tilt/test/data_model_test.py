from unittest import TestCase

from mantidimaging.core.cor_tilt import CorTiltDataModel
from mantidimaging.core.cor_tilt.data_model import Point
from mantidimaging.gui.windows.cor_tilt import Column, COLUMN_NAMES


class CorTiltDataModelTest(TestCase):
    def test_field_defs_sanity(self):
        self.assertEquals(len(Column), len(COLUMN_NAMES))

    def test_init(self):
        m = CorTiltDataModel()

        self.assertTrue(m.empty)
        self.assertEquals(m.num_points, 0)
        self.assertEquals(m.slices, [])
        self.assertEquals(m.cors, [])
        self.assertFalse(m.has_results)

    def test_add_points(self):
        m = CorTiltDataModel()
        m.add_point(0)
        m.add_point(0, 20, 5.0)
        m.add_point(1, 60, 7.8)

        self.assertFalse(m.empty)
        self.assertEquals(m.num_points, 3)
        self.assertEquals(m.slices, [20, 60, 0])
        self.assertEquals(m.cors, [5.0, 7.8, 0.0])

    def test_add_points_no_index(self):
        m = CorTiltDataModel()
        m.add_point(None)
        m.add_point(None, 20, 5.0)
        m.add_point(None, 60, 7.8)

        self.assertFalse(m.empty)
        self.assertEquals(m.num_points, 3)
        self.assertEquals(m.slices, [0, 20, 60])
        self.assertEquals(m.cors, [0.0, 5.0, 7.8])

    def test_clear_points(self):
        m = CorTiltDataModel()
        m.add_point(0)
        m.add_point(0, 20, 5.0)
        m.add_point(1, 60, 7.8)
        m.clear_points()

        self.assertTrue(m.empty)
        self.assertEquals(m.num_points, 0)
        self.assertEquals(m.slices, [])
        self.assertEquals(m.cors, [])

    def test_populate_slice_indices_no_cor(self):
        m = CorTiltDataModel()
        m.populate_slice_indices(300, 400, 20)

        self.assertEquals(m.num_points, 20)
        self.assertEquals(m.point(0)[0], 300)
        self.assertEquals(m.point(19)[0], 400)

        for i in range(20):
            self.assertEquals(m.point(i)[1], 0.0)

    def test_populate_slice_indices_with_cor(self):
        m = CorTiltDataModel()
        m.populate_slice_indices(300, 400, 20, 56.7)

        self.assertEquals(m.num_points, 20)
        self.assertEquals(m.point(0)[0], 300)
        self.assertEquals(m.point(19)[0], 400)

        for i in range(20):
            self.assertEquals(m.point(i)[1], 56.7)

    def test_linear_regression_no_data(self):
        m = CorTiltDataModel()

        with self.assertRaises(ValueError):
            m.linear_regression()

        self.assertFalse(m.has_results)

    def test_linear_regression(self):
        m = CorTiltDataModel()
        m.add_point(None, 0, 5.0)
        m.add_point(None, 10, 6.0)
        m.add_point(None, 20, 7.0)
        m.add_point(None, 30, 8.0)
        m.linear_regression()

        self.assertTrue(m.has_results)
        self.assertAlmostEqual(m.gradient, 0.1)
        self.assertAlmostEqual(m.cor, 5.0)

    def test_linear_regression_data(self):
        m = CorTiltDataModel()
        m._points = [
            Point(1409, 1401),
            Point(1386, 1400),
            Point(1363, 1400),
            Point(1340, 1401),
            Point(1317, 1400),
            Point(1294, 1399),
            Point(1271, 1398),
            Point(1248, 1400),
            Point(1225, 1398),
            Point(1202, 1400),
            Point(1179, 1399),
            Point(1156, 1399),
            Point(1133, 1400),
            Point(1110, 1402),
            Point(1087, 1398),
            Point(1064, 1398),
            Point(1041, 1397),
            Point(1018, 1399),
            Point(995, 1398),
            Point(972, 1401),
            Point(949, 1397),
            Point(926, 1398),
            Point(903, 1398),
            Point(880, 1398),
            Point(857, 1396),
            Point(834, 1397),
        ]
        m.linear_regression()

        self.assertAlmostEqual(m.gradient, 0.005292, places=6)
        self.assertAlmostEqual(m.cor, 1392.99, places=2)

    def test_stack_properties(self):
        m = CorTiltDataModel()
        m.add_point(None, 0, 5.0)
        m.add_point(None, 10, 6.0)
        m.add_point(None, 20, 7.0)
        m.add_point(None, 30, 8.0)
        m.linear_regression()

        d = m.stack_properties
        self.assertEqual(len(d), 5)

        self.assertEqual(d['fitted_gradient'], m.gradient)
        self.assertEqual(d['rotation_centre'], m.cor)
        self.assertEqual(d['slice_indices'], m.slices)
        self.assertEqual(d['rotation_centres'], m.cors)
        self.assertTrue(isinstance(d['tilt_angle_rad'], float))

    def test_clear_results(self):
        m = CorTiltDataModel()
        m.add_point(None, 0, 5.0)
        m.add_point(None, 10, 6.0)
        m.add_point(None, 20, 7.0)
        m.add_point(None, 30, 8.0)
        m.linear_regression()

        m.clear_results()

        self.assertFalse(m.has_results)

    def test_data_ordering(self):
        m = CorTiltDataModel()
        m.add_point(None, 30, 7.0)
        m.add_point(None, 10, 5.0)
        m.add_point(None, 40, 8.0)
        m.add_point(None, 20, 6.0)

        m.sort_points()

        # Expect data to be sorted as it is inserted
        self.assertEquals(m.slices, [10, 20, 30, 40])
        self.assertEquals(m.cors, [5.0, 6.0, 7.0, 8.0])

        m.linear_regression()

        self.assertTrue(m.has_results)
        self.assertAlmostEqual(m.gradient, 0.1)
        self.assertAlmostEqual(m.cor, 4.0)

    def test_get_cor_for_slice(self):
        m = CorTiltDataModel()
        m.add_point(None, 10, 5.0)
        m.add_point(None, 20, 6.0)
        m.add_point(None, 30, 7.0)
        m.add_point(None, 40, 8.0)

        self.assertEquals(m.get_cor_for_slice(10), 5.0)
        self.assertEquals(m.get_cor_for_slice(30), 7.0)
        self.assertIsNone(m.get_cor_for_slice(45))

    def test_get_cor_for_slice_from_regression(self):
        m = CorTiltDataModel()
        m.add_point(None, 10, 5.0)
        m.add_point(None, 20, 6.0)
        m.add_point(None, 30, 7.0)
        m.add_point(None, 40, 8.0)

        m.linear_regression()

        self.assertEquals(m.get_cor_for_slice_from_regression(0), 4.0)
        self.assertEquals(m.get_cor_for_slice_from_regression(10), 5.0)
        self.assertEquals(m.get_cor_for_slice_from_regression(50), 9.0)

    def test_get_data_idx_for_slice_idx(self):
        m = CorTiltDataModel()
        m.add_point(None, 10, 5.0)
        m.add_point(None, 20, 6.0)
        m.add_point(None, 30, 7.0)
        m.add_point(None, 40, 8.0)

        self.assertEquals(m._get_data_idx_from_slice_idx(10), 0)
        self.assertIsNone(m._get_data_idx_from_slice_idx(100))

    def test_set_cor_at_slice(self):
        m = CorTiltDataModel()
        m.add_point(None, 10, 5.0)
        m.add_point(None, 20, 6.0)
        m.add_point(None, 30, 7.0)
        m.add_point(None, 40, 8.0)

        m.set_cor_at_slice(30, 15)
        self.assertEquals(m.cors, [5.0, 6.0, 15.0, 8.0])

import unittest
import uuid

import mock

from mantidimaging.core.utility.data_containers import LoadingParameters
from mantidimaging.gui.windows.main import MainWindowModel
from mantidimaging.gui.windows.main.model import StackId


class MainWindowModelTest(unittest.TestCase):
    def __init__(self, *args, **kwargs):
        super(MainWindowModelTest, self).__init__(*args, **kwargs)

    def setUp(self):
        self.model = MainWindowModel()
        self.model_class_name = f"{self.model.__module__}.{self.model.__class__.__name__}"
        self.stack_list_property = f"{self.model_class_name}.stack_list"

    def test_initial_stack_list(self):
        self.assertEqual(self.model._stack_names, [])

    def test_create_name_no_stacks_loaded(self):
        # Mock the stack list function (this depends on Qt)
        with mock.patch(self.stack_list_property, new_callable=mock.PropertyMock) as mock_stack_list:
            mock_stack_list.return_value = []
            self.assertEqual(self.model.create_name("test"), "test")

    def test_create_name_one_duplicate_stack_loaded(self):
        with mock.patch(self.stack_list_property, new_callable=mock.PropertyMock) as mock_stack_list:
            mock_stack_list.return_value = [StackId('aaa', 'test')]
            self.assertEqual(self.model.create_name("test"), "test_2")

    def test_create_name_multiple_duplicate_stacks_loaded(self):
        with mock.patch(self.stack_list_property, new_callable=mock.PropertyMock) as mock_stack_list:
            mock_stack_list.return_value = [StackId('aaa', 'test'), StackId('aaa', 'test_2'), StackId('aaa', 'test_3')]
            self.assertEqual(self.model.create_name("test"), "test_4")

    def test_create_name_strips_extension(self):
        with mock.patch(self.stack_list_property, new_callable=mock.PropertyMock) as mock_stack_list:
            mock_stack_list.return_value = []
            self.assertEqual(self.model.create_name("test.tif"), "test")

    def _add_mock_widget(self):
        expected_name = "stackname"
        widget_mock = mock.Mock()
        widget_mock.windowTitle.return_value = expected_name
        uid = uuid.uuid4()
        self.model.active_stacks = {uid: widget_mock}
        return uid, widget_mock, expected_name

    def test_add_stack(self):
        stack_mock = mock.Mock()
        expected_name = "stackname"
        widget_mock = mock.Mock()
        widget_mock.windowTitle.return_value = expected_name

        self.model.add_stack(stack_mock, widget_mock)

        self.assertTrue(hasattr(stack_mock, 'uuid'))
        self.assertEqual(1, len(self.model.stack_list))
        self.assertEqual(1, len(self.model._stack_names))
        self.assertEqual(expected_name, self.model._stack_names[0])

    def test_stack_list(self):
        uid, widget_mock, expected_name = self._add_mock_widget()

        self.assertEqual(1, len(self.model.stack_list))
        self.assertEqual(1, len(self.model._stack_names))
        self.assertEqual(uid, self.model.stack_list[0].id)
        self.assertEqual(expected_name, self.model._stack_names[0])

    def test_get_stack(self):
        uid, widget_mock, _ = self._add_mock_widget()

        self.assertIs(widget_mock, self.model.get_stack(uid))

    def test_get_stack_by_name(self):
        _, widget_mock, expected_name = self._add_mock_widget()

        self.assertIs(widget_mock, self.model.get_stack_by_name(expected_name))

    def test_get_stack_by_images(self):
        _, widget_mock, expected_name = self._add_mock_widget()

        self.assertIs(widget_mock, self.model.get_stack_by_name(expected_name))

    def test_get_stack_visualiser(self):
        uid, widget_mock, _ = self._add_mock_widget()
        expected_widget = mock.Mock()
        widget_mock.widget.return_value = expected_widget

        self.assertIs(expected_widget, self.model.get_stack_visualiser(uid))
        widget_mock.widget.assert_called_once()

    def test_do_remove_stack(self):
        uid, _, _ = self._add_mock_widget()

        self.assertEqual(1, len(self.model.stack_list))
        self.model.do_remove_stack(uid)
        self.assertEqual(0, len(self.model.stack_list))

    def test_have_active_stacks(self):
        uid, _, _ = self._add_mock_widget()
        self.assertTrue(self.model.have_active_stacks)
        self.model.do_remove_stack(uid)
        self.assertFalse(self.model.have_active_stacks)

    @mock.patch('mantidimaging.core.io.loader.load_log')
    @mock.patch('mantidimaging.core.io.loader.load_p')
    def test_do_load_stack_sample_only(self, load_p_mock: mock.Mock, load_log_mock: mock.Mock):
        lp = LoadingParameters()
        sample_mock = mock.Mock()
        sample_mock.log_file = None
        lp.sample = sample_mock
        lp.dtype = "dtype_test"
        lp.sinograms = True
        lp.pixel_size = 101
        progress_mock = mock.Mock()

        self.model.do_load_stack(lp, progress_mock)

        load_p_mock.assert_called_once_with(sample_mock, lp.dtype, progress_mock)
        load_log_mock.assert_not_called()

    @mock.patch('mantidimaging.core.io.loader.load_log')
    @mock.patch('mantidimaging.core.io.loader.load_p')
    def test_do_load_stack_sample_and_sample_log(self, load_p_mock: mock.Mock, load_log_mock: mock.Mock):
        lp = LoadingParameters()
        sample_mock = mock.Mock()
        lp.sample = sample_mock
        lp.dtype = "dtype_test"
        lp.sinograms = False
        lp.pixel_size = 101
        progress_mock = mock.Mock()

        self.model.do_load_stack(lp, progress_mock)

        load_p_mock.assert_called_once_with(sample_mock, lp.dtype, progress_mock)
        load_log_mock.assert_called_once_with(sample_mock.log_file)

    @mock.patch('mantidimaging.core.io.loader.load_log')
    @mock.patch('mantidimaging.core.io.loader.load_p')
    def test_do_load_stack_sample_and_flat(self, load_p_mock: mock.Mock, load_log_mock: mock.Mock):
        lp = LoadingParameters()
        sample_mock = mock.Mock()
        lp.sample = sample_mock
        lp.dtype = "dtype_test"
        lp.sinograms = False
        lp.pixel_size = 101

        flat_before_mock = mock.Mock()
        lp.flat_before = flat_before_mock
        flat_after_mock = mock.Mock()
        lp.flat_after = flat_after_mock
        progress_mock = mock.Mock()

        self.model.do_load_stack(lp, progress_mock)

        load_p_mock.assert_has_calls(
            [mock.call(sample_mock, lp.dtype, progress_mock),
             mock.call(flat_before_mock, lp.dtype, progress_mock),
             mock.call(flat_after_mock, lp.dtype, progress_mock)])
        load_log_mock.assert_has_calls([mock.call(sample_mock.log_file), mock.call(flat_before_mock.log_file),
                                        mock.call(flat_after_mock.log_file)])

    @mock.patch('mantidimaging.core.io.loader.load_log')
    @mock.patch('mantidimaging.core.io.loader.load_p')
    def test_do_load_stack_sample_and_flat_and_dark_and_180deg(self, load_p_mock: mock.Mock, load_log_mock: mock.Mock):
        lp = LoadingParameters()
        sample_mock = mock.Mock()
        lp.sample = sample_mock
        lp.dtype = "dtype_test"
        lp.sinograms = False
        lp.pixel_size = 101

        flat_before_mock = mock.Mock()
        lp.flat_before = flat_before_mock
        flat_after_mock = mock.Mock()
        lp.flat_after = flat_after_mock

        dark_before_mock = mock.Mock()
        lp.dark_before = dark_before_mock
        dark_after_mock = mock.Mock()
        lp.dark_after = dark_after_mock

        proj_180deg_mock = mock.Mock()
        lp.proj_180deg = proj_180deg_mock

        progress_mock = mock.Mock()

        self.model.do_load_stack(lp, progress_mock)

        load_p_mock.assert_has_calls([
            mock.call(sample_mock, lp.dtype, progress_mock),
            mock.call(flat_before_mock, lp.dtype, progress_mock),
            mock.call(flat_after_mock, lp.dtype, progress_mock),
            mock.call(dark_before_mock, lp.dtype, progress_mock),
            mock.call(dark_after_mock, lp.dtype, progress_mock),
            mock.call(proj_180deg_mock, lp.dtype, progress_mock)
        ])

        load_log_mock.assert_has_calls([mock.call(sample_mock.log_file), mock.call(flat_before_mock.log_file),
                                        mock.call(flat_after_mock.log_file)])

    def test_create_name(self):
        self.assertEqual("apple", self.model.create_name("apple"))

        taken_name = "apple"
        widget_mock = mock.Mock()
        widget_mock.windowTitle.return_value = taken_name
        self.model.active_stacks = {"some_uuid": widget_mock}

        self.assertEqual("apple_2", self.model.create_name("apple"))


if __name__ == '__main__':
    unittest.main()

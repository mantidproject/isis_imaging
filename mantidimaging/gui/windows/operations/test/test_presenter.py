# Copyright (C) 2020 ISIS Rutherford Appleton Laboratory UKRI
# SPDX - License - Identifier: GPL-3.0-or-later

import unittest
from functools import partial

import mock
import pytest

from mantidimaging.gui.windows.main import MainWindowView
from mantidimaging.gui.windows.operations import FiltersWindowPresenter
from mantidimaging.test_helpers.unit_test_helper import assert_called_once_with, generate_images


class FiltersWindowPresenterTest(unittest.TestCase):
    def setUp(self) -> None:
        self.main_window = mock.create_autospec(MainWindowView)
        self.view = mock.MagicMock()
        self.presenter = FiltersWindowPresenter(self.view, self.main_window)
        self.view.presenter = self.presenter

    @mock.patch('mantidimaging.gui.windows.operations.presenter.FiltersWindowModel.filter_registration_func')
    def test_register_active_filter(self, filter_reg_mock: mock.Mock):
        reg_fun_mock = mock.Mock()
        filter_reg_mock.return_value = reg_fun_mock
        self.view.filterSelector.currentIndex.return_value = 0
        self.presenter.do_register_active_filter()

        reg_fun_mock.assert_called_once()
        filter_reg_mock.assert_called_once()

    @mock.patch('mantidimaging.gui.windows.operations.presenter.FiltersWindowModel.do_apply_filter')
    def test_apply_filter(self, apply_filter_mock: mock.Mock):
        stack = mock.Mock()
        presenter = mock.Mock()
        stack.presenter = presenter
        presenter.images.has_proj180deg.return_value = False
        self.presenter.stack = stack
        self.presenter.view.safeApply.isChecked.return_value = False
        self.presenter.do_apply_filter()
        self.view.clear_previews.assert_called_once()

        expected_apply_to = [stack]
        assert_called_once_with(apply_filter_mock, expected_apply_to,
                                partial(self.presenter._post_filter, expected_apply_to))

    @mock.patch("mantidimaging.gui.windows.operations.presenter.operation_in_progress")
    @mock.patch('mantidimaging.gui.windows.operations.presenter.FiltersWindowModel.do_apply_filter')
    def test_apply_filter_to_all(self, apply_filter_mock: mock.Mock, _):
        self.view.ask_confirmation.return_value = False
        self.presenter.do_apply_filter_to_all()

        self.view.ask_confirmation.assert_called_once()

        self.view.ask_confirmation.reset_mock()
        self.view.ask_confirmation.return_value = True
        mock_stack_visualisers = [mock.Mock(), mock.Mock()]
        self.presenter.main_window = mock.Mock()
        self.presenter.main_window.get_all_stack_visualisers = mock.Mock()
        self.presenter.main_window.get_all_stack_visualisers.return_value = mock_stack_visualisers

        self.presenter.do_apply_filter_to_all()

        assert_called_once_with(apply_filter_mock, mock_stack_visualisers,
                                partial(self.presenter._post_filter, mock_stack_visualisers))

    @mock.patch('mantidimaging.gui.windows.operations.presenter.FiltersWindowPresenter.do_update_previews')
    def test_post_filter_success(self, update_previews_mock):
        self.presenter.view.safeApply.isChecked.return_value = False
        mock_stack_visualisers = [mock.Mock(), mock.Mock()]
        mock_task = mock.Mock()
        mock_task.error = None
        self.presenter._do_apply_filter = mock.MagicMock()
        self.presenter._post_filter(mock_stack_visualisers, mock_task)

        for i, msv in enumerate(mock_stack_visualisers):
            assert msv.presenter.images == self.view.main_window.update_stack_with_images.call_args_list[i].args[0]
        update_previews_mock.assert_called_once()
        self.view.clear_notification_dialog.assert_called_once()
        self.view.show_operation_completed.assert_called_once_with(self.presenter.model.selected_filter.filter_name)

    @mock.patch('mantidimaging.gui.windows.operations.presenter.FiltersWindowPresenter.do_update_previews')
    def test_post_filter_fail(self, update_previews_mock):
        self.presenter.view.safeApply.isChecked.return_value = False
        self.presenter.view.show_error_dialog = mock.MagicMock()
        mock_stack_visualisers = [mock.Mock(), mock.Mock()]
        mock_task = mock.Mock()
        mock_task.error = 123
        self.presenter._do_apply_filter = mock.MagicMock()
        self.presenter._post_filter(mock_stack_visualisers, mock_task)

        self.presenter.view.show_error_dialog.assert_called_once_with('Operation failed: 123')
        update_previews_mock.assert_called_once()

    def test_images_with_180_deg_proj_calls_filter_on_the_180_deg(self):
        self.presenter.view.safeApply.isChecked.return_value = False
        self.presenter._do_apply_filter = mock.MagicMock()
        self.presenter.applying_to_all = False
        mock_stack = mock.MagicMock()
        mock_stack.presenter.images.has_proj180deg.return_value = True
        mock_stack_visualisers = [mock_stack]
        mock_task = mock.MagicMock()
        mock_task.error = None

        self.presenter._post_filter(mock_stack_visualisers, mock_task)

        self.presenter._do_apply_filter.assert_called_once()

    def test_update_previews_no_stack(self):
        self.presenter.do_update_previews()
        self.view.clear_previews.assert_called_once()

    @mock.patch('mantidimaging.gui.windows.operations.presenter.FiltersWindowPresenter._update_preview_image')
    @mock.patch('mantidimaging.gui.windows.operations.presenter.FiltersWindowModel.apply_to_images')
    def test_update_previews_apply_throws_exception(self, apply_mock: mock.Mock, update_preview_image_mock: mock.Mock):
        apply_mock.side_effect = Exception
        stack = mock.Mock()
        presenter = mock.Mock()
        stack.presenter = presenter
        images = generate_images()
        presenter.get_image.return_value = images
        self.presenter.stack = stack

        self.presenter.do_update_previews()

        presenter.get_image.assert_called_once_with(self.presenter.model.preview_image_idx)
        self.view.clear_previews.assert_called_once()
        update_preview_image_mock.assert_called_once()
        apply_mock.assert_called_once()

    @mock.patch('mantidimaging.gui.windows.operations.presenter.FiltersWindowPresenter._update_preview_image')
    @mock.patch('mantidimaging.gui.windows.operations.presenter.FiltersWindowModel.apply_to_images')
    def test_update_previews(self, apply_mock: mock.Mock, update_preview_image_mock: mock.Mock):
        stack = mock.Mock()
        presenter = mock.Mock()
        stack.presenter = presenter
        images = generate_images()
        presenter.get_image.return_value = images
        self.presenter.stack = stack
        self.presenter.do_update_previews()

        presenter.get_image.assert_called_once_with(self.presenter.model.preview_image_idx)
        self.view.clear_previews.assert_called_once()
        self.view.previews.auto_range.assert_called_once()
        self.assertEqual(3, update_preview_image_mock.call_count)
        apply_mock.assert_called_once()

    def test_get_filter_module_name(self):
        self.presenter.model.filters = mock.MagicMock()

        module_name = self.presenter.get_filter_module_name(0)

        self.assertEqual("mock.mock", module_name)

    @mock.patch('mantidimaging.gui.windows.operations.presenter.StackChoicePresenter')
    def test_safe_apply_starts_stack_choice_presenter(self, stack_choice_presenter):
        self.presenter.view.safeApply.isChecked.return_value = True
        stack_choice_presenter.done = True
        self.presenter._do_apply_filter = mock.MagicMock()
        task = mock.MagicMock()
        task.error = None
        self.presenter._post_filter([mock.MagicMock(), mock.MagicMock()], task)

        self.assertEqual(2, stack_choice_presenter.call_count)

    @mock.patch('mantidimaging.gui.windows.operations.presenter.StackChoicePresenter')
    def test_unchecked_safe_apply_does_not_start_stack_choice_presenter(self, stack_choice_presenter):
        self.presenter.view.safeApply.isChecked.return_value = False
        stack_choice_presenter.done = True
        self.presenter._do_apply_filter = mock.MagicMock()
        task = mock.MagicMock()
        task.error = None
        self.presenter._post_filter([mock.MagicMock(), mock.MagicMock()], task)

        stack_choice_presenter.assert_not_called()

    @mock.patch("mantidimaging.gui.windows.operations.presenter.operation_in_progress")
    def test_original_stack_assigned_when_safe_apply_checked(self, _):
        stack = mock.MagicMock()
        self.presenter.stack = stack
        stack_data = "THIS IS USEFUL STACK DATA"
        stack.presenter.images.copy.return_value = stack_data
        self.presenter._do_apply_filter = mock.MagicMock()

        self.presenter.do_apply_filter()

        stack.presenter.images.copy.assert_called_once()
        self.assertEqual(stack_data, self.presenter.original_images_stack)


@pytest.mark.parametrize('allow_180_degree, confirm_with_user_for_180degree', [(True, False), (True, True),
                                                                               (False, False), (False, True)])
@mock.patch("mantidimaging.gui.windows.operations.presenter.partial", return_value="Partial")
def test_apply_filter_on_180_deg_proj_behaviour_not_180_projection(partial_mock, allow_180_degree,
                                                                   confirm_with_user_for_180degree):
    main_window = mock.create_autospec(MainWindowView)
    view = mock.MagicMock()
    presenter = FiltersWindowPresenter(view, main_window)
    view.presenter = presenter
    model = mock.MagicMock()
    presenter.model = model
    view.ask_confirmation.return_value = True
    images = "images"
    post_filter = "post_filter"
    presenter._post_filter = post_filter
    presenter.is_a_proj180deg = mock.MagicMock(return_value=False)

    presenter._do_apply_filter(apply_to=[images],
                               allow_180_degree=allow_180_degree,
                               confirm_with_user_for_180degree=confirm_with_user_for_180degree)

    model.do_apply_filter.assert_called_once_with([images], "Partial")
    partial_mock.assert_called_once_with(post_filter, [images])


@pytest.mark.parametrize('allow_180_degree, confirm_with_user_for_180degree', [(True, False), (True, True),
                                                                               (False, False), (False, True)])
@mock.patch("mantidimaging.gui.windows.operations.presenter.partial", return_value="Partial")
def test_apply_filter_on_180_deg_proj_behaviour_with_180_projection(partial_mock, allow_180_degree,
                                                                    confirm_with_user_for_180degree):
    main_window = mock.create_autospec(MainWindowView)
    view = mock.MagicMock()
    presenter = FiltersWindowPresenter(view, main_window)
    view.presenter = presenter
    model = mock.MagicMock()
    presenter.model = model
    view.ask_confirmation.return_value = True
    images = "images"
    post_filter = "post_filter"
    presenter._post_filter = post_filter
    presenter.is_a_proj180deg = mock.MagicMock(return_value=True)

    presenter._do_apply_filter(apply_to=[images],
                               allow_180_degree=allow_180_degree,
                               confirm_with_user_for_180degree=confirm_with_user_for_180degree)

    if not allow_180_degree:
        if confirm_with_user_for_180degree:
            model.do_apply_filter.assert_called_once_with([images], "Partial")
            partial_mock.assert_called_once_with(post_filter, [images])
        else:
            model.do_apply_filter.assert_not_called()
            partial_mock.assert_not_called()
            view.clear_previews.assert_called_once()
    else:
        # Confirm_with_user is supposed to be ignored if allow_180_degree is True
        model.do_apply_filter.assert_called_once_with([images], "Partial")
        partial_mock.assert_called_once_with(post_filter, [images])

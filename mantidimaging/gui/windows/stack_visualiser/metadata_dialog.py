from PyQt5 import Qt
from PyQt5.QtWidgets import QWidget, QTreeWidget, QTreeWidgetItem

from mantidimaging.core.data import Images
from mantidimaging.core.operation_history import const


class MetadataDialog(Qt.QDialog):
    """
    Dialog used to show a pretty formatted version of the image metadata.
    """

    def __init__(self, parent: QWidget, images: Images):
        super(MetadataDialog, self).__init__(parent)

        self.setWindowTitle('Image Metadata')
        self.setSizeGripEnabled(True)
        self.resize(600, 300)

        main_widget = MetadataDialog.build_metadata_tree(images.metadata)

        buttons = Qt.QDialogButtonBox(Qt.QDialogButtonBox.Ok)
        buttons.accepted.connect(self.accept)

        layout = Qt.QVBoxLayout()
        layout.addWidget(main_widget)
        layout.addWidget(buttons)
        self.setLayout(layout)

    @staticmethod
    def build_metadata_tree(metadata):
        """
        Builds a QTreeWidget from the 'operation_history' metadata of an image.

        The top level items are operations, and each has any args and/or kwargs as child nodes.
        """
        main_widget = QTreeWidget()
        main_widget.setHeaderLabel("Operation history")
        if len(metadata) != 0:
            for key, value in metadata.items():
                if key == const.OPERATION_HISTORY:
                    MetadataDialog._build_operation_history(main_widget, metadata)
                else:
                    item = QTreeWidgetItem(main_widget)
                    item.setText(0, value)
                    main_widget.insertTopLevelItem(0, item)

        return main_widget

    @staticmethod
    def _build_operation_history(main_widget, metadata):
        for i, op in enumerate(metadata[const.OPERATION_HISTORY]):
            operation_item = QTreeWidgetItem(main_widget)
            if const.OPERATION_DISPLAY_NAME in op and op[const.OPERATION_DISPLAY_NAME]:
                operation_item.setText(0, op[const.OPERATION_DISPLAY_NAME])
            else:
                operation_item.setText(0, op[const.OPERATION_NAME])

            main_widget.insertTopLevelItem(i, operation_item)

            if op.get(const.TIMESTAMP, False):
                date_item = QTreeWidgetItem(operation_item)
                date_item.setText(0, f"Date: {op[const.TIMESTAMP]}")

            if op.get(const.OPERATION_ARGS, False):
                args_item = QTreeWidgetItem(operation_item)
                args_item.setText(0, f"Positional arguments: {op[const.OPERATION_ARGS]}")

            if op.get(const.OPERATION_KEYWORD_ARGS, False):
                kwargs_list_item = QTreeWidgetItem(operation_item)
                kwargs_list_item.setText(0, "Keyword arguments")
                # Note: Items must be added to the tree before they can expanded.
                # Nodes are added as they are created so these can be expanded by default
                kwargs_list_item.setExpanded(True)
                for kw, val in op[const.OPERATION_KEYWORD_ARGS].items():
                    kwargs_item = QTreeWidgetItem(kwargs_list_item)
                    kwargs_item.setText(0, f"{kw}: {val}")

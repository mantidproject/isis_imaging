from enum import Enum
from typing import Optional

from PyQt5.QtCore import Qt, QAbstractTableModel, QModelIndex

from mantidimaging.core.rotation import CorTiltDataModel
from mantidimaging.core.rotation.data_model import Point


class Column(Enum):
    SLICE_INDEX = 0
    CENTRE_OF_ROTATION = 1


COLUMN_NAMES = {Column.SLICE_INDEX: 'Slice Index', Column.CENTRE_OF_ROTATION: 'COR'}


class CorTiltPointQtModel(QAbstractTableModel, CorTiltDataModel):
    """
    Model of the slice/rotation point data in the rotation/tilt view's tableView.

    This class handles GUI interaction with the tableView  whilst CorTiltDataModel provides
    methods for calculating rotation and gradient from the stored values.
    """
    def __init__(self, parent=None):
        super().__init__(parent)

    def populate_slice_indices(self, begin, end, count, cor=0.0):
        self.beginResetModel()
        super(CorTiltPointQtModel, self).populate_slice_indices(begin, end, count, cor)
        self.endResetModel()

    def sort_points(self):
        self.layoutAboutToBeChanged.emit()
        super(CorTiltPointQtModel, self).sort_points()
        self.layoutChanged.emit()

    def set_point(self, idx, slice_idx: int = None, cor: float = None, reset_results=True):
        super(CorTiltPointQtModel, self).set_point(idx, slice_idx, cor, reset_results)
        self.dataChanged.emit(self.index(idx, 0), self.index(idx, 1))

    def columnCount(self, parent=None):
        return 2

    def rowCount(self, parent):
        if parent.isValid():
            return 0
        return self.num_points

    def flags(self, index):
        flags = super(CorTiltPointQtModel, self).flags(index)
        flags |= Qt.ItemIsEditable
        return flags

    def data(self, index, role=Qt.DisplayRole):
        if not index.isValid():
            return None

        col = index.column()
        col_field = Column(col)

        if role == Qt.DisplayRole:
            if col_field == Column.SLICE_INDEX:
                return self._points[index.row()].slice_index
            if col_field == Column.CENTRE_OF_ROTATION:
                return self._points[index.row()].cor

        elif role == Qt.ToolTipRole:
            if col_field == Column.SLICE_INDEX:
                return 'Slice index (y coordinate of projection)'
            elif col_field == Column.CENTRE_OF_ROTATION:
                return 'Centre of rotation for specific slice'
            return ''

    def setData(self, index, val, role=Qt.EditRole):
        if role != Qt.EditRole:
            return False

        self.clear_results()

        col_field = Column(index.column())

        try:
            original_point = self._points[index.row()]
            if col_field == Column.SLICE_INDEX:
                self._points[index.row()] = Point(int(val), original_point.cor)
            elif col_field == Column.CENTRE_OF_ROTATION:
                self._points[index.row()] = Point(original_point.slice_index, float(val))
        except ValueError:
            return False

        self.dataChanged.emit(index, index)
        self.sort_points()

        return True

    def insertRows(self, row, count, parent=None, slice_idx: int = None, cor: float = None):
        self.beginInsertRows(parent if parent is not None else QModelIndex(), row, row + count - 1)

        for _ in range(count):
            self.add_point(row, slice_idx, cor)

        self.endInsertRows()

    def removeRows(self, row, count, parent=None):
        if self.empty:
            return

        self.beginRemoveRows(parent if parent is not None else QModelIndex(), row, row + count - 1)

        for _ in range(count):
            self.remove_point(row)

        self.endRemoveRows()

    def removeAllRows(self, parent=None):
        if self.empty:
            return

        self.beginRemoveRows(parent if parent else QModelIndex(), 0, self.num_points - 1)
        self.clear_points()
        self.endRemoveRows()

    def appendNewRow(self, row: Optional[int], slice_idx: int, cor: float = 0.0):
        self.insertRows(row, 1, slice_idx=slice_idx, cor=cor)
        self.set_point(row, slice_idx, cor)
        self.sort_points()

    def headerData(self, section, orientation, role):
        if orientation != Qt.Horizontal:
            return None

        if role != Qt.DisplayRole:
            return None

        return COLUMN_NAMES[Column(section)]

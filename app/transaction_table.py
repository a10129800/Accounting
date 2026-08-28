from PySide6.QtCore import QAbstractTableModel, QModelIndex, Qt
from PySide6.QtWidgets import QTableView

from .models import Transaction


class TransactionTableModel(QAbstractTableModel):
    HEADERS = ["日期", "類型", "分類", "金額", "備註"]

    def __init__(self, transactions: list[Transaction] | None = None) -> None:
        super().__init__()
        self._transactions = transactions or []

    def set_transactions(self, transactions: list[Transaction]) -> None:
        self.beginResetModel()
        self._transactions = transactions
        self.endResetModel()

    def transaction_at(self, row: int) -> Transaction | None:
        if 0 <= row < len(self._transactions):
            return self._transactions[row]
        return None

    def rowCount(self, parent: QModelIndex = QModelIndex()) -> int:
        return 0 if parent.isValid() else len(self._transactions)

    def columnCount(self, parent: QModelIndex = QModelIndex()) -> int:
        return 0 if parent.isValid() else len(self.HEADERS)

    def data(self, index: QModelIndex, role: int = Qt.ItemDataRole.DisplayRole):
        if not index.isValid() or not (transaction := self.transaction_at(index.row())):
            return None
        if role != Qt.ItemDataRole.DisplayRole:
            return None

        values = [
            transaction.transaction_date.isoformat(),
            "收入" if transaction.type == "income" else "支出",
            transaction.category.name,
            f"{transaction.amount:,}",
            transaction.note,
        ]
        return values[index.column()]

    def headerData(self, section: int, orientation: Qt.Orientation, role: int = Qt.ItemDataRole.DisplayRole):
        if role == Qt.ItemDataRole.DisplayRole and orientation == Qt.Orientation.Horizontal:
            return self.HEADERS[section]
        return None


class TransactionTable(QTableView):
    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setModel(TransactionTableModel())
        self.setSelectionBehavior(QTableView.SelectionBehavior.SelectRows)
        self.setSelectionMode(QTableView.SelectionMode.SingleSelection)
        self.setEditTriggers(QTableView.EditTrigger.NoEditTriggers)
        self.setAlternatingRowColors(True)
        self.horizontalHeader().setStretchLastSection(True)

    @property
    def transaction_model(self) -> TransactionTableModel:
        return self.model()

    def selected_transaction(self) -> Transaction | None:
        indexes = self.selectionModel().selectedRows()
        return self.transaction_model.transaction_at(indexes[0].row()) if indexes else None

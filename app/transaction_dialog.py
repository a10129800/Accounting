from datetime import date

from PySide6.QtWidgets import (
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QFormLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QSpinBox,
    QDateEdit,
)

from .models import Category, Transaction
from .services import TransactionInput


class TransactionDialog(QDialog):
    def __init__(
        self,
        categories: list[Category],
        transaction_type: str,
        transaction: Transaction | None = None,
        parent=None,
    ) -> None:
        super().__init__(parent)
        self.setWindowTitle("編輯交易" if transaction else "新增交易")
        self._transaction_type = transaction_type
        self._categories = categories

        self.amount_input = QSpinBox()
        self.amount_input.setRange(1, 2_147_483_647)
        self.amount_input.setSuffix(" 元")

        self.category_input = QComboBox()
        for category in categories:
            self.category_input.addItem(category.name, category.id)

        self.date_input = QDateEdit()
        self.date_input.setCalendarPopup(True)
        self.date_input.setDate(date.today())

        self.note_input = QLineEdit()
        self.note_input.setMaxLength(500)

        form = QFormLayout(self)
        form.addRow("類型", QLabel("收入" if transaction_type == "income" else "支出"))
        form.addRow("金額", self.amount_input)
        form.addRow("分類", self.category_input)
        form.addRow("日期", self.date_input)
        form.addRow("備註", self.note_input)

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Save | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        form.addRow(buttons)

        if transaction is not None:
            self.amount_input.setValue(transaction.amount)
            category_index = self.category_input.findData(transaction.category_id)
            if category_index >= 0:
                self.category_input.setCurrentIndex(category_index)
            self.date_input.setDate(transaction.transaction_date)
            self.note_input.setText(transaction.note)

    def get_data(self) -> TransactionInput:
        return TransactionInput(
            amount=self.amount_input.value(),
            transaction_type=self._transaction_type,
            category_id=self.category_input.currentData(),
            transaction_date=self.date_input.date().toPython(),
            note=self.note_input.text(),
        )

    def show_validation_error(self, message: str) -> None:
        QMessageBox.warning(self, "資料錯誤", message)

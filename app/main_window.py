from datetime import date

from PySide6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QMessageBox,
    QDateEdit,
    QLineEdit,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from .services import AccountingService, ValidationError
from .transaction_dialog import TransactionDialog
from .transaction_table import TransactionTable
from .category_manager_dialog import CategoryManagerDialog
from .statistics_dialog import StatisticsDialog


class MainWindow(QMainWindow):
    def __init__(self, service: AccountingService) -> None:
        super().__init__()
        self.service = service
        self.setWindowTitle("簡易記帳")
        self.resize(1000, 600)

        self.income_label = QLabel()
        self.expense_label = QLabel()
        self.balance_label = QLabel()
        summary_layout = QHBoxLayout()
        summary_layout.addWidget(self.income_label)
        summary_layout.addWidget(self.expense_label)
        summary_layout.addWidget(self.balance_label)

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("搜尋分類或備註")
        self.start_date_input = QDateEdit()
        self.start_date_input.setCalendarPopup(True)
        self.start_date_input.setDate(date(1900, 1, 1))
        self.end_date_input = QDateEdit()
        self.end_date_input.setCalendarPopup(True)
        self.end_date_input.setDate(date(2100, 12, 31))
        clear_filter_button = QPushButton("清除篩選")
        self.search_input.textChanged.connect(self.refresh)
        self.start_date_input.dateChanged.connect(self.refresh)
        self.end_date_input.dateChanged.connect(self.refresh)
        clear_filter_button.clicked.connect(self.clear_filters)
        filter_layout = QHBoxLayout()
        filter_layout.addWidget(self.search_input)
        filter_layout.addWidget(QLabel("從"))
        filter_layout.addWidget(self.start_date_input)
        filter_layout.addWidget(QLabel("至"))
        filter_layout.addWidget(self.end_date_input)
        filter_layout.addWidget(clear_filter_button)

        self.table = TransactionTable()
        self.table.horizontalHeader().setDefaultSectionSize(120)

        income_button = QPushButton("新增收入")
        expense_button = QPushButton("新增支出")
        edit_button = QPushButton("編輯")
        delete_button = QPushButton("刪除")
        category_button = QPushButton("分類管理")
        statistics_button = QPushButton("統計")
        income_button.clicked.connect(lambda: self.add_transaction("income"))
        expense_button.clicked.connect(lambda: self.add_transaction("expense"))
        edit_button.clicked.connect(self.edit_transaction)
        delete_button.clicked.connect(self.delete_transaction)
        category_button.clicked.connect(self.manage_categories)
        statistics_button.clicked.connect(self.show_statistics)

        action_layout = QHBoxLayout()
        action_layout.addWidget(income_button)
        action_layout.addWidget(expense_button)
        action_layout.addWidget(edit_button)
        action_layout.addWidget(delete_button)
        action_layout.addWidget(category_button)
        action_layout.addWidget(statistics_button)

        layout = QVBoxLayout()
        layout.addLayout(summary_layout)
        layout.addLayout(filter_layout)
        layout.addWidget(self.table)
        layout.addLayout(action_layout)
        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)
        self.refresh()

    def refresh(self) -> None:
        keyword = self.search_input.text().strip()
        start_date = self.start_date_input.date().toPython()
        end_date = self.end_date_input.date().toPython()
        self.table.transaction_model.set_transactions(
            self.service.list_transactions(keyword, start_date, end_date)
        )
        total_income, total_expense, balance = self.service.get_summary(
            keyword, start_date, end_date
        )
        self.income_label.setText(f"總收入：{total_income:,} 元")
        self.expense_label.setText(f"總支出：{total_expense:,} 元")
        self.balance_label.setText(f"餘額：{balance:,} 元")

    def clear_filters(self) -> None:
        self.search_input.clear()
        self.start_date_input.setDate(date(1900, 1, 1))
        self.end_date_input.setDate(date(2100, 12, 31))

    def add_transaction(self, transaction_type: str) -> None:
        categories = self.service.list_categories(transaction_type)
        dialog = TransactionDialog(categories, transaction_type, parent=self)
        if dialog.exec():
            try:
                self.service.add_transaction(dialog.get_data())
            except ValidationError as error:
                dialog.show_validation_error(str(error))
                return
            self.refresh()

    def edit_transaction(self) -> None:
        transaction = self.table.selected_transaction()
        if transaction is None:
            QMessageBox.information(self, "提示", "請先選取一筆交易")
            return
        categories = self.service.list_categories(transaction.type)
        dialog = TransactionDialog(categories, transaction.type, transaction, self)
        if dialog.exec():
            try:
                self.service.update_transaction(transaction.id, dialog.get_data())
            except ValidationError as error:
                dialog.show_validation_error(str(error))
                return
            self.refresh()

    def delete_transaction(self) -> None:
        transaction = self.table.selected_transaction()
        if transaction is None:
            QMessageBox.information(self, "提示", "請先選取一筆交易")
            return
        answer = QMessageBox.question(self, "確認刪除", "確定要刪除選取的交易嗎？")
        if answer == QMessageBox.StandardButton.Yes:
            self.service.delete_transaction(transaction.id)
            self.refresh()

    def manage_categories(self) -> None:
        dialog = CategoryManagerDialog(self.service, self)
        if dialog.exec():
            self.refresh()

    def show_statistics(self) -> None:
        dialog = StatisticsDialog(self.service, self)
        dialog.exec()

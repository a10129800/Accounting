from datetime import date, datetime
from pathlib import Path

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
    QFileDialog,
)

from .backup import BackupError, backup_database, restore_database
from .database import engine
from .services import AccountingService, ValidationError
from .transaction_dialog import TransactionDialog
from .transaction_table import TransactionTable
from .category_manager_dialog import CategoryManagerDialog
from .statistics_dialog import StatisticsDialog
from .exporters import ExcelExporter


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
        export_button = QPushButton("匯出 Excel")
        backup_button = QPushButton("備份資料")
        restore_button = QPushButton("還原資料")
        income_button.clicked.connect(lambda: self.add_transaction("income"))
        expense_button.clicked.connect(lambda: self.add_transaction("expense"))
        edit_button.clicked.connect(self.edit_transaction)
        delete_button.clicked.connect(self.delete_transaction)
        category_button.clicked.connect(self.manage_categories)
        statistics_button.clicked.connect(self.show_statistics)
        export_button.clicked.connect(self.export_to_excel)
        backup_button.clicked.connect(self.backup_database)
        restore_button.clicked.connect(self.restore_database)

        action_layout = QHBoxLayout()
        action_layout.addWidget(income_button)
        action_layout.addWidget(expense_button)
        action_layout.addWidget(edit_button)
        action_layout.addWidget(delete_button)
        action_layout.addWidget(category_button)
        action_layout.addWidget(statistics_button)
        action_layout.addWidget(export_button)
        action_layout.addWidget(backup_button)
        action_layout.addWidget(restore_button)

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

    def backup_database(self) -> None:
        default_path = Path.home() / "Desktop" / (
            f"accounting_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db"
        )
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "備份資料庫",
            str(default_path),
            "SQLite 資料庫 (*.db)",
        )
        if not file_path:
            return

        try:
            backup_database(file_path)
        except BackupError as error:
            QMessageBox.warning(self, "備份失敗", str(error))
            return
        QMessageBox.information(self, "備份成功", f"資料已備份至：\n{file_path}")

    def restore_database(self) -> None:
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "選擇備份檔",
            str(Path.home() / "Desktop"),
            "SQLite 資料庫 (*.db);;所有檔案 (*.*)",
        )
        if not file_path:
            return

        answer = QMessageBox.question(
            self,
            "確認還原",
            "還原會覆蓋目前所有資料，確定要繼續嗎？",
        )
        if answer != QMessageBox.StandardButton.Yes:
            return

        try:
            engine.dispose()
            restore_database(file_path)
        except BackupError as error:
            QMessageBox.warning(self, "還原失敗", str(error))
            return
        self.refresh()
        QMessageBox.information(self, "還原成功", "資料庫已成功還原")

    def export_to_excel(self) -> None:
        """Export current transactions to Excel file."""
        # Get current filter values
        keyword = self.search_input.text().strip()
        start_date = self.start_date_input.date().toPython()
        end_date = self.end_date_input.date().toPython()
        
        # Get filtered transactions and summary
        transactions = self.service.list_transactions(keyword, start_date, end_date)
        total_income, total_expense, _ = self.service.get_summary(
            keyword, start_date, end_date
        )
        
        if not transactions:
            QMessageBox.information(self, "提示", "沒有交易記錄可匯出")
            return
        
        # Ask user for file location
        default_filename = f"交易紀錄_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "匯出為 Excel",
            str(Path.home() / "Desktop" / default_filename),
            "Excel 檔案 (*.xlsx)",
        )
        
        if not file_path:
            return
        
        # Export
        exporter = ExcelExporter(file_path)
        title = f"交易紀錄 ({start_date} ~ {end_date})"
        if keyword:
            title += f" [搜尋: {keyword}]"
        
        success = exporter.export_transactions(
            transactions, total_income, total_expense, title
        )
        
        if success:
            QMessageBox.information(
                self,
                "匯出成功",
                f"已匯出 {len(transactions)} 筆交易到:\n{file_path}",
            )
        else:
            QMessageBox.warning(self, "匯出失敗", "匯出過程中發生錯誤")

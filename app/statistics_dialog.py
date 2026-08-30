from PySide6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QTabWidget,
    QTableWidget,
    QTableWidgetItem,
    QPushButton,
)
from PySide6.QtCore import Qt

from .services import AccountingService


class StatisticsDialog(QDialog):
    def __init__(self, service: AccountingService, parent=None) -> None:
        super().__init__(parent)
        self.setWindowTitle("統計報表")
        self.service = service
        self.resize(600, 500)

        tabs = QTabWidget()

        # Monthly statistics tab
        monthly_table = QTableWidget()
        monthly_table.setColumnCount(5)
        monthly_table.setHorizontalHeaderLabels(["年份", "月份", "收入", "支出", "結餘"])
        monthly_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        monthly_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)

        monthly_stats = self.service.get_monthly_statistics()
        monthly_table.setRowCount(len(monthly_stats))
        for row, (year, month, income, expense, balance) in enumerate(monthly_stats):
            monthly_table.setItem(row, 0, QTableWidgetItem(str(year)))
            monthly_table.setItem(row, 1, QTableWidgetItem(str(month).zfill(2)))
            monthly_table.setItem(row, 2, QTableWidgetItem(f"{income:,}"))
            monthly_table.setItem(row, 3, QTableWidgetItem(f"{expense:,}"))
            balance_item = QTableWidgetItem(f"{balance:,}")
            if balance >= 0:
                balance_item.setForeground(Qt.GlobalColor.green)
            else:
                balance_item.setForeground(Qt.GlobalColor.red)
            monthly_table.setItem(row, 4, balance_item)
        monthly_table.resizeColumnsToContents()

        # Category statistics tab
        category_table = QTableWidget()
        category_table.setColumnCount(3)
        category_table.setHorizontalHeaderLabels(["分類", "收入", "支出"])
        category_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        category_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)

        category_stats = self.service.get_category_statistics()
        sorted_categories = sorted(category_stats.keys())
        category_table.setRowCount(len(sorted_categories))
        for row, category_name in enumerate(sorted_categories):
            stats = category_stats[category_name]
            category_table.setItem(row, 0, QTableWidgetItem(category_name))
            category_table.setItem(row, 1, QTableWidgetItem(f"{stats['income']:,}"))
            category_table.setItem(row, 2, QTableWidgetItem(f"{stats['expense']:,}"))
        category_table.resizeColumnsToContents()

        tabs.addTab(monthly_table, "月份統計")
        tabs.addTab(category_table, "分類統計")

        close_button = QPushButton("關閉")
        close_button.clicked.connect(self.accept)

        layout = QVBoxLayout(self)
        layout.addWidget(tabs)
        layout.addWidget(close_button)

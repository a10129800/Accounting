from PySide6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QTabWidget,
    QTableWidget,
    QTableWidgetItem,
    QPushButton,
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont

from .services import AccountingService


class StatisticsDialog(QDialog):
    def __init__(self, service: AccountingService, parent=None) -> None:
        super().__init__(parent)
        self.setWindowTitle("統計報表")
        self.service = service
        self.resize(700, 550)

        tabs = QTabWidget()

        # Monthly statistics tab
        monthly_table = QTableWidget()
        monthly_table.setColumnCount(5)
        monthly_table.setHorizontalHeaderLabels(["年份", "月份", "收入", "支出", "結餘"])
        monthly_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        monthly_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)

        monthly_stats = self.service.get_monthly_statistics()
        total_income = sum(s[2] for s in monthly_stats)
        total_expense = sum(s[3] for s in monthly_stats)
        total_balance = total_income - total_expense
        
        monthly_table.setRowCount(len(monthly_stats) + 1)  # +1 for total row
        for row, (year, month, income, expense, balance) in enumerate(monthly_stats):
            year_item = QTableWidgetItem(str(year))
            year_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            monthly_table.setItem(row, 0, year_item)
            
            month_item = QTableWidgetItem(str(month).zfill(2))
            month_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            monthly_table.setItem(row, 1, month_item)
            
            income_item = QTableWidgetItem(f"{income:,}")
            income_item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            income_item.setForeground(Qt.GlobalColor.green)
            monthly_table.setItem(row, 2, income_item)
            
            expense_item = QTableWidgetItem(f"{expense:,}")
            expense_item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            expense_item.setForeground(Qt.GlobalColor.red)
            monthly_table.setItem(row, 3, expense_item)
            
            balance_item = QTableWidgetItem(f"{balance:,}")
            balance_item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            balance_item.setForeground(Qt.GlobalColor.green if balance >= 0 else Qt.GlobalColor.red)
            monthly_table.setItem(row, 4, balance_item)
        
        # Add total row
        total_row = len(monthly_stats)
        total_year_item = QTableWidgetItem("合計")
        total_year_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
        font = QFont()
        font.setBold(True)
        total_year_item.setFont(font)
        monthly_table.setItem(total_row, 0, total_year_item)
        
        total_income_item = QTableWidgetItem(f"{total_income:,}")
        total_income_item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        total_income_item.setForeground(Qt.GlobalColor.green)
        total_income_item.setFont(font)
        monthly_table.setItem(total_row, 2, total_income_item)
        
        total_expense_item = QTableWidgetItem(f"{total_expense:,}")
        total_expense_item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        total_expense_item.setForeground(Qt.GlobalColor.red)
        total_expense_item.setFont(font)
        monthly_table.setItem(total_row, 3, total_expense_item)
        
        total_balance_item = QTableWidgetItem(f"{total_balance:,}")
        total_balance_item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        total_balance_item.setForeground(Qt.GlobalColor.green if total_balance >= 0 else Qt.GlobalColor.red)
        total_balance_item.setFont(font)
        monthly_table.setItem(total_row, 4, total_balance_item)
        
        monthly_table.resizeColumnsToContents()

        # Category statistics tab
        category_table = QTableWidget()
        category_table.setColumnCount(3)
        category_table.setHorizontalHeaderLabels(["分類", "收入", "支出"])
        category_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        category_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)

        category_stats = self.service.get_category_statistics()
        sorted_categories = sorted(category_stats.keys())
        total_cat_income = sum(s['income'] for s in category_stats.values())
        total_cat_expense = sum(s['expense'] for s in category_stats.values())
        
        category_table.setRowCount(len(sorted_categories) + 1)  # +1 for total row
        for row, category_name in enumerate(sorted_categories):
            stats = category_stats[category_name]
            category_table.setItem(row, 0, QTableWidgetItem(category_name))
            
            income_item = QTableWidgetItem(f"{stats['income']:,}")
            income_item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            income_item.setForeground(Qt.GlobalColor.green)
            category_table.setItem(row, 1, income_item)
            
            expense_item = QTableWidgetItem(f"{stats['expense']:,}")
            expense_item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            expense_item.setForeground(Qt.GlobalColor.red)
            category_table.setItem(row, 2, expense_item)
        
        # Add total row
        total_row = len(sorted_categories)
        total_cat_item = QTableWidgetItem("合計")
        font = QFont()
        font.setBold(True)
        total_cat_item.setFont(font)
        category_table.setItem(total_row, 0, total_cat_item)
        
        total_cat_income_item = QTableWidgetItem(f"{total_cat_income:,}")
        total_cat_income_item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        total_cat_income_item.setForeground(Qt.GlobalColor.green)
        total_cat_income_item.setFont(font)
        category_table.setItem(total_row, 1, total_cat_income_item)
        
        total_cat_expense_item = QTableWidgetItem(f"{total_cat_expense:,}")
        total_cat_expense_item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        total_cat_expense_item.setForeground(Qt.GlobalColor.red)
        total_cat_expense_item.setFont(font)
        category_table.setItem(total_row, 2, total_cat_expense_item)
        
        category_table.resizeColumnsToContents()

        tabs.addTab(monthly_table, "月份統計")
        tabs.addTab(category_table, "分類統計")

        close_button = QPushButton("關閉")
        close_button.clicked.connect(self.accept)

        layout = QVBoxLayout(self)
        layout.addWidget(tabs)
        layout.addWidget(close_button)

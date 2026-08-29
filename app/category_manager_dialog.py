from PySide6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QListWidget,
    QListWidgetItem,
    QLineEdit,
    QComboBox,
    QLabel,
    QMessageBox,
    QDialogButtonBox,
)

from .models import Category
from .services import AccountingService, ValidationError


class CategoryManagerDialog(QDialog):
    def __init__(self, service: AccountingService, parent=None) -> None:
        super().__init__(parent)
        self.setWindowTitle("分類管理")
        self.service = service
        self.resize(400, 350)

        self.category_list = QListWidget()
        self.category_list.itemSelectionChanged.connect(self.on_category_selected)

        self.type_combo = QComboBox()
        self.type_combo.addItems(["income", "expense"])
        self.type_combo.currentTextChanged.connect(self.refresh_list)

        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("分類名稱")

        add_button = QPushButton("新增")
        add_button.clicked.connect(self.add_category)

        update_button = QPushButton("編輯")
        update_button.clicked.connect(self.update_category)

        delete_button = QPushButton("刪除")
        delete_button.clicked.connect(self.delete_category)

        close_button = QPushButton("關閉")
        close_button.clicked.connect(self.accept)

        type_layout = QHBoxLayout()
        type_layout.addWidget(QLabel("類型："))
        type_layout.addWidget(self.type_combo)

        input_layout = QHBoxLayout()
        input_layout.addWidget(self.name_input)
        input_layout.addWidget(add_button)

        button_layout = QHBoxLayout()
        button_layout.addWidget(update_button)
        button_layout.addWidget(delete_button)
        button_layout.addStretch()
        button_layout.addWidget(close_button)

        layout = QVBoxLayout(self)
        layout.addLayout(type_layout)
        layout.addWidget(self.category_list)
        layout.addLayout(input_layout)
        layout.addLayout(button_layout)

        self.refresh_list()

    def refresh_list(self) -> None:
        category_type = self.type_combo.currentText()
        categories = self.service.list_categories(category_type)
        self.category_list.clear()
        for category in categories:
            item = QListWidgetItem(category.name)
            item.setData(1001, category.id)
            self.category_list.addItem(item)
        self.name_input.clear()

    def on_category_selected(self) -> None:
        current = self.category_list.currentItem()
        if current:
            self.name_input.setText(current.text())

    def add_category(self) -> None:
        name = self.name_input.text().strip()
        if not name:
            QMessageBox.warning(self, "錯誤", "請輸入分類名稱")
            return
        category_type = self.type_combo.currentText()
        try:
            self.service.add_category(name, category_type)
            self.refresh_list()
        except ValidationError as error:
            QMessageBox.warning(self, "錯誤", str(error))

    def update_category(self) -> None:
        current = self.category_list.currentItem()
        if not current:
            QMessageBox.information(self, "提示", "請先選取一筆分類")
            return
        category_id = current.data(1001)
        name = self.name_input.text().strip()
        if not name:
            QMessageBox.warning(self, "錯誤", "請輸入分類名稱")
            return
        try:
            self.service.update_category(category_id, name)
            self.refresh_list()
        except ValidationError as error:
            QMessageBox.warning(self, "錯誤", str(error))

    def delete_category(self) -> None:
        current = self.category_list.currentItem()
        if not current:
            QMessageBox.information(self, "提示", "請先選取一筆分類")
            return
        answer = QMessageBox.question(self, "確認刪除", f"確定要刪除分類 '{current.text()}' 嗎？")
        if answer == QMessageBox.StandardButton.Yes:
            category_id = current.data(1001)
            try:
                self.service.delete_category(category_id)
                self.refresh_list()
            except ValidationError as error:
                QMessageBox.warning(self, "錯誤", str(error))

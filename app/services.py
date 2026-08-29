from dataclasses import dataclass
from datetime import date
from typing import Callable

from sqlalchemy.orm import Session

from .models import Category, Transaction
from .repositories import CategoryRepository, TransactionRepository


class ValidationError(ValueError):
    pass


@dataclass(frozen=True)
class TransactionInput:
    amount: int
    transaction_type: str
    category_id: int
    transaction_date: date
    note: str = ""


class AccountingService:
    def __init__(self, session_factory: Callable[[], Session]) -> None:
        self._session_factory = session_factory

    def list_transactions(
        self,
        keyword: str = "",
        start_date: date | None = None,
        end_date: date | None = None,
    ) -> list[Transaction]:
        with self._session_factory() as session:
            return TransactionRepository.list_all(session, keyword, start_date, end_date)

    def list_categories(self, transaction_type: str) -> list[Category]:
        self._validate_type(transaction_type)
        with self._session_factory() as session:
            return CategoryRepository.list_by_type(session, transaction_type)

    def add_transaction(self, data: TransactionInput) -> Transaction:
        self._validate_input(data)
        with self._session_factory.begin() as session:
            self._validate_category(session, data)
            return TransactionRepository.add(
                session,
                data.amount,
                data.transaction_type,
                data.category_id,
                data.transaction_date,
                data.note.strip(),
            )

    def update_transaction(self, transaction_id: int, data: TransactionInput) -> bool:
        self._validate_input(data)
        with self._session_factory.begin() as session:
            transaction = TransactionRepository.get_by_id(session, transaction_id)
            if transaction is None:
                return False
            self._validate_category(session, data)
            TransactionRepository.update(
                transaction,
                data.amount,
                data.transaction_type,
                data.category_id,
                data.transaction_date,
                data.note.strip(),
            )
            return True

    def delete_transaction(self, transaction_id: int) -> bool:
        with self._session_factory.begin() as session:
            transaction = TransactionRepository.get_by_id(session, transaction_id)
            if transaction is None:
                return False
            TransactionRepository.delete(session, transaction)
            return True

    def list_all_categories(self) -> list[Category]:
        with self._session_factory() as session:
            return CategoryRepository.list_all(session)

    def add_category(self, name: str, category_type: str) -> Category:
        name = name.strip()
        if not name:
            raise ValidationError("分類名稱不能為空")
        self._validate_type(category_type)
        with self._session_factory.begin() as session:
            existing = [c for c in CategoryRepository.list_by_type(session, category_type) if c.name == name]
            if existing:
                raise ValidationError(f"分類 '{name}' 已存在")
            return CategoryRepository.add(session, name, category_type)

    def update_category(self, category_id: int, name: str) -> bool:
        name = name.strip()
        if not name:
            raise ValidationError("分類名稱不能為空")
        with self._session_factory.begin() as session:
            category = CategoryRepository.get_by_id(session, category_id)
            if category is None:
                return False
            existing = [c for c in CategoryRepository.list_by_type(session, category.type) if c.name == name and c.id != category_id]
            if existing:
                raise ValidationError(f"分類 '{name}' 已存在")
            CategoryRepository.update(category, name)
            return True

    def delete_category(self, category_id: int) -> bool:
        with self._session_factory.begin() as session:
            category = CategoryRepository.get_by_id(session, category_id)
            if category is None:
                return False
            transaction_count = CategoryRepository.count_transactions(session, category_id)
            if transaction_count > 0:
                raise ValidationError(f"無法刪除分類：已有 {transaction_count} 筆交易使用此分類")
            CategoryRepository.delete(session, category)
            return True

    def get_summary(
        self,
        keyword: str = "",
        start_date: date | None = None,
        end_date: date | None = None,
    ) -> tuple[int, int, int]:
        transactions = self.list_transactions(keyword, start_date, end_date)
        total_income = sum(item.amount for item in transactions if item.type == "income")
        total_expense = sum(item.amount for item in transactions if item.type == "expense")
        return total_income, total_expense, total_income - total_expense

    @staticmethod
    def _validate_input(data: TransactionInput) -> None:
        if data.amount <= 0:
            raise ValidationError("金額必須大於 0")
        AccountingService._validate_type(data.transaction_type)

    @staticmethod
    def _validate_type(transaction_type: str) -> None:
        if transaction_type not in {"income", "expense"}:
            raise ValidationError("無效的交易類型")

    @staticmethod
    def _validate_category(session: Session, data: TransactionInput) -> None:
        category = session.get(Category, data.category_id)
        if category is None:
            raise ValidationError("分類不存在")
        if category.type != data.transaction_type:
            raise ValidationError("交易類型與分類不一致")

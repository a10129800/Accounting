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

    def list_transactions(self) -> list[Transaction]:
        with self._session_factory() as session:
            return TransactionRepository.list_all(session)

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

    def get_summary(self) -> tuple[int, int, int]:
        transactions = self.list_transactions()
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

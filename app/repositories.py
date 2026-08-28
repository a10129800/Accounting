from datetime import date

from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from .models import Category, Transaction


class CategoryRepository:
    @staticmethod
    def list_by_type(session: Session, category_type: str) -> list[Category]:
        statement = select(Category).where(Category.type == category_type).order_by(Category.id)
        return list(session.scalars(statement))


class TransactionRepository:
    @staticmethod
    def list_all(session: Session) -> list[Transaction]:
        statement = (
            select(Transaction)
            .options(joinedload(Transaction.category))
            .order_by(Transaction.transaction_date.desc(), Transaction.id.desc())
        )
        return list(session.scalars(statement))

    @staticmethod
    def get_by_id(session: Session, transaction_id: int) -> Transaction | None:
        statement = (
            select(Transaction)
            .options(joinedload(Transaction.category))
            .where(Transaction.id == transaction_id)
        )
        return session.scalar(statement)

    @staticmethod
    def add(
        session: Session,
        amount: int,
        transaction_type: str,
        category_id: int,
        transaction_date: date,
        note: str,
    ) -> Transaction:
        transaction = Transaction(
            amount=amount,
            type=transaction_type,
            category_id=category_id,
            transaction_date=transaction_date,
            note=note,
        )
        session.add(transaction)
        session.flush()
        return transaction

    @staticmethod
    def update(
        transaction: Transaction,
        amount: int,
        transaction_type: str,
        category_id: int,
        transaction_date: date,
        note: str,
    ) -> Transaction:
        transaction.amount = amount
        transaction.type = transaction_type
        transaction.category_id = category_id
        transaction.transaction_date = transaction_date
        transaction.note = note
        return transaction

    @staticmethod
    def delete(session: Session, transaction: Transaction) -> None:
        session.delete(transaction)

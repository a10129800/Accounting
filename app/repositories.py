from datetime import date

from sqlalchemy import or_, select
from sqlalchemy.orm import Session, joinedload

from .models import Category, Transaction


class CategoryRepository:
    @staticmethod
    def list_by_type(session: Session, category_type: str) -> list[Category]:
        statement = select(Category).where(Category.type == category_type).order_by(Category.id)
        return list(session.scalars(statement))


class TransactionRepository:
    @staticmethod
    def list_all(
        session: Session,
        keyword: str = "",
        start_date: date | None = None,
        end_date: date | None = None,
    ) -> list[Transaction]:
        statement = (
            select(Transaction)
            .options(joinedload(Transaction.category))
            .order_by(Transaction.transaction_date.desc(), Transaction.id.desc())
        )
        if keyword:
            pattern = f"%{keyword}%"
            statement = statement.join(Transaction.category).where(
                or_(Transaction.note.like(pattern), Category.name.like(pattern))
            )
        if start_date is not None:
            statement = statement.where(Transaction.transaction_date >= start_date)
        if end_date is not None:
            statement = statement.where(Transaction.transaction_date <= end_date)
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

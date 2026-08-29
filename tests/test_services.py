from datetime import date

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.models import Base, Category
from app.services import AccountingService, TransactionInput, ValidationError


@pytest.fixture
def service():
    engine = create_engine("sqlite:///:memory:", future=True)
    Base.metadata.create_all(engine)
    session_factory = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)
    with session_factory.begin() as session:
        session.add_all(
            [
                Category(name="薪資", type="income"),
                Category(name="餐飲", type="expense"),
            ]
        )
    return AccountingService(session_factory)


def transaction_input(service, amount, transaction_type, category_id, note=""):
    return TransactionInput(
        amount=amount,
        transaction_type=transaction_type,
        category_id=category_id,
        transaction_date=date(2026, 8, 28),
        note=note,
    )


def category_ids(service):
    return {
        category.name: category.id
        for category_type in ("income", "expense")
        for category in service.list_categories(category_type)
    }


def test_add_income_and_expense(service):
    ids = category_ids(service)
    service.add_transaction(transaction_input(service, 50000, "income", ids["薪資"]))
    service.add_transaction(transaction_input(service, 120, "expense", ids["餐飲"]))

    transactions = service.list_transactions()
    assert len(transactions) == 2
    assert {transaction.type for transaction in transactions} == {"income", "expense"}


def test_amount_must_be_positive(service):
    ids = category_ids(service)
    with pytest.raises(ValidationError, match="金額必須大於 0"):
        service.add_transaction(transaction_input(service, 0, "income", ids["薪資"]))


def test_edit_transaction(service):
    ids = category_ids(service)
    transaction = service.add_transaction(
        transaction_input(service, 100, "expense", ids["餐飲"], "午餐")
    )

    assert service.update_transaction(
        transaction.id,
        transaction_input(service, 200, "expense", ids["餐飲"], "晚餐"),
    )
    updated = service.list_transactions()[0]
    assert updated.amount == 200
    assert updated.note == "晚餐"


def test_delete_transaction(service):
    ids = category_ids(service)
    transaction = service.add_transaction(transaction_input(service, 100, "expense", ids["餐飲"]))

    assert service.delete_transaction(transaction.id)
    assert service.list_transactions() == []
    assert not service.delete_transaction(transaction.id)


def test_summary(service):
    ids = category_ids(service)
    service.add_transaction(transaction_input(service, 50000, "income", ids["薪資"]))
    service.add_transaction(transaction_input(service, 120, "expense", ids["餐飲"]))
    service.add_transaction(transaction_input(service, 80, "expense", ids["餐飲"]))

    assert service.get_summary() == (50000, 200, 49800)


def test_category_type_must_match_transaction(service):
    ids = category_ids(service)
    with pytest.raises(ValidationError, match="交易類型與分類不一致"):
        service.add_transaction(transaction_input(service, 100, "income", ids["餐飲"]))

    with pytest.raises(ValidationError, match="交易類型與分類不一致"):
        service.add_transaction(transaction_input(service, 100, "expense", ids["薪資"]))


def test_search_and_date_filter(service):
    ids = category_ids(service)
    service.add_transaction(transaction_input(service, 50000, "income", ids["薪資"], "八月薪資"))
    service.add_transaction(transaction_input(service, 120, "expense", ids["餐飲"], "午餐"))

    assert len(service.list_transactions(keyword="薪資")) == 1
    assert len(service.list_transactions(keyword="午餐")) == 1
    assert len(service.list_transactions(start_date=date(2026, 8, 28), end_date=date(2026, 8, 28))) == 2
    assert service.get_summary(keyword="薪資") == (50000, 0, 50000)


def test_add_custom_category(service):
    category = service.add_category("房租", "expense")
    assert category.name == "房租"
    assert category.type == "expense"
    categories = service.list_categories("expense")
    assert any(c.name == "房租" for c in categories)


def test_duplicate_category_name(service):
    service.add_category("房租", "expense")
    with pytest.raises(ValidationError, match="分類 '房租' 已存在"):
        service.add_category("房租", "expense")


def test_update_category(service):
    category = service.add_category("房屋", "expense")
    assert service.update_category(category.id, "房租")
    categories = service.list_categories("expense")
    assert any(c.name == "房租" for c in categories)


def test_delete_category_without_transactions(service):
    category = service.add_category("測試分類", "expense")
    assert service.delete_category(category.id)
    categories = service.list_categories("expense")
    assert not any(c.name == "測試分類" for c in categories)


def test_cannot_delete_category_with_transactions(service):
    ids = category_ids(service)
    service.add_transaction(transaction_input(service, 100, "expense", ids["餐飲"]))
    
    with pytest.raises(ValidationError, match="無法刪除分類"):
        service.delete_category(ids["餐飲"])

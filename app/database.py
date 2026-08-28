from collections.abc import Generator

from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session, sessionmaker

from .config import DATABASE_PATH
from .models import Base, Category


engine = create_engine(f"sqlite:///{DATABASE_PATH}", future=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)

DEFAULT_CATEGORIES = (
    ("薪資", "income"),
    ("獎金", "income"),
    ("其他收入", "income"),
    ("餐飲", "expense"),
    ("交通", "expense"),
    ("娛樂", "expense"),
    ("生活用品", "expense"),
    ("其他支出", "expense"),
)


def initialize_database() -> None:
    Base.metadata.create_all(engine)
    with SessionLocal.begin() as session:
        existing_names = set(session.scalars(select(Category.name)))
        for name, category_type in DEFAULT_CATEGORIES:
            if name not in existing_names:
                session.add(Category(name=name, type=category_type))


def get_session() -> Generator[Session, None, None]:
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()

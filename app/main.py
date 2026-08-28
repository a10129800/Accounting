import sys

from PySide6.QtWidgets import QApplication

from .database import SessionLocal, initialize_database
from .main_window import MainWindow
from .services import AccountingService


def main() -> int:
    initialize_database()
    application = QApplication(sys.argv)
    window = MainWindow(AccountingService(SessionLocal))
    window.show()
    return application.exec()


if __name__ == "__main__":
    raise SystemExit(main())

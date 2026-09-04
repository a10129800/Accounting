import sqlite3
from pathlib import Path

from .config import DATABASE_PATH


class BackupError(Exception):
    """Raised when a database backup or restore cannot be completed."""


def backup_database(destination: Path | str) -> Path:
    """Create a consistent SQLite backup at destination."""
    destination_path = Path(destination)
    destination_path.parent.mkdir(parents=True, exist_ok=True)

    if destination_path.resolve() == DATABASE_PATH.resolve():
        raise BackupError("備份檔不能與目前資料庫相同")

    source_connection = None
    target_connection = None
    try:
        source_connection = sqlite3.connect(DATABASE_PATH)
        target_connection = sqlite3.connect(destination_path)
        source_connection.backup(target_connection)
        target_connection.commit()
    except (OSError, sqlite3.Error) as error:
        raise BackupError(f"備份失敗：{error}") from error
    finally:
        if target_connection is not None:
            target_connection.close()
        if source_connection is not None:
            source_connection.close()

    return destination_path


def restore_database(source: Path | str) -> None:
    """Restore a valid SQLite database over the current database."""
    source_path = Path(source)
    if not source_path.is_file():
        raise BackupError("找不到備份檔")

    source_connection = None
    target_connection = None
    try:
        source_connection = sqlite3.connect(source_path)
        is_valid = source_connection.execute(
            "PRAGMA integrity_check"
        ).fetchone()[0] == "ok"
        if not is_valid:
            raise BackupError("備份檔驗證失敗，無法還原")

        target_connection = sqlite3.connect(DATABASE_PATH)
        source_connection.backup(target_connection)
        target_connection.commit()
    except BackupError:
        raise
    except (OSError, sqlite3.Error) as error:
        raise BackupError(f"還原失敗：{error}") from error
    finally:
        if target_connection is not None:
            target_connection.close()
        if source_connection is not None:
            source_connection.close()

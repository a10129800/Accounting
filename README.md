# My Accounting App
![](https://github.com/a10129800/Accounting/blob/master/img/2026-08-29%2017%2047%2059.png)
一個使用 Python、PySide6、SQLAlchemy 與 SQLite 建立的簡易桌面記帳軟體。

A simple desktop accounting application built with Python, PySide6, SQLAlchemy, and SQLite.

## Features / 功能

- 新增收入與支出 / Add income and expense transactions (8/28)
- 編輯交易 / Edit transactions (8/28)
- 刪除交易 / Delete transactions (8/28)
- 記錄日期與備註 / Record transaction date and notes (8/28)
- 顯示交易紀錄 / Display transaction history (8/28)
- 依分類或備註搜尋交易 / Search transactions by category or note (8/28)
- 依日期範圍篩選交易 / Filter transactions by date range (8/28)
- 顯示總收入、總支出與餘額 / Display total income, total expense, and balance (8/28)
- 啟動時自動建立 SQLite 資料庫與預設分類 / Automatically create the SQLite database and default categories on startup (8/28)
- 新增自訂分類 / Add custom categories (8/29)
- 編輯分類 / Edit categories (8/29)
- 刪除未使用的分類 / Delete unused categories (8/29)
- 月份統計 / Monthly statistics (8/30)
- 分類統計 / Category statistics (8/30)

## Requirements / 系統需求

- Python 3.12 or newer / Python 3.12 或更新版本
- Windows, macOS, or Linux / Windows、macOS 或 Linux

## Installation / 安裝

在專案根目錄建立並啟用虛擬環境：

Create and activate a virtual environment in the project root:

### Windows PowerShell

```powershell
py -3.12 -m venv .venv
.venv\Scripts\Activate.ps1
```

### macOS / Linux

```bash
python3.12 -m venv .venv
source .venv/bin/activate
```

安裝依賴套件：

Install the dependencies:

```bash
python -m pip install -r requirements.txt
```

## Run / 啟動

在專案根目錄執行：

Run the following command from the project root:

```bash
python -m app.main
```

第一次啟動時，程式會自動建立 `accounting.db`，並建立尚未存在的預設分類。資料庫檔案屬於本機資料，不會提交到 Git。

On the first launch, the application automatically creates `accounting.db` and any missing default categories. The database is local application data and is not committed to Git.

## Test / 測試

執行 pytest：

Run the pytest suite:

```bash
python -m pytest -q
```

測試涵蓋：

The tests cover:

- 新增收入與支出 / Adding income and expense
- 金額必須大於零 / Positive amount validation
- 編輯交易 / Editing transactions
- 刪除交易 / Deleting transactions
- 總收入、總支出與餘額 / Income, expense, and balance calculations
- 收入分類與支出分類驗證 / Matching transaction types with categories

## Project Structure / 專案結構

```text
MyAccountingApp/
├── app/
│   ├── main.py                 # 程式進入點 / Application entry point
│   ├── config.py               # 設定 / Configuration
│   ├── database.py             # 資料庫初始化與 Session / Database initialization and sessions
│   ├── models.py               # Category、Transaction / Data models
│   ├── repositories.py         # 資料存取 / Data access
│   ├── services.py             # 驗證與商業邏輯 / Validation and business logic
│   ├── main_window.py          # 主視窗 / Main window
│   ├── transaction_dialog.py   # 新增與編輯視窗 / Create and edit dialog
│   └── transaction_table.py    # 交易列表 / Transaction table
├── tests/
│   └── test_services.py        # 服務層測試 / Service-layer tests
├── requirements.txt
└── README.md
```

## Architecture / 架構說明

本專案採用簡單的分層設計：

The project uses a simple layered design:

- `main.py` only starts the application and does not contain business logic.
- `main_window.py` handles the main window and coordinates user actions.
- `transaction_dialog.py` collects and displays transaction input.
- `transaction_table.py` displays transaction records.
- `services.py` validates input and applies business rules.
- `repositories.py` performs database CRUD operations only.
- `models.py` defines the SQLAlchemy ORM models.
- `database.py` configures SQLite, SQLAlchemy, sessions, and default categories.

## Default Categories / 預設分類

### Income / 收入

- 薪資 / Salary
- 獎金 / Bonus
- 其他收入 / Other income

### Expense / 支出

- 餐飲 / Food and dining
- 交通 / Transportation
- 娛樂 / Entertainment
- 生活用品 / Household items
- 其他支出 / Other expense

## Data Model / 資料模型

`Transaction` contains:

- `id`
- `amount`：integer amount in currency units / 以整數儲存的金額
- `type`
- `category_id`
- `transaction_date`
- `note`
- `created_at`
- `updated_at`

`Category` contains:

- `id`
- `name`
- `type`
- `created_at`

金額使用整數，以元為單位，不使用浮點數，以避免金額計算誤差。

Amounts are stored as integers in whole currency units. Floating-point values are not used, avoiding monetary calculation errors.

## Future Extensions / 未來擴充

目前的模組邊界可繼續支援：

The current module boundaries can be extended with:

- 預算管理 / Budget management
- Excel 匯出 / Excel export
- 資料庫備份與還原 / Database backup and restore

## License / 授權

此專案目前尚未指定授權條款。

No license has been specified for this project yet.

# Smart Expense Tracker API

A lightweight REST API to manage personal expenses, built using Python and FastAPI. Data is persisted locally in a structured JSON file, and operations are fully thread-safe.

This project is structured specifically to meet the evaluation guidelines of the Software Engineering Apprenticeship Take-Home Assignment.

## Features

- **Base Expense Management (CRUD):** Add, view, filter by multiple criteria, and delete expenses.
- **Advanced Query Filtering:** Filter transactions by category, receiver, date range, amount range, and payment method simultaneously.
- **Keyword Search Filter (Bonus Pick):** Run text searches across transaction titles and receiver names.
- **Data Validation:** Strict payload validation (positive amount constraints, length limits, string sanitization, and payment type constraints) using Pydantic v2.
- **Analytics Dashboard Endpoint:** Get overall total, category-wise breakdowns, category percentages, counts, average expense amounts, and payment type breakdowns.
- **Monthly Budget Tracker:** Set a monthly spending limit and check status (remaining budget and warnings for exceedances).
- **Data Export:** Export all tracked expenses directly into a downloadable CSV spreadsheet including all transaction metadata.
- **Interactive Documentation:** Automatic OpenAPI documentation page generated at `/docs`.
- **Automated Test Suite:** Full suite of unit tests with a mock database setup using pytest.

---

## File Structure

```
your-repo/
  README.md        # What was built, installation, server and test commands
  AI_NOTES.md      # AI collaboration notes
  expenses.json    # Pre-seeded database with 100 transaction records
  requirements.txt # Project dependencies
  .gitignore       # Git untracked patterns
  src/             # Source code directory
    ├── main.py         # Main entry point with routes and server initialization
    ├── database.py     # Thread-safe JSON database manager
    └── schemas.py      # Pydantic v2 data validation schemas
  tests/           # Test suite directory
    └── test_api.py     # pytest test suite
```

---

## Getting Started

### Prerequisites

Ensure you have Python 3.8+ installed on your system.

### Installation

1. Create a virtual environment:
   ```bash
   python -m venv .venv
   ```

2. Activate the virtual environment:
   - **Windows (Command Prompt):**
     ```cmd
     .venv\Scripts\activate.bat
     ```
   - **Windows (PowerShell):**
     ```powershell
     .venv\Scripts\Activate.ps1
     ```
   - **macOS/Linux:**
     ```bash
     source .venv/bin/activate
     ```

3. Install the dependencies:
   ```bash
   pip install -r requirements.txt
   ```

---

## Running the Application

Start the local Uvicorn development server from the project root:

```bash
uvicorn src.main:app --reload
```

Once running, you can access the application at:
- **Base API URL:** `http://127.0.0.1:8000`
- **Interactive Swagger Documentation:** `http://127.0.0.1:8000/docs` (Use this to test endpoints in your browser)

---

## Running the Tests

To run the automated verification suite, execute the following command in the project root:

```bash
pytest tests/test_api.py -v
```

This will run the tests against an isolated, temporary database file (`test_expenses.json`) and clean up afterward.

---

## API Endpoints Reference

### Expense Operations

#### Add an Expense
- **Method:** `POST`
- **Path:** `/expenses`
- **Body Example:**
  ```json
  {
    "title": "Groceries",
    "amount": 1250.00,
    "category": "Food",
    "payment_type": "mobile_payment",
    "receiver": "Kirana Shop"
  }
  ```
  *Note: Allowed values for `payment_type` are: `cash`, `credit_card`, `debit_card`, `bank_transfer`, `mobile_payment`.*
- **Response Example (201 Created):**
  ```json
  {
    "id": "e5d8a9e7-578d-4e92-ba78-2d88a104fa2f",
    "title": "Groceries",
    "amount": 1250.0,
    "category": "food",
    "date": "2026-08-02",
    "payment_type": "mobile_payment",
    "receiver": "Kirana Shop"
  }
  ```

#### View All Expenses
- **Method:** `GET`
- **Path:** `/expenses`
- **Query Parameters:** 
  - `category` (optional, string for category filter, case-insensitive)
  - `receiver` (optional, string for receiver filter, case-insensitive substring match)
  - `start_date` (optional, date string `YYYY-MM-DD` for filtering expenses starting from this date)
  - `end_date` (optional, date string `YYYY-MM-DD` for filtering expenses up to this date)
  - `min_amount` (optional, float for filtering expenses with amount greater than or equal to this value)
  - `max_amount` (optional, float for filtering expenses with amount less than or equal to this value)
  - `payment_type` (optional, string for matching payment type, case-insensitive)
  - `search` (optional, string for keyword matching against both transaction `title` and `receiver` fields, case-insensitive substring match)
- **Response Example (200 OK):**
  ```json
  [
    {
      "id": "e5d8a9e7-578d-4e92-ba78-2d88a104fa2f",
      "title": "Groceries",
      "amount": 1250.0,
      "category": "food",
      "date": "2026-08-02",
      "payment_type": "mobile_payment",
      "receiver": "Kirana Shop"
    }
  ]
  ```

#### Delete an Expense
- **Method:** `DELETE`
- **Path:** `/expenses/{expense_id}`
- **Response Example (200 OK):**
  ```json
  {
    "success": true,
    "message": "Expense successfully deleted"
  }
  ```

---

### Smart Operations

#### Get Detailed Analytics
- **Method:** `GET`
- **Path:** `/expenses/analytics`
- **Response Example (200 OK):**
  ```json
  {
    "overall_total": 1250.0,
    "average_expense": 1250.0,
    "total_count": 1,
    "category_breakdown": {
      "food": 1250.0
    },
    "category_percentages": {
      "food": 100.0
    },
    "payment_type_breakdown": {
      "mobile_payment": 1250.0
    }
  }
  ```

#### Export to CSV
- **Method:** `GET`
- **Path:** `/expenses/export`
- **Response:** CSV file download (`expenses.csv`). Columns exported: `id`, `title`, `amount`, `category`, `date`, `payment_type`, `receiver`.

#### Get Monthly Budget Status
- **Method:** `GET`
- **Path:** `/budget`
- **Response Example (200 OK):**
  ```json
  {
    "monthly_budget": 45000.0,
    "current_month_spending": 1250.0,
    "remaining_budget": 43750.0,
    "is_exceeded": false
  }
  ```

#### Set Monthly Budget
- **Method:** `POST`
- **Path:** `/budget`
- **Body Example:**
  ```json
  {
    "limit": 45000.00
  }
  ```
- **Response Example (200 OK):**
  ```json
  {
    "limit": 45000.0
  }
  ```

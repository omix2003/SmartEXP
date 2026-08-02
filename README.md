# Smart Expense Tracker API

A lightweight REST API to manage personal expenses, built using Python and FastAPI. Data is persisted locally in a structured JSON file, and operations are fully thread-safe.

## Features

- **Base Expense Management (CRUD):** Add, view, filter by category (case-insensitive), and delete expenses.
- **Data Validation:** Strict payload validation (positive amount constraints, length limits, string sanitization) using Pydantic v2.
- **Analytics Dashboard Endpoint:** Get overall total, category-wise breakdowns, category percentages, counts, and average expense amounts.
- **Monthly Budget Tracker:** Set a monthly spending limit and check status (remaining budget and warnings for exceedances).
- **Data Export:** Export all tracked expenses directly into a downloadable CSV spreadsheet.
- **Interactive Documentation:** Automatic OpenAPI documentation page generated at `/docs`.
- **Automated Test Suite:** Full suite of unit tests with a mock database setup using pytest.

---

## File Structure

```
d:\ads\SEM\
├── main.py         # Main entry point with routes and server initialization
├── database.py     # Thread-safe JSON database manager
├── schemas.py      # Pydantic v2 data validation schemas
├── test_api.py     # pytest test suite
├── requirements.txt# Project dependencies
├── .gitignore      # Git untracked patterns
└── README.md       # Project documentation
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

Start the local Uvicorn development server:

```bash
uvicorn main:app --reload
```

Once running, you can access the application at:
- **Base API URL:** `http://127.0.0.1:8000`
- **Interactive Swagger Documentation:** `http://127.0.0.1:8000/docs` (Use this to test endpoints in your browser)

---

## Running the Tests

To run the automated verification suite, execute the following command in the project root:

```bash
pytest test_api.py -v
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
    "amount": 54.20,
    "category": "Food",
    "date": "2026-08-02"
  }
  ```
- **Response Example (201 Created):**
  ```json
  {
    "id": "f51270b2-78d1-4db5-9e6a-2d449339e8ba",
    "title": "Groceries",
    "amount": 54.2,
    "category": "food",
    "date": "2026-08-02"
  }
  ```

#### View All Expenses
- **Method:** `GET`
- **Path:** `/expenses`
- **Query Parameter:** `category` (optional, string for category filter)
- **Response Example (200 OK):**
  ```json
  [
    {
      "id": "f51270b2-78d1-4db5-9e6a-2d449339e8ba",
      "title": "Groceries",
      "amount": 54.2,
      "category": "food",
      "date": "2026-08-02"
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
    "overall_total": 54.2,
    "average_expense": 54.2,
    "total_count": 1,
    "category_breakdown": {
      "food": 54.2
    },
    "category_percentages": {
      "food": 100.0
    }
  }
  ```

#### Export to CSV
- **Method:** `GET`
- **Path:** `/expenses/export`
- **Response:** CSV file download (`expenses.csv`).

#### Get Monthly Budget Status
- **Method:** `GET`
- **Path:** `/budget`
- **Response Example (200 OK):**
  ```json
  {
    "monthly_budget": 500.0,
    "current_month_spending": 54.2,
    "remaining_budget": 445.8,
    "is_exceeded": false
  }
  ```

#### Set Monthly Budget
- **Method:** `POST`
- **Path:** `/budget`
- **Body Example:**
  ```json
  {
    "limit": 500.00
  }
  ```
- **Response Example (200 OK):**
  ```json
  {
    "limit": 500.0
  }
  ```

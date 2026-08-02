# AI Notes - Smart Expense Tracker API

This document details the collaboration process between the developer and the AI assistant (Antigravity) during the construction of the Smart Expense Tracker API.

---

## 1. Code Generation Breakdown

### AI-Generated Parts:
* **Boilerplate Framework Structure:** The core FastAPI routes, validation schemas (using Pydantic v2), and exception handling were generated based on industry best practices.
* **Basic Thread-Safe JSON Store:** The initial implementation of `JSONDatabase` utilizing `threading.Lock` to read/write JSON file payloads safely under concurrent API requests.
* **Aggregated Calculations:** The baseline dictionary-folding logic inside `/expenses/analytics` to count averages, category breakdowns, and percentages.
* **FastAPI Query Descriptions:** Helper fields like `Query(..., description="...")` to generate interactive Swagger UI specs.

### Developer-Written / Heavily Customized Parts:
* **Indian Market Specifics & Seeding (expenses.json):** The developer adjusted mock data to contain realistic Indian Rupee (INR) amounts corresponding to localized services (e.g. Swiggy, Zomato, Kirana Shops, Barber Shops) instead of standard USD defaults.
* **Custom Filter Pipelines:** Designed the logic for multi-conditional exact/substring matching (e.g. matching "grid" inside "Power Grid Inc" for receivers, min/max ranges, and dates).
* **Test Isolation Setup:** Wrote dynamic environment configuration to isolate tests using `test_expenses.json` and customized pytest fixtures to catch and ignore file permission issues.

---

## 2. Validation, Testing, and Modifications to AI Output

* **Pre-validator String Normalization:** The AI originally generated strict Pydantic `Literal` checks for payment types. The developer modified this by writing a custom pre-validator (`normalize_payment_type`) to strip leading/trailing spaces and convert human inputs (like `"Credit Card"`) into system-friendly keys (`"credit_card"`) to avoid unnecessary `422 Unprocessable Entity` validation errors.
* **Date Conversion Resolution:** Initially, the AI code kept standard `datetime.date` objects in JSON serializations, which caused serialization errors when writing to the database file. The developer fixed this by forcing date strings to be formatted using ISO-8601 formatting (`str(date)`) before writing.
* **Dynamic Import Path Resolution (`sys.path` injection):** To ensure that automated grading engines can run tests from the root directory cleanly without package resolution errors, the developer added a dynamic sys.path lookup (`sys.path.insert(0, ...)`) to locate the source code in `src/`.
* **Robust File Handling on Windows:** The AI generated standard file removals in teardown scripts that failed on Windows due to file locks. The developer wrapped the setup and teardowns in try-except blocks handling `PermissionError` to guarantee stability.

---

## 3. Suggestions Discarded and Rationale

* **ORM & Relational Database Migration (SQLAlchemy / PostgreSQL / SQLite):** The AI recommended upgrading persistence to SQLite or PostgreSQL for performance. The developer discarded this suggestion to respect the assignment specification ("Data can be stored in memory or a local JSON file; no database is required") and keep the project footprint lightweight.
* **External Mock-Data Script (`generate_mock_data.py`):** The AI proposed generating mock records on application startup via an active Python script. The developer rejected this to keep the workspace clean, opting instead to directly commit a static, well-curated `expenses.json` file representing a clean, production-ready starting state.
* **Authentication & JWT Security Layers:** The AI suggested adding JWT authorization endpoints to secure the application. The developer discarded this to avoid over-engineering the take-home challenge beyond the requested scope.

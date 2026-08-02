import json
import os
from typing import List, Dict, Any, Optional
from threading import Lock

class JSONDatabase:
    def __init__(self, filepath: str = "expenses.json"):
        self.filepath = filepath
        self.lock = Lock()
        self._init_db()

    def _init_db(self) -> None:
        """Initializes the JSON file with empty collections if it does not exist."""
        with self.lock:
            if not os.path.exists(self.filepath):
                initial_data = {
                    "expenses": [],
                    "budget_limit": 0.0
                }
                with open(self.filepath, "w", encoding="utf-8") as f:
                    json.dump(initial_data, f, indent=4)

    def _read_db(self) -> Dict[str, Any]:
        """Reads and returns the database contents."""
        with open(self.filepath, "r", encoding="utf-8") as f:
            return json.load(f)

    def _write_db(self, data: Dict[str, Any]) -> None:
        """Writes the updated data back to the JSON file."""
        with open(self.filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4)

    def get_expenses(self, category: Optional[str] = None) -> List[Dict[str, Any]]:
        """Retrieves all expenses, optionally filtered by category (case-insensitive)."""
        with self.lock:
            data = self._read_db()
            expenses = data.get("expenses", [])
            if category:
                category_lower = category.lower().strip()
                return [exp for exp in expenses if exp.get("category", "").lower() == category_lower]
            return expenses

    def get_expense_by_id(self, expense_id: str) -> Optional[Dict[str, Any]]:
        """Retrieves a single expense by its ID."""
        with self.lock:
            data = self._read_db()
            expenses = data.get("expenses", [])
            for exp in expenses:
                if exp.get("id") == expense_id:
                    return exp
            return None

    def add_expense(self, expense: Dict[str, Any]) -> Dict[str, Any]:
        """Appends a new expense to the database."""
        with self.lock:
            data = self._read_db()
            data["expenses"].append(expense)
            self._write_db(data)
            return expense

    def delete_expense(self, expense_id: str) -> bool:
        """Deletes an expense by its ID. Returns True if found and deleted, False otherwise."""
        with self.lock:
            data = self._read_db()
            expenses = data.get("expenses", [])
            original_length = len(expenses)
            data["expenses"] = [exp for exp in expenses if exp.get("id") != expense_id]
            if len(data["expenses"]) < original_length:
                self._write_db(data)
                return True
            return False

    def get_budget_limit(self) -> float:
        """Retrieves the monthly budget limit."""
        with self.lock:
            data = self._read_db()
            return float(data.get("budget_limit", 0.0))

    def set_budget_limit(self, limit: float) -> float:
        """Sets a new monthly budget limit."""
        with self.lock:
            data = self._read_db()
            data["budget_limit"] = limit
            self._write_db(data)
            return limit

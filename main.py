from fastapi import FastAPI, HTTPException, Query, status
from typing import List, Optional
import uuid
from database import JSONDatabase
from schemas import ExpenseCreate, ExpenseResponse

app = FastAPI(
    title="Smart Expense Tracker API",
    description="A clean REST API for managing personal expenses with local JSON storage.",
    version="1.0.0"
)

db = JSONDatabase()

@app.post("/expenses", response_model=ExpenseResponse, status_code=status.HTTP_201_CREATED)
def create_expense(expense: ExpenseCreate):
    """Add a new expense. Generates a unique UUID and converts the date to ISO format."""
    new_expense = expense.model_dump()
    new_expense["id"] = str(uuid.uuid4())
    new_expense["date"] = str(new_expense["date"])
    db.add_expense(new_expense)
    return new_expense

@app.get("/expenses", response_model=List[ExpenseResponse], status_code=status.HTTP_200_OK)
def read_expenses(category: Optional[str] = Query(None, description="Filter expenses by category (case-insensitive)")):
    """Retrieve all expenses, optionally filtered by category."""
    return db.get_expenses(category=category)

@app.delete("/expenses/{expense_id}", status_code=status.HTTP_200_OK)
def delete_expense(expense_id: str):
    """Delete an expense by its unique ID. Returns 404 if not found."""
    success = db.delete_expense(expense_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Expense with ID {expense_id} not found"
        )
    return {
        "success": True,
        "message": "Expense successfully deleted"
    }

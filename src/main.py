import sys
import os
# Ensure that the directory containing this file is in the search path for module imports
sys.path.insert(0, os.path.dirname(__file__))

from fastapi import FastAPI, HTTPException, Query, status, Response
from typing import List, Optional
import uuid
import csv
import io
from datetime import date
from database import JSONDatabase
from schemas import (
    ExpenseCreate,
    ExpenseResponse,
    BudgetLimit,
    BudgetStatusResponse,
    AnalyticsResponse
)

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
def read_expenses(
    category: Optional[str] = Query(None, description="Filter expenses by category (case-insensitive)"),
    receiver: Optional[str] = Query(None, description="Filter expenses by receiver (case-insensitive substring match)"),
    start_date: Optional[date] = Query(None, description="Filter expenses starting from this date (inclusive, YYYY-MM-DD)"),
    end_date: Optional[date] = Query(None, description="Filter expenses up to this date (inclusive, YYYY-MM-DD)"),
    min_amount: Optional[float] = Query(None, description="Filter expenses with amount greater than or equal to this value", gt=0.0),
    max_amount: Optional[float] = Query(None, description="Filter expenses with amount less than or equal to this value", gt=0.0),
    payment_type: Optional[str] = Query(None, description="Filter expenses by payment type (case-insensitive)"),
    search: Optional[str] = Query(None, description="General search query matching title or receiver (case-insensitive substring match)")
):
    """Retrieve all expenses, optionally filtered by category, receiver, date range, amount range, payment type, and search keyword."""
    return db.get_expenses(
        category=category,
        receiver=receiver,
        start_date=start_date,
        end_date=end_date,
        min_amount=min_amount,
        max_amount=max_amount,
        payment_type=payment_type,
        search=search
    )

@app.get("/expenses/analytics", response_model=AnalyticsResponse, status_code=status.HTTP_200_OK)
def get_analytics():
    """Retrieve detailed analytics on expenses, including category and payment type breakdowns."""
    expenses = db.get_expenses()
    total_count = len(expenses)
    if total_count == 0:
        return AnalyticsResponse(
            overall_total=0.0,
            average_expense=0.0,
            total_count=0,
            category_breakdown={},
            category_percentages={},
            payment_type_breakdown={}
        )

    overall_total = sum(exp["amount"] for exp in expenses)
    average_expense = overall_total / total_count

    category_breakdown = {}
    payment_type_breakdown = {}
    for exp in expenses:
        cat = exp["category"]
        ptype = exp.get("payment_type", "cash")
        
        category_breakdown[cat] = category_breakdown.get(cat, 0.0) + exp["amount"]
        payment_type_breakdown[ptype] = payment_type_breakdown.get(ptype, 0.0) + exp["amount"]

    category_percentages = {}
    for cat, amt in category_breakdown.items():
        category_percentages[cat] = round((amt / overall_total) * 100.0, 2)
        category_breakdown[cat] = round(amt, 2)

    for ptype, amt in payment_type_breakdown.items():
        payment_type_breakdown[ptype] = round(amt, 2)

    return AnalyticsResponse(
        overall_total=round(overall_total, 2),
        average_expense=round(average_expense, 2),
        total_count=total_count,
        category_breakdown=category_breakdown,
        category_percentages=category_percentages,
        payment_type_breakdown=payment_type_breakdown
    )

@app.get("/expenses/export", status_code=status.HTTP_200_OK)
def export_expenses():
    """Export all expenses to a CSV file."""
    expenses = db.get_expenses()
    
    output = io.StringIO()
    writer = csv.writer(output)
    
    writer.writerow(["id", "title", "amount", "category", "date", "payment_type", "receiver"])
    
    for exp in expenses:
        writer.writerow([
            exp.get("id"),
            exp.get("title"),
            exp.get("amount"),
            exp.get("category"),
            exp.get("date"),
            exp.get("payment_type", "cash"),
            exp.get("receiver", "")
        ])
    
    csv_content = output.getvalue()
    output.close()
    
    return Response(
        content=csv_content,
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=expenses.csv"}
    )

@app.get("/budget", response_model=BudgetStatusResponse, status_code=status.HTTP_200_OK)
def get_budget_status():
    """Calculate and return the monthly budget status based on current calendar month spending."""
    budget_limit = db.get_budget_limit()
    
    today = date.today()
    current_year = today.year
    current_month = today.month
    
    expenses = db.get_expenses()
    current_month_spending = 0.0
    for exp in expenses:
        try:
            exp_date = date.fromisoformat(exp["date"])
            if exp_date.year == current_year and exp_date.month == current_month:
                current_month_spending += exp["amount"]
        except (ValueError, TypeError):
            continue
            
    remaining_budget = budget_limit - current_month_spending
    is_exceeded = False
    if budget_limit > 0.0 and current_month_spending > budget_limit:
        is_exceeded = True
        
    return BudgetStatusResponse(
        monthly_budget=round(budget_limit, 2),
        current_month_spending=round(current_month_spending, 2),
        remaining_budget=round(remaining_budget, 2),
        is_exceeded=is_exceeded
    )

@app.post("/budget", response_model=BudgetLimit, status_code=status.HTTP_200_OK)
def set_budget(budget: BudgetLimit):
    """Set the monthly budget limit."""
    db.set_budget_limit(budget.limit)
    return budget

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

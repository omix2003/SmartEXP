import os
import pytest
from datetime import date
from fastapi.testclient import TestClient

# Set testing environment variable before importing main
os.environ["DATABASE_FILEPATH"] = "test_expenses.json"

from main import app, db

client = TestClient(app)

@pytest.fixture(autouse=True)
def clean_test_database():
    """Fixture to ensure each test case starts with a clean database and files are cleaned up after."""
    if os.path.exists("test_expenses.json"):
        try:
            os.remove("test_expenses.json")
        except PermissionError:
            pass
    db._init_db()
    yield
    if os.path.exists("test_expenses.json"):
        try:
            os.remove("test_expenses.json")
        except PermissionError:
            pass

def test_create_expense():
    """Verify adding an expense works, auto-populates date if omitted, and strips strings."""
    payload = {
        "title": " Groceries ",
        "amount": 45.50,
        "category": " Food "
    }
    response = client.post("/expenses", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert "id" in data
    assert data["title"] == "Groceries"
    assert data["amount"] == 45.50
    assert data["category"] == "food"
    assert data["date"] == str(date.today())

def test_create_expense_validation():
    """Verify schema validation rules for negative amount and empty titles/categories."""
    # Invalid amount
    payload = {"title": "Coffee", "amount": -2.50, "category": "Food"}
    response = client.post("/expenses", json=payload)
    assert response.status_code == 422

    # Empty title
    payload = {"title": "", "amount": 5.00, "category": "Food"}
    response = client.post("/expenses", json=payload)
    assert response.status_code == 422

    # Empty category
    payload = {"title": "Coffee", "amount": 5.00, "category": "   "}
    response = client.post("/expenses", json=payload)
    assert response.status_code == 422

def test_get_expenses_and_filtering():
    """Verify retrieval and category filtering (case-insensitive)."""
    # Create two expenses in different categories
    client.post("/expenses", json={"title": "Tacos", "amount": 15.00, "category": "Food"})
    client.post("/expenses", json={"title": "Electric Bill", "amount": 120.00, "category": "Utilities"})

    # Get all
    response = client.get("/expenses")
    assert response.status_code == 200
    assert len(response.json()) == 2

    # Filter by category (food)
    response = client.get("/expenses?category=food")
    assert response.status_code == 200
    expenses = response.json()
    assert len(expenses) == 1
    assert expenses[0]["title"] == "Tacos"

    # Filter by category (case-insensitive and trailing space check)
    response = client.get("/expenses?category=  UTILITIES ")
    assert response.status_code == 200
    expenses = response.json()
    assert len(expenses) == 1
    assert expenses[0]["title"] == "Electric Bill"

def test_analytics():
    """Verify calculations of total, average, and category percentage breakdown."""
    client.post("/expenses", json={"title": "Lunch", "amount": 20.00, "category": "Food"})
    client.post("/expenses", json={"title": "Dinner", "amount": 30.00, "category": "Food"})
    client.post("/expenses", json={"title": "Train", "amount": 50.00, "category": "Transport"})

    response = client.get("/expenses/analytics")
    assert response.status_code == 200
    data = response.json()
    assert data["overall_total"] == 100.00
    assert data["average_expense"] == 33.33
    assert data["total_count"] == 3
    assert data["category_breakdown"]["food"] == 50.00
    assert data["category_breakdown"]["transport"] == 50.00
    assert data["category_percentages"]["food"] == 50.00
    assert data["category_percentages"]["transport"] == 50.00

def test_export_csv():
    """Verify CSV export contains header and rows matching expenses."""
    client.post("/expenses", json={"title": "Lunch", "amount": 20.00, "category": "Food"})
    
    response = client.get("/expenses/export")
    assert response.status_code == 200
    assert response.headers["content-type"] == "text/csv; charset=utf-8"
    assert "attachment; filename=expenses.csv" in response.headers["content-disposition"]
    
    content = response.text
    lines = content.strip().split("\r\n")
    assert len(lines) == 2
    assert lines[0] == "id,title,amount,category,date"
    assert "Lunch,20.0,food" in lines[1]

def test_budget_flow():
    """Verify budget creation, threshold checking, and limit warning flags."""
    # Initial status
    response = client.get("/budget")
    assert response.status_code == 200
    assert response.json()["monthly_budget"] == 0.0

    # Set budget
    response = client.post("/budget", json={"limit": 100.00})
    assert response.status_code == 200
    assert response.json()["limit"] == 100.00

    # Verify status (no spending yet)
    response = client.get("/budget")
    assert response.json()["monthly_budget"] == 100.00
    assert response.json()["current_month_spending"] == 0.0
    assert response.json()["remaining_budget"] == 100.00
    assert response.json()["is_exceeded"] is False

    # Add expense within budget
    client.post("/expenses", json={"title": "Groceries", "amount": 60.00, "category": "Food"})
    response = client.get("/budget")
    assert response.json()["current_month_spending"] == 60.00
    assert response.json()["remaining_budget"] == 40.00
    assert response.json()["is_exceeded"] is False

    # Add expense exceeding budget
    client.post("/expenses", json={"title": "Dinner", "amount": 50.00, "category": "Food"})
    response = client.get("/budget")
    assert response.json()["current_month_spending"] == 110.00
    assert response.json()["remaining_budget"] == -10.00
    assert response.json()["is_exceeded"] is True

def test_delete_expense():
    """Verify expense deletion and error handling for missing IDs."""
    # Add an expense
    response = client.post("/expenses", json={"title": "Tacos", "amount": 15.00, "category": "Food"})
    expense_id = response.json()["id"]

    # Delete the expense
    response = client.delete(f"/expenses/{expense_id}")
    assert response.status_code == 200
    assert response.json()["success"] is True

    # Retrieve expenses (should be empty)
    response = client.get("/expenses")
    assert len(response.json()) == 0

    # Try to delete again (should fail with 404)
    response = client.delete(f"/expenses/{expense_id}")
    assert response.status_code == 404

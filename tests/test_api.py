import os
import sys
import pytest
from datetime import date, timedelta
from fastapi.testclient import TestClient

# Inject the src/ directory into the python module lookup path before importing main
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../src")))

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
    """Verify adding an expense works, auto-populates date if omitted, and strips/normalizes strings."""
    payload = {
        "title": " Groceries ",
        "amount": 45.50,
        "category": " Food ",
        "payment_type": " Credit Card ",
        "receiver": " Walmart "
    }
    response = client.post("/expenses", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert "id" in data
    assert data["title"] == "Groceries"
    assert data["amount"] == 45.50
    assert data["category"] == "food"
    assert data["payment_type"] == "credit_card"
    assert data["receiver"] == "Walmart"
    assert data["date"] == str(date.today())

def test_create_expense_validation():
    """Verify schema validation rules for negative amount, empty values, and invalid payment types."""
    # Invalid amount
    payload = {"title": "Coffee", "amount": -2.50, "category": "Food", "payment_type": "cash", "receiver": "Starbucks"}
    response = client.post("/expenses", json=payload)
    assert response.status_code == 422

    # Empty title
    payload = {"title": "", "amount": 5.00, "category": "Food", "payment_type": "cash", "receiver": "Starbucks"}
    response = client.post("/expenses", json=payload)
    assert response.status_code == 422

    # Empty category
    payload = {"title": "Coffee", "amount": 5.00, "category": "   ", "payment_type": "cash", "receiver": "Starbucks"}
    response = client.post("/expenses", json=payload)
    assert response.status_code == 422

    # Invalid payment type
    payload = {"title": "Coffee", "amount": 5.00, "category": "Food", "payment_type": "crypto", "receiver": "Starbucks"}
    response = client.post("/expenses", json=payload)
    assert response.status_code == 422

    # Empty receiver
    payload = {"title": "Coffee", "amount": 5.00, "category": "Food", "payment_type": "cash", "receiver": "   "}
    response = client.post("/expenses", json=payload)
    assert response.status_code == 422

def test_get_expenses_and_filtering():
    """Verify retrieval and category/receiver filtering (case-insensitive & substring match)."""
    # Create two expenses
    client.post("/expenses", json={"title": "Tacos", "amount": 15.00, "category": "Food", "payment_type": "cash", "receiver": "Zomato Delivery"})
    client.post("/expenses", json={"title": "Electric Bill", "amount": 120.00, "category": "Utilities", "payment_type": "bank_transfer", "receiver": "Power Grid Inc"})

    # Get all
    response = client.get("/expenses")
    assert response.status_code == 200
    assert len(response.json()) == 2

    # Filter by category
    response = client.get("/expenses?category=food")
    assert response.status_code == 200
    expenses = response.json()
    assert len(expenses) == 1
    assert expenses[0]["title"] == "Tacos"

    # Filter by receiver (exact case-insensitive match)
    response = client.get("/expenses?receiver=zomato delivery")
    assert response.status_code == 200
    expenses = response.json()
    assert len(expenses) == 1
    assert expenses[0]["title"] == "Tacos"

    # Filter by receiver (substring case-insensitive match)
    response = client.get("/expenses?receiver=  grid ")
    assert response.status_code == 200
    expenses = response.json()
    assert len(expenses) == 1
    assert expenses[0]["title"] == "Electric Bill"

    # Filter by both category and receiver
    response = client.get("/expenses?category=food&receiver=zomato")
    assert response.status_code == 200
    expenses = response.json()
    assert len(expenses) == 1

    # Filter by both (no match)
    response = client.get("/expenses?category=utilities&receiver=zomato")
    assert response.status_code == 200
    expenses = response.json()
    assert len(expenses) == 0

def test_additional_filters():
    """Verify amount range, date range, payment method, and search keyword filtering."""
    today = date.today()
    yesterday = today - timedelta(days=1)
    tomorrow = today + timedelta(days=1)

    # Seed transactions
    client.post("/expenses", json={"title": "Tacos", "amount": 15.00, "category": "Food", "payment_type": "cash", "receiver": "Zomato Delivery", "date": str(yesterday)})
    client.post("/expenses", json={"title": "Electric Bill", "amount": 120.00, "category": "Utilities", "payment_type": "bank_transfer", "receiver": "Power Grid Inc", "date": str(today)})
    client.post("/expenses", json={"title": "Laptop", "amount": 1500.00, "category": "Shopping", "payment_type": "credit_card", "receiver": "Amazon Store", "date": str(tomorrow)})

    # Filter by min_amount
    response = client.get("/expenses?min_amount=100.00")
    assert len(response.json()) == 2
    
    # Filter by max_amount
    response = client.get("/expenses?max_amount=150.00")
    assert len(response.json()) == 2

    # Filter by amount range
    response = client.get("/expenses?min_amount=20.00&max_amount=500.00")
    assert len(response.json()) == 1
    assert response.json()[0]["title"] == "Electric Bill"

    # Filter by start_date
    response = client.get(f"/expenses?start_date={str(today)}")
    assert len(response.json()) == 2

    # Filter by end_date
    response = client.get(f"/expenses?end_date={str(today)}")
    assert len(response.json()) == 2

    # Filter by date range
    response = client.get(f"/expenses?start_date={str(yesterday)}&end_date={str(today)}")
    assert len(response.json()) == 2

    # Filter by payment_type
    response = client.get("/expenses?payment_type=credit_card")
    assert len(response.json()) == 1
    assert response.json()[0]["title"] == "Laptop"

    # Search filter matching title
    response = client.get("/expenses?search=tacos")
    assert len(response.json()) == 1
    assert response.json()[0]["title"] == "Tacos"

    # Search filter matching receiver (substring match)
    response = client.get("/expenses?search=amazon")
    assert len(response.json()) == 1
    assert response.json()[0]["title"] == "Laptop"

    # Search filter matching receiver (case-insensitive substring)
    response = client.get("/expenses?search=  deliv ")
    assert len(response.json()) == 1
    assert response.json()[0]["title"] == "Tacos"

    # Combined complex filtering with search
    response = client.get(f"/expenses?min_amount=10.00&max_amount=200.00&start_date={str(yesterday)}&payment_type=cash&search=zomato")
    assert len(response.json()) == 1
    assert response.json()[0]["title"] == "Tacos"

def test_analytics():
    """Verify calculations of total, average, category breakdown, and payment type breakdown."""
    client.post("/expenses", json={"title": "Lunch", "amount": 20.00, "category": "Food", "payment_type": "cash", "receiver": "Diner"})
    client.post("/expenses", json={"title": "Dinner", "amount": 30.00, "category": "Food", "payment_type": "credit_card", "receiver": "Zomato"})
    client.post("/expenses", json={"title": "Train", "amount": 50.00, "category": "Transport", "payment_type": "debit_card", "receiver": "Rail Corp"})

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
    assert data["payment_type_breakdown"]["cash"] == 20.00
    assert data["payment_type_breakdown"]["credit_card"] == 30.00
    assert data["payment_type_breakdown"]["debit_card"] == 50.00

def test_export_csv():
    """Verify CSV export contains header (with payment_type & receiver) and matching data rows."""
    client.post("/expenses", json={"title": "Lunch", "amount": 20.00, "category": "Food", "payment_type": "cash", "receiver": "Swiggy"})
    
    response = client.get("/expenses/export")
    assert response.status_code == 200
    assert response.headers["content-type"] == "text/csv; charset=utf-8"
    assert "attachment; filename=expenses.csv" in response.headers["content-disposition"]
    
    content = response.text
    lines = content.strip().split("\r\n")
    assert len(lines) == 2
    assert lines[0] == "id,title,amount,category,date,payment_type,receiver"
    assert "Lunch,20.0,food" in lines[1]
    assert "cash" in lines[1]
    assert "Swiggy" in lines[1]

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
    client.post("/expenses", json={"title": "Groceries", "amount": 60.00, "category": "Food", "payment_type": "debit_card", "receiver": "Walmart"})
    response = client.get("/budget")
    assert response.json()["current_month_spending"] == 60.00
    assert response.json()["remaining_budget"] == 40.00
    assert response.json()["is_exceeded"] is False

    # Add expense exceeding budget
    client.post("/expenses", json={"title": "Dinner", "amount": 50.00, "category": "Food", "payment_type": "credit_card", "receiver": "Zomato"})
    response = client.get("/budget")
    assert response.json()["current_month_spending"] == 110.00
    assert response.json()["remaining_budget"] == -10.00
    assert response.json()["is_exceeded"] is True

def test_delete_expense():
    """Verify expense deletion and error handling for missing IDs."""
    # Add an expense
    response = client.post("/expenses", json={"title": "Tacos", "amount": 15.00, "category": "Food", "payment_type": "cash", "receiver": "Tacos Shop"})
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

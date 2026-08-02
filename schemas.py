from pydantic import BaseModel, Field, field_validator
import datetime
from typing import Optional, Dict, Any, Literal

class ExpenseBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=100)
    amount: float = Field(..., gt=0.0)
    category: str = Field(..., min_length=1, max_length=50)
    date: datetime.date = Field(default_factory=datetime.date.today)
    payment_type: Literal["cash", "credit_card", "debit_card", "bank_transfer", "mobile_payment"] = Field(
        ..., description="Method used to pay for the expense"
    )
    receiver: str = Field(..., min_length=1, max_length=100, description="The recipient of the payment")

    @field_validator("title", "category", "payment_type", "receiver", mode="before")
    @classmethod
    def strip_strings(cls, v: Any) -> Any:
        if isinstance(v, str):
            return v.strip()
        return v

    @field_validator("category")
    @classmethod
    def normalize_category(cls, v: str) -> str:
        if not v:
            raise ValueError("Category cannot be empty")
        return v.lower()

    @field_validator("payment_type", mode="before")
    @classmethod
    def normalize_payment_type(cls, v: Any) -> Any:
        if isinstance(v, str):
            return v.strip().lower().replace(" ", "_")
        return v

class ExpenseCreate(ExpenseBase):
    pass

class ExpenseResponse(ExpenseBase):
    id: str

class BudgetLimit(BaseModel):
    limit: float = Field(..., ge=0.0)

class BudgetStatusResponse(BaseModel):
    monthly_budget: float
    current_month_spending: float
    remaining_budget: float
    is_exceeded: bool

class AnalyticsResponse(BaseModel):
    overall_total: float
    average_expense: float
    total_count: int
    category_breakdown: Dict[str, float]
    category_percentages: Dict[str, float]
    payment_type_breakdown: Dict[str, float]

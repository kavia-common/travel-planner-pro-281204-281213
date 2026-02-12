"""
Pydantic schemas for the Travel Planner API.

These schemas are used for request validation and response serialization.
"""

from __future__ import annotations

from datetime import date, datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field, field_validator


class ApiMessage(BaseModel):
    """Generic message response."""

    message: str = Field(..., description="Human-readable status message")


class UserCreate(BaseModel):
    """Create a user (simple, no auth in this template)."""

    email: str = Field(..., description="User email address", examples=["alex@example.com"])
    full_name: str = Field(..., description="User full name", examples=["Alex Doe"])


class UserOut(BaseModel):
    """User returned by the API."""

    id: UUID = Field(..., description="User id (UUID)")
    email: str = Field(..., description="User email address")
    full_name: str = Field(..., description="User full name")
    created_at: datetime = Field(..., description="Creation timestamp")

    class Config:
        from_attributes = True


def _normalize_currency_code(code: str) -> str:
    """Normalize a currency code to uppercase and validate basic ISO-4217 formatting."""
    c = (code or "").strip().upper()
    if len(c) != 3 or not c.isalpha():
        raise ValueError("currency_code must be a 3-letter ISO-4217 code (e.g., USD, EUR)")
    return c


class TripCreate(BaseModel):
    """Create a trip."""

    user_id: UUID = Field(..., description="Owner user id (UUID)")
    name: str = Field(..., description="Trip name", examples=["Japan Spring 2026"])
    start_date: Optional[date] = Field(None, description="Trip start date")
    end_date: Optional[date] = Field(None, description="Trip end date")
    currency_code: str = Field("USD", description="Trip base currency (ISO-4217)", examples=["USD", "EUR", "JPY"])

    @field_validator("currency_code")
    @classmethod
    def validate_currency_code(cls, v: str) -> str:
        return _normalize_currency_code(v)


class TripUpdate(BaseModel):
    """Update a trip."""

    name: Optional[str] = Field(None, description="Trip name")
    start_date: Optional[date] = Field(None, description="Trip start date")
    end_date: Optional[date] = Field(None, description="Trip end date")
    currency_code: Optional[str] = Field(None, description="Trip base currency (ISO-4217)")

    @field_validator("currency_code")
    @classmethod
    def validate_currency_code(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return None
        return _normalize_currency_code(v)


class TripOut(BaseModel):
    """Trip returned by the API."""

    id: UUID = Field(..., description="Trip id (UUID)")
    user_id: UUID = Field(..., description="Owner user id (UUID)")
    name: str = Field(..., description="Trip name")
    start_date: Optional[date] = Field(None, description="Trip start date")
    end_date: Optional[date] = Field(None, description="Trip end date")
    currency_code: str = Field(..., description="Trip base currency (ISO-4217)")
    created_at: datetime = Field(..., description="Created timestamp")
    updated_at: datetime = Field(..., description="Updated timestamp")

    class Config:
        from_attributes = True


class DestinationCreate(BaseModel):
    """Add a destination to a trip."""

    name: str = Field(..., description="Destination name (city/region)", examples=["Tokyo"])
    country: Optional[str] = Field(None, description="Country name", examples=["Japan"])
    start_date: Optional[date] = Field(None, description="Destination arrival date")
    end_date: Optional[date] = Field(None, description="Destination departure date")
    sort_order: int = Field(0, description="Ordering within the trip")


class DestinationOut(BaseModel):
    """Destination returned by the API."""

    id: UUID = Field(..., description="Destination id (UUID)")
    trip_id: UUID = Field(..., description="Trip id (UUID)")
    name: str = Field(..., description="Destination name")
    country: Optional[str] = Field(None, description="Country name")
    start_date: Optional[date] = Field(None, description="Start date")
    end_date: Optional[date] = Field(None, description="End date")
    sort_order: int = Field(..., description="Ordering within the trip")
    created_at: datetime = Field(..., description="Created timestamp")

    class Config:
        from_attributes = True


class DayCreate(BaseModel):
    """Create an itinerary day for a trip."""

    day_date: date = Field(..., description="Calendar date for this itinerary day")
    title: Optional[str] = Field(None, description="Day title", examples=["Arrive + Shibuya"])
    summary: Optional[str] = Field(None, description="Day summary")


class DayOut(BaseModel):
    """Itinerary day returned by the API."""

    id: UUID = Field(..., description="Day id (UUID)")
    trip_id: UUID = Field(..., description="Trip id (UUID)")
    day_date: date = Field(..., description="Calendar date")
    title: Optional[str] = Field(None, description="Title")
    summary: Optional[str] = Field(None, description="Summary")
    created_at: datetime = Field(..., description="Created timestamp")

    class Config:
        from_attributes = True


class AccommodationCreate(BaseModel):
    """Create accommodation."""

    destination_id: Optional[UUID] = Field(None, description="Optional destination id")
    name: str = Field(..., description="Hotel / lodging name")
    address: Optional[str] = Field(None, description="Address")
    check_in: Optional[datetime] = Field(None, description="Check-in datetime")
    check_out: Optional[datetime] = Field(None, description="Check-out datetime")
    confirmation_number: Optional[str] = Field(None, description="Confirmation number")
    booking_url: Optional[str] = Field(None, description="Booking URL")
    phone: Optional[str] = Field(None, description="Phone number")
    notes: Optional[str] = Field(None, description="Notes")


class AccommodationOut(BaseModel):
    """Accommodation returned by API."""

    id: UUID = Field(..., description="Accommodation id (UUID)")
    trip_id: UUID = Field(..., description="Trip id (UUID)")
    destination_id: Optional[UUID] = Field(None, description="Destination id (UUID)")
    name: str = Field(..., description="Name")
    address: Optional[str] = Field(None, description="Address")
    check_in: Optional[datetime] = Field(None, description="Check-in datetime")
    check_out: Optional[datetime] = Field(None, description="Check-out datetime")
    confirmation_number: Optional[str] = Field(None, description="Confirmation number")
    booking_url: Optional[str] = Field(None, description="Booking URL")
    phone: Optional[str] = Field(None, description="Phone")
    notes: Optional[str] = Field(None, description="Notes")
    created_at: datetime = Field(..., description="Created timestamp")

    class Config:
        from_attributes = True


class ActivityCreate(BaseModel):
    """Create activity."""

    destination_id: Optional[UUID] = Field(None, description="Optional destination id")
    day_id: Optional[UUID] = Field(None, description="Optional itinerary day id")
    name: str = Field(..., description="Activity name", examples=["TeamLab Planets"])
    start_time: Optional[datetime] = Field(None, description="Start time")
    end_time: Optional[datetime] = Field(None, description="End time")
    location: Optional[str] = Field(None, description="Location")
    booking_url: Optional[str] = Field(None, description="Booking URL")
    cost: Optional[float] = Field(None, description="Estimated cost")
    notes: Optional[str] = Field(None, description="Notes")


class ActivityOut(BaseModel):
    """Activity returned by API."""

    id: UUID = Field(..., description="Activity id (UUID)")
    trip_id: UUID = Field(..., description="Trip id (UUID)")
    destination_id: Optional[UUID] = Field(None, description="Destination id (UUID)")
    day_id: Optional[UUID] = Field(None, description="Day id (UUID)")
    name: str = Field(..., description="Name")
    start_time: Optional[datetime] = Field(None, description="Start time")
    end_time: Optional[datetime] = Field(None, description="End time")
    location: Optional[str] = Field(None, description="Location")
    booking_url: Optional[str] = Field(None, description="Booking URL")
    cost: Optional[float] = Field(None, description="Cost")
    notes: Optional[str] = Field(None, description="Notes")
    created_at: datetime = Field(..., description="Created timestamp")

    class Config:
        from_attributes = True


class NoteCreate(BaseModel):
    """Create note."""

    destination_id: Optional[UUID] = Field(None, description="Optional destination id")
    day_id: Optional[UUID] = Field(None, description="Optional day id")
    title: Optional[str] = Field(None, description="Note title")
    content: str = Field(..., description="Note content")


class NoteOut(BaseModel):
    """Note returned by API."""

    id: UUID = Field(..., description="Note id (UUID)")
    trip_id: UUID = Field(..., description="Trip id (UUID)")
    destination_id: Optional[UUID] = Field(None, description="Destination id (UUID)")
    day_id: Optional[UUID] = Field(None, description="Day id (UUID)")
    title: Optional[str] = Field(None, description="Title")
    content: str = Field(..., description="Content")
    created_at: datetime = Field(..., description="Created timestamp")
    updated_at: datetime = Field(..., description="Updated timestamp")

    class Config:
        from_attributes = True


# -----------------------
# Budget tracker
# -----------------------


class BudgetCategoryCreate(BaseModel):
    """Create a budget category for a trip."""

    name: str = Field(..., description="Category name", examples=["Food"])
    planned_amount: float = Field(0, description="Planned budget for this category")
    color: Optional[str] = Field(None, description="Optional color hint (hex or label)", examples=["#3b82f6"])


class BudgetCategoryUpdate(BaseModel):
    """Update a budget category."""

    name: Optional[str] = Field(None, description="Category name")
    planned_amount: Optional[float] = Field(None, description="Planned budget for this category")
    color: Optional[str] = Field(None, description="Optional color hint")


class BudgetCategoryOut(BaseModel):
    """Budget category returned by API."""

    id: UUID = Field(..., description="Category id (UUID)")
    trip_id: UUID = Field(..., description="Trip id (UUID)")
    name: str = Field(..., description="Category name")
    planned_amount: float = Field(..., description="Planned amount")
    color: Optional[str] = Field(None, description="Color hint")
    created_at: datetime = Field(..., description="Created timestamp")
    updated_at: datetime = Field(..., description="Updated timestamp")

    class Config:
        from_attributes = True


class BudgetExpenseCreate(BaseModel):
    """Create a budget expense row."""

    category_id: Optional[UUID] = Field(None, description="Optional budget category id")
    amount: float = Field(..., description="Expense amount (positive number)")
    currency_code: Optional[str] = Field(
        None,
        description="Expense currency (ISO-4217). If omitted, the trip currency is implied.",
        examples=["USD", "EUR", "JPY"],
    )
    spent_on: Optional[date] = Field(None, description="Date expense was incurred")
    description: Optional[str] = Field(None, description="Short description", examples=["Ramen dinner"])

    @field_validator("currency_code")
    @classmethod
    def validate_currency_code(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return None
        return _normalize_currency_code(v)


class BudgetExpenseOut(BaseModel):
    """Budget expense returned by API."""

    id: UUID = Field(..., description="Expense id (UUID)")
    trip_id: UUID = Field(..., description="Trip id (UUID)")
    category_id: Optional[UUID] = Field(None, description="Category id (UUID)")
    category_name: Optional[str] = Field(None, description="Category name (denormalized for convenience)")
    amount: float = Field(..., description="Amount")
    currency_code: Optional[str] = Field(None, description="Expense currency (ISO-4217); if null, trip currency is implied")
    spent_on: Optional[date] = Field(None, description="Spent on date")
    description: Optional[str] = Field(None, description="Description")
    created_at: datetime = Field(..., description="Created timestamp")

    class Config:
        from_attributes = True


class BudgetCategorySummary(BaseModel):
    """Summary numbers for a single category."""

    id: UUID = Field(..., description="Category id (UUID)")
    name: str = Field(..., description="Category name")
    planned_amount: float = Field(..., description="Planned amount")
    actual_amount: float = Field(..., description="Actual spend for this category")
    remaining_amount: float = Field(..., description="Planned minus actual (negative means over budget)")


class BudgetTotals(BaseModel):
    """Overall totals for a trip budget."""

    planned_total: float = Field(..., description="Sum of planned category amounts")
    actual_total: float = Field(..., description="Sum of all expenses")
    remaining_total: float = Field(..., description="Planned minus actual")


class BudgetSummaryOut(BaseModel):
    """Budget summary response."""

    trip_id: UUID = Field(..., description="Trip id (UUID)")
    totals: BudgetTotals = Field(..., description="Budget totals")
    by_category: list[BudgetCategorySummary] = Field(..., description="Per-category breakdown")

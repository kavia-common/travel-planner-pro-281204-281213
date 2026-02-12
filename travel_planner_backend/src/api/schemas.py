"""
Pydantic schemas for the Travel Planner API.

These schemas are used for request validation and response serialization.
"""

from __future__ import annotations

from datetime import date, datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field


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


class TripCreate(BaseModel):
    """Create a trip."""

    user_id: UUID = Field(..., description="Owner user id (UUID)")
    name: str = Field(..., description="Trip name", examples=["Japan Spring 2026"])
    start_date: Optional[date] = Field(None, description="Trip start date")
    end_date: Optional[date] = Field(None, description="Trip end date")


class TripUpdate(BaseModel):
    """Update a trip."""

    name: Optional[str] = Field(None, description="Trip name")
    start_date: Optional[date] = Field(None, description="Trip start date")
    end_date: Optional[date] = Field(None, description="Trip end date")


class TripOut(BaseModel):
    """Trip returned by the API."""

    id: UUID = Field(..., description="Trip id (UUID)")
    user_id: UUID = Field(..., description="Owner user id (UUID)")
    name: str = Field(..., description="Trip name")
    start_date: Optional[date] = Field(None, description="Trip start date")
    end_date: Optional[date] = Field(None, description="Trip end date")
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

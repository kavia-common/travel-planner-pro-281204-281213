"""
SQLAlchemy ORM models for the Travel Planner app.
"""

from __future__ import annotations

import uuid
from datetime import date, datetime
from typing import Optional

from sqlalchemy import Date, DateTime, ForeignKey, Integer, Numeric, String, Text, UniqueConstraint, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    """Base class for SQLAlchemy models."""


class User(Base):
    """Application user."""

    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email: Mapped[str] = mapped_column(Text, unique=True, nullable=False)
    full_name: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    trips: Mapped[list["Trip"]] = relationship(back_populates="user", cascade="all, delete-orphan")


class Trip(Base):
    """A trip owned by a user."""

    __tablename__ = "trips"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)

    name: Mapped[str] = mapped_column(Text, nullable=False)
    start_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    end_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    home_timezone: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Trip-wide base currency (ISO-4217), used for all planned budgets and as the default for expenses.
    currency_code: Mapped[str] = mapped_column(String(3), nullable=False, default="USD")

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    user: Mapped["User"] = relationship(back_populates="trips")
    destinations: Mapped[list["TripDestination"]] = relationship(back_populates="trip", cascade="all, delete-orphan")
    days: Mapped[list["ItineraryDay"]] = relationship(back_populates="trip", cascade="all, delete-orphan")
    accommodations: Mapped[list["Accommodation"]] = relationship(back_populates="trip", cascade="all, delete-orphan")
    activities: Mapped[list["Activity"]] = relationship(back_populates="trip", cascade="all, delete-orphan")
    notes: Mapped[list["Note"]] = relationship(back_populates="trip", cascade="all, delete-orphan")

    budget_categories: Mapped[list["BudgetCategory"]] = relationship(back_populates="trip", cascade="all, delete-orphan")
    budget_expenses: Mapped[list["BudgetExpense"]] = relationship(back_populates="trip", cascade="all, delete-orphan")


class TripDestination(Base):
    """Destination attached to a trip."""

    __tablename__ = "trip_destinations"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    trip_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("trips.id", ondelete="CASCADE"), nullable=False)

    name: Mapped[str] = mapped_column(Text, nullable=False)
    country: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    start_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    end_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    sort_order: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    trip: Mapped["Trip"] = relationship(back_populates="destinations")


class ItineraryDay(Base):
    """A dated day within a trip itinerary."""

    __tablename__ = "itinerary_days"
    __table_args__ = (UniqueConstraint("trip_id", "day_date", name="uq_itinerary_days_trip_day_date"),)

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    trip_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("trips.id", ondelete="CASCADE"), nullable=False)

    day_date: Mapped[date] = mapped_column(Date, nullable=False)
    title: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    summary: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    trip: Mapped["Trip"] = relationship(back_populates="days")
    items: Mapped[list["ItineraryItem"]] = relationship(back_populates="day", cascade="all, delete-orphan")


class Accommodation(Base):
    """Accommodation entry for a trip."""

    __tablename__ = "accommodations"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    trip_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("trips.id", ondelete="CASCADE"), nullable=False)
    destination_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), ForeignKey("trip_destinations.id", ondelete="SET NULL"), nullable=True)

    name: Mapped[str] = mapped_column(Text, nullable=False)
    address: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    check_in: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    check_out: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    confirmation_number: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    booking_url: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    phone: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    trip: Mapped["Trip"] = relationship(back_populates="accommodations")


class Activity(Base):
    """Activity entry for a trip."""

    __tablename__ = "activities"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    trip_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("trips.id", ondelete="CASCADE"), nullable=False)
    destination_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), ForeignKey("trip_destinations.id", ondelete="SET NULL"), nullable=True)
    day_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), ForeignKey("itinerary_days.id", ondelete="SET NULL"), nullable=True)

    name: Mapped[str] = mapped_column(Text, nullable=False)
    start_time: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    end_time: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    location: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    booking_url: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    cost: Mapped[Optional[float]] = mapped_column(Numeric(12, 2), nullable=True)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    trip: Mapped["Trip"] = relationship(back_populates="activities")


class ItineraryItem(Base):
    """A scheduled item within a specific itinerary day."""

    __tablename__ = "itinerary_items"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    day_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("itinerary_days.id", ondelete="CASCADE"), nullable=False)

    item_type: Mapped[str] = mapped_column(String(32), nullable=False)  # activity, accommodation, custom
    title: Mapped[str] = mapped_column(Text, nullable=False)
    start_time: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    end_time: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    activity_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), ForeignKey("activities.id", ondelete="SET NULL"), nullable=True)
    accommodation_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), ForeignKey("accommodations.id", ondelete="SET NULL"), nullable=True)

    details: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    sort_order: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    day: Mapped["ItineraryDay"] = relationship(back_populates="items")


class Note(Base):
    """Free-form note for a trip."""

    __tablename__ = "notes"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    trip_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("trips.id", ondelete="CASCADE"), nullable=False)
    destination_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), ForeignKey("trip_destinations.id", ondelete="SET NULL"), nullable=True)
    day_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), ForeignKey("itinerary_days.id", ondelete="SET NULL"), nullable=True)

    title: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    trip: Mapped["Trip"] = relationship(back_populates="notes")


class BudgetCategory(Base):
    """Planned budget category (per trip)."""

    __tablename__ = "budget_categories"
    __table_args__ = (UniqueConstraint("trip_id", "name", name="uq_budget_categories_trip_name"),)

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    trip_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("trips.id", ondelete="CASCADE"), nullable=False)

    name: Mapped[str] = mapped_column(Text, nullable=False)
    planned_amount: Mapped[float] = mapped_column(Numeric(12, 2), nullable=False, default=0)
    color: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    trip: Mapped["Trip"] = relationship(back_populates="budget_categories")
    expenses: Mapped[list["BudgetExpense"]] = relationship(
        back_populates="category", cascade="save-update, merge", passive_deletes=True
    )


class BudgetExpense(Base):
    """Actual expense row (per trip), optionally categorized."""

    __tablename__ = "budget_expenses"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    trip_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("trips.id", ondelete="CASCADE"), nullable=False)
    category_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("budget_categories.id", ondelete="SET NULL"), nullable=True
    )

    amount: Mapped[float] = mapped_column(Numeric(12, 2), nullable=False)

    # Optional expense currency (ISO-4217). If NULL, the trip currency is implied.
    currency_code: Mapped[Optional[str]] = mapped_column(String(3), nullable=True)

    spent_on: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    trip: Mapped["Trip"] = relationship(back_populates="budget_expenses")
    category: Mapped[Optional["BudgetCategory"]] = relationship(back_populates="expenses")

"""
Travel Planner Backend API (FastAPI).

Provides REST endpoints for:
- Users
- Trips
- Destinations
- Itinerary (days + items)
- Accommodations
- Activities
- Notes

Environment variables:
- ALLOWED_ORIGINS: comma-separated list of allowed origins for CORS.
- POSTGRES_URL: SQLAlchemy/PostgreSQL connection URL.

Returns:
- JSON responses with Pydantic-validated models.
"""

from __future__ import annotations

import os
from typing import List
from uuid import UUID

from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from .db import get_db_session
from .models import Activity, Accommodation, Base, ItineraryDay, Note, Trip, TripDestination, User
from .schemas import (
    AccommodationCreate,
    AccommodationOut,
    ActivityCreate,
    ActivityOut,
    ApiMessage,
    DayCreate,
    DayOut,
    DestinationCreate,
    DestinationOut,
    NoteCreate,
    NoteOut,
    TripCreate,
    TripOut,
    TripUpdate,
    UserCreate,
    UserOut,
)

openapi_tags = [
    {"name": "Health", "description": "Service health checks"},
    {"name": "Users", "description": "User management (simple template; no auth)"},
    {"name": "Trips", "description": "Trip CRUD"},
    {"name": "Destinations", "description": "Destinations within a trip"},
    {"name": "Itinerary", "description": "Itinerary days for a trip"},
    {"name": "Accommodations", "description": "Lodging tracking"},
    {"name": "Activities", "description": "Activities tracking"},
    {"name": "Notes", "description": "Travel notes"},
]


def _get_allowed_origins() -> List[str]:
    """Parse ALLOWED_ORIGINS env var."""
    raw = os.getenv("ALLOWED_ORIGINS", "*")
    if raw.strip() == "*":
        return ["*"]
    return [o.strip() for o in raw.split(",") if o.strip()]


app = FastAPI(
    title="Travel Planner API",
    description="API for a travel planner app (trips, destinations, itinerary, accommodations, activities, notes).",
    version="0.1.0",
    openapi_tags=openapi_tags,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=_get_allowed_origins(),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get(
    "/",
    tags=["Health"],
    summary="Health check",
    response_model=ApiMessage,
    operation_id="health_check",
)
def health_check() -> ApiMessage:
    """Health check endpoint."""
    return ApiMessage(message="Healthy")


# -----------------------
# Users
# -----------------------

# PUBLIC_INTERFACE
@app.post(
    "/users",
    tags=["Users"],
    summary="Create user",
    response_model=UserOut,
    status_code=status.HTTP_201_CREATED,
    operation_id="create_user",
)
def create_user(payload: UserCreate, db: Session = Depends(get_db_session)) -> UserOut:
    """
    Create a user.

    Note: This template does not implement authentication; the frontend uses a local 'current user'
    concept and creates a user on demand.
    """
    user = User(email=payload.email, full_name=payload.full_name)
    db.add(user)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail="Email already exists")
    db.refresh(user)
    return user


# PUBLIC_INTERFACE
@app.get(
    "/users",
    tags=["Users"],
    summary="List users",
    response_model=list[UserOut],
    operation_id="list_users",
)
def list_users(db: Session = Depends(get_db_session)) -> list[UserOut]:
    """List users."""
    return list(db.scalars(select(User).order_by(User.created_at.desc())).all())


# -----------------------
# Trips
# -----------------------

# PUBLIC_INTERFACE
@app.post(
    "/trips",
    tags=["Trips"],
    summary="Create trip",
    response_model=TripOut,
    status_code=status.HTTP_201_CREATED,
    operation_id="create_trip",
)
def create_trip(payload: TripCreate, db: Session = Depends(get_db_session)) -> TripOut:
    """Create a trip for a user."""
    # validate user exists
    user = db.get(User, payload.user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    trip = Trip(
        user_id=payload.user_id,
        name=payload.name,
        start_date=payload.start_date,
        end_date=payload.end_date,
    )
    db.add(trip)
    db.commit()
    db.refresh(trip)
    return trip


# PUBLIC_INTERFACE
@app.get(
    "/trips",
    tags=["Trips"],
    summary="List trips (optionally filter by user_id)",
    response_model=list[TripOut],
    operation_id="list_trips",
)
def list_trips(user_id: UUID | None = None, db: Session = Depends(get_db_session)) -> list[TripOut]:
    """List trips; if user_id provided, returns trips for that user only."""
    stmt = select(Trip).order_by(Trip.created_at.desc())
    if user_id:
        stmt = stmt.where(Trip.user_id == user_id)
    return list(db.scalars(stmt).all())


# PUBLIC_INTERFACE
@app.get(
    "/trips/{trip_id}",
    tags=["Trips"],
    summary="Get trip",
    response_model=TripOut,
    operation_id="get_trip",
)
def get_trip(trip_id: UUID, db: Session = Depends(get_db_session)) -> TripOut:
    """Get a trip by id."""
    trip = db.get(Trip, trip_id)
    if not trip:
        raise HTTPException(status_code=404, detail="Trip not found")
    return trip


# PUBLIC_INTERFACE
@app.patch(
    "/trips/{trip_id}",
    tags=["Trips"],
    summary="Update trip",
    response_model=TripOut,
    operation_id="update_trip",
)
def update_trip(trip_id: UUID, payload: TripUpdate, db: Session = Depends(get_db_session)) -> TripOut:
    """Update a trip."""
    trip = db.get(Trip, trip_id)
    if not trip:
        raise HTTPException(status_code=404, detail="Trip not found")

    if payload.name is not None:
        trip.name = payload.name
    if payload.start_date is not None:
        trip.start_date = payload.start_date
    if payload.end_date is not None:
        trip.end_date = payload.end_date

    db.add(trip)
    db.commit()
    db.refresh(trip)
    return trip


# PUBLIC_INTERFACE
@app.delete(
    "/trips/{trip_id}",
    tags=["Trips"],
    summary="Delete trip",
    response_model=ApiMessage,
    operation_id="delete_trip",
)
def delete_trip(trip_id: UUID, db: Session = Depends(get_db_session)) -> ApiMessage:
    """Delete a trip and all associated data."""
    trip = db.get(Trip, trip_id)
    if not trip:
        raise HTTPException(status_code=404, detail="Trip not found")
    db.delete(trip)
    db.commit()
    return ApiMessage(message="Trip deleted")


# -----------------------
# Destinations
# -----------------------

# PUBLIC_INTERFACE
@app.post(
    "/trips/{trip_id}/destinations",
    tags=["Destinations"],
    summary="Add destination to trip",
    response_model=DestinationOut,
    status_code=status.HTTP_201_CREATED,
    operation_id="add_destination",
)
def add_destination(trip_id: UUID, payload: DestinationCreate, db: Session = Depends(get_db_session)) -> DestinationOut:
    """Add a destination to a trip."""
    trip = db.get(Trip, trip_id)
    if not trip:
        raise HTTPException(status_code=404, detail="Trip not found")

    dest = TripDestination(
        trip_id=trip_id,
        name=payload.name,
        country=payload.country,
        start_date=payload.start_date,
        end_date=payload.end_date,
        sort_order=payload.sort_order,
    )
    db.add(dest)
    db.commit()
    db.refresh(dest)
    return dest


# PUBLIC_INTERFACE
@app.get(
    "/trips/{trip_id}/destinations",
    tags=["Destinations"],
    summary="List destinations for trip",
    response_model=list[DestinationOut],
    operation_id="list_destinations",
)
def list_destinations(trip_id: UUID, db: Session = Depends(get_db_session)) -> list[DestinationOut]:
    """List destinations for a trip."""
    trip = db.get(Trip, trip_id)
    if not trip:
        raise HTTPException(status_code=404, detail="Trip not found")
    stmt = select(TripDestination).where(TripDestination.trip_id == trip_id).order_by(TripDestination.sort_order.asc())
    return list(db.scalars(stmt).all())


# -----------------------
# Itinerary (Days)
# -----------------------

# PUBLIC_INTERFACE
@app.post(
    "/trips/{trip_id}/itinerary/days",
    tags=["Itinerary"],
    summary="Create itinerary day",
    response_model=DayOut,
    status_code=status.HTTP_201_CREATED,
    operation_id="create_itinerary_day",
)
def create_itinerary_day(trip_id: UUID, payload: DayCreate, db: Session = Depends(get_db_session)) -> DayOut:
    """Create an itinerary day for a trip."""
    trip = db.get(Trip, trip_id)
    if not trip:
        raise HTTPException(status_code=404, detail="Trip not found")

    day = ItineraryDay(trip_id=trip_id, day_date=payload.day_date, title=payload.title, summary=payload.summary)
    db.add(day)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail="Itinerary day already exists for this date")
    db.refresh(day)
    return day


# PUBLIC_INTERFACE
@app.get(
    "/trips/{trip_id}/itinerary/days",
    tags=["Itinerary"],
    summary="List itinerary days",
    response_model=list[DayOut],
    operation_id="list_itinerary_days",
)
def list_itinerary_days(trip_id: UUID, db: Session = Depends(get_db_session)) -> list[DayOut]:
    """List itinerary days for a trip."""
    trip = db.get(Trip, trip_id)
    if not trip:
        raise HTTPException(status_code=404, detail="Trip not found")
    stmt = select(ItineraryDay).where(ItineraryDay.trip_id == trip_id).order_by(ItineraryDay.day_date.asc())
    return list(db.scalars(stmt).all())


# -----------------------
# Accommodations
# -----------------------

# PUBLIC_INTERFACE
@app.post(
    "/trips/{trip_id}/accommodations",
    tags=["Accommodations"],
    summary="Create accommodation",
    response_model=AccommodationOut,
    status_code=status.HTTP_201_CREATED,
    operation_id="create_accommodation",
)
def create_accommodation(
    trip_id: UUID, payload: AccommodationCreate, db: Session = Depends(get_db_session)
) -> AccommodationOut:
    """Create accommodation for a trip."""
    trip = db.get(Trip, trip_id)
    if not trip:
        raise HTTPException(status_code=404, detail="Trip not found")

    acc = Accommodation(trip_id=trip_id, **payload.model_dump())
    db.add(acc)
    db.commit()
    db.refresh(acc)
    return acc


# PUBLIC_INTERFACE
@app.get(
    "/trips/{trip_id}/accommodations",
    tags=["Accommodations"],
    summary="List accommodations",
    response_model=list[AccommodationOut],
    operation_id="list_accommodations",
)
def list_accommodations(trip_id: UUID, db: Session = Depends(get_db_session)) -> list[AccommodationOut]:
    """List accommodations for a trip."""
    trip = db.get(Trip, trip_id)
    if not trip:
        raise HTTPException(status_code=404, detail="Trip not found")
    stmt = select(Accommodation).where(Accommodation.trip_id == trip_id).order_by(Accommodation.created_at.desc())
    return list(db.scalars(stmt).all())


# -----------------------
# Activities
# -----------------------

# PUBLIC_INTERFACE
@app.post(
    "/trips/{trip_id}/activities",
    tags=["Activities"],
    summary="Create activity",
    response_model=ActivityOut,
    status_code=status.HTTP_201_CREATED,
    operation_id="create_activity",
)
def create_activity(trip_id: UUID, payload: ActivityCreate, db: Session = Depends(get_db_session)) -> ActivityOut:
    """Create an activity for a trip."""
    trip = db.get(Trip, trip_id)
    if not trip:
        raise HTTPException(status_code=404, detail="Trip not found")

    act = Activity(trip_id=trip_id, **payload.model_dump())
    db.add(act)
    db.commit()
    db.refresh(act)
    return act


# PUBLIC_INTERFACE
@app.get(
    "/trips/{trip_id}/activities",
    tags=["Activities"],
    summary="List activities",
    response_model=list[ActivityOut],
    operation_id="list_activities",
)
def list_activities(trip_id: UUID, db: Session = Depends(get_db_session)) -> list[ActivityOut]:
    """List activities for a trip."""
    trip = db.get(Trip, trip_id)
    if not trip:
        raise HTTPException(status_code=404, detail="Trip not found")
    stmt = select(Activity).where(Activity.trip_id == trip_id).order_by(Activity.created_at.desc())
    return list(db.scalars(stmt).all())


# -----------------------
# Notes
# -----------------------

# PUBLIC_INTERFACE
@app.post(
    "/trips/{trip_id}/notes",
    tags=["Notes"],
    summary="Create note",
    response_model=NoteOut,
    status_code=status.HTTP_201_CREATED,
    operation_id="create_note",
)
def create_note(trip_id: UUID, payload: NoteCreate, db: Session = Depends(get_db_session)) -> NoteOut:
    """Create a note for a trip."""
    trip = db.get(Trip, trip_id)
    if not trip:
        raise HTTPException(status_code=404, detail="Trip not found")

    note = Note(trip_id=trip_id, **payload.model_dump())
    db.add(note)
    db.commit()
    db.refresh(note)
    return note


# PUBLIC_INTERFACE
@app.get(
    "/trips/{trip_id}/notes",
    tags=["Notes"],
    summary="List notes",
    response_model=list[NoteOut],
    operation_id="list_notes",
)
def list_notes(trip_id: UUID, db: Session = Depends(get_db_session)) -> list[NoteOut]:
    """List notes for a trip."""
    trip = db.get(Trip, trip_id)
    if not trip:
        raise HTTPException(status_code=404, detail="Trip not found")
    stmt = select(Note).where(Note.trip_id == trip_id).order_by(Note.updated_at.desc(), Note.created_at.desc())
    return list(db.scalars(stmt).all())

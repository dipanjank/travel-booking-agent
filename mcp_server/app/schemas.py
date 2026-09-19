import datetime as dt
from typing import Literal

from pydantic import BaseModel, Field

# --- Search tool schemas ---


class FlightSearchRequest(BaseModel):
    origin: str = Field(..., pattern=r"^[A-Z]{3}$", description="Departure airport IATA code")
    destination: str = Field(..., pattern=r"^[A-Z]{3}$", description="Arrival airport IATA code")
    date: dt.date | None = Field(None, description="Departure date")
    time_of_day: Literal["morning", "afternoon", "evening"] | None = None
    airline: str | None = Field(
        None,
        pattern=r"^[A-Z0-9]{2}$",
        description="Airline IATA code. Matches routes with at least one leg by this airline.",
    )
    max_price: float | None = Field(None, gt=0)
    max_stops: int | None = Field(None, ge=0)
    cabin_class: Literal["economy", "business", "first"] | None = Field(
        None,
        description="Matches routes with at least one leg in this cabin class."
        " Connecting routes may mix cabin classes.",
    )


class FlightLeg(BaseModel):
    flight_number: str
    airline: str
    departure_airport: str
    arrival_airport: str
    departure_time: dt.datetime
    arrival_time: dt.datetime
    duration_minutes: int
    cabin_class: str


class FlightSearchResult(BaseModel):
    route_id: int
    legs: list[FlightLeg]
    total_duration_minutes: int
    num_stops: int
    total_price: float


# --- Booking tool schemas ---


class PassengerDetails(BaseModel):
    name: str = Field(..., min_length=1)
    date_of_birth: dt.date
    passport_number: str = Field(..., min_length=5)


class BookingRequest(BaseModel):
    route_id: int
    passengers: list[PassengerDetails] = Field(..., min_length=1)
    contact_email: str = Field(..., pattern=r"^[^@]+@[^@]+\.[^@]+$")
    contact_phone: str


class BookingConfirmation(BaseModel):
    pnr: str
    route_id: int
    legs: list[FlightLeg]
    passengers: list[PassengerDetails]
    total_price: float
    status: str
    booked_at: dt.datetime

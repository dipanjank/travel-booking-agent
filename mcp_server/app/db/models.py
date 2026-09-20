from sqlalchemy import Column, DateTime, ForeignKey, Integer, Numeric, String, func
from sqlalchemy.orm import DeclarativeBase, relationship


class Base(DeclarativeBase):
    pass


class Airport(Base):
    __tablename__ = "airports"

    iata_code = Column(String(3), primary_key=True)
    name = Column(String(255), nullable=False)
    city = Column(String(255), nullable=False)
    country = Column(String(100), nullable=False)
    timezone = Column(String(50), nullable=False)


class Airline(Base):
    __tablename__ = "airlines"

    iata_code = Column(String(2), primary_key=True)
    name = Column(String(255), nullable=False)


class Flight(Base):
    __tablename__ = "flights"

    flight_id = Column(Integer, primary_key=True, autoincrement=True)
    airline_code = Column(String(2), ForeignKey("airlines.iata_code"), nullable=False)
    flight_number = Column(String(10), nullable=False)
    departure_airport = Column(String(3), ForeignKey("airports.iata_code"), nullable=False)
    arrival_airport = Column(String(3), ForeignKey("airports.iata_code"), nullable=False)
    departure_time = Column(DateTime(timezone=True), nullable=False)
    arrival_time = Column(DateTime(timezone=True), nullable=False)
    duration_minutes = Column(Integer, nullable=False)
    cabin_class = Column(String(20), nullable=False)
    base_price = Column(Numeric(10, 2), nullable=False)
    available_seats = Column(Integer, nullable=False)

    airline = relationship("Airline", lazy="joined")


class Route(Base):
    __tablename__ = "routes"

    route_id = Column(Integer, primary_key=True, autoincrement=True)
    departure_airport = Column(String(3), ForeignKey("airports.iata_code"), nullable=False)
    arrival_airport = Column(String(3), ForeignKey("airports.iata_code"), nullable=False)
    total_duration = Column(Integer, nullable=False)
    total_price = Column(Numeric(10, 2), nullable=False)
    num_stops = Column(Integer, nullable=False)

    route_flights = relationship("RouteFlight", order_by="RouteFlight.leg_order", lazy="joined")


class RouteFlight(Base):
    __tablename__ = "route_flights"

    route_id = Column(Integer, ForeignKey("routes.route_id"), primary_key=True)
    flight_id = Column(Integer, ForeignKey("flights.flight_id"))
    leg_order = Column(Integer, primary_key=True)

    flight = relationship("Flight", lazy="joined")


class Booking(Base):
    __tablename__ = "bookings"

    booking_id = Column(Integer, primary_key=True, autoincrement=True)
    pnr = Column(String(6), unique=True, nullable=False)
    route_id = Column(Integer, ForeignKey("routes.route_id"), nullable=False)
    user_id = Column(String(36), nullable=False)
    booked_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    status = Column(String(20), nullable=False, server_default="CONFIRMED")

    route = relationship("Route", lazy="joined")

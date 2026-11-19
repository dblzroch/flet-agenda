"""Domain models for flet-agenda."""

from dataclasses import dataclass


@dataclass
class Client:
    """A client."""

    id: int | None = None
    name: str = ""
    phone: str = ""
    email: str = ""


@dataclass
class Professional:
    """A service professional."""

    id: int | None = None
    name: str = ""
    specialty: str = ""


@dataclass
class Appointment:
    """An appointment."""

    id: int | None = None
    client_id: int = 0
    professional_id: int = 0
    starts_at: str = ""  # ISO datetime
    ends_at: str = ""  # ISO datetime
    status: str = "scheduled"  # scheduled, confirmed, completed, cancelled
    notes: str = ""


@dataclass
class Payment:
    """A payment for an appointment."""

    id: int | None = None
    appointment_id: int = 0
    amount: float = 0.0
    paid_at: str = ""  # ISO datetime
    method: str = "cash"  # cash, card, pix

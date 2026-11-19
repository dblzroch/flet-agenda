"""Tests for flet-agenda database and models."""

from py_flet_agenda.database import Database
from py_flet_agenda.models import Appointment, Client, Payment, Professional


# ------------------------------------------------------------------
# Models
# ------------------------------------------------------------------
def test_client_defaults():
    c = Client(name="Ana", phone="11999999999", email="ana@email.com")
    assert c.name == "Ana"
    assert c.phone == "11999999999"
    assert c.email == "ana@email.com"
    assert c.id is None


def test_professional_defaults():
    p = Professional(name="Maria", specialty="Cabelo")
    assert p.name == "Maria"
    assert p.specialty == "Cabelo"
    assert p.id is None


def test_appointment_defaults():
    a = Appointment(
        client_id=1,
        professional_id=1,
        starts_at="2024-01-15T10:00:00",
        ends_at="2024-01-15T10:30:00",
    )
    assert a.client_id == 1
    assert a.professional_id == 1
    assert a.status == "scheduled"
    assert a.id is None


def test_payment_defaults():
    p = Payment(appointment_id=1, amount=150.0, method="pix")
    assert p.appointment_id == 1
    assert p.amount == 150.0
    assert p.method == "pix"
    assert p.id is None


# ------------------------------------------------------------------
# Database: clients
# ------------------------------------------------------------------
def test_add_and_get_client(tmp_path):
    db = Database(tmp_path / "test.db")
    rid = db.add_client(Client(name="Ana", phone="11999999999"))
    assert rid == 1

    clients = db.get_clients()
    assert len(clients) == 1
    assert clients[0].name == "Ana"


# ------------------------------------------------------------------
# Database: professionals
# ------------------------------------------------------------------
def test_add_and_get_professional(tmp_path):
    db = Database(tmp_path / "test.db")
    rid = db.add_professional(Professional(name="Maria", specialty="Cabelo"))
    assert rid == 1

    pros = db.get_professionals()
    assert len(pros) == 1
    assert pros[0].name == "Maria"


# ------------------------------------------------------------------
# Database: appointments
# ------------------------------------------------------------------
def test_add_and_get_appointment(tmp_path):
    db = Database(tmp_path / "test.db")
    db.add_client(Client(name="Ana", phone="11999999999"))
    db.add_professional(Professional(name="Maria", specialty="Cabelo"))

    rid = db.add_appointment(
        Appointment(
            client_id=1,
            professional_id=1,
            starts_at="2024-01-15T10:00:00",
            ends_at="2024-01-15T10:30:00",
        )
    )
    assert rid == 1

    apps = db.get_appointments()
    assert len(apps) == 1
    assert apps[0].status == "scheduled"


def test_get_appointments_by_date(tmp_path):
    db = Database(tmp_path / "test.db")
    db.add_client(Client(name="Ana", phone="11999999999"))
    db.add_professional(Professional(name="Maria", specialty="Cabelo"))

    db.add_appointment(
        Appointment(
            client_id=1,
            professional_id=1,
            starts_at="2024-01-15T10:00:00",
            ends_at="2024-01-15T10:30:00",
        )
    )
    db.add_appointment(
        Appointment(
            client_id=1,
            professional_id=1,
            starts_at="2024-01-16T10:00:00",
            ends_at="2024-01-16T10:30:00",
        )
    )

    jan15 = db.get_appointments_by_date("2024-01-15")
    assert len(jan15) == 1
    assert jan15[0].starts_at.startswith("2024-01-15")


def test_confirm_appointment(tmp_path):
    db = Database(tmp_path / "test.db")
    db.add_client(Client(name="Ana", phone="11999999999"))
    db.add_professional(Professional(name="Maria", specialty="Cabelo"))
    rid = db.add_appointment(
        Appointment(
            client_id=1,
            professional_id=1,
            starts_at="2024-01-15T10:00:00",
            ends_at="2024-01-15T10:30:00",
        )
    )

    assert db.confirm_appointment(rid) is True
    apps = db.get_appointments()
    assert apps[0].status == "confirmed"


def test_delete_appointment(tmp_path):
    db = Database(tmp_path / "test.db")
    db.add_client(Client(name="Ana", phone="11999999999"))
    db.add_professional(Professional(name="Maria", specialty="Cabelo"))
    rid = db.add_appointment(
        Appointment(
            client_id=1,
            professional_id=1,
            starts_at="2024-01-15T10:00:00",
            ends_at="2024-01-15T10:30:00",
        )
    )

    assert db.delete_appointment(rid) is True
    assert db.get_appointments() == []


# ------------------------------------------------------------------
# Database: payments and revenue
# ------------------------------------------------------------------
def test_add_payment_and_revenue(tmp_path):
    db = Database(tmp_path / "test.db")
    db.add_client(Client(name="Ana", phone="11999999999"))
    db.add_professional(Professional(name="Maria", specialty="Cabelo"))
    ap_id = db.add_appointment(
        Appointment(
            client_id=1,
            professional_id=1,
            starts_at="2024-01-15T10:00:00",
            ends_at="2024-01-15T10:30:00",
        )
    )

    db.add_payment(Payment(appointment_id=ap_id, amount=150.0, method="pix"))

    rev = db.revenue_by_professional(1)
    assert rev == 150.0


# ------------------------------------------------------------------
# CLI
# ------------------------------------------------------------------
def test_cli_main(monkeypatch):
    """Test that cli.main calls ft.app with the right target."""
    import py_flet_agenda.cli as cli_mod

    called = {}

    def fake_app(target):
        called["target"] = target

    monkeypatch.setattr(cli_mod, "ft_app", fake_app)
    cli_mod.main()
    assert callable(called.get("target"))

"""Database layer for flet-agenda."""

import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Self

from py_flet_agenda.models import Appointment, Client, Payment, Professional


class Database:
    """SQLite storage for clients, professionals, appointments and payments."""

    def __init__(self: Self, db_path: Path) -> None:
        self.db_path = db_path
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.conn = sqlite3.connect(str(db_path))
        self.conn.row_factory = sqlite3.Row
        self.conn.execute("PRAGMA foreign_keys = ON")
        self._init_schema()

    def _init_schema(self: Self) -> None:
        """Create tables if they don't exist."""
        self.conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS clients (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                phone TEXT,
                email TEXT
            );
            CREATE TABLE IF NOT EXISTS professionals (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                specialty TEXT
            );
            CREATE TABLE IF NOT EXISTS appointments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                client_id INTEGER NOT NULL,
                professional_id INTEGER NOT NULL,
                starts_at TEXT NOT NULL,
                ends_at TEXT NOT NULL,
                status TEXT NOT NULL DEFAULT 'scheduled',
                notes TEXT DEFAULT '',
                FOREIGN KEY(client_id) REFERENCES clients(id) ON DELETE CASCADE,
                FOREIGN KEY(professional_id)
                REFERENCES professionals(id) ON DELETE CASCADE
            );
            CREATE TABLE IF NOT EXISTS payments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                appointment_id INTEGER NOT NULL,
                amount REAL NOT NULL,
                paid_at TEXT NOT NULL,
                method TEXT NOT NULL DEFAULT 'cash',
                FOREIGN KEY(appointment_id)
                REFERENCES appointments(id) ON DELETE CASCADE
            );
            CREATE INDEX IF NOT EXISTS idx_appointments_professional
            ON appointments(professional_id, starts_at);
            CREATE INDEX IF NOT EXISTS idx_appointments_status
            ON appointments(status);
        """
        )
        self.conn.commit()

    def _now(self: Self) -> str:
        return datetime.now().isoformat()

    # --- Clients ---

    def add_client(self: Self, client: Client) -> int:
        cur = self.conn.execute(
            "INSERT INTO clients (name, phone, email) VALUES (?, ?, ?)",
            (client.name, client.phone, client.email),
        )
        self.conn.commit()
        last_id = cur.lastrowid
        assert last_id is not None
        return int(last_id)

    def get_clients(self: Self) -> list[Client]:
        rows = self.conn.execute(
            "SELECT id, name, phone, email FROM clients ORDER BY name"
        ).fetchall()
        return [
            Client(
                id=r["id"],
                name=r["name"],
                phone=r["phone"],
                email=r["email"],
            )
            for r in rows
        ]

    # --- Professionals ---

    def add_professional(self: Self, professional: Professional) -> int:
        cur = self.conn.execute(
            "INSERT INTO professionals (name, specialty) VALUES (?, ?)",
            (professional.name, professional.specialty),
        )
        self.conn.commit()
        last_id = cur.lastrowid
        assert last_id is not None
        return int(last_id)

    def get_professionals(self: Self) -> list[Professional]:
        rows = self.conn.execute(
            "SELECT id, name, specialty FROM professionals ORDER BY name"
        ).fetchall()
        return [
            Professional(
                id=r["id"],
                name=r["name"],
                specialty=r["specialty"],
            )
            for r in rows
        ]

    # --- Appointments ---

    def add_appointment(self: Self, appointment: Appointment) -> int:
        cur = self.conn.execute(
            """
            INSERT INTO appointments (client_id, professional_id, starts_at,
                                      ends_at, status, notes)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                appointment.client_id,
                appointment.professional_id,
                appointment.starts_at,
                appointment.ends_at,
                appointment.status,
                appointment.notes,
            ),
        )
        self.conn.commit()
        last_id = cur.lastrowid
        assert last_id is not None
        return int(last_id)

    def get_appointments(self: Self) -> list[Appointment]:
        rows = self.conn.execute(
            """
            SELECT id, client_id, professional_id, starts_at, ends_at, status, notes
            FROM appointments
            ORDER BY starts_at
            """
        ).fetchall()
        return [
            Appointment(
                id=r["id"],
                client_id=r["client_id"],
                professional_id=r["professional_id"],
                starts_at=r["starts_at"],
                ends_at=r["ends_at"],
                status=r["status"],
                notes=r["notes"],
            )
            for r in rows
        ]

    def get_appointments_by_professional(
        self: Self, professional_id: int
    ) -> list[Appointment]:
        rows = self.conn.execute(
            """
            SELECT id, client_id, professional_id, starts_at, ends_at, status, notes
            FROM appointments
            WHERE professional_id = ?
            ORDER BY starts_at
            """,
            (professional_id,),
        ).fetchall()
        return [
            Appointment(
                id=r["id"],
                client_id=r["client_id"],
                professional_id=r["professional_id"],
                starts_at=r["starts_at"],
                ends_at=r["ends_at"],
                status=r["status"],
                notes=r["notes"],
            )
            for r in rows
        ]

    def get_appointments_by_date(self: Self, date_str: str) -> list[Appointment]:
        rows = self.conn.execute(
            """
            SELECT id, client_id, professional_id, starts_at, ends_at, status, notes
            FROM appointments
            WHERE date(starts_at) = ?
            ORDER BY starts_at
            """,
            (date_str,),
        ).fetchall()
        return [
            Appointment(
                id=r["id"],
                client_id=r["client_id"],
                professional_id=r["professional_id"],
                starts_at=r["starts_at"],
                ends_at=r["ends_at"],
                status=r["status"],
                notes=r["notes"],
            )
            for r in rows
        ]

    def confirm_appointment(self: Self, appointment_id: int) -> bool:
        cur = self.conn.execute(
            "UPDATE appointments SET status = 'confirmed' WHERE id = ?",
            (appointment_id,),
        )
        self.conn.commit()
        return cur.rowcount > 0

    def delete_appointment(self: Self, appointment_id: int) -> bool:
        cur = self.conn.execute(
            "DELETE FROM appointments WHERE id = ?", (appointment_id,)
        )
        self.conn.commit()
        return cur.rowcount > 0

    # --- Payments ---

    def add_payment(self: Self, payment: Payment) -> int:
        cur = self.conn.execute(
            """
            INSERT INTO payments (appointment_id, amount, paid_at, method)
            VALUES (?, ?, ?, ?)
            """,
            (
                payment.appointment_id,
                payment.amount,
                payment.paid_at or self._now(),
                payment.method,
            ),
        )
        self.conn.commit()
        last_id = cur.lastrowid
        assert last_id is not None
        return int(last_id)

    def revenue_by_professional(self: Self, professional_id: int) -> float:
        row = self.conn.execute(
            """
            SELECT COALESCE(SUM(p.amount), 0) as total
            FROM payments p
            JOIN appointments a ON p.appointment_id = a.id
            WHERE a.professional_id = ?
            """,
            (professional_id,),
        ).fetchone()
        return float(row["total"])

    def close(self: Self) -> None:
        self.conn.close()

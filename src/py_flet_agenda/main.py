"""Flet UI for flet-agenda.  # pragma: no cover"""

from datetime import date, datetime, timedelta
from pathlib import Path

import flet as ft

from py_flet_agenda.database import Database
from py_flet_agenda.models import Appointment, Client, Professional


def app_main(page: ft.Page) -> None:  # pragma: no cover
    """Build the Flet UI."""
    page.title = "py-agenda"
    page.theme_mode = ft.ThemeMode.LIGHT
    page.window_width = 700  # type: ignore[attr-defined]
    page.window_height = 700  # type: ignore[attr-defined]

    db = Database(Path.home() / ".local" / "share" / "flet-agenda" / "agenda.db")

    # --- UI state ---
    client_name_field = ft.TextField(label="Nome do cliente", width=250)
    client_phone_field = ft.TextField(label="Telefone", width=150)
    client_email_field = ft.TextField(label="E-mail", width=200)

    prof_name_field = ft.TextField(label="Nome do profissional", width=250)
    prof_spec_field = ft.TextField(label="Especialidade", width=200)

    client_dropdown = ft.Dropdown(label="Cliente", options=[], width=200)
    prof_dropdown = ft.Dropdown(label="Profissional", options=[], width=200)
    date_field = ft.TextField(
        label="Data (YYYY-MM-DD)", value=date.today().isoformat(), width=180
    )
    time_field = ft.TextField(label="Horário (HH:MM)", width=150)
    duration_field = ft.TextField(
        label="Duração (min)",
        value="30",
        width=120,
        keyboard_type=ft.KeyboardType.NUMBER,
    )
    notes_field = ft.TextField(label="Observações", width=300)

    appointments_list = ft.ListView(expand=True, spacing=6, padding=20)
    revenue_text = ft.Text(size=14)

    def refresh_dropdowns() -> None:
        clients = db.get_clients()
        client_dropdown.options = [
            ft.dropdown.Option(str(c.id), c.name) for c in clients
        ]
        professionals = db.get_professionals()
        prof_dropdown.options = [
            ft.dropdown.Option(str(p.id), f"{p.name} — {p.specialty}")
            for p in professionals
        ]
        page.update()

    def refresh_appointments() -> None:
        date_str = date_field.value.strip() or date.today().isoformat()
        appointments = db.get_appointments_by_date(date_str)
        appointments_list.controls.clear()

        for ap in appointments:
            client = next((c for c in db.get_clients() if c.id == ap.client_id), None)
            prof = next(
                (p for p in db.get_professionals() if p.id == ap.professional_id), None
            )
            cname = client.name if client else "?"
            pname = prof.name if prof else "?"
            status_color = {
                "scheduled": ft.colors.BLUE,
                "confirmed": ft.colors.GREEN,
                "completed": ft.colors.TEAL,
                "cancelled": ft.colors.RED,
            }.get(ap.status, ft.colors.GREY)

            appointments_list.controls.append(
                ft.ListTile(
                    title=ft.Text(f"{cname} — {pname}"),
                    subtitle=ft.Text(
                        f"{ap.starts_at[11:16]} às {ap.ends_at[11:16]} — {ap.status}"
                    ),
                    trailing=ft.IconButton(
                        icon=ft.icons.CHECK_CIRCLE,  # type: ignore[attr-defined]
                        icon_color=status_color,
                        on_click=lambda e, aid=ap.id: confirm_ap(aid),
                    ),
                )
            )
        page.update()

    def add_client(e: ft.ControlEvent) -> None:
        if not client_name_field.value:
            return
        db.add_client(
            Client(
                name=client_name_field.value,
                phone=client_phone_field.value or "",
                email=client_email_field.value or "",
            )
        )
        client_name_field.value = ""
        client_phone_field.value = ""
        client_email_field.value = ""
        refresh_dropdowns()

    def add_professional(e: ft.ControlEvent) -> None:
        if not prof_name_field.value:
            return
        db.add_professional(
            Professional(
                name=prof_name_field.value,
                specialty=prof_spec_field.value or "",
            )
        )
        prof_name_field.value = ""
        prof_spec_field.value = ""
        refresh_dropdowns()

    def add_appointment(e: ft.ControlEvent) -> None:
        if not client_dropdown.value or not prof_dropdown.value:
            return
        try:
            duration = int(duration_field.value or 30)
        except ValueError:
            duration = 30

        starts_at = f"{date_field.value} {time_field.value}:00"
        start_dt = datetime.fromisoformat(starts_at)
        end_dt = start_dt + timedelta(minutes=duration)

        ap = Appointment(
            client_id=int(client_dropdown.value),
            professional_id=int(prof_dropdown.value),
            starts_at=start_dt.isoformat(),
            ends_at=end_dt.isoformat(),
        )
        db.add_appointment(ap)
        refresh_appointments()

    def confirm_ap(appointment_id: int) -> None:
        db.confirm_appointment(appointment_id)
        refresh_appointments()

    def refresh_revenue() -> None:
        professionals = db.get_professionals()
        lines = []
        total = 0.0
        for p in professionals:
            assert p.id is not None
            rev = db.revenue_by_professional(p.id)
            total += rev
            lines.append(f"{p.name}: R$ {rev:.2f}")
        lines.append("---")
        lines.append(f"Total: R$ {total:.2f}")
        revenue_text.value = " | ".join(lines)
        page.update()

    # --- Layout ---
    page.add(
        ft.Text("Agenda de Clientes", size=24, weight=ft.FontWeight.BOLD),
        ft.Divider(),
        ft.Row(
            [client_name_field, client_phone_field, client_email_field],
            wrap=True,
        ),
        ft.ElevatedButton("Cadastrar cliente", on_click=add_client),
        ft.Row(
            [prof_name_field, prof_spec_field],
            wrap=True,
        ),
        ft.ElevatedButton("Cadastrar profissional", on_click=add_professional),
        ft.Divider(),
        ft.Row(
            [client_dropdown, prof_dropdown, date_field, time_field, duration_field],
            wrap=True,
        ),
        notes_field,
        ft.ElevatedButton("Agendar", on_click=add_appointment),
        ft.Divider(),
        ft.Text("Hoje", size=18, weight=ft.FontWeight.BOLD),
        appointments_list,
        revenue_text,
        ft.ElevatedButton("Atualizar receita", on_click=lambda _: refresh_revenue()),
    )

    refresh_dropdowns()
    refresh_appointments()
    refresh_revenue()

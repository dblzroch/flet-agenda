# flet-agenda

> Client appointment scheduler with day/week view, confirmations and per-professional finance.

[![CI](https://github.com/dblzroch/flet-agenda/actions/workflows/ci.yml/badge.svg)](https://github.com/dblzroch/flet-agenda/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Python 3.12+](https://img.shields.io/badge/python-3.12+-blue.svg)](pyproject.toml)
[![Code style: ruff](https://img.shields.io/badge/code%20style-ruff-000000.svg)](https://github.com/astral-sh/ruff)

Agenda de clientes para clínicas e salões construída com [Flet](https://flet.dev/). Agende atendimentos,
visualize por dia ou semana, confirme consultas e acompanhe o financeiro por profissional.

## Quickstart

```bash
# Clone
git clone https://github.com/dblzroch/flet-agenda.git
cd flet-agenda

# Install (uv)
uv sync --dev

# Run the desktop app
uv run flet-agenda
```

## How it works

- **UI**: Flet (Flutter-based) desktop/mobile GUI.
- **Storage**: SQLite database for clients, professionals, appointments and payments.
- **Features**: Client and professional registry, appointment scheduling,
  day/week calendar view, confirmation status, payment tracking, per-professional revenue report.
- **Tests**: `pytest` with coverage gate at 80%.
- **CI**: GitHub Actions runs ruff, mypy and pytest on every push/PR.

## Tests & quality

```bash
make test      # pytest with coverage
make lint      # ruff + mypy
make fmt       # ruff format
```

## License

MIT

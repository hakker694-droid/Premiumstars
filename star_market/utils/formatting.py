"""Formatting helpers."""
from __future__ import annotations

from datetime import datetime, timedelta, timezone

TASHKENT = timezone(timedelta(hours=5))


def fmt_uzs(amount: int) -> str:
    """27399 -> '27 399 UZS' (integer arithmetic only)."""
    return f"{int(amount):,}".replace(",", " ") + " UZS"


def fmt_dt(value: datetime | None) -> str:
    """Format a datetime in Tashkent time. Naive values are treated as UTC."""
    if value is None:
        return "—"
    if value.tzinfo is None:
        value = value.replace(tzinfo=timezone.utc)
    return value.astimezone(TASHKENT).strftime("%d.%m.%Y %H:%M")

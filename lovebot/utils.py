"""Small helpers shared across the bot (dates, numbers, formatting)."""

from __future__ import annotations

from datetime import date, datetime
from typing import Iterable

import pytz


PERSIAN_DIGITS = str.maketrans("0123456789", "۰۱۲۳۴۵۶۷۸۹")


def to_persian_digits(value: int | str) -> str:
    """Convert a value's ASCII digits to Persian digits."""
    return str(value).translate(PERSIAN_DIGITS)


def format_number(value: int, lang: str) -> str:
    """Format a number for display, switching digit set by language."""
    return to_persian_digits(value) if lang == "fa" else str(value)


def parse_date(text: str) -> date | None:
    """Parse a YYYY-MM-DD or YYYY/MM/DD string into a ``date`` instance."""
    text = (text or "").strip().replace("/", "-").replace(".", "-")
    for fmt in ("%Y-%m-%d", "%Y-%m-%d"):
        try:
            return datetime.strptime(text, fmt).date()
        except ValueError:
            continue
    return None


def parse_birthday(text: str) -> str | None:
    """Parse a MM-DD birthday into a canonical ``MM-DD`` string.

    Accepts ``MM-DD``, ``MM/DD``, ``DD-MM`` (only when DD>12 makes it unambiguous),
    and full ``YYYY-MM-DD`` (year is dropped).
    """
    text = (text or "").strip().replace("/", "-").replace(".", "-")
    if not text:
        return None

    parts = text.split("-")
    if len(parts) == 3:
        # Full date — keep month/day only.
        try:
            d = datetime.strptime(text, "%Y-%m-%d").date()
            return f"{d.month:02d}-{d.day:02d}"
        except ValueError:
            return None
    if len(parts) != 2:
        return None

    try:
        a, b = int(parts[0]), int(parts[1])
    except ValueError:
        return None

    # Disambiguate: a=month, b=day by default; flip only if a>12.
    if 1 <= a <= 12 and 1 <= b <= 31:
        return f"{a:02d}-{b:02d}"
    if 1 <= b <= 12 and 1 <= a <= 31:
        return f"{b:02d}-{a:02d}"
    return None


def parse_time(text: str) -> tuple[int, int] | None:
    """Parse ``HH:MM`` (or ``HH``) into ``(hour, minute)``."""
    text = (text or "").strip()
    if not text:
        return None
    try:
        if ":" in text:
            hour_s, minute_s = text.split(":", 1)
            hour, minute = int(hour_s), int(minute_s)
        else:
            hour, minute = int(text), 0
    except ValueError:
        return None
    if 0 <= hour < 24 and 0 <= minute < 60:
        return hour, minute
    return None


def days_between(start: date | str, end: date | None = None) -> int:
    """Inclusive days between two dates (start counts as day 1)."""
    if isinstance(start, str):
        start = datetime.strptime(start, "%Y-%m-%d").date()
    end = end or date.today()
    return (end - start).days + 1


SPECIAL_MILESTONES: tuple[int, ...] = (
    7, 14, 30, 50, 60, 90, 100, 150, 200, 222, 250, 300, 333, 365,
    400, 444, 500, 555, 600, 666, 700, 730, 777, 800, 888, 900, 999,
    1000, 1095, 1111, 1234, 1500, 1825, 2000, 2222, 2555, 2929, 3000,
    3333, 3650, 5000, 5555, 7000, 7777, 10000,
)


def is_special_milestone(days: int) -> bool:
    return days in SPECIAL_MILESTONES


def next_milestone(days: int) -> int:
    for m in SPECIAL_MILESTONES:
        if m > days:
            return m
    return ((days // 1000) + 1) * 1000


def humanise_duration(days: int, lang: str) -> str:
    """Render ``days`` as ``X years, Y months, Z days``."""
    years, rem = divmod(days, 365)
    months, final = divmod(rem, 30)

    n = lambda v: format_number(v, lang)  # noqa: E731

    if lang == "fa":
        parts: list[str] = []
        if years:
            parts.append(f"{n(years)} سال")
        if months:
            parts.append(f"{n(months)} ماه")
        if final or not parts:
            parts.append(f"{n(final)} روز")
        return " و ".join(parts)

    parts: list[str] = []
    if years:
        parts.append(f"{years} year{'s' if years != 1 else ''}")
    if months:
        parts.append(f"{months} month{'s' if months != 1 else ''}")
    if final or not parts:
        parts.append(f"{final} day{'s' if final != 1 else ''}")
    return ", ".join(parts)


def get_tz(name: str) -> pytz.BaseTzInfo:
    """Safely fetch a timezone, falling back to UTC if unknown."""
    try:
        return pytz.timezone(name)
    except pytz.UnknownTimeZoneError:
        return pytz.UTC


def now_in(tz_name: str) -> datetime:
    return datetime.now(get_tz(tz_name))


def chunked(seq: Iterable, size: int) -> list[list]:
    """Split ``seq`` into chunks of ``size`` elements (last chunk may be shorter)."""
    chunk: list = []
    out: list[list] = []
    for item in seq:
        chunk.append(item)
        if len(chunk) >= size:
            out.append(chunk)
            chunk = []
    if chunk:
        out.append(chunk)
    return out

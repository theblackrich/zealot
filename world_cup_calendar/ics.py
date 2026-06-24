from __future__ import annotations

import re
from datetime import datetime, timedelta, timezone

from .models import MatchEvent
from .state import EventState, fingerprint_event


def build_calendar(events: list[MatchEvent], existing_state: dict[str, EventState], match_duration_minutes: int) -> tuple[str, dict[str, EventState]]:
    now = datetime.now(timezone.utc)
    updated_state: dict[str, EventState] = {}
    sections = [
        "BEGIN:VCALENDAR",
        "VERSION:2.0",
        "PRODID:-//zealot//World Cup Calendar//EN",
        "CALSCALE:GREGORIAN",
        "METHOD:PUBLISH",
        "X-WR-CALNAME:World Cup Schedule",
        "X-WR-TIMEZONE:UTC",
    ]

    for event in sorted(events, key=lambda item: item.start_utc):
        uid = build_uid(event)
        fingerprint = fingerprint_event(event)
        prior = existing_state.get(uid)
        sequence = 0 if prior is None else prior.sequence + int(prior.fingerprint != fingerprint)
        updated_state[uid] = EventState(sequence=sequence, fingerprint=fingerprint)
        sections.extend(
            build_event_lines(
                event=event,
                uid=uid,
                sequence=sequence,
                generated_at=now,
                duration_minutes=match_duration_minutes,
            )
        )

    sections.append("END:VCALENDAR")
    return "\r\n".join(fold_ical_line(line) for line in sections) + "\r\n", updated_state


def build_uid(event: MatchEvent) -> str:
    slug = slugify(f"{event.tournament}-{event.home_team}-{event.away_team}-{event.start_utc:%Y%m%dT%H%M%SZ}")
    return f"{slug}@zealot.local"


def build_event_lines(
    event: MatchEvent,
    uid: str,
    sequence: int,
    generated_at: datetime,
    duration_minutes: int,
) -> list[str]:
    end_utc = event.start_utc + timedelta(minutes=duration_minutes)
    summary = f"{event.home_team} vs {event.away_team}"
    description = f"{event.tournament} - {event.stage}"
    return [
        "BEGIN:VEVENT",
        f"UID:{uid}",
        f"DTSTAMP:{format_ics_datetime(generated_at)}",
        f"LAST-MODIFIED:{format_ics_datetime(generated_at)}",
        f"SEQUENCE:{sequence}",
        f"SUMMARY:{escape_text(summary)}",
        f"DESCRIPTION:{escape_text(description)}",
        f"LOCATION:{escape_text(event.location)}",
        f"DTSTART:{format_ics_datetime(event.start_utc)}",
        f"DTEND:{format_ics_datetime(end_utc)}",
        "STATUS:CONFIRMED",
        "TRANSP:OPAQUE",
        "END:VEVENT",
    ]


def format_ics_datetime(value: datetime) -> str:
    return value.astimezone(timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def escape_text(value: str) -> str:
    return (
        value.replace("\\", "\\\\")
        .replace(";", r"\;")
        .replace(",", r"\,")
        .replace("\n", r"\n")
    )


def slugify(value: str) -> str:
    collapsed = re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")
    return collapsed or "event"


def fold_ical_line(line: str, limit: int = 75) -> str:
    if len(line) <= limit:
        return line

    chunks = [line[:limit]]
    remaining = line[limit:]
    while remaining:
        chunks.append(f" {remaining[: limit - 1]}")
        remaining = remaining[limit - 1 :]
    return "\r\n".join(chunks)

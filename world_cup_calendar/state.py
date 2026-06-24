from __future__ import annotations

import hashlib
import json
from dataclasses import asdict, dataclass
from pathlib import Path

from .models import MatchEvent


@dataclass
class EventState:
    sequence: int
    fingerprint: str


def load_state(path: Path) -> dict[str, EventState]:
    if not path.exists():
        return {}

    payload = json.loads(path.read_text(encoding="utf-8"))
    return {uid: EventState(**value) for uid, value in payload.items()}


def save_state(path: Path, state: dict[str, EventState]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = {uid: asdict(value) for uid, value in state.items()}
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")


def fingerprint_event(event: MatchEvent) -> str:
    raw = "|".join(
        [
            event.tournament,
            event.stage,
            event.start_utc.isoformat(),
            event.home_team,
            event.away_team,
            event.location,
        ]
    )
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()

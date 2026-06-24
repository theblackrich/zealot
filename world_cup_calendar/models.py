from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class MatchEvent:
    source_id: str
    tournament: str
    stage: str
    start_utc: datetime
    home_team: str
    away_team: str
    location: str

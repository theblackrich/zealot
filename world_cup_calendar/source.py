from __future__ import annotations

import json
import re
from dataclasses import dataclass
from datetime import date, datetime, timedelta, timezone
from urllib.parse import quote
from urllib.request import urlopen

from .models import MatchEvent


TOURNAMENT_PATTERN = re.compile(r"^(?P<year>\d{4})--")
HEADER_PATTERN = re.compile(r"^=\s*(?P<name>.+?)\s+(?P<year>\d{4})\b")
DATE_PATTERN = re.compile(
    r"^(?:Mon|Tue|Wed|Thu|Fri|Sat|Sun)\s+"
    r"(?P<month>[A-Za-z]+)\s+"
    r"(?P<day>\d{1,2})$"
)
MATCH_PATTERN = re.compile(
    r"^\s*(?P<time>\d{1,2}:\d{2})\s+"
    r"(?P<offset>UTC[+-]\d{1,2})\s+"
    r"(?P<home>.+?)\s+v\s+"
    r"(?P<away>.+?)\s+@\s+"
    r"(?P<location>.+?)\s*$"
)

MONTHS = {
    "jan": 1,
    "january": 1,
    "feb": 2,
    "february": 2,
    "mar": 3,
    "march": 3,
    "apr": 4,
    "april": 4,
    "may": 5,
    "jun": 6,
    "june": 6,
    "jul": 7,
    "july": 7,
    "aug": 8,
    "august": 8,
    "sep": 9,
    "sept": 9,
    "september": 9,
    "oct": 10,
    "october": 10,
    "nov": 11,
    "november": 11,
    "dec": 12,
    "december": 12,
}


@dataclass(frozen=True)
class TournamentSource:
    owner: str
    repo: str
    tournament_path: str | None = None

    def fetch_matches(self) -> list[MatchEvent]:
        tournament_path = self.tournament_path or self._latest_tournament_path()
        text = self._fetch_text_file(f"{tournament_path}/cup.txt")
        return parse_openfootball_matches(text)

    def _latest_tournament_path(self) -> str:
        url = f"https://api.github.com/repos/{quote(self.owner)}/{quote(self.repo)}/contents/"
        with urlopen(url) as response:
            items = json.load(response)

        tournaments = [
            item["path"]
            for item in items
            if item.get("type") == "dir" and TOURNAMENT_PATTERN.match(item.get("name", ""))
        ]
        if not tournaments:
            raise ValueError("No World Cup tournament directories were found in the source repository.")
        return max(tournaments, key=lambda path: int(TOURNAMENT_PATTERN.match(path).group("year")))

    def _fetch_text_file(self, path: str) -> str:
        metadata_url = (
            f"https://api.github.com/repos/{quote(self.owner)}/"
            f"{quote(self.repo)}/contents/{quote(path)}"
        )
        with urlopen(metadata_url) as response:
            metadata = json.load(response)
        with urlopen(metadata["download_url"]) as response:
            return response.read().decode("utf-8")


def parse_openfootball_matches(text: str) -> list[MatchEvent]:
    lines = text.splitlines()
    header = next((HEADER_PATTERN.match(line) for line in lines if line.startswith("=")), None)
    if header is None:
        raise ValueError("Could not find a tournament header in the source file.")

    tournament_name = f"{header.group('name').strip()} {header.group('year')}"
    tournament_year = int(header.group("year"))
    current_stage: str | None = None
    current_date: date | None = None
    matches: list[MatchEvent] = []

    for raw_line in lines:
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue

        if line.startswith("▪"):
            label = line.removeprefix("▪").strip()
            if "|" in label:
                label = label.split("|", maxsplit=1)[0].strip()
            if DATE_PATTERN.match(label):
                current_date = _parse_date(label, tournament_year)
            else:
                current_stage = label
            continue

        date_match = DATE_PATTERN.match(line)
        if date_match:
            current_date = _parse_date(line, tournament_year)
            continue

        match_match = MATCH_PATTERN.match(raw_line)
        if match_match:
            if current_stage is None or current_date is None:
                raise ValueError(f"Encountered a match before establishing stage/date context: {raw_line}")
            start_utc = _parse_start(current_date, match_match.group("time"), match_match.group("offset"))
            matches.append(
                MatchEvent(
                    tournament=tournament_name,
                    stage=current_stage,
                    start_utc=start_utc,
                    home_team=match_match.group("home").strip(),
                    away_team=match_match.group("away").strip(),
                    location=match_match.group("location").strip(),
                )
            )

    return matches


def _parse_date(value: str, year: int) -> date:
    match = DATE_PATTERN.match(value)
    if match is None:
        raise ValueError(f"Invalid date line: {value}")

    month = MONTHS[match.group("month").lower()]
    day = int(match.group("day"))
    return date(year, month, day)


def _parse_start(match_date: date, time_value: str, offset_value: str) -> datetime:
    hours, minutes = [int(part) for part in time_value.split(":")]
    sign = 1 if "+" in offset_value else -1
    offset_hours = int(offset_value.split("UTC", maxsplit=1)[1].replace("+", "").replace("-", ""))
    tz = timezone(sign * timedelta(hours=offset_hours))
    local_dt = datetime(match_date.year, match_date.month, match_date.day, hours, minutes, tzinfo=tz)
    return local_dt.astimezone(timezone.utc)

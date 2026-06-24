from __future__ import annotations

import shutil
from pathlib import Path

from .config import load_settings
from .ics import build_calendar
from .source import TournamentSource
from .state import load_state, save_state
from .summary import build_summary_html, summary_path_for_calendar_path


def main() -> int:
    settings = load_settings()
    source = TournamentSource(
        owner=settings.repo_owner,
        repo=settings.repo_name,
        tournament_path=settings.tournament_path,
    )
    events = source.fetch_matches()
    state = load_state(settings.state_path)
    calendar_text, updated_state = build_calendar(
        events=events,
        existing_state=state,
        match_duration_minutes=settings.match_duration_minutes,
    )

    _write_text(settings.output_path, calendar_text)
    save_state(settings.state_path, updated_state)
    summary_path = summary_path_for_calendar_path(settings.output_path)
    _write_text(summary_path, build_summary_html(settings, len(events)))

    if settings.publish_path is not None:
        settings.publish_path.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(settings.output_path, settings.publish_path)
        publish_summary_path = summary_path_for_calendar_path(settings.publish_path)
        shutil.copyfile(summary_path, publish_summary_path)

    print(f"Wrote {len(events)} events to {settings.output_path}")
    print(f"Wrote summary to {summary_path}")
    if settings.publish_path is not None:
        print(f"Copied calendar to {settings.publish_path}")
        print(f"Copied summary to {publish_summary_path}")
    return 0


def _write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8", newline="")

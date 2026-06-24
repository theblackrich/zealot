from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


DEFAULT_WINDOWS_PUBLISH_DIR = Path(r"C:\Users\thebl\OneDrive\Projects\Zealot")
DEFAULT_FILE_NAME = "world-cup.ics"
DEFAULT_OUTPUT_PATH = Path("dist") / DEFAULT_FILE_NAME
DEFAULT_STATE_PATH = Path(".state") / "world-cup-state.json"


@dataclass(frozen=True)
class Settings:
    output_path: Path
    state_path: Path
    publish_path: Path | None
    match_duration_minutes: int
    repo_owner: str
    repo_name: str
    tournament_path: str | None


def load_settings() -> Settings:
    publish = _resolve_publish_path()
    return Settings(
        output_path=Path(os.getenv("WORLD_CUP_OUTPUT_PATH", str(DEFAULT_OUTPUT_PATH))),
        state_path=Path(os.getenv("WORLD_CUP_STATE_PATH", str(DEFAULT_STATE_PATH))),
        publish_path=publish,
        match_duration_minutes=int(os.getenv("WORLD_CUP_MATCH_DURATION_MINUTES", "135")),
        repo_owner=os.getenv("WORLD_CUP_REPO_OWNER", "openfootball"),
        repo_name=os.getenv("WORLD_CUP_REPO_NAME", "worldcup"),
        tournament_path=os.getenv("WORLD_CUP_TOURNAMENT_PATH"),
    )


def _resolve_publish_path() -> Path | None:
    configured = os.getenv("WORLD_CUP_PUBLISH_PATH")
    if configured:
        configured_path = Path(configured)
        return configured_path if configured_path.suffix.lower() == ".ics" else configured_path / DEFAULT_FILE_NAME

    if os.name == "nt":
        return DEFAULT_WINDOWS_PUBLISH_DIR / DEFAULT_FILE_NAME

    return None

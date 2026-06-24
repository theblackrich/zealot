# World Cup calendar feed

This project generates a subscribable `.ics` feed for World Cup matches and keeps event UIDs stable so calendar clients update existing events instead of creating duplicates. It also generates an HTML summary that explains how to use the outputs, the current plan, and the actions already taken.

## What it does

- Pulls the latest World Cup tournament text from the public `openfootball/worldcup` dataset
- Parses upcoming fixtures from the tournament file
- Generates a deterministic ICS calendar feed
- Persists event fingerprints and increments `SEQUENCE` only when an event changes
- Writes the feed to disk and copies it to your OneDrive publish location on Windows by default
- Generates a companion HTML summary beside the ICS file in each output location

## Why this works for Outlook, Apple Calendar, and Google Calendar

To avoid duplicates, consumers should **subscribe to a URL** that always serves the same ICS file. Re-importing files creates duplicates; subscriptions update existing events when `UID` stays stable and the event metadata changes.

## Requirements

- Python 3.11+

## Usage

```powershell
python -m world_cup_calendar
```

By default this writes:

- `dist\world-cup.ics`
- `dist\world-cup-summary.html`
- `.state\world-cup-state.json`
- `C:\Users\thebl\OneDrive\Projects\Zealot\world-cup.ics` on Windows
- `C:\Users\thebl\OneDrive\Projects\Zealot\world-cup-summary.html` on Windows

## Configuration

Set environment variables before running:

| Variable | Default | Purpose |
| --- | --- | --- |
| `WORLD_CUP_OUTPUT_PATH` | `dist\world-cup.ics` | ICS output file |
| `WORLD_CUP_STATE_PATH` | `.state\world-cup-state.json` | Event fingerprint state |
| `WORLD_CUP_PUBLISH_PATH` | `C:\Users\thebl\OneDrive\Projects\Zealot\world-cup.ics` on Windows; unset elsewhere | Copy destination for the generated ICS file |
| `WORLD_CUP_MATCH_DURATION_MINUTES` | `135` | Default event duration |
| `WORLD_CUP_REPO_OWNER` | `openfootball` | Source repository owner |
| `WORLD_CUP_REPO_NAME` | `worldcup` | Source repository name |
| `WORLD_CUP_TOURNAMENT_PATH` | latest tournament directory | Override source tournament folder |

If `WORLD_CUP_PUBLISH_PATH` points to a directory, the generator writes `world-cup.ics` inside it.

Example override:

```powershell
$env:WORLD_CUP_PUBLISH_PATH = 'C:\Users\you\OneDrive\Public'
python -m world_cup_calendar
```

## Publishing

The generated file must be exposed through a stable URL for subscriptions. A synced folder alone is not enough unless the sharing link resolves to a direct download of the raw ICS file.

Good options:

1. Static hosting or object storage that serves `world-cup.ics` directly
2. OneDrive or iCloud only if you can provide a durable direct-download URL to the exact file

## HTML summary

Each run also writes `world-cup-summary.html` beside the ICS output. The summary includes:

- how to run and use the project,
- where the generated files were written,
- the current implementation plan,
- the actions already taken.

## Scheduler

The repository includes `.github\workflows\refresh-calendar.yml`, which refreshes the feed at:

- 2:00 PM PT
- 4:00 PM PT
- 6:00 PM PT
- 10:00 PM PT

Those cron values are encoded in UTC for the World Cup summer window, when Pacific Time is PDT (UTC-7).

## Calendar subscription steps

### Outlook

Use **Add calendar > Subscribe from web** and paste the public ICS URL.

### Apple Calendar

Use **File > New Calendar Subscription** and paste the public ICS URL.

### Google Calendar

Use **Other calendars > From URL** and paste the public ICS URL.

## Notes

- The current source adapter intentionally parses scheduled fixtures (`v`) rather than completed result lines.
- If the source file changes event time, venue, or matchup text, the event `UID` stays stable and the `SEQUENCE` increases.

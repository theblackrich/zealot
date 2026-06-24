from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from html import escape
from pathlib import Path

from .config import Settings


SUMMARY_FILE_NAME = "world-cup-summary.html"
DEFAULT_SUMMARY_THEME_KEY = "starlight-signal"
SUMMARY_PREVIEW_THEME_KEYS = ("eclipse-amber", "ion-rose", "lunar-lime")
TITLE_FONT_STACK = (
    '"Edge of the Galaxy", "Death Star", "Alien and Cows", "Orbitron", '
    '"Arial Black", "Segoe UI", sans-serif'
)
BODY_FONT_STACK = '"Inter", "Segoe UI", Arial, sans-serif'

CURRENT_PLAN = [
    "Generate the World Cup ICS feed and the HTML summary on every run.",
    "Copy the generated artifacts into the local OneDrive project folder on Windows.",
    "Publish the ICS file from the live GitHub Pages URL https://theblackrich.github.io/zealot/world-cup.ics for Outlook, Apple Calendar, and Google Calendar subscriptions.",
    "Keep deterministic UIDs and sequence tracking so subscribed clients update events instead of duplicating them.",
]

IMPLEMENTED_ACTIONS = [
    "Scaffolded a greenfield Python project in the previously empty repository.",
    "Integrated the openfootball/worldcup source dataset and selected the latest tournament directory automatically.",
    "Parsed only scheduled fixture lines so the calendar contains upcoming World Cup matches.",
    "Generated a deterministic ICS feed with stable event UIDs and persisted sequence state.",
    "Added scheduled refresh automation for 2 PM, 4 PM, 6 PM, and 10 PM Pacific Time.",
    "Configured Windows runs to copy the ICS file into C:\\Users\\thebl\\OneDrive\\Projects\\Zealot.",
    "Published the calendar, landing page, and summary on GitHub Pages at https://theblackrich.github.io/zealot/.",
    "Added this HTML summary artifact so usage, plan, and implementation details ship with each run.",
]

HOW_TO_USE = [
    "Run python -m world_cup_calendar to regenerate the calendar artifacts.",
    "Use the ICS file for publishing or subscription workflows; do not repeatedly import separate copies if you want update-in-place behavior.",
    "Subscribe to https://theblackrich.github.io/zealot/world-cup.ics from Outlook, Apple Calendar, or Google Calendar for automatic updates.",
    "Open this HTML file in a browser for the current project summary and operating instructions, then compare the preview sibling files if you want to review alternate visual directions.",
]


@dataclass(frozen=True)
class SummaryTheme:
    key: str
    label: str
    accent: str
    accent_soft: str
    accent_glow: str


SUMMARY_THEMES = {
    theme.key: theme
    for theme in (
        SummaryTheme(
            key="starlight-signal",
            label="Starlight Signal",
            accent="#67e8f9",
            accent_soft="rgba(103, 232, 249, 0.16)",
            accent_glow="rgba(103, 232, 249, 0.42)",
        ),
        SummaryTheme(
            key="eclipse-amber",
            label="Eclipse Amber",
            accent="#fbbf24",
            accent_soft="rgba(251, 191, 36, 0.15)",
            accent_glow="rgba(251, 191, 36, 0.38)",
        ),
        SummaryTheme(
            key="ion-rose",
            label="Ion Rose",
            accent="#f472b6",
            accent_soft="rgba(244, 114, 182, 0.14)",
            accent_glow="rgba(244, 114, 182, 0.38)",
        ),
        SummaryTheme(
            key="lunar-lime",
            label="Lunar Lime",
            accent="#a3e635",
            accent_soft="rgba(163, 230, 53, 0.14)",
            accent_glow="rgba(163, 230, 53, 0.34)",
        ),
    )
}


def build_summary_html(
    settings: Settings,
    event_count: int,
    *,
    theme_key: str = DEFAULT_SUMMARY_THEME_KEY,
) -> str:
    theme = summary_theme(theme_key)
    generated_at = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%SZ")
    output_summary_path = summary_path_for_calendar_path(settings.output_path)
    publish_summary_path = summary_path_for_calendar_path(settings.publish_path) if settings.publish_path else None
    outputs = [
        ("ICS output", settings.output_path),
        ("HTML summary output", output_summary_path),
        ("State file", settings.state_path),
    ]
    for preview_theme_key in SUMMARY_PREVIEW_THEME_KEYS:
        preview_theme = summary_theme(preview_theme_key)
        outputs.append(
            (
                f"HTML preview ({preview_theme.label})",
                summary_preview_path_for_summary_path(output_summary_path, preview_theme.key),
            )
        )
    if settings.publish_path is not None:
        outputs.append(("Published ICS copy", settings.publish_path))
    if publish_summary_path is not None:
        outputs.append(("Published HTML summary copy", publish_summary_path))
        for preview_theme_key in SUMMARY_PREVIEW_THEME_KEYS:
            preview_theme = summary_theme(preview_theme_key)
            outputs.append(
                (
                    f"Published preview ({preview_theme.label})",
                    summary_preview_path_for_summary_path(publish_summary_path, preview_theme.key),
                )
            )

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>World Cup Calendar Summary</title>
  <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Orbitron:wght@500;700;800&display=swap');

    :root {{
      color-scheme: dark;
      --page-bg: #050608;
      --page-bg-secondary: #10141b;
      --panel-bg: rgba(15, 18, 24, 0.9);
      --panel-border: rgba(192, 192, 192, 0.28);
      --panel-border-strong: rgba(255, 255, 255, 0.14);
      --text-main: #f4f6f8;
      --text-muted: #b1bac4;
      --code-bg: rgba(255, 255, 255, 0.05);
      --row-line: rgba(255, 255, 255, 0.1);
      --shadow: 0 24px 60px rgba(0, 0, 0, 0.45);
      --accent: {theme.accent};
      --accent-soft: {theme.accent_soft};
      --accent-glow: {theme.accent_glow};
      --title-font: {TITLE_FONT_STACK};
      --body-font: {BODY_FONT_STACK};
    }}

    body {{
      font-family: var(--body-font);
      line-height: 1.6;
      margin: 0;
      min-height: 100vh;
      background:
        radial-gradient(circle at top, rgba(255, 255, 255, 0.09), transparent 32%),
        linear-gradient(180deg, var(--page-bg-secondary) 0%, var(--page-bg) 52%, #010101 100%);
      color: var(--text-main);
      letter-spacing: 0.01em;
      position: relative;
    }}
    body::before {{
      content: "";
      position: fixed;
      inset: 0;
      background:
        radial-gradient(circle at 14% 18%, rgba(255, 255, 255, 0.18) 0 1px, transparent 1px),
        radial-gradient(circle at 76% 10%, rgba(255, 255, 255, 0.14) 0 1px, transparent 1px),
        radial-gradient(circle at 28% 72%, rgba(255, 255, 255, 0.16) 0 1px, transparent 1px),
        linear-gradient(120deg, transparent 0%, rgba(255, 255, 255, 0.02) 45%, transparent 100%);
      background-size: 240px 240px, 320px 320px, 280px 280px, 100% 100%;
      opacity: 0.55;
      pointer-events: none;
    }}
    main {{
      max-width: 1040px;
      margin: 0 auto;
      padding: 40px 20px 56px;
      position: relative;
      z-index: 1;
    }}
    section {{
      background: linear-gradient(180deg, rgba(255, 255, 255, 0.045), rgba(255, 255, 255, 0.015));
      border: 1px solid var(--panel-border);
      border-radius: 16px;
      padding: 22px;
      margin-bottom: 20px;
      box-shadow: var(--shadow);
      backdrop-filter: blur(8px);
    }}
    .hero {{
      border-color: var(--panel-border-strong);
      position: relative;
      overflow: hidden;
    }}
    .hero::after {{
      content: "";
      position: absolute;
      inset: 0 auto auto 0;
      width: 100%;
      height: 3px;
      background: linear-gradient(90deg, var(--accent), transparent 72%);
      box-shadow: 0 0 20px var(--accent-glow);
    }}
    .eyebrow {{
      display: inline-block;
      margin-bottom: 14px;
      padding: 5px 10px;
      border-radius: 999px;
      background: var(--accent-soft);
      color: var(--accent);
      font-size: 0.72rem;
      font-weight: 700;
      letter-spacing: 0.18em;
      text-transform: uppercase;
    }}
    h1, h2 {{
      font-family: var(--title-font);
      margin-top: 0;
      text-transform: uppercase;
      letter-spacing: 0.1em;
    }}
    h1 {{
      margin-bottom: 14px;
      font-size: clamp(2rem, 5vw, 3.2rem);
      line-height: 1.05;
      text-shadow: 0 0 18px rgba(255, 255, 255, 0.08);
    }}
    h2 {{
      margin-bottom: 14px;
      font-size: 1rem;
      color: #ffffff;
    }}
    p {{
      margin-top: 0;
    }}
    strong {{
      color: #ffffff;
    }}
    code {{
      background: var(--code-bg);
      border: 1px solid rgba(255, 255, 255, 0.08);
      padding: 2px 7px;
      border-radius: 999px;
      color: #f8fafc;
    }}
    ul {{
      padding-left: 20px;
      margin-bottom: 0;
    }}
    li + li {{
      margin-top: 8px;
    }}
    li::marker {{
      color: var(--accent);
    }}
    table {{
      width: 100%;
      border-collapse: collapse;
    }}
    th, td {{
      text-align: left;
      border-bottom: 1px solid var(--row-line);
      padding: 10px 8px;
      vertical-align: top;
    }}
    th {{
      width: 225px;
      color: #ffffff;
      font-size: 0.76rem;
      letter-spacing: 0.12em;
      text-transform: uppercase;
    }}
    .meta {{
      color: var(--text-muted);
      margin-bottom: 18px;
    }}
    .theme-note {{
      color: var(--text-muted);
      margin-bottom: 0;
    }}
    .accent {{
      color: var(--accent);
    }}
    @media (max-width: 720px) {{
      main {{
        padding: 28px 14px 40px;
      }}
      section {{
        padding: 18px;
      }}
      th, td {{
        display: block;
        width: auto;
        padding-left: 0;
        padding-right: 0;
      }}
      th {{
        border-bottom: none;
        padding-bottom: 2px;
      }}
    }}
  </style>
</head>
<body>
  <main>
    <section class="hero">
      <div class="eyebrow">Retro Modern Spaceframe</div>
      <h1>World Cup Calendar <span class="accent">Project Summary</span></h1>
      <p class="meta">Generated at {escape(generated_at)} UTC. Current feed contains {event_count} scheduled matches.</p>
      <p class="theme-note">Default theme: <strong>{escape(theme.label)}</strong>. Accent color is intentionally limited to headings, markers, and signal lines so the page stays anchored in black, white, silver, and grey.</p>
      <p>This file is regenerated by <code>python -m world_cup_calendar</code>. If the process changes and the generator runs again, this summary updates with the latest instructions and project state.</p>
    </section>
    <section>
      <h2>How to use the project and files</h2>
      {render_list(HOW_TO_USE)}
    </section>
    <section>
      <h2>Artifacts written by the process</h2>
      {render_outputs_table(outputs)}
    </section>
    <section>
      <h2>Current implementation plan</h2>
      {render_list(CURRENT_PLAN)}
    </section>
    <section>
      <h2>Actions already taken</h2>
      {render_list(IMPLEMENTED_ACTIONS)}
    </section>
    <section>
      <h2>Calendar subscription notes</h2>
      <ul>
        <li>Outlook: use <strong>Add calendar &gt; Subscribe from web</strong> with the final public ICS URL.</li>
        <li>Apple Calendar: use <strong>File &gt; New Calendar Subscription</strong> with the final public ICS URL.</li>
        <li>Google Calendar: use <strong>Other calendars &gt; From URL</strong> with the final public ICS URL.</li>
        <li>Repeated file import creates duplicates. Stable subscription URLs plus stable ICS UIDs are what enable update-in-place behavior.</li>
      </ul>
    </section>
  </main>
</body>
</html>
"""


def summary_path_for_calendar_path(calendar_path: Path) -> Path:
    return calendar_path.with_name(SUMMARY_FILE_NAME)


def summary_preview_path_for_summary_path(summary_path: Path, theme_key: str) -> Path:
    return summary_path.with_name(f"{summary_path.stem}-preview-{theme_key}{summary_path.suffix}")


def build_summary_preview_pages(settings: Settings, event_count: int) -> dict[str, str]:
    return {
        theme_key: build_summary_html(settings, event_count, theme_key=theme_key)
        for theme_key in SUMMARY_PREVIEW_THEME_KEYS
    }


def summary_theme(theme_key: str) -> SummaryTheme:
    try:
        return SUMMARY_THEMES[theme_key]
    except KeyError as exc:
        raise ValueError(f"Unknown summary theme: {theme_key}") from exc


def render_list(items: list[str]) -> str:
    return "<ul>" + "".join(f"<li>{escape(item)}</li>" for item in items) + "</ul>"


def render_outputs_table(outputs: list[tuple[str, Path]]) -> str:
    rows = "".join(
        f"<tr><th>{escape(label)}</th><td><code>{escape(str(path))}</code></td></tr>"
        for label, path in outputs
    )
    return f"<table>{rows}</table>"

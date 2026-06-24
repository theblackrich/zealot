from __future__ import annotations

import unittest
from pathlib import Path

from world_cup_calendar.config import Settings
from world_cup_calendar.summary import (
    SUMMARY_FILE_NAME,
    SUMMARY_PREVIEW_THEME_KEYS,
    build_summary_html,
    build_summary_preview_pages,
    summary_path_for_calendar_path,
    summary_preview_path_for_summary_path,
)


class SummaryTests(unittest.TestCase):
    def test_summary_uses_sibling_file_name(self) -> None:
        self.assertEqual(
            summary_path_for_calendar_path(Path("dist") / "world-cup.ics"),
            Path("dist") / "world-cup-summary.html",
        )
        self.assertEqual(
            summary_preview_path_for_summary_path(
                Path("dist") / SUMMARY_FILE_NAME,
                "ion-rose",
            ),
            Path("dist") / "world-cup-summary-preview-ion-rose.html",
        )

    def test_summary_contains_plan_actions_and_paths(self) -> None:
        settings = Settings(
            output_path=Path("dist") / "world-cup.ics",
            state_path=Path(".state") / "world-cup-state.json",
            publish_path=Path(r"C:\Users\thebl\OneDrive\Projects\Zealot\world-cup.ics"),
            match_duration_minutes=135,
            repo_owner="openfootball",
            repo_name="worldcup",
            tournament_path=None,
        )

        html = build_summary_html(settings, 28)

        self.assertIn("World Cup Calendar", html)
        self.assertIn("Project Summary</span>", html)
        self.assertIn("Starlight Signal", html)
        self.assertIn("Edge of the Galaxy", html)
        self.assertIn("Current implementation plan", html)
        self.assertIn("Actions already taken", html)
        self.assertIn("HTML preview (Eclipse Amber)", html)
        self.assertIn("C:\\Users\\thebl\\OneDrive\\Projects\\Zealot\\world-cup.ics", html)
        self.assertIn(SUMMARY_FILE_NAME, html)

    def test_preview_pages_cover_each_preview_theme(self) -> None:
        settings = Settings(
            output_path=Path("dist") / "world-cup.ics",
            state_path=Path(".state") / "world-cup-state.json",
            publish_path=None,
            match_duration_minutes=135,
            repo_owner="openfootball",
            repo_name="worldcup",
            tournament_path=None,
        )

        preview_pages = build_summary_preview_pages(settings, 28)

        self.assertEqual(tuple(preview_pages), SUMMARY_PREVIEW_THEME_KEYS)
        for theme_key in SUMMARY_PREVIEW_THEME_KEYS:
            self.assertIn(theme_key, preview_pages[theme_key])


if __name__ == "__main__":
    unittest.main()

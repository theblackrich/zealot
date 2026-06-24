from __future__ import annotations

import unittest
from pathlib import Path

from world_cup_calendar.config import Settings
from world_cup_calendar.summary import SUMMARY_FILE_NAME, build_summary_html, summary_path_for_calendar_path


class SummaryTests(unittest.TestCase):
    def test_summary_uses_sibling_file_name(self) -> None:
        self.assertEqual(
            summary_path_for_calendar_path(Path("dist") / "world-cup.ics"),
            Path("dist") / "world-cup-summary.html",
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

        self.assertIn("World Cup Calendar Project Summary", html)
        self.assertIn("Current implementation plan", html)
        self.assertIn("Actions already taken", html)
        self.assertIn("C:\\Users\\thebl\\OneDrive\\Projects\\Zealot\\world-cup.ics", html)
        self.assertIn(SUMMARY_FILE_NAME, html)


if __name__ == "__main__":
    unittest.main()

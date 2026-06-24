from __future__ import annotations

import unittest
from datetime import datetime, timezone

from world_cup_calendar.source import parse_openfootball_matches


SAMPLE = """= World Cup 2026

▪ Group A
Thu June 11
  13:00 UTC-6     Mexico  v South Africa        @ Mexico City
  20:00 UTC-6     South Korea  v Czech Republic     @ Guadalajara (Zapopan)

▪ Group B
Fri June 12
  15:00 UTC-4     Canada   1-1 (0-1) Bosnia & Herzegovina    @ Toronto
Wed June 24
  12:00 UTC-7     Switzerland           v Canada    @ Vancouver

▪ Round of 16
Sat Jul 4
  (89) 17:00 UTC-4  W74 v W77   @ Philadelphia
"""


class SourceTests(unittest.TestCase):
    def test_parser_reads_only_scheduled_fixture_lines(self) -> None:
        matches = parse_openfootball_matches(SAMPLE)

        self.assertEqual([match.home_team for match in matches], ["Mexico", "South Korea", "Switzerland", "W74"])
        self.assertEqual(matches[0].away_team, "South Africa")
        self.assertEqual(matches[0].stage, "Group A")
        self.assertEqual(matches[0].location, "Mexico City")
        self.assertEqual(matches[0].source_id, "group-a-20260611-mexico-south-africa")
        self.assertEqual(matches[0].start_utc, datetime(2026, 6, 11, 19, 0, tzinfo=timezone.utc))
        self.assertEqual(matches[-1].source_id, "match-089")
        self.assertEqual(matches[-1].home_team, "W74")
        self.assertEqual(matches[-1].location, "Philadelphia")


if __name__ == "__main__":
    unittest.main()

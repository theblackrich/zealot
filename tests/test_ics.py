from __future__ import annotations

import unittest
from datetime import datetime, timezone

from world_cup_calendar.ics import build_calendar, build_uid
from world_cup_calendar.models import MatchEvent
from world_cup_calendar.state import EventState


class IcsTests(unittest.TestCase):
    def setUp(self) -> None:
        self.event = MatchEvent(
            tournament="World Cup 2026",
            stage="Group A",
            start_utc=datetime(2026, 6, 24, 1, 0, tzinfo=timezone.utc),
            home_team="Mexico",
            away_team="South Korea",
            location="Guadalajara (Zapopan)",
        )

    def test_uid_is_stable_for_same_event(self) -> None:
        self.assertEqual(build_uid(self.event), build_uid(self.event))

    def test_sequence_only_increments_when_event_changes(self) -> None:
        uid = build_uid(self.event)
        _, state_one = build_calendar([self.event], {}, 135)
        _, state_two = build_calendar([self.event], state_one, 135)
        changed_event = MatchEvent(**{**self.event.__dict__, "location": "Mexico City"})
        _, state_three = build_calendar([changed_event], state_two, 135)

        self.assertEqual(state_one[uid].sequence, 0)
        self.assertEqual(state_two[uid].sequence, 0)
        self.assertEqual(state_three[uid].sequence, 1)

    def test_calendar_contains_uid_and_sequence(self) -> None:
        uid = build_uid(self.event)
        text, _ = build_calendar([self.event], {uid: EventState(sequence=4, fingerprint="changed")}, 135)

        self.assertIn(f"UID:{uid}", text)
        self.assertIn("SEQUENCE:5", text)


if __name__ == "__main__":
    unittest.main()

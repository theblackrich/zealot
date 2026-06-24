from __future__ import annotations

import unittest
from datetime import datetime, timezone

from world_cup_calendar.ics import build_calendar, build_uid
from world_cup_calendar.models import MatchEvent
from world_cup_calendar.state import EventState


class IcsTests(unittest.TestCase):
    def setUp(self) -> None:
        self.event = MatchEvent(
            source_id="group-a-20260624-mexico-south-korea",
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

    def test_knockout_placeholder_updates_keep_same_uid(self) -> None:
        placeholder = MatchEvent(
            source_id="match-089",
            tournament="World Cup 2026",
            stage="Round of 16",
            start_utc=datetime(2026, 7, 4, 21, 0, tzinfo=timezone.utc),
            home_team="W74",
            away_team="W77",
            location="Philadelphia",
        )
        resolved = MatchEvent(
            source_id="match-089",
            tournament="World Cup 2026",
            stage="Round of 16",
            start_utc=datetime(2026, 7, 4, 21, 0, tzinfo=timezone.utc),
            home_team="Germany",
            away_team="USA",
            location="Philadelphia",
        )

        placeholder_uid = build_uid(placeholder)
        resolved_uid = build_uid(resolved)
        _, placeholder_state = build_calendar([placeholder], {}, 135)
        _, resolved_state = build_calendar([resolved], placeholder_state, 135)

        self.assertEqual(placeholder_uid, resolved_uid)
        self.assertEqual(resolved_state[resolved_uid].sequence, 1)


if __name__ == "__main__":
    unittest.main()

from __future__ import annotations

import os
import unittest
from pathlib import Path
from unittest.mock import patch

from world_cup_calendar.config import DEFAULT_FILE_NAME, load_settings


class ConfigTests(unittest.TestCase):
    def test_directory_publish_override_appends_default_file_name(self) -> None:
        with patch.dict(os.environ, {"WORLD_CUP_PUBLISH_PATH": r"C:\Temp\Publish"}, clear=False):
            settings = load_settings()

        self.assertEqual(settings.publish_path, Path(r"C:\Temp\Publish") / DEFAULT_FILE_NAME)

    def test_file_publish_override_is_used_as_is(self) -> None:
        with patch.dict(os.environ, {"WORLD_CUP_PUBLISH_PATH": r"C:\Temp\custom.ics"}, clear=False):
            settings = load_settings()

        self.assertEqual(settings.publish_path, Path(r"C:\Temp\custom.ics"))


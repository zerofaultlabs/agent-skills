#!/usr/bin/env python3

import json
import subprocess
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).with_name("heartbeat_state.py")


class HeartbeatStateTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.state = Path(self.temp.name) / "state.json"

    def tearDown(self):
        self.temp.cleanup()

    def run_cmd(self, *args):
        result = subprocess.run(
            ["python3", str(SCRIPT), *args],
            check=True,
            capture_output=True,
            text=True,
        )
        return json.loads(result.stdout) if result.stdout else None

    def init(self):
        self.run_cmd(
            "init",
            "--state",
            str(self.state),
            "--checkpoint",
            "feedback=2026-08-08T14:00:00-07:00",
            "--checkpoint",
            "sermon=2026-08-02T16:00:00-07:00",
            "--checkpoint",
            "inspiration=2026-08-04T10:30:00-07:00",
        )

    def plan(self, now):
        return {
            item["workflow"]: item
            for item in self.run_cmd(
                "plan", "--state", str(self.state), "--now", now
            )["workflows"]
        }

    def test_wednesday_wake_recovers_missed_sunday_and_tuesday(self):
        self.init()
        plan = self.plan("2026-08-12T09:00:00-07:00")
        self.assertTrue(plan["feedback"]["due"])
        self.assertTrue(plan["sermon"]["due"])
        self.assertTrue(plan["inspiration"]["due"])

    def test_failure_does_not_advance_success(self):
        self.init()
        self.run_cmd(
            "fail",
            "--state",
            str(self.state),
            "--workflow",
            "sermon",
            "--now",
            "2026-08-12T09:10:00-07:00",
            "--error",
            "YouTube unavailable",
        )
        plan = self.plan("2026-08-12T10:00:00-07:00")
        self.assertTrue(plan["sermon"]["due"])
        self.assertEqual(plan["sermon"]["last_error"], "YouTube unavailable")
        state = json.loads(self.state.read_text())
        self.assertEqual(
            state["workflows"]["sermon"]["last_success_at"],
            "2026-08-02T16:00:00-07:00",
        )

    def test_completion_deduplicates_ids_and_clears_due(self):
        self.init()
        self.run_cmd(
            "complete",
            "--state",
            str(self.state),
            "--workflow",
            "sermon",
            "--now",
            "2026-08-12T09:30:00-07:00",
            "--processed-id",
            "youtube:abc123",
            "--processed-id",
            "youtube:abc123",
            "--output",
            "https://example.test/result",
        )
        plan = self.plan("2026-08-12T10:00:00-07:00")
        self.assertFalse(plan["sermon"]["due"])
        state = json.loads(self.state.read_text())
        self.assertEqual(
            state["workflows"]["sermon"]["processed_ids"], ["youtube:abc123"]
        )

    def test_before_tuesday_deadline_does_not_run_early(self):
        self.init()
        self.run_cmd(
            "complete",
            "--state",
            str(self.state),
            "--workflow",
            "inspiration",
            "--now",
            "2026-08-04T10:30:00-07:00",
        )
        plan = self.plan("2026-08-11T09:00:00-07:00")
        self.assertFalse(plan["inspiration"]["due"])


if __name__ == "__main__":
    unittest.main()

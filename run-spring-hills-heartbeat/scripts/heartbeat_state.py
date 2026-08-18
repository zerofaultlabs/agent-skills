#!/usr/bin/env python3
"""Plan and record idempotent Spring Hills heartbeat runs."""

from __future__ import annotations

import argparse
import json
import os
import tempfile
from datetime import datetime, timedelta
from pathlib import Path
from zoneinfo import ZoneInfo

TZ = ZoneInfo("America/Los_Angeles")
WORKFLOWS = {
    "feedback": {"kind": "daily", "hour": 14},
    "sermon": {"kind": "weekly", "weekday": 6, "hour": 14},
    "inspiration": {"kind": "weekly", "weekday": 1, "hour": 10},
}
MAX_IDS = 500


def parse_time(value: str) -> datetime:
    parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=TZ)
    return parsed.astimezone(TZ)


def iso(value: datetime) -> str:
    return value.astimezone(TZ).isoformat(timespec="seconds")


def blank_state() -> dict:
    return {
        "version": 1,
        "timezone": "America/Los_Angeles",
        "workflows": {
            name: {
                "status": "never",
                "last_attempt_at": None,
                "last_success_at": None,
                "cursor": None,
                "processed_ids": [],
                "outputs": [],
                "last_error": None,
            }
            for name in WORKFLOWS
        },
    }


def load_state(path: Path, allow_create: bool = False) -> dict:
    if not path.exists():
        if not allow_create:
            raise SystemExit(
                f"State file does not exist: {path}. Reconstruct checkpoints first, "
                "then run init with explicit --checkpoint values."
            )
        return blank_state()
    state = json.loads(path.read_text())
    if state.get("version") != 1 or not isinstance(state.get("workflows"), dict):
        raise SystemExit("Unsupported or invalid heartbeat state")
    for name in WORKFLOWS:
        if name not in state["workflows"]:
            raise SystemExit(f"Heartbeat state is missing workflow: {name}")
    return state


def save_state(path: Path, state: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    handle, tmp_name = tempfile.mkstemp(prefix=path.name, dir=path.parent)
    try:
        with os.fdopen(handle, "w") as tmp:
            json.dump(state, tmp, indent=2, sort_keys=True)
            tmp.write("\n")
        os.replace(tmp_name, path)
    finally:
        if os.path.exists(tmp_name):
            os.unlink(tmp_name)


def latest_occurrence(now: datetime, rule: dict) -> datetime:
    candidate = now.replace(hour=rule["hour"], minute=0, second=0, microsecond=0)
    if rule["kind"] == "daily":
        return candidate if candidate <= now else candidate - timedelta(days=1)
    days_back = (candidate.weekday() - rule["weekday"]) % 7
    candidate -= timedelta(days=days_back)
    if candidate > now:
        candidate -= timedelta(days=7)
    return candidate


def due_item(name: str, workflow: dict, now: datetime) -> dict:
    occurrence = latest_occurrence(now, WORKFLOWS[name])
    success = parse_time(workflow["last_success_at"]) if workflow["last_success_at"] else None
    due = success is None or success < occurrence
    return {
        "workflow": name,
        "due": due,
        "scheduled_through": iso(occurrence),
        "window_start": iso(success) if success else None,
        "window_end": iso(now),
        "previous_status": workflow["status"],
        "last_error": workflow.get("last_error"),
    }


def command_init(args: argparse.Namespace) -> None:
    path = Path(args.state)
    if path.exists() and not args.force:
        raise SystemExit(f"Refusing to overwrite existing state: {path}")
    state = blank_state()
    for value in args.checkpoint:
        name, timestamp = value.split("=", 1)
        if name not in WORKFLOWS:
            raise SystemExit(f"Unknown workflow in checkpoint: {name}")
        state["workflows"][name]["last_success_at"] = iso(parse_time(timestamp))
        state["workflows"][name]["status"] = "success"
    save_state(path, state)
    print(json.dumps(state, indent=2, sort_keys=True))


def command_plan(args: argparse.Namespace) -> None:
    state = load_state(Path(args.state))
    now = parse_time(args.now)
    plan = [due_item(name, state["workflows"][name], now) for name in WORKFLOWS]
    print(json.dumps({"now": iso(now), "workflows": plan}, indent=2, sort_keys=True))


def command_begin(args: argparse.Namespace) -> None:
    path = Path(args.state)
    state = load_state(path)
    workflow = state["workflows"][args.workflow]
    workflow["status"] = "running"
    workflow["last_attempt_at"] = iso(parse_time(args.now))
    workflow["last_error"] = None
    save_state(path, state)


def command_complete(args: argparse.Namespace) -> None:
    path = Path(args.state)
    state = load_state(path)
    workflow = state["workflows"][args.workflow]
    now = iso(parse_time(args.now))
    workflow["status"] = "success"
    workflow["last_attempt_at"] = workflow["last_attempt_at"] or now
    workflow["last_success_at"] = now
    if args.cursor is not None:
        workflow["cursor"] = args.cursor
    workflow["processed_ids"] = list(
        dict.fromkeys(workflow["processed_ids"] + args.processed_id)
    )[-MAX_IDS:]
    workflow["outputs"] = args.output[-20:]
    workflow["last_error"] = None
    save_state(path, state)


def command_fail(args: argparse.Namespace) -> None:
    path = Path(args.state)
    state = load_state(path)
    workflow = state["workflows"][args.workflow]
    workflow["status"] = "failed"
    workflow["last_attempt_at"] = iso(parse_time(args.now))
    workflow["last_error"] = args.error
    save_state(path, state)


def parser() -> argparse.ArgumentParser:
    root = argparse.ArgumentParser()
    sub = root.add_subparsers(dest="command", required=True)
    init = sub.add_parser("init")
    init.add_argument("--state", required=True)
    init.add_argument("--checkpoint", action="append", default=[])
    init.add_argument("--force", action="store_true")
    init.set_defaults(func=command_init)
    plan = sub.add_parser("plan")
    plan.add_argument("--state", required=True)
    plan.add_argument("--now", required=True)
    plan.set_defaults(func=command_plan)
    for name, func in (("begin", command_begin), ("fail", command_fail)):
        item = sub.add_parser(name)
        item.add_argument("--state", required=True)
        item.add_argument("--workflow", choices=WORKFLOWS, required=True)
        item.add_argument("--now", required=True)
        if name == "fail":
            item.add_argument("--error", required=True)
        item.set_defaults(func=func)
    complete = sub.add_parser("complete")
    complete.add_argument("--state", required=True)
    complete.add_argument("--workflow", choices=WORKFLOWS, required=True)
    complete.add_argument("--now", required=True)
    complete.add_argument("--cursor")
    complete.add_argument("--processed-id", action="append", default=[])
    complete.add_argument("--output", action="append", default=[])
    complete.set_defaults(func=command_complete)
    return root


if __name__ == "__main__":
    arguments = parser().parse_args()
    arguments.func(arguments)

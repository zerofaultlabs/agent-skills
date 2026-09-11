---
name: run-spring-hills-heartbeat
description: Reconcile and run Spring Hills Church production work that is due or was missed while a Mac, ChatGPT desktop app, or local project was unavailable. Use for scheduled or manual Spring Hills heartbeats, offline catch-up, feedback collection, Sunday sermon processing, Tuesday inspiration scouting, deduplication, retrying incomplete work, and maintaining per-workflow checkpoints. Coordinate the installed Spring Hills content skills without replacing their editorial instructions.
---

# Run Spring Hills Heartbeat

Treat the schedule as a wake-up signal, not proof that earlier work ran. On every wake, calculate work due since each workflow's last verified success and reconcile the full gap.

## Sources of truth

Read the project `AGENTS.md` first. Use:

- Spring Hills Tracker `1_jvc-LGHrvD68_aYv7PEdMHCuMJZdnua8AMHhOeT54k` as working memory and audit trail.
- `#sh-agent-log` `C0BJYFN7CBS` for material activity.
- `#sh-feedback` `C0BJ7HML736` for Nastia's judgment.
- `#sh-general` `C0BJRTHN5G8` as an additional feedback-intake channel when Nastia discusses Spring Hills work there.
- `#sh-ideas` `C0BM6VDL4FM` for qualifying inspiration.
- `work/spring-hills-heartbeat-state.json` in the project as the fast local ledger.

Read [references/workflows.md](references/workflows.md) before a scheduled run.

## Reconciliation workflow

1. Locate the project root and ledger. If the ledger is absent, reconstruct safe starting checkpoints from the tracker, Slack, local artifacts, and stable source IDs before creating it. Never assume an empty ledger means all historical work is due.
2. Run `scripts/heartbeat_state.py plan --state <path> --now <ISO-8601>` to calculate due workflows.
3. For each due workflow, inspect its entire returned window. A workflow can be due on Wednesday because a Sunday or Tuesday run was missed.
4. Before external writes, search the tracker, Slack, and local artifacts for the stable item ID. Reuse or finish existing work instead of reposting it.
5. Mark an attempt with `begin`. Run the appropriate installed skill and follow its instructions exactly.
6. Verify every required artifact and external write. Then use `complete`, recording the new source cursor, processed stable IDs, and output links.
7. On failure or blocked access, use `fail`. Do not move the success checkpoint. The workflow remains due on a later wake.
8. Stay silent when nothing is due and no new finding exists.

## Stable IDs

- Feedback: Slack channel ID + parent message timestamp + reply/reaction identifier.
- Sermon: YouTube video ID, with service date as supporting metadata.
- Inspiration: canonical source-post URL; use account + provider post ID when necessary.
- Skill release: approved Git commit or release identifier when update distribution is implemented.

Keep only the newest 500 processed IDs per workflow in the local ledger. The tracker and external systems remain the durable cross-machine audit record.

## Workflow routing

- `feedback`: Read all new reactions and thread replies in `#sh-feedback` since the Slack cursor. Also inspect new Spring Hills-related messages from Nastia in `#sh-general`; treat them as feedback intake and acknowledge or continue them in a thread under her message. Channel history orders parent messages, so do not rely on parent timestamps alone: inspect any visible thread whose `latest_reply` is newer than the last verified success, even when its parent is older. Every new Nastia reply must receive the promised follow-through in that same thread, or a brief same-thread acknowledgement that names the remaining action. Follow the existing standalone-message and Quick view rules. Update the tracker without duplicates.
- `sermon`: Find every unprocessed official Sunday sermon in the due window that remains useful for the current content cycle. Run `youtube-sermon-transcript`, then `create-spring-hills-sermon-content` with `write-spring-hills-social`. Do not recreate a package already identified by YouTube ID. Use the sermon skill's one-screen Quick view for Nastia; keep the full brief as an artifact.
- `inspiration`: Scan from the last verified boundary through now. Run `scout-spring-hills-content-ideas`; preserve its evidence thresholds, use its Nastia Quick view, and allow zero findings.

Process oldest due items first. If several missed sermons exist, do not flood `#sh-feedback`: prepare current useful work first, record older items as recovered references or explicitly stale, and explain that judgment in `#sh-agent-log`.

## Completion requirements

Advance a workflow's `last_success_at` only after all required actions for its inspected window are verified. A no-findings inspiration scan counts as successful when the required sources were actually inspected and the access/no-findings result was logged correctly.

For feedback, reconcile the set of thread replies and reactions against `processed_ids` before advancing the cursor. Do not mark success merely because the channel read completed. A choice such as A/B/C remains incomplete until the promised next-stage deliverable or an explicit same-thread status reply has been posted and verified.

Never let one failed workflow prevent independent due workflows from running. Summarize successes and remaining failures at the end.

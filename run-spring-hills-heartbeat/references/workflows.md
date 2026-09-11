# Workflow schedule and verification

All times use `America/Los_Angeles`. The heartbeat may wake more often than any workflow is due.

| Workflow | Nominal cadence | Catch-up rule | Verified completion |
|---|---|---|---|
| Feedback | Daily by 2:00 PM | Read `#sh-feedback` and Spring Hills-related messages from Nastia in `#sh-general` from the last stored Slack cursor through the current run. Also inspect threads whose latest reply is newer than the last success even when the parent is older. | Every new response receives same-thread follow-through or an explicit status acknowledgement; promised deliverables, tracker rows, stable IDs, and material activity are verified. A verified no-change check may advance success. |
| Sermon | Sunday after the newest official service is available | On any later wake, inspect official sermons since the last verified boundary. Process each unprocessed sermon still useful to the current content cycle. | Transcript artifacts, direction brief, Slack feedback item, tracker audit row, source video ID, and activity log are verified. |
| Inspiration | Tuesday by 10:00 AM; 30-day emphasis on the first Tuesday | On any later wake, scan from the last verified boundary through now. Do not restrict execution to Tuesday. | Required sources were inspected, qualifying ideas were posted and recorded without duplicates, or a no-findings/access-limited result was logged. |

## Freshness policy

- Prefer the current week's sermon package.
- Do not post several overdue feedback items merely to replay a schedule.
- Mark work `stale` only when producing it would no longer help Nastia. Log the source, scheduled occurrence, and reason.
- A stale occurrence is not a silent success: record it in the tracker or activity log and include its stable source ID so later runs do not reconsider it indefinitely.

## Ledger rules

- `last_attempt_at` records every attempt.
- `last_success_at` means the entire inspected window was reconciled and verified.
- `cursor` stores the provider boundary needed for the next incremental read.
- `processed_ids` prevents duplicate external output.
- `status` is `never`, `running`, `success`, or `failed`.
- `last_error` preserves a concise retry reason.
- `outputs` stores the most recent useful Slack, tracker, or artifact links.

If local state conflicts with Slack, YouTube, artifacts, or the tracker, trust the verified external evidence and repair the ledger before continuing.

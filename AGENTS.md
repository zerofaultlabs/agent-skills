# Repository development guidance

## Canonical source and scope

- This repository is the canonical source for every skill maintained here. Read README, the affected `SKILL.md`, and relevant supporting files before editing.
- Make changes in this checkout first. Installed skill folders are deployment copies; compare and reconcile drift before updating them. Do not import an installed edit without reviewing its purpose.
- Track development work in GitHub issues. Reference the issue in implementation PRs and record material findings, decisions, validation results, and remaining limitations there. Close an issue only when its acceptance criteria are fulfilled and the change is integrated.
- Preserve confirmed editorial rules and distinguish them from observed patterns or hypotheses. Keep case-specific historical answers outside production skills.

## Validation and distribution

- Keep skill instructions, agent metadata, and local reference links consistent. Declare companion dependencies in README when routing changes.
- Run applicable existing checks and validate changed skill structure. Use meaningful regression tests for behavior changes; documentation-only migration does not require new behavioral tests.
- Review the complete diff, including added files, before committing. Keep changes focused on the referenced issue.
- Distribute reviewed repository revisions. Check installed differences first and preserve local work. Release automation and the updater remain planned until their issues land; do not describe them as existing capabilities.
- Keep source media, runtime state, credentials, private feedback, and historical evaluation answer keys outside skill folders and distributable artifacts. Include only intentional skill resources in packages.

## Production context

README defines the working-memory roles. This file governs development, not production scheduling. The heartbeat's project guidance and ledger belong in a separate production workspace; identify that workspace and its configuration before running production workflows.

Editing a skill does not itself request a heartbeat run, a content package, or a message to Nastia. Use GitHub issues for development records. When production work is authorized, follow the invoked skill's tracker and Slack routing rules, including same-thread follow-through in `#sh-general`.

# agent-skills

Canonical source for the Spring Hills Church social-media skills. Make and review changes here, then distribute the reviewed revision to installed copies.

## Skills and dependencies

Each linked folder contains its instructions, references, and agent metadata. Install dependencies alongside the selected skill.

| Skill | Purpose | Required companion skills |
| --- | --- | --- |
| [write-spring-hills-social](write-spring-hills-social/SKILL.md) | Shared voice, church context, and safeguards | None |
| [create-spring-hills-caption](create-spring-hills-caption/SKILL.md) | Captions from photos, briefs, or selected content | `write-spring-hills-social` |
| [youtube-sermon-transcript](youtube-sermon-transcript/SKILL.md) | Prepare captions and organize a timestamped sermon | None |
| [create-spring-hills-sermon-content](create-spring-hills-sermon-content/SKILL.md) | Sermon directions, carousels, graphics, and reels | `write-spring-hills-social` |
| [scout-spring-hills-content-ideas](scout-spring-hills-content-ideas/SKILL.md) | Source-backed inspiration and adaptation | `write-spring-hills-social` for public-facing copy |
| [run-spring-hills-heartbeat](run-spring-hills-heartbeat/SKILL.md) | Reconcile feedback, sermons, and inspiration after missed runs | `youtube-sermon-transcript`, `create-spring-hills-sermon-content`, `write-spring-hills-social`, `scout-spring-hills-content-ideas` |

Caption and inspiration requests that need sermon moment selection route to `create-spring-hills-sermon-content`. A supplied transcript can enter that skill directly; a YouTube/VTT source first uses `youtube-sermon-transcript`. Install all six folders for the complete Spring Hills workflow.

The Python helpers require Python 3.10 or newer. YouTube caption acquisition additionally requires `yt-dlp`; local VTT preparation uses only the standard library. The transcript helper does not implement audio transcription. Content skills need an agent capable of reading their source material; live discovery and production reconciliation also need access to the relevant web, Slack, and Google Drive sources.

## Installation and updates

Use a reviewed Git revision of this repository. Copy each selected skill folder intact, including `SKILL.md`, `agents/`, `references/`, and `scripts/` where present, into the target environment's skill directory. For this project's local installation, that directory is `~/.codex/skills/`.

Before replacing an existing copy, compare its files with the chosen repository revision and preserve any local differences. Resolve intended changes in the repository first. Record the revision installed and verify that copied files match it. A developer may instead link a skill folder to a dedicated checkout, understanding that checkout edits become active immediately.

Automated ZIP releases and verified updates are planned in [#8](https://github.com/zerofaultlabs/agent-skills/issues/8) and [#9](https://github.com/zerofaultlabs/agent-skills/issues/9). No releases were listed during the issue #1 inventory. Until that work lands, installation and update verification are manual; do not assume a suite ZIP or updater exists.

## Development and validation

Read [AGENTS.md](AGENTS.md) before editing. Track work in [GitHub issues](https://github.com/zerofaultlabs/agent-skills/issues); [#10](https://github.com/zerofaultlabs/agent-skills/issues/10) records the review and implementation sequence.

For a skill change, read its instructions and affected references, check local reference paths and companion dependencies, and inspect the final diff. When the skill-creator validator is available, run its `scripts/quick_validate.py` against each changed skill. This checks structure, not editorial quality.

Run the current executable tests from the repository root:

```bash
python3 -B run-spring-hills-heartbeat/scripts/test_heartbeat_state.py
git diff --check
```

The existing suite contains four heartbeat tests. Transcript regressions, final artifact validation, editorial evaluations, and CI are tracked in [#2](https://github.com/zerofaultlabs/agent-skills/issues/2), [#4](https://github.com/zerofaultlabs/agent-skills/issues/4), [#5](https://github.com/zerofaultlabs/agent-skills/issues/5), and [#7](https://github.com/zerofaultlabs/agent-skills/issues/7). Use each content skill's validation protocol for semantic review; passing structural checks does not establish transcript fidelity or editorial quality.

## Production project and working memory

This checkout maintains skill source. A separate production project owns source media, generated content, credentials, and runtime state. The heartbeat's instruction to read the project `AGENTS.md` refers to that production project's operating configuration; this repository's `AGENTS.md` governs skill development. Identify the production project before running the heartbeat.

| Location | Role |
| --- | --- |
| Spring Hills Tracker | Working memory and durable audit trail |
| `#sh-agent-log` | Material work, findings, decisions, and changes |
| `#sh-feedback` | Questions requiring Nastia's judgment |
| `#sh-ideas` | Qualifying inspiration ideas |
| `#sh-general` | Additional intake when Nastia discusses Spring Hills work there; follow up in the originating thread |
| Production project's `work/spring-hills-heartbeat-state.json` | Fast local reconciliation ledger |
| GitHub issues, PRs, and releases | Implementation scope, reviewed skill changes, and distribution history |

Existing tracker/channel identifiers and cadence remain in the [heartbeat skill](run-spring-hills-heartbeat/SKILL.md) and its [workflow reference](run-spring-hills-heartbeat/references/workflows.md). Keep credentials, private feedback, runtime ledgers, source media, generated deliverables, and historical evaluation answer keys outside skill folders and release bundles.

## Canonicalization record

Issue [#1](https://github.com/zerofaultlabs/agent-skills/issues/1), September 15, 2026:

- Imported the installed voice, caption, and inspiration skills and supporting files as migration inputs. Future edits originate here.
- Preserved caption and inspiration content, normalizing trailing blank lines in two caption references. In the voice examples, replaced one dated historical comparison with its transferable selection rule so the production skill does not contain that case's answer.
- Preserved existing sermon-content and heartbeat files, which matched installed copies.
- Reconciled the installed-only WAV cleanup rule as conditional guidance, preserving user audio and failed-run recovery without implying an implemented audio fallback.
- Installed directories were left intact. Their migration differences are intentional until a reviewed revision is installed.

## License

Licensed under the [MIT License](LICENSE).

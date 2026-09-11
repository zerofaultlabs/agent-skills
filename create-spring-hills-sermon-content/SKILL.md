---
name: create-spring-hills-sermon-content
description: Turn a Spring Hills Church sermon transcript into evidence-backed social content concepts and finished copy. Use when Codex needs to analyze a sermon, rank content moments, select a 60–90 second reel, propose a carousel or graphic, identify hooks and timestamps, write captions, build a Tuesday/Thursday sermon-content package, or evaluate sermon-derived ideas against Nastia’s known editorial choices. Use the installed write-spring-hills-social skill as the voice layer.
---

# Create Spring Hills Sermon Content

Turn one sermon into a focused, usable social package without treating the transcript as a list of equally important moments.

## Load the source and references

1. Read the full supplied sermon transcript, including its title, passage, chapters, and timestamps when available.
2. Read `references/editorial-selection.md` before ranking moments.
3. Read `references/output-package.md` before drafting deliverables.
4. Read `references/validation-protocol.md` when running a historical test or resolving competing moments.
5. Invoke or read `$write-spring-hills-social` before writing public-facing copy. Its voice, church context, approved examples, and safeguards govern all finished copy.

Do not infer a speaker identity, quotation, Scripture reference, timestamp, event detail, or theological claim that the source does not establish.

## Build the sermon map

Capture only source-grounded information:

- sermon title, date, passage, and named speaker if explicitly present;
- central biblical truth in one sentence;
- the human problem or felt need;
- the Christ, gospel, or Scripture anchor;
- one to three supported responses;
- distinct sections and their timestamp ranges;
- vivid anecdotes, illustrations, logistics, or asides that may distract from the central message.

If the transcript has no timestamps, continue with concept and copy development but label reel timing as unavailable. Never estimate or fabricate timestamps.

## Rank candidate moments

Identify three to six candidates, then apply the rubric in `references/editorial-selection.md`. Rank by biblical importance, audience relevance, usefulness, completeness, format fit, and freshness—not novelty alone.

Reject or demote a candidate when it:

- is a memorable but secondary anecdote;
- requires substantial missing context;
- leaves the audience in diagnosis without supported hope;
- duplicates the companion post without a distinct role;
- depends on an uncertain paraphrase, attribution, or theological leap;
- is mostly service logistics, an introduction, or an aside.

Allow a self-contained opening, transition, or pastoral application to outrank the formal outline only when it is faithful, complete, and clearly stronger for short-form content. Label this as an editorial recommendation, not as a known Nastia preference.

## Select the weekly treatment

Choose one recommended Tuesday treatment and one recommended Thursday reel.

Build the carousel and reel candidate lists independently. Scan the entire sermon for reel candidates, including the opening, transitions, pastoral applications, and conclusion; do not inherit the carousel thesis automatically.

- Let the carousel teach, explain, or progress through one idea.
- Let the reel deliver one emotionally and theologically complete moment.
- Make the two pieces complementary rather than repetitive. Reject a reel candidate that mainly restates the carousel’s teaching role when another faithful, self-contained Christ- or gospel-centered moment is available.
- Prefer one clear takeaway or one to three memorable actions over a sermon summary.
- Move from the human problem toward Christ, Scripture, and a hopeful response.
- Target 60–90 seconds for a reel. Select an exact start and end from the transcript and ensure the clip begins intelligibly and lands a complete thought.
- Let a complete, faithful gospel application outrank the formal outline for the reel when it is substantially stronger as a self-contained short-form message. Explain the tradeoff and label it as a recommendation when the pattern is not confirmed.
- Before choosing the reel, include at least one candidate from the sermon’s strongest direct Christ/gospel reassurance, even when it appears outside the formal outline. Compare it against the best outline-based clip on audience usefulness, emotional completeness, and differentiation from Tuesday.

If a graphic is stronger than a carousel, recommend it and explain why. Do not force every sermon into every format.

## Use the two-stage editorial workflow

Follow `references/output-package.md`.

Default to **Stage 1: Sermon Direction Brief** when the user wants to explore what to make, test creative judgment, or involve Nastia before production. Present three genuinely different paired weekly directions. Each direction must include a concrete working title for Tuesday's graphic or first carousel slide, plus the Thursday reel's verified start timestamp, end timestamp, and duration. It must also explain Tuesday's role, Thursday's role, audience value, main strength, and caution. Recommend one direction, then stop for a choice. Do not write the finished carousel, reel package, or captions yet.

Continue to **Stage 2: Production Package** only after the user or Nastia chooses a direction. Build the exact Tuesday and Thursday deliverables for that direction and preserve the choice as the governing editorial decision.

If the user explicitly asks for a full package immediately, give a concise three-direction comparison, state the recommendation, and then continue automatically with the recommended direction unless the user names another. Include alternatives only when a genuine production-level choice remains; provide no more than two.

For transcript excerpts:

- preserve the speaker’s meaning;
- distinguish exact transcript wording from a social hook or paraphrase;
- use ellipses only when the omission does not change meaning;
- flag obvious transcription uncertainty rather than silently repairing a consequential word;
- never present polished social copy as a direct pastor quotation.

## Validate before returning

Confirm that:

- the central truth, application, and Scripture are faithful to the source;
- the chosen reel is complete, supported, and within the requested duration;
- a vivid anecdote did not win merely because it was memorable;
- carousel and reel have distinct jobs;
- captions follow `$write-spring-hills-social`;
- all timestamps and quoted words are traceable;
- uncertainty is explicit;
- the output is ready to use and does not make Nastia repeat analysis already available in the transcript.

When back-testing, keep historical posts and answer keys outside the skill folder. Generate and seal the source-only result before revealing the expected post or editorial choice.

## Request editorial feedback

When sending a comparison to Nastia, make the evidence understandable without requiring her to open the tracker:

- Use progressive disclosure. Put a **Quick view** in the standalone message and move optional reasoning to its thread, an attachment, the tracker, or `#sh-agent-log`.
- Optimize the Quick view for a 10–20 second first read and approximately one phone screen. Use short sentences and everyday labels.
- For Stage 1, show the sermon link, a one-sentence sermon idea, exactly three choices, the recommendation near the top, and one action: reply **A**, **B**, **C**, or **use your recommendation**. For every choice, show the Tuesday format and proposed cover/title, then the Thursday reel's exact timestamp range and duration. Use compact labels so the message remains easy to scan.
- Do not put the full sermon snapshot, audience value, strength, caution, and rejected-direction analysis in the standalone decision message. Preserve those details in the internal artifact or an optional thread reply.
- For Stage 2, begin with **What to use**: Tuesday format/headline, Thursday timestamps, captions or artifact links, and only the facts that still need verification. Put edit notes and source analysis after the usable deliverables or in an attachment.
- link directly to every Instagram post or reel being evaluated;
- link the source sermon when it helps identify the week;
- state whether the post-to-sermon relationship is **confirmed** or only a **possible match**;
- describe the original published choice, the generated or refined alternative, and the exact difference being tested;
- ask separately for match confirmation and creative judgment when the relationship is uncertain;
- keep each feedback item in one standalone Slack message and handle clarifying questions in that message's thread;
- use the spreadsheet as the audit trail, not as the primary explanation.

Never describe a possible historical match as Nastia's sermon selection. Do not train on her preference until the match is confirmed.

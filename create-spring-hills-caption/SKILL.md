---
name: create-spring-hills-caption
description: Create ready-to-use Spring Hills Church social captions from photos, a brief description, event details, a post theme, carousel or graphic copy, a reel summary, an existing draft, or a desired call to action. Use for weekend invitations, service photos, event promotions and recaps, community posts, testimonies, holidays, pastor appreciation, ministry updates, and non-transcript sermon content. Minimize follow-up prompting while using the installed write-spring-hills-social skill as the authoritative voice layer.
---

# Create Spring Hills Caption

Draft one polished caption from the smallest useful brief while protecting factual and theological accuracy.

## Load the voice and routing guidance

1. Read `$write-spring-hills-social` and its references before drafting. Apply its voice, church context, approved patterns, and safeguards.
2. Read `references/input-routing.md` to decide whether to draft, flag a fact, or ask one question.
3. Read `references/caption-patterns.md` for the selected post type.
4. Read `references/validation-protocol.md` when validating behavior or resolving an unfamiliar input.

If the user supplies a full sermon transcript or asks for moment selection, timestamps, a carousel, or a weekly sermon package, use `$create-spring-hills-sermon-content` instead. Use this skill for a caption when the reel, post, or theme is already known.

## Build a compact brief

Derive what is available without making the user restate it:

- post type and what the audience will see;
- one primary message or feeling;
- intended response;
- exact names, dates, times, locations, links, and registration status;
- supported Scripture, sermon truth, testimony, or ministry context;
- campaign wording or CTA supplied by the user.

Do not require every field. Draft when the known facts are enough for an accurate caption.

## Handle photos safely

Inspect supplied photos before drafting.

- Describe only clearly visible people, actions, setting, objects, and overall energy.
- Use a shared theme across multiple photos instead of narrating every image.
- Do not identify a person, ministry, event, relationship, role, age, emotion, disability, ethnicity, or spiritual decision unless the user or reliable metadata provides it.
- Do not claim a service was full, lives were changed, someone was baptized, or people made decisions for Jesus based on appearance alone.
- If the images support a general community or recap caption, draft one without asking for the event name.
- Ask one concise question only when naming the event, person, testimony, or next step is essential to the requested caption.

## Draft with minimal prompting

Follow the decision rules in `references/input-routing.md`.

1. Choose one primary angle that complements the visual rather than repeating it.
2. For an event invitation, lead with a safe audience benefit or felt need derived from the verified event purpose before naming the event or logistics. Do not open with “Event name is tonight” when the supplied activities support a warmer benefit-led opening.
3. Write the finished caption first.
4. Keep short paragraphs and natural second-person or collective language.
5. Use one primary CTA only when it follows from the post.
6. Preserve exact official names and supplied logistics.
7. For appreciation copy, move from the supplied qualities directly to the participation CTA. Do not add generic praise, biography, impact, leadership, care, or celebration filler that was not in the brief.
8. Omit unknown optional facts instead of inserting placeholders into otherwise publishable copy.
9. Add a short `Verify:` line after the caption only when a material fact must be confirmed before publishing.

Default to one caption. Provide up to three meaningfully different versions only when requested or when the creative direction is genuinely open.

## Apply factual and theological safeguards

- Never invent logistics, registration status, URLs, attendance, outcomes, quotations, testimonies, Scripture references, or pastor wording.
- Never turn a paraphrase into a quotation.
- Never promise a particular spiritual result from attending, praying, giving, or participating.
- For sensitive doctrine, personal testimony, pastoral attribution, a child’s identity, or a potentially controversial claim, request the missing authoritative detail or flag review.
- Use a generic invitation such as “We’d love to see you” only when it remains truthful without missing logistics.
- When the brief gives changing facts, treat them as authoritative for the draft but surface obvious conflicts.

## Return the result

Return:

1. the ready-to-use caption;
2. one `Verify:` line only if necessary;
3. no process explanation unless requested.

When delivering a caption to Nastia in Slack, start with **Ready to use** and put the caption first. Keep any `Verify:` item to one short line. Move optional rationale, alternatives, and process notes to the thread or omit them.

Before returning, confirm the caption is accurate, warm, newcomer-friendly, mobile-readable, not corporate, not repetitive, restrained in emoji and CTA use, and consistent with `$write-spring-hills-social`.

When back-testing, keep historical captions and answer keys outside the skill folder. Generate and seal the source-only caption before revealing what was published.

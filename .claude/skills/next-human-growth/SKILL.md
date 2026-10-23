---
name: next-human-growth
description: "Growth system for Next Human (@nnexthuman): reads every metric of every reel, diagnoses what failed and what worked, runs experiments, and updates the living playbook so each new reel is better than the last. Use for the mid-day and evening reviews, before writing or rendering any new reel (pre-production check), when generating reel ideas, and whenever Graziano asks why a reel did well or badly."
---

# Next Human growth system

The goal: more watch time, more sends, more saves, more follows, every day. This skill is the loop that gets
there. It never guesses when data exists, it never changes more than it can measure, and it writes down what
it learned so the next session starts smarter.

Files (all in the repository):
- `growth/playbook.md`: the living rules. Every rule has a status (PROVEN, TESTING, IDEA, REJECTED), the
  evidence behind it and the date. The production of every reel follows the PROVEN and TESTING rules.
- `growth/experiments.json`: one entry per experiment: hypothesis, variable, variants, which episodes carry
  which variant, the metric that decides, the result.
- `growth/learnings.md`: dated log of what each review learned (newest first). Short, factual.
- `growth/catalog.json`: attributes of every episode (duration, hook, topic, pillar, format, tags). Add a row
  for every new episode the same day it is rendered (see "Pre-production").
- `growth/ideas.md`: the idea bank, ranked; ideas from the research and from what the data says works.
- `stats/*.json`: data written by `python3 stats.py` (reels, daily history, comments, snapshots).

References (method, read when needed):
- `references/diagnose.md`: the ordered diagnosis of one reel against our metrics.
- `references/hooks-and-retention.md`: hook archetypes, the 3-second cliff, retention structure for our timer
  format.
- `references/sends-and-captions.md`: how to earn DM sends and saves; captions, CTAs, pinned comment.
- `references/virality-research.md`: studies and platform statements the playbook is built on.
- `references/competitors.md`: channels with similar formats and the patterns to replicate.
Parts of these references are adapted from vyralcontent/content-skills (MIT, see
`references/LICENSE-vyral-content-skills.txt`).

## Non-negotiables

1. Every claim in a reel stays true. Hype lives in the tone, the framing and the open loops, never in invented
   or inflated facts. Health content: no dosing, no personal medical advice.
2. Judge by rates, not totals: skip rate, watch %, sends per reach, saves per reach, follows. Totals only for
   context.
3. One variable at a time per experiment, with at least 3 reels per variant before calling a winner. One
   outlier never changes a PROVEN rule.
4. Compare each reel with the account's own baseline (median of the last 10 reels), not with other accounts.
5. Never touch approved captions, videos or times in `queue.json` (CLAUDE.md rules). Suggestions go to the
   review and to Graziano.

## Mode A: review (mid-day ~13:05 and evening ~23:05)

1. Run `python3 stats.py`. Read its output, `stats/reels.json`, `stats/history.json`, `stats/comments.json`,
   the last 2 days of `stats/snapshots.jsonl`, `growth/playbook.md`, `growth/experiments.json` and the last
   entries of `growth/learnings.md`.
2. Baseline: compute the median skip %, watch %, share/save/like rate per reach and views per hour of the
   last 10 Instagram reels (fewer if the account is new; say so).
3. Diagnose every reel younger than 72 h with `references/diagnose.md`: name the earliest failing lever with
   its number versus baseline ("skip 51% vs baseline 44%: hook failed"). For the best reel, name what made it
   work (hook type, topic, length, slot).
4. Velocity: from the snapshots, views per hour since the last read for each reel; flag reels still growing
   (keep pushing that format) and reels that stopped.
5. Comments: read every new comment; note questions (future reel ideas), objections (facts to double check)
   and the words people use (caption keywords).
6. Experiments: for each open experiment in `growth/experiments.json`, add the new numbers; when a variant has
   3+ reels, compare medians, write the result, and update the rule in `growth/playbook.md` (TESTING to
   PROVEN or REJECTED, with the evidence and date).
7. Write `stats/notes.json` (rows `{date, order, kind, text}`): order 1 "Sintesi" (key numbers and the change
   since the last review), then "Funziona", "Non funziona", and 3 "Da cambiare" (concrete, numbered, each
   tied to a number). Mid-day review: mark it "meta' giornata" in the Sintesi.
8. Append to `growth/learnings.md` (date, 3-6 lines: what we learned, with numbers). Add new hypotheses as
   IDEA rules in the playbook; propose the next experiment if none is open.
9. Commit `stats/` and `growth/` on main and push. Update the dashboard (CLAUDE.md, Statistiche) by uploading
   `stats/reels.json`, `stats/daily.json`, `stats/notes.json` as assets and updating their `datasets/*`
   documents.
10. Reply in Italian, short: key numbers, the 3 changes, any rule that changed status.

## Mode B: pre-production (before scripting any reel)

1. Read `growth/playbook.md` and the open experiments. Every new reel follows all PROVEN rules and carries
   exactly the variant its experiment assigns.
2. Score the draft against the checklist below; fix every NO before rendering.
3. After rendering, add the episode to `growth/catalog.json` (episode, title, pillar, topic, caption_match
   regex matching the caption's first line, slot, duration_s, segments, hook, intro_segment,
   first_timer_at_s, scenes, booms, bg_fx, music_mode, format, tags including the experiment variant).

Pre-production checklist (all YES):
- First frame: the subject and the key number or claim are on screen at frame 1 (no title card, no subtitle
  intro, no empty scene).
- Hook names the viewer or a situation they recognise ("your", a time, a habit) or a shocking true number, in
  max 8 words of on-screen text.
- Hook promise is paid off before the end; there is a re-hook ("but...", "the catch") around the middle.
- Length follows the playbook rule for length; a change of shot, number or text every 2-3 s.
- One shareable payoff a specific person needs ("send this to the friend who...") and the CTA names that
  person.
- Caption first line = the hook with the topic keyword; 3-5 hashtags; source line.
- Every fact checked against a source; the caveat is there when evidence is weak.

## Mode C: ideas

Generate ideas from: (1) the PROVEN topics and hook types in the playbook, (2) the competitor patterns in
`references/competitors.md`, (3) questions in the comments, (4) this week's news. Rank by expected sends and
watch %, not by personal taste. Write them to `growth/ideas.md` with the rule each idea exploits.

## How the system improves itself

Each review either confirms a rule, rejects it, or adds a new hypothesis. Rules carry the evidence that
promoted them, so a later session can see why. When a PROVEN rule starts failing (3 reels in a row below
baseline on the metric it was proven on), set it back to TESTING and say so in the review. Keep the playbook
short: merge duplicates, delete REJECTED rules older than 30 days after moving the lesson to learnings.
